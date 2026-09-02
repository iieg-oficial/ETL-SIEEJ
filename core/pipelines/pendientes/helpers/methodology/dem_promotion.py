from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path
from typing import Any

import geopandas as gpd

from core.pipelines.pendientes.constants import (
    ANALYTIC_DEM_FILENAME,
    AOI_FILENAME,
    AOI_TERRITORIAL_LAYER,
    CONDITIONED_DEM_PRODUCT,
    DEM_PROMOTION_AOI_SHA256,
    DEM_PROMOTION_DECISIONS,
    DEM_PROMOTION_DIRECTORY_NAME,
    DEM_PROMOTION_MANIFEST_FILENAME,
    DEM_PROMOTION_PARENT_MANIFEST_SHA256,
    DEM_PROMOTION_SOURCE_SHA256,
    DEM_PROMOTION_TERRITORIAL_FILENAME,
    EXPERIMENT_BASELINE_SHA256,
    PIPELINE_NAME,
    PIPELINE_VERSION,
    STATEWIDE_CANDIDATE_DIRECTORY_NAME,
    STATEWIDE_CANDIDATE_FILENAME,
    STATEWIDE_CANDIDATE_FP2_CONFIG,
    STATEWIDE_CANDIDATE_MANIFEST_FILENAME,
    STATEWIDE_CANDIDATE_SHA256,
)
from core.pipelines.pendientes.helpers.territorial_dem import (
    create_territorial_dem,
    validate_territorial_dem,
)
from core.utils.files import read_json, sha256_file, write_json_atomic


class PendientesDemPromotion:
    """Validate the context DEM and derive the aligned territorial DEM by masking only."""

    def __init__(self) -> None:
        self.transform_dir = Path("data") / "transform" / PIPELINE_NAME
        self.extract_manifest_path = Path("data") / "extract" / PIPELINE_NAME / "manifest.json"
        self.baseline_path = self.transform_dir / ANALYTIC_DEM_FILENAME
        self.aoi_path = self.transform_dir / AOI_FILENAME
        self.parent_dir = self.transform_dir / STATEWIDE_CANDIDATE_DIRECTORY_NAME
        self.context_path = self.parent_dir / STATEWIDE_CANDIDATE_FILENAME
        self.parent_manifest_path = self.parent_dir / STATEWIDE_CANDIDATE_MANIFEST_FILENAME
        self.output_dir = self.transform_dir / DEM_PROMOTION_DIRECTORY_NAME
        self.territorial_path = self.output_dir / DEM_PROMOTION_TERRITORIAL_FILENAME
        self.manifest_path = self.output_dir / DEM_PROMOTION_MANIFEST_FILENAME

    def execute(self) -> dict[str, Any]:
        started = time.perf_counter()
        parent_manifest, source_manifest = self._validate_integrity()
        boundary, aoi = self._read_aoi()
        if self.territorial_path.exists():
            processing = {
                "existing_artifact_reused": True,
                "production_elapsed_seconds": None,
                "note": "Existing territorial DEM was validated without overwriting it.",
            }
        else:
            processing = {
                **create_territorial_dem(self.context_path, self.territorial_path, boundary),
                "existing_artifact_reused": False,
            }
        qa = validate_territorial_dem(
            self.context_path,
            self.territorial_path,
            boundary,
            float(boundary.area),
        )
        territorial_sha256 = sha256_file(self.territorial_path)
        gates = {
            "source_checksum": source_manifest["tiff_sha256"] == DEM_PROMOTION_SOURCE_SHA256,
            "baseline_checksum": sha256_file(self.baseline_path) == EXPERIMENT_BASELINE_SHA256,
            "phase6a_manifest_checksum": sha256_file(self.parent_manifest_path)
            == DEM_PROMOTION_PARENT_MANIFEST_SHA256,
            "validated_context_dem_checksum": sha256_file(self.context_path) == STATEWIDE_CANDIDATE_SHA256,
            "frozen_aoi_checksum": aoi["sha256"] == DEM_PROMOTION_AOI_SHA256,
            "territorial_grid": qa["grid"]["passed"],
            "bitwise_value_preservation": qa["value_equality"]["bitwise_equal"],
            "mask_match": qa["mask"]["mask_mismatch_pixels"] == 0,
            "no_valid_pixels_outside_jalisco": qa["mask"]["valid_outside_jalisco_pixels"] == 0,
            "no_unexplained_nodata_inside_jalisco": qa["mask"]["nodata_inside_jalisco_pixels"]
            == qa["mask"]["inherited_parent_nodata_inside_jalisco_pixels"],
        }
        gates["all_passed"] = all(gates.values())
        decision = (
            "conditioned_dem_validated_for_derivatives"
            if gates["all_passed"]
            else "dem_validation_failed"
        )
        manifest = {
            "phase": "6B_conditioned_DEM_validation_and_promotion",
            "pipeline_version": PIPELINE_VERSION,
            "created_at": datetime.now().astimezone().isoformat(),
            "status": decision,
            "decision": {
                "allowed": list(DEM_PROMOTION_DECISIONS),
                "value": decision,
                "published": False,
                "loaded": False,
                "served": False,
            },
            "lineage": {
                "source": {
                    "producer": "INEGI",
                    "product": "Continuo de Elevaciones Mexicano 4.0",
                    "sha256": DEM_PROMOTION_SOURCE_SHA256,
                    "role": "source_original",
                    "immutable": True,
                },
                "baseline": {
                    "path": str(self.baseline_path),
                    "sha256": EXPERIMENT_BASELINE_SHA256,
                    "crs_epsg": 6368,
                    "resampling": "bilinear",
                    "role": "staging_baseline",
                },
                "validated_context_dem": {
                    "path": str(self.context_path),
                    "sha256": STATEWIDE_CANDIDATE_SHA256,
                    "parent_manifest_path": str(self.parent_manifest_path),
                    "parent_manifest_sha256": DEM_PROMOTION_PARENT_MANIFEST_SHA256,
                },
                "territorial_operation": "aligned source-grid window plus Jalisco pixel-center mask",
                "territorial_dem_sha256": territorial_sha256,
            },
            "conditioning": {
                "method": "WhiteboxTools FeaturePreservingSmoothing",
                "candidate_id": "FP2",
                "parameters": dict(STATEWIDE_CANDIDATE_FP2_CONFIG),
                "validated_halo_pixels": 24,
                "whitebox_backend": parent_manifest["whitebox_backend"],
                "selection_closed": True,
                "validated_for_derivatives": gates["all_passed"],
            },
            "context_dem": {
                "conceptual_id": "modelo_elevacion_acondicionado_contexto",
                "path": str(self.context_path),
                "sha256": STATEWIDE_CANDIDATE_SHA256,
                "validated": gates["all_passed"],
                "includes_analytic_buffer": True,
                "territorially_publishable": False,
            },
            "territorial_dem": {
                "conceptual_id": CONDITIONED_DEM_PRODUCT,
                "path": str(self.territorial_path),
                "sha256": territorial_sha256,
                "size_bytes": self.territorial_path.stat().st_size,
                "grid": qa["grid"],
                "mask": qa["mask"],
                "statistics_m": qa["statistics_m"],
                "vertical_quantity": "length",
                "vertical_unit": "metre",
                "effective_z_factor": 1.0,
                "cog": False,
            },
            "territorial_mask": aoi,
            "processing": processing,
            "qa": {
                "value_equality_with_context_parent": qa["value_equality"],
                "mask": qa["mask"],
                "area": qa["area"],
                "vertical_contract": {
                    "xy_unit": "metre",
                    "z_unit": "metre",
                    "effective_z_factor": 1.0,
                    "z_values_modified_during_territorial_operation": False,
                },
            },
            "quality_gates": gates,
            "master_grid": {
                "role": "canonical_territorial_grid_and_mask_for_final_product_family",
                "crs_epsg": 6368,
                "resolution_m": [15.0, 15.0],
                "transform": qa["grid"]["transform"],
                "bounds": qa["grid"]["bounds"],
                "width": qa["grid"]["width"],
                "height": qa["grid"]["height"],
                "nodata": -9999.0,
                "mask_source_aoi_sha256": DEM_PROMOTION_AOI_SHA256,
                "mask_rule": "pixel_center; all_touched=false; no antialiasing",
                "master_dem_sha256": territorial_sha256,
                "required_products": [
                    "modelo_elevacion_acondicionado",
                    "pendiente_grados",
                    "pendiente_porcentaje",
                ],
            },
            "derivative_contract": {
                "slope_parent": "validated_context_dem",
                "validated_context_dem_sha256": STATEWIDE_CANDIDATE_SHA256,
                "prohibited_slope_parent": "territorially_clipped_dem",
                "workflow": [
                    "validated_context_dem",
                    "slope_algorithm",
                    "context_slope",
                    "master_territorial_window_and_jalisco_mask",
                    "final_territorial_slope",
                ],
                "slope_algorithm_selected": False,
            },
            "elapsed_seconds": time.perf_counter() - started,
            "slopes_generated": False,
            "load_executed": False,
        }
        write_json_atomic(manifest, self.manifest_path)
        return manifest

    def _validate_integrity(self) -> tuple[dict[str, Any], dict[str, Any]]:
        checks = {
            self.context_path: STATEWIDE_CANDIDATE_SHA256,
            self.parent_manifest_path: DEM_PROMOTION_PARENT_MANIFEST_SHA256,
            self.baseline_path: EXPERIMENT_BASELINE_SHA256,
        }
        for path, expected in checks.items():
            if not path.is_file() or sha256_file(path) != expected:
                raise ValueError(f"Frozen Phase-6B input integrity failed: {path}")
        parent_manifest = read_json(self.parent_manifest_path)
        source_manifest = read_json(self.extract_manifest_path)
        if parent_manifest is None or source_manifest is None:
            raise FileNotFoundError("Phase-6A and Extract manifests are required")
        if parent_manifest["status"] != "statewide_candidate_generated_not_promoted":
            raise ValueError("Phase 6A candidate is not finalized")
        if parent_manifest["quality_gates"]["all_passed"] is not True:
            raise ValueError("Phase 6A quality gates did not pass")
        if parent_manifest["conditioning"]["parameters"] != STATEWIDE_CANDIDATE_FP2_CONFIG:
            raise ValueError("Frozen FP2 parameters changed")
        if source_manifest["tiff_sha256"] != DEM_PROMOTION_SOURCE_SHA256:
            raise ValueError("Original INEGI CEM checksum changed")
        return parent_manifest, source_manifest

    def _read_aoi(self) -> tuple[Any, dict[str, Any]]:
        if not self.aoi_path.is_file() or sha256_file(self.aoi_path) != DEM_PROMOTION_AOI_SHA256:
            raise ValueError("Frozen AOI checksum changed")
        boundary = gpd.read_file(self.aoi_path, layer=AOI_TERRITORIAL_LAYER)
        if (
            len(boundary) != 1
            or boundary.crs is None
            or boundary.crs.to_epsg() != 6368
            or boundary.geometry.iloc[0] is None
            or boundary.geometry.iloc[0].is_empty
            or not boundary.geometry.iloc[0].is_valid
        ):
            raise ValueError("Frozen Jalisco AOI contract failed")
        geometry = boundary.geometry.iloc[0]
        return geometry, {
            "path": str(self.aoi_path),
            "layer": AOI_TERRITORIAL_LAYER,
            "sha256": DEM_PROMOTION_AOI_SHA256,
            "crs_epsg": 6368,
            "feature_count": 1,
            "geometry_valid": True,
            "geometry_empty": False,
            "bounds": [float(value) for value in geometry.bounds],
            "vector_area_m2": float(geometry.area),
            "vector_area_km2": float(geometry.area / 1_000_000),
            "rasterization_rule": {
                "pixel_inclusion": "pixel_center",
                "all_touched": False,
                "antialiasing": False,
            },
        }
