from __future__ import annotations

from datetime import datetime
from pathlib import Path
import time
from typing import Any

from core.pipelines.pendientes.config import settings
from core.pipelines.pendientes.constants import (
    ANALYTIC_DEM_FILENAME,
    AOI_FILENAME,
    EXTRACT_MANIFEST_FILENAME,
    PIPELINE_NAME,
    PIPELINE_VERSION,
    TRANSFORM_MANIFEST_FILENAME,
)
from core.pipelines.pendientes.helpers.aoi import (
    aoi_manifest,
    build_analytic_aoi,
    read_jalisco_boundary,
    read_jalisco_boundary_snapshot,
    write_aoi_artifact,
)
from core.pipelines.pendientes.helpers.diagnostics import (
    baseline_qa,
    diagnostic_chip_plan,
    source_window_summary,
)
from core.pipelines.pendientes.helpers.raster import inspect_raster, reproject_dem, validate_analytic_grid
from core.pipelines.stage import Stage
from core.utils.files import read_json, sha256_file, write_json_atomic


class PendientesTransform(Stage):
    """AOI plus windowed, aligned EPSG:6368/15 m analytic DEM."""

    def __init__(self, pipeline_name: str = PIPELINE_NAME, mode: str = "bootstrap") -> None:
        self.mode = mode
        super().__init__(pipeline_name, "transform")
        self.extract_manifest_path = Path("data") / "extract" / pipeline_name / EXTRACT_MANIFEST_FILENAME
        self.aoi_path = self.work_dir / AOI_FILENAME
        self.analytic_dem_path = self.work_dir / ANALYTIC_DEM_FILENAME
        self.manifest_path = self.work_dir / TRANSFORM_MANIFEST_FILENAME

    def source(self, input_data: Any | None = None) -> dict[str, Any]:
        manifest = read_json(self.extract_manifest_path)
        if manifest is None:
            raise FileNotFoundError(f"Extract manifest not found: {self.extract_manifest_path}")
        source_path = Path(str(manifest.get("tiff_path", "")))
        if not source_path.is_file():
            raise FileNotFoundError(f"Immutable source TIFF not found: {source_path}")
        if sha256_file(source_path) != manifest.get("tiff_sha256"):
            raise ValueError("Immutable source TIFF checksum no longer matches Extract manifest")
        return manifest

    def action(self, input_data: dict[str, Any]) -> dict[str, Any]:
        stage_started = time.perf_counter()
        if settings.CVEGEO_BOUNDARY_SNAPSHOT_PATH is not None:
            boundary = read_jalisco_boundary_snapshot(
                settings.CVEGEO_BOUNDARY_SNAPSHOT_PATH.expanduser().resolve(),
                settings.BOUNDARY_GEOMETRY_COLUMN,
            )
            boundary_access_mode = "ewkb_snapshot_from_real_cvegeo_query"
        else:
            boundary = read_jalisco_boundary(settings.cvegeo_database_url, settings.BOUNDARY_GEOMETRY_COLUMN)
            boundary_access_mode = "direct_database_query"
        analytic_aoi, grid = build_analytic_aoi(
            boundary,
            buffer_m=settings.AOI_BUFFER_M,
            resolution=settings.TARGET_RESOLUTION_M,
            target_srid=settings.TARGET_SRID,
        )
        write_aoi_artifact(boundary, analytic_aoi, self.aoi_path)
        processing_report = reproject_dem(
            Path(input_data["tiff_path"]),
            self.analytic_dem_path,
            target_srid=settings.TARGET_SRID,
            resolution=settings.TARGET_RESOLUTION_M,
            aligned_bounds=grid.bounds,
        )
        raster = inspect_raster(self.analytic_dem_path, max_cells=settings.STATS_MAX_CELLS)
        validate_analytic_grid(raster, settings.TARGET_SRID, settings.TARGET_RESOLUTION_M, grid.bounds)
        qa = baseline_qa(
            self.analytic_dem_path,
            maximum_sample_cells=settings.DIAGNOSTIC_SAMPLE_MAX_CELLS,
        )
        source_footprint_qa = source_window_summary(
            Path(input_data["tiff_path"]),
            processing_report["source_window"],
            maximum_sample_cells=settings.DIAGNOSTIC_SAMPLE_MAX_CELLS,
        )
        return {
            "extract_manifest_path": str(self.extract_manifest_path),
            "extract_manifest_sha256": sha256_file(self.extract_manifest_path),
            "source_tiff_sha256": input_data["tiff_sha256"],
            "aoi_path": str(self.aoi_path),
            "aoi_sha256": sha256_file(self.aoi_path),
            "aoi": aoi_manifest(
                boundary,
                analytic_aoi,
                grid,
                settings.BOUNDARY_GEOMETRY_COLUMN,
                settings.AOI_BUFFER_M,
                boundary_access_mode,
            ),
            "analytic_dem_path": str(self.analytic_dem_path),
            "analytic_dem_sha256": sha256_file(self.analytic_dem_path),
            "analytic_dem_size_bytes": self.analytic_dem_path.stat().st_size,
            "analytic_dem_uncompressed_size_bytes": grid.width * grid.height * 4,
            "analytic_dem": raster.to_dict(),
            "baseline_qa": qa,
            "source_footprint_qa": source_footprint_qa,
            "diagnostic_chips": diagnostic_chip_plan(),
            "reprojection": {
                "target_srid": settings.TARGET_SRID,
                "resolution_m": settings.TARGET_RESOLUTION_M,
                "target_aligned_pixels": True,
                "resampling": "bilinear",
                "source_resampling_documented": "bilinear",
                "spatial_interpolation_sequence": [
                    "INEGI production resample to published 0.5 arcsec CEM (bilinear)",
                    "ETL reprojection to EPSG:6368 / 15 m (bilinear baseline)",
                ],
                "second_spatial_interpolation": True,
                "processing": processing_report,
                "conditioning": "none (RAW baseline)",
            },
            "reprojection_qa_contract": {
                "comparison_scope": "same geographic test-window footprint",
                "native_grid_summaries": True,
                "direct_cross_grid_pixel_index_comparison": False,
                "metrics": [
                    "elevation_range",
                    "mean",
                    "stddev",
                    "percentiles",
                    "reproducible_histogram",
                    "valid_surface",
                    "nodata",
                ],
                "visual_strata": ["flat_terrain", "mountain_terrain"],
                "controlled_future_continuous_resampling_comparison": True,
                "alternative_selected": False,
            },
            "effect_separation": [
                "artifacts already present in the published CEM",
                "additional effect of EPSG:6368 / 15 m reprojection",
                "effect of later conditioning",
                "effect of the slope algorithm",
            ],
            "phase": "base_dem_before_conditioning",
            "artifact_role": "staging_baseline",
            "publishable": False,
            "includes_analytic_buffer": True,
            "stage_elapsed_seconds": time.perf_counter() - stage_started,
            "pipeline_version": PIPELINE_VERSION,
            "created_at": datetime.now().astimezone().isoformat(),
        }

    def finalization(self, input_data: dict[str, Any]) -> dict[str, Any]:
        write_json_atomic(input_data, self.manifest_path)
        return input_data
