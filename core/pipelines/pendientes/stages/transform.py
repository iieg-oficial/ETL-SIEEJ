from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

import geopandas as gpd

from core.pipelines.pendientes.config import settings
from core.pipelines.pendientes.constants import (
    ANALYTIC_DEM_FILENAME,
    AOI_FILENAME,
    AOI_TERRITORIAL_LAYER,
    CLASSIFICATION_SOURCES,
    DEGREES_CLASSIFICATION,
    EXTRACT_MANIFEST_FILENAME,
    FINAL_ANALYTICAL_DIRECTORY_NAME,
    FINAL_CARTOGRAPHIC_DIRECTORY_NAME,
    FINAL_DEGREES_CLASSIFIED_FILENAME,
    FINAL_DIRECTORY_NAME,
    FINAL_ELEVATION_Q10_FILENAME,
    FINAL_INTERMEDIATE_DIRECTORY_NAME,
    FINAL_MUNICIPAL_STATISTICS_FILENAME,
    FINAL_PERCENT_CLASSIFIED_FILENAME,
    FINAL_TABLE_DIRECTORY_NAME,
    FINAL_TRANSFORM_MANIFEST_FILENAME,
    GAUSSIAN_SIGMA_METRES,
    GAUSSIAN_SIGMA_PIXELS,
    GAUSSIAN_TILE_SIZE_PIXELS,
    GAUSSIAN_TRUNCATE,
    MUNICIPAL_INDICATOR_IDS,
    PERCENT_CLASSIFICATION,
    PIPELINE_NAME,
    PIPELINE_VERSION,
    SIEVE_CONNECTIVITY,
    SIEVE_THRESHOLD,
)
from core.pipelines.pendientes.helpers.cartography import create_elevation_q10_raster, create_restricted_sieve_raster
from core.pipelines.pendientes.helpers.classification import create_classified_raster
from core.pipelines.pendientes.helpers.cog import create_cog, inspect_cog_driver, validate_lossless_cog
from core.pipelines.pendientes.helpers.conditioning import (
    create_gaussian_conditioned_dem,
    validate_gaussian_conditioning,
)
from core.pipelines.pendientes.helpers.methodology.aoi import build_analytic_aoi, write_aoi_artifact
from core.pipelines.pendientes.helpers.municipal import calculate_municipal_statistics, write_parquet_atomic
from core.pipelines.pendientes.helpers.productive_we5 import (
    inspect_productive_we5_backend,
    run_context_we5,
    validate_we5_context,
)
from core.pipelines.pendientes.helpers.raster import inspect_raster, reproject_dem, validate_analytic_grid
from core.pipelines.pendientes.helpers.slope_products import (
    create_territorial_degrees,
    create_territorial_percent,
    validate_slope_family,
)
from core.pipelines.pendientes.helpers.territorial_dem import create_territorial_dem, validate_territorial_dem
from core.pipelines.stage import Stage
from core.utils.files import read_json, sha256_file, write_json_atomic


class PendientesTransform(Stage):
    """Produce the G15/WE5 analytical family and its cartographic COG derivatives."""

    def __init__(self, pipeline_name: str = PIPELINE_NAME, mode: str = "bootstrap") -> None:
        self.mode = mode
        super().__init__(pipeline_name, "transform")
        self.extract_manifest_path = Path("data") / "extract" / pipeline_name / EXTRACT_MANIFEST_FILENAME
        self.baseline_manifest_path = self.work_dir / "transform_manifest.json"
        self.baseline_path = self.work_dir / ANALYTIC_DEM_FILENAME
        self.aoi_path = self.work_dir / AOI_FILENAME
        self.staging_dir = self.work_dir / "staging_g15"
        self.context_dem_path = self.staging_dir / "dem_g15_contexto_jalisco_15m.tif"
        self.master_dem_path = self.staging_dir / "modelo_elevacion_acondicionado_jalisco_15m.tif"
        self.context_degrees_path = self.staging_dir / "pendiente_grados_contexto_jalisco_15m.tif"
        self.degrees_path = self.staging_dir / "pendiente_grados_jalisco_15m.tif"
        self.percent_path = self.staging_dir / "pendiente_porcentaje_jalisco_15m.tif"
        self.raw_classified_dir = self.staging_dir / "clasificados_crudos"
        self.generalized_dir = self.staging_dir / "clasificados_generalizados"
        self.raw_degrees_classified_path = self.raw_classified_dir / FINAL_DEGREES_CLASSIFIED_FILENAME
        self.raw_percent_classified_path = self.raw_classified_dir / FINAL_PERCENT_CLASSIFIED_FILENAME
        self.degrees_classified_path = self.generalized_dir / FINAL_DEGREES_CLASSIFIED_FILENAME
        self.percent_classified_path = self.generalized_dir / FINAL_PERCENT_CLASSIFIED_FILENAME
        self.elevation_q10_path = self.staging_dir / FINAL_ELEVATION_Q10_FILENAME
        self.final_dir = self.work_dir / FINAL_DIRECTORY_NAME
        self.analytical_dir = self.final_dir / FINAL_ANALYTICAL_DIRECTORY_NAME
        self.cartographic_dir = self.final_dir / FINAL_CARTOGRAPHIC_DIRECTORY_NAME
        self.table_dir = self.final_dir / FINAL_TABLE_DIRECTORY_NAME
        self.intermediate_dir = self.final_dir / FINAL_INTERMEDIATE_DIRECTORY_NAME
        self.manifest_path = self.final_dir / FINAL_TRANSFORM_MANIFEST_FILENAME
        self.packaging_manifest_path = self.final_dir / "cog_packaging_manifest.json"

    def source(self, input_data: Any | None = None) -> dict[str, Any]:
        extract = read_json(self.extract_manifest_path)
        if extract is None:
            raise FileNotFoundError(f"Extract manifest not found: {self.extract_manifest_path}")
        source_path = Path(str(extract.get("tiff_path", "")))
        if not source_path.is_file() or sha256_file(source_path) != extract.get("tiff_sha256"):
            raise ValueError("Immutable CEM TIFF is missing or differs from the Extract manifest")
        boundaries = extract.get("municipal_boundaries", {})
        boundary_path = Path(str(boundaries.get("path", "")))
        if not boundary_path.is_file() or sha256_file(boundary_path) != boundaries.get("sha256"):
            raise ValueError("Extract boundary snapshot is missing or changed")
        return {
            "extract_manifest": extract,
            "extract_manifest_sha256": sha256_file(self.extract_manifest_path),
            "source_path": source_path,
            "boundary_path": boundary_path,
        }

    def _completed(self, input_data: dict[str, Any]) -> dict[str, Any] | None:
        previous = read_json(self.manifest_path)
        method = (previous or {}).get("methodology", {}).get("conditioned_dem", {})
        if not isinstance(method, dict) or method.get("method") != "normalized_gaussian":
            return None
        if previous.get("status") != "transform_complete":
            return None
        if previous.get("extract_manifest_sha256") != input_data["extract_manifest_sha256"]:
            return None
        for product in previous.get("rasters", {}).values():
            path = Path(product["path"])
            if not path.is_file() or sha256_file(path) != product["sha256"]:
                raise ValueError(f"Completed Transform raster changed: {path}")
        table = previous.get("municipal_statistics", {})
        path = Path(str(table.get("path", "")))
        if not path.is_file() or sha256_file(path) != table.get("sha256"):
            raise ValueError("Completed municipal statistics changed")
        return {**previous, "reused": True}

    def _baseline(self, input_data: dict[str, Any]) -> dict[str, Any]:
        previous = read_json(self.baseline_manifest_path)
        if previous is not None and self.baseline_path.is_file() and self.aoi_path.is_file():
            if previous.get("source_tiff_sha256") != input_data["extract_manifest"]["tiff_sha256"]:
                raise ValueError("Existing baseline belongs to a different CEM source")
            if sha256_file(self.baseline_path) != previous.get("analytic_dem_sha256"):
                raise ValueError("Existing baseline checksum changed")
            if sha256_file(self.aoi_path) != previous.get("aoi_sha256"):
                raise ValueError("Existing AOI checksum changed")
            return {**previous, "reused": True}

        layer = f"estado_{settings.BOUNDARY_GEOMETRY_COLUMN.removeprefix('geom_')}"
        try:
            boundary = gpd.read_file(input_data["boundary_path"], layer=layer)
        except Exception as error:
            raise FileNotFoundError(
                "A fresh baseline requires the state boundary layer frozen by the current Extract stage"
            ) from error
        analytic_aoi, grid = build_analytic_aoi(
            boundary,
            settings.AOI_BUFFER_M,
            settings.TARGET_RESOLUTION_M,
            settings.TARGET_SRID,
        )
        write_aoi_artifact(boundary, analytic_aoi, self.aoi_path)
        processing = reproject_dem(
            input_data["source_path"],
            self.baseline_path,
            settings.TARGET_SRID,
            settings.TARGET_RESOLUTION_M,
            grid.bounds,
        )
        metadata = inspect_raster(self.baseline_path, max_cells=settings.STATS_MAX_CELLS)
        validate_analytic_grid(metadata, settings.TARGET_SRID, settings.TARGET_RESOLUTION_M, grid.bounds)
        manifest = {
            "status": "baseline_complete",
            "source_tiff_sha256": input_data["extract_manifest"]["tiff_sha256"],
            "aoi_path": str(self.aoi_path),
            "aoi_sha256": sha256_file(self.aoi_path),
            "analytic_dem_path": str(self.baseline_path),
            "analytic_dem_sha256": sha256_file(self.baseline_path),
            "grid": grid.to_dict(),
            "reprojection": {
                "target_srid": settings.TARGET_SRID,
                "resolution_m": settings.TARGET_RESOLUTION_M,
                "resampling": "bilinear",
                "second_spatial_interpolation": True,
                "processing": processing,
            },
        }
        write_json_atomic(manifest, self.baseline_manifest_path)
        return {**manifest, "reused": False}

    def _checkpoint(self, input_data: dict[str, Any], baseline: dict[str, Any]) -> dict[str, Any]:
        previous = read_json(self.manifest_path)
        if previous is not None and previous.get("status") == "transform_g15_in_progress":
            if previous.get("extract_manifest_sha256") != input_data["extract_manifest_sha256"]:
                raise ValueError("Transform checkpoint belongs to another Extract manifest")
            return previous
        checkpoint = {
            "status": "transform_g15_in_progress",
            "pipeline_version": PIPELINE_VERSION,
            "created_at": datetime.now().astimezone().isoformat(),
            "extract_manifest_sha256": input_data["extract_manifest_sha256"],
            "baseline": {
                "path": str(self.baseline_path),
                "sha256": baseline["analytic_dem_sha256"],
                "manifest_path": str(self.baseline_manifest_path),
                "manifest_sha256": sha256_file(self.baseline_manifest_path),
            },
            "artifacts": {},
        }
        write_json_atomic(checkpoint, self.manifest_path)
        return checkpoint

    def _artifact(
        self,
        checkpoint: dict[str, Any],
        key: str,
        path: Path,
        producer: Callable[[], dict[str, Any]],
    ) -> dict[str, Any]:
        recorded = checkpoint["artifacts"].get(key)
        if path.exists():
            if recorded is None or sha256_file(path) != recorded["sha256"]:
                raise ValueError(f"Untracked or changed Transform artifact: {path}")
            return {**recorded, "reused": True}
        processing = producer()
        record = {"path": str(path), "sha256": sha256_file(path), "processing": processing}
        checkpoint["artifacts"][key] = record
        write_json_atomic(checkpoint, self.manifest_path)
        return {**record, "reused": False}

    def _package(
        self,
        checkpoint: dict[str, Any],
        key: str,
        parent: Path,
        destination: Path,
        *,
        role: str,
        unit: str,
    ) -> dict[str, Any]:
        artifact_key = f"cog_{key}"
        recorded = checkpoint["artifacts"].get(artifact_key)
        if recorded is not None and destination.is_file() and sha256_file(destination) == recorded["sha256"]:
            return {**recorded["processing"], "reused": True}
        candidate = self.staging_dir / "cog_staging" / destination.name
        candidate.unlink(missing_ok=True)
        classified = role == "classified"
        elevation_q10 = role == "elevation_q10"
        creation = create_cog(parent, candidate, classified=classified, elevation_q10=elevation_q10)
        qa = validate_lossless_cog(parent, candidate, classified=classified, elevation_q10=elevation_q10)
        if not qa["hard_gates"]["all_passed"]:
            raise ValueError(f"Lossless COG QA failed: {key}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        os.replace(candidate, destination)
        processing = {
            "path": str(destination),
            "analytical_parent": str(parent),
            "scientific_sha256": sha256_file(parent),
            "product_role": role,
            "unit": unit,
            "creation": creation,
            **qa,
        }
        checkpoint["artifacts"][artifact_key] = {
            "path": str(destination),
            "sha256": sha256_file(destination),
            "processing": processing,
        }
        write_json_atomic(checkpoint, self.manifest_path)
        return processing

    def action(self, input_data: dict[str, Any]) -> dict[str, Any]:
        completed = self._completed(input_data)
        if completed is not None:
            return completed
        baseline = self._baseline(input_data)
        checkpoint = self._checkpoint(input_data, baseline)
        backend = inspect_productive_we5_backend()

        conditioned = self._artifact(
            checkpoint,
            "context_dem_g15",
            self.context_dem_path,
            lambda: create_gaussian_conditioned_dem(
                self.baseline_path,
                self.context_dem_path,
                sigma_pixels=GAUSSIAN_SIGMA_PIXELS,
                truncate=GAUSSIAN_TRUNCATE,
                tile_size=GAUSSIAN_TILE_SIZE_PIXELS,
            ),
        )
        conditioning_qa = validate_gaussian_conditioning(self.baseline_path, self.context_dem_path)
        if not conditioning_qa["hard_gates"]["all_passed"]:
            raise ValueError("G15 conditioning QA failed")

        boundary = gpd.read_file(self.aoi_path, layer=AOI_TERRITORIAL_LAYER)
        geometry = boundary.geometry.iloc[0]
        territorial = self._artifact(
            checkpoint,
            "territorial_dem_g15",
            self.master_dem_path,
            lambda: create_territorial_dem(self.context_dem_path, self.master_dem_path, geometry),
        )
        territorial_qa = validate_territorial_dem(
            self.context_dem_path,
            self.master_dem_path,
            geometry,
            float(geometry.area),
        )

        context_slope = self._artifact(
            checkpoint,
            "context_degrees_we5",
            self.context_degrees_path,
            lambda: run_context_we5(self.context_dem_path, self.context_degrees_path, backend),
        )
        context_slope_qa = validate_we5_context(self.context_dem_path, self.context_degrees_path)
        if not context_slope_qa["hard_gates"]["all_passed"]:
            raise ValueError("WE5 context QA failed")
        degrees = self._artifact(
            checkpoint,
            "territorial_degrees_we5",
            self.degrees_path,
            lambda: create_territorial_degrees(
                self.context_degrees_path,
                self.master_dem_path,
                self.degrees_path,
                territorial["processing"]["territorial_window"],
            ),
        )
        percent = self._artifact(
            checkpoint,
            "territorial_percent",
            self.percent_path,
            lambda: create_territorial_percent(self.degrees_path, self.percent_path),
        )
        slope_qa = validate_slope_family(self.master_dem_path, self.degrees_path, self.percent_path)
        if not slope_qa["hard_gates"]["all_passed"]:
            raise ValueError("WE5 slope family QA failed")

        specs = {
            "degrees": (
                self.degrees_path,
                self.raw_degrees_classified_path,
                self.degrees_classified_path,
                DEGREES_CLASSIFICATION,
                CLASSIFICATION_SOURCES["degrees"],
            ),
            "percent": (
                self.percent_path,
                self.raw_percent_classified_path,
                self.percent_classified_path,
                PERCENT_CLASSIFICATION,
                CLASSIFICATION_SOURCES["percent"],
            ),
        }
        classifications: dict[str, Any] = {}
        for name, (parent, raw, generalized, classes, source) in specs.items():
            raw_record = self._artifact(
                checkpoint,
                f"classified_{name}_raw",
                raw,
                lambda parent=parent, raw=raw, classes=classes, source=source: create_classified_raster(
                    parent, raw, classes, source
                ),
            )
            generalized_record = self._artifact(
                checkpoint,
                f"classified_{name}_generalized",
                generalized,
                lambda raw=raw, generalized=generalized: create_restricted_sieve_raster(raw, generalized),
            )
            classifications[name] = {"raw": raw_record, "generalized": generalized_record}

        elevation_q10 = self._artifact(
            checkpoint,
            "elevation_q10",
            self.elevation_q10_path,
            lambda: create_elevation_q10_raster(self.master_dem_path, self.elevation_q10_path),
        )

        raster_specs = {
            "modelo_elevacion_acondicionado": (
                self.master_dem_path,
                self.analytical_dir / self.master_dem_path.name,
                "continuous",
                "metre",
            ),
            "pendiente_grados": (
                self.degrees_path,
                self.analytical_dir / self.degrees_path.name,
                "continuous",
                "degree",
            ),
            "pendiente_porcentaje": (
                self.percent_path,
                self.analytical_dir / self.percent_path.name,
                "continuous",
                "percent",
            ),
            "elevacion_q10": (
                self.elevation_q10_path,
                self.cartographic_dir / self.elevation_q10_path.name,
                "elevation_q10",
                "metre",
            ),
            "pendiente_grados_clasificada": (
                self.degrees_classified_path,
                self.cartographic_dir / FINAL_DEGREES_CLASSIFIED_FILENAME,
                "classified",
                "class",
            ),
            "pendiente_porcentaje_clasificada": (
                self.percent_classified_path,
                self.cartographic_dir / FINAL_PERCENT_CLASSIFIED_FILENAME,
                "classified",
                "class",
            ),
        }
        rasters = {
            key: self._package(checkpoint, key, parent, destination, role=role, unit=unit)
            for key, (parent, destination, role, unit) in raster_specs.items()
        }
        packaging = {
            "status": "cog_packaging_validated",
            "created_at": datetime.now().astimezone().isoformat(),
            "gdal_cog_driver": inspect_cog_driver(),
            "rasters": rasters,
        }
        write_json_atomic(packaging, self.packaging_manifest_path)

        statistics, municipal_qa = calculate_municipal_statistics(
            input_data["boundary_path"], self.context_dem_path, self.context_degrees_path
        )
        provenance = {
            "source_dem_sha256": sha256_file(self.context_dem_path),
            "source_slope_degrees_sha256": sha256_file(self.context_degrees_path),
            "conditioning_method": "normalized_gaussian",
            "conditioning_sigma_pixels": str(GAUSSIAN_SIGMA_PIXELS),
            "slope_method": "WoodEvans5x5",
            "source_municipal_snapshot_sha256": input_data["extract_manifest"]["municipal_boundaries"]["sha256"],
            "pixel_inclusion_rule": "pixel_center; all_touched=false",
            "percentile_method": "exact",
        }
        table = write_parquet_atomic(
            statistics,
            self.table_dir / FINAL_MUNICIPAL_STATISTICS_FILENAME,
            metadata=provenance,
        )
        return self._final_manifest(
            input_data,
            baseline,
            backend,
            rasters,
            table,
            municipal_qa,
            provenance,
            conditioned,
            conditioning_qa,
            territorial,
            territorial_qa,
            context_slope,
            context_slope_qa,
            degrees,
            percent,
            slope_qa,
            classifications,
            elevation_q10,
            packaging,
        )

    def _final_manifest(
        self,
        input_data: dict[str, Any],
        baseline: dict[str, Any],
        backend: dict[str, Any],
        rasters: dict[str, Any],
        table: dict[str, Any],
        municipal_qa: dict[str, Any],
        provenance: dict[str, str],
        conditioned: dict[str, Any],
        conditioning_qa: dict[str, Any],
        territorial: dict[str, Any],
        territorial_qa: dict[str, Any],
        context_slope: dict[str, Any],
        context_slope_qa: dict[str, Any],
        degrees: dict[str, Any],
        percent: dict[str, Any],
        slope_qa: dict[str, Any],
        classifications: dict[str, Any],
        elevation_q10: dict[str, Any],
        packaging: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "status": "transform_complete",
            "reused": False,
            "pipeline_version": PIPELINE_VERSION,
            "created_at": datetime.now().astimezone().isoformat(),
            "extract_manifest_path": str(self.extract_manifest_path),
            "extract_manifest_sha256": input_data["extract_manifest_sha256"],
            "municipal_boundaries": input_data["extract_manifest"]["municipal_boundaries"],
            "source": {
                "product": input_data["extract_manifest"]["source"]["product"],
                "producer": input_data["extract_manifest"]["source"]["producer"],
                "sha256": input_data["extract_manifest"]["tiff_sha256"],
            },
            "methodology": {
                "conditioned_dem": {
                    "method": "normalized_gaussian",
                    "sigma_pixels": GAUSSIAN_SIGMA_PIXELS,
                    "sigma_metres": GAUSSIAN_SIGMA_METRES,
                    "truncate": GAUSSIAN_TRUNCATE,
                    "nodata_policy": "normalized convolution; source NoData preserved",
                },
                "slope": {
                    "backend": "GRASS r.param.scale",
                    "method": "slope",
                    "size": 5,
                    "exponent": 0,
                    "zscale": 1,
                    "backend_contract": backend,
                },
                "slope_percent": "float32(tan(radians(float64(degrees))) * 100)",
                "cartographic_generalization": {
                    "scope": "classified rasters only",
                    "sieve_threshold": SIEVE_THRESHOLD,
                    "connectivity": SIEVE_CONNECTIVITY,
                    "acceptance_rule": "abs(candidate_class - original_class) == 1",
                },
                "elevation_geoportal": {
                    "method": "round(z / 10) * 10",
                    "vertical_representation_interval_m": 10,
                    "additional_spatial_filter": None,
                },
            },
            "processing": {
                "baseline": baseline,
                "conditioned_context": conditioned,
                "conditioned_context_qa": conditioning_qa,
                "territorial_dem": territorial,
                "territorial_dem_qa": territorial_qa,
                "context_slope": context_slope,
                "context_slope_qa": context_slope_qa,
                "territorial_degrees": degrees,
                "territorial_percent": percent,
                "slope_family_qa": slope_qa,
                "classifications": classifications,
                "elevation_q10": elevation_q10,
            },
            "lineage": {
                "graph": (
                    "CEM 4.0 -> bilinear EPSG:6368/15m baseline -> normalized Gaussian sigma=1.5 -> "
                    "territorial analytical DEM -> Wood-Evans 5x5 degrees -> percent; classified products -> "
                    "restricted <=7-pixel sieve; analytical DEM -> Q10 RAW; scientific rasters -> lossless COG"
                ),
                "context_dem": {"path": str(self.context_dem_path), "sha256": sha256_file(self.context_dem_path)},
                "context_slope_degrees": {
                    "path": str(self.context_degrees_path),
                    "sha256": sha256_file(self.context_degrees_path),
                },
                "scientific_recalculation_performed": True,
            },
            "gdal_cog_driver": packaging["gdal_cog_driver"],
            "rasters": rasters,
            "classifications": {
                "degrees": "INEGI cartographic precedent",
                "percent": "FAO/GAEZ",
                "spatially_equivalent": False,
            },
            "municipal_statistics": {**table, "provenance": provenance, "qa": municipal_qa},
            "indicators": {
                "status": "definitions_validated",
                "ids": list(MUNICIPAL_INDICATOR_IDS),
                "source": "continuous non-generalized slope",
            },
        }

    def finalization(self, input_data: dict[str, Any]) -> dict[str, Any]:
        write_json_atomic(input_data, self.manifest_path)
        return input_data
