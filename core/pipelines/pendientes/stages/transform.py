from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from core.pipelines.pendientes.constants import (
    CONTEXT_DEM_PATH,
    CONTEXT_DEM_SHA256,
    CONTEXT_WE5_DEGREES_PATH,
    CONTEXT_WE5_DEGREES_SHA256,
    DEM_PROMOTION_DIRECTORY_NAME,
    DEM_PROMOTION_TERRITORIAL_FILENAME,
    EXTRACT_MANIFEST_FILENAME,
    FINAL_ANALYTICAL_DIRECTORY_NAME,
    FINAL_CARTOGRAPHIC_DIRECTORY_NAME,
    FINAL_DIRECTORY_NAME,
    FINAL_INTERMEDIATE_DIRECTORY_NAME,
    FINAL_MUNICIPAL_STATISTICS_FILENAME,
    FINAL_TABLE_DIRECTORY_NAME,
    FINAL_TRANSFORM_MANIFEST_FILENAME,
    FROZEN_RELEASE_COG_SHA256,
    MUNICIPAL_INDICATOR_IDS,
    PIPELINE_NAME,
    PIPELINE_VERSION,
    VALIDATED_DEM_SHA256,
)
from core.pipelines.pendientes.helpers.municipal import calculate_municipal_statistics, write_parquet_atomic
from core.pipelines.stage import Stage
from core.utils.files import read_json, sha256_file, write_json_atomic


class PendientesTransform(Stage):
    """Package frozen scientific rasters and derive the final local products."""

    def __init__(self, pipeline_name: str = PIPELINE_NAME, mode: str = "bootstrap") -> None:
        self.mode = mode
        super().__init__(pipeline_name, "transform")
        self.extract_manifest_path = Path("data") / "extract" / pipeline_name / EXTRACT_MANIFEST_FILENAME
        self.final_dir = self.work_dir / FINAL_DIRECTORY_NAME
        self.analytical_dir = self.final_dir / FINAL_ANALYTICAL_DIRECTORY_NAME
        self.cartographic_dir = self.final_dir / FINAL_CARTOGRAPHIC_DIRECTORY_NAME
        self.table_dir = self.final_dir / FINAL_TABLE_DIRECTORY_NAME
        self.intermediate_dir = self.final_dir / FINAL_INTERMEDIATE_DIRECTORY_NAME
        self.manifest_path = self.final_dir / FINAL_TRANSFORM_MANIFEST_FILENAME
        self.packaging_manifest_path = self.final_dir / "cog_packaging_manifest.json"
        self.context_dem_path = Path(CONTEXT_DEM_PATH)
        self.context_degrees_path = Path(CONTEXT_WE5_DEGREES_PATH)
        self.parents = {
            "modelo_elevacion_acondicionado": {
                "path": self.work_dir / DEM_PROMOTION_DIRECTORY_NAME / DEM_PROMOTION_TERRITORIAL_FILENAME,
                "sha256": VALIDATED_DEM_SHA256,
                "unit": "metre",
            },
        }

    def source(self, input_data: Any | None = None) -> dict[str, Any]:
        extract = read_json(self.extract_manifest_path)
        if extract is None:
            raise FileNotFoundError(f"Extract manifest not found: {self.extract_manifest_path}")
        boundaries = extract.get("municipal_boundaries", {})
        boundary_path = Path(str(boundaries["path"])) if boundaries.get("path") else None
        if boundary_path is not None and (
            not boundary_path.is_file() or sha256_file(boundary_path) != boundaries.get("sha256")
        ):
            raise ValueError("Extract municipal snapshot checksum no longer matches")
        snapshot_manifest_path = Path(str(boundaries.get("manifest_path", "")))
        if (
            not snapshot_manifest_path.is_file()
            or sha256_file(snapshot_manifest_path) != boundaries.get("manifest_sha256")
        ):
            raise ValueError("Extract municipal snapshot manifest is missing or changed")
        context_inputs = {
            "conditioned_dem_fp2": (self.context_dem_path, CONTEXT_DEM_SHA256),
            "slope_degrees_wood_evans_5x5": (self.context_degrees_path, CONTEXT_WE5_DEGREES_SHA256),
        }
        for name, (path, expected_sha256) in context_inputs.items():
            if not path.is_file() or sha256_file(path) != expected_sha256:
                raise ValueError(f"Frozen contextual input is missing or changed: {name}")
        for product, parent in self.parents.items():
            path = parent["path"]
            if not path.is_file():
                raise FileNotFoundError(f"Validated analytical parent is missing for {product}: {path}")
            if sha256_file(path) != parent["sha256"]:
                raise ValueError(f"Validated analytical parent checksum changed for {product}")
        return {
            "extract_manifest": extract,
            "extract_manifest_sha256": sha256_file(self.extract_manifest_path),
            "municipal_boundaries_path": boundary_path,
            "context_inputs": context_inputs,
        }

    def _validated_previous_result(self, input_data: dict[str, Any]) -> dict[str, Any] | None:
        previous = read_json(self.manifest_path)
        if previous is None:
            return None
        current_snapshot = input_data["extract_manifest"]["municipal_boundaries"]
        if previous.get("municipal_boundaries", {}).get("sha256") != current_snapshot.get("sha256"):
            return None
        if previous.get("status") != "transform_complete":
            raise ValueError("Existing final Transform manifest is not complete")
        for product in previous.get("rasters", {}).values():
            path = Path(product["path"])
            if not path.is_file() or sha256_file(path) != product["sha256"]:
                raise ValueError(f"Existing Transform product is incomplete or changed: {path}")
        table = previous.get("municipal_statistics", {})
        table_path = Path(str(table.get("path", "")))
        if not table_path.is_file() or sha256_file(table_path) != table.get("sha256"):
            raise ValueError("Existing Transform municipal statistics are incomplete or changed")
        return {
            **previous,
            "reused": True,
            "extract_manifest_sha256": input_data["extract_manifest_sha256"],
            "municipal_boundaries": current_snapshot,
        }

    def package_rasters(self) -> dict[str, Any]:
        """Validate and reuse the five frozen COGs without invoking scientific production."""
        packaging = read_json(self.packaging_manifest_path)
        if packaging is None:
            raise FileNotFoundError(f"Frozen COG packaging manifest is missing: {self.packaging_manifest_path}")
        if set(packaging.get("rasters", {})) != set(FROZEN_RELEASE_COG_SHA256):
            raise ValueError("Frozen COG packaging manifest does not contain the exact five-product family")
        for product, expected_sha256 in FROZEN_RELEASE_COG_SHA256.items():
            details = packaging["rasters"][product]
            path = Path(details["path"])
            if details.get("sha256") != expected_sha256 or not path.is_file() or sha256_file(path) != expected_sha256:
                raise ValueError(f"Frozen release COG changed: {product}")
        return {**packaging, "reused": True, "scientific_recalculation_performed": False}

    def action(self, input_data: dict[str, Any]) -> dict[str, Any]:
        previous = self._validated_previous_result(input_data)
        if previous is not None:
            return previous
        packaging = self.package_rasters()
        continuous = {
            key: value for key, value in packaging["rasters"].items() if value["product_role"] == "continuous"
        }
        classified = {
            key: value for key, value in packaging["rasters"].items() if value["product_role"] == "classified"
        }

        if input_data["municipal_boundaries_path"] is None:
            raise FileNotFoundError(
                "COG packaging completed, but Transform statistics require an Extract municipal snapshot "
                "with both cvegeo geom_iieg and geom_inegi sources"
            )

        statistics, municipal_qa = calculate_municipal_statistics(
            input_data["municipal_boundaries_path"],
            self.context_dem_path,
            self.context_degrees_path,
        )
        provenance = {
            "source_dem_sha256": CONTEXT_DEM_SHA256,
            "source_slope_degrees_sha256": CONTEXT_WE5_DEGREES_SHA256,
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
        return {
            "status": "transform_complete",
            "raster_family_status": "validated",
            "municipal_extraction_status": "validated",
            "municipal_statistics_status": "validated",
            "reused": False,
            "pipeline_version": PIPELINE_VERSION,
            "created_at": datetime.now().astimezone().isoformat(),
            "extract_manifest_path": str(self.extract_manifest_path),
            "extract_manifest_sha256": input_data["extract_manifest_sha256"],
            "municipal_boundaries": input_data["extract_manifest"]["municipal_boundaries"],
            "source": {
                "product": input_data["extract_manifest"]["source"]["product"],
                "producer": input_data["extract_manifest"]["source"]["producer"],
                "edition": input_data["extract_manifest"]["source"]["edition"],
                "temporal_coverage": input_data["extract_manifest"]["source"]["temporal_coverage"],
                "sha256": input_data["extract_manifest"]["tiff_sha256"],
            },
            "methodology": {
                "conditioned_dem": "FP2 filter=11 norm_diff=5 num_iter=1 max_diff=0.5 zfactor=1 halo=24",
                "slope": "GRASS GIS r.param.scale Wood-Evans size=5 exponent=0 zscale=1",
                "slope_percent": "tan(radians(pendiente_grados))*100",
                "territorial_mask": "pixel_center",
                "method_reference": "Horn3x3",
                "selected_method": "WoodEvans5x5",
            },
            "lineage": {
                "graph": (
                    "CEM 4.0 INEGI -> FP2 contextual -> WoodEvans5x5 contextual -> "
                    "municipal zonal statistics; analytical raster -> lossless COG packaging -> release raster"
                ),
                "context_dem": {"path": str(self.context_dem_path), "sha256": CONTEXT_DEM_SHA256},
                "context_slope_degrees": {
                    "path": str(self.context_degrees_path),
                    "sha256": CONTEXT_WE5_DEGREES_SHA256,
                },
                "scientific_recalculation_performed": False,
            },
            "gdal_cog_driver": packaging["gdal_cog_driver"],
            "rasters": {**continuous, **classified},
            "classifications": {
                "degrees": "INEGI cartographic precedent",
                "percent": "FAO/GAEZ",
            },
            "municipal_statistics": {**table, "provenance": provenance, "qa": municipal_qa},
            "indicators": {
                "status": "definitions_validated",
                "ids": list(MUNICIPAL_INDICATOR_IDS),
                "classified_indicators_created": False,
            },
        }

    def finalization(self, input_data: dict[str, Any]) -> dict[str, Any]:
        write_json_atomic(input_data, self.manifest_path)
        return input_data
