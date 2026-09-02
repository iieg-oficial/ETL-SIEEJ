from __future__ import annotations

import importlib.metadata
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import rasterio
from rasterio.windows import Window

from core.pipelines.pendientes.constants import (
    ANALYTIC_DEM_FILENAME,
    EXPERIMENT_BASELINE_SHA256,
    GLOBAL_VALIDATION_DIRECTORY_NAME,
    GLOBAL_VALIDATION_MANIFEST_FILENAME,
    PIPELINE_NAME,
    PIPELINE_VERSION,
    STATE_VALIDATION_CHIP_COUNT_TARGET,
    STATE_VALIDATION_DIRECTORY_NAME,
    STATE_VALIDATION_INVENTORY_FILENAME,
    STATEWIDE_CANDIDATE_DECISIONS,
    STATEWIDE_CANDIDATE_DIRECTORY_NAME,
    STATEWIDE_CANDIDATE_FILENAME,
    STATEWIDE_CANDIDATE_FLOAT_TOLERANCE_M,
    STATEWIDE_CANDIDATE_FP2_CONFIG,
    STATEWIDE_CANDIDATE_HALO_TEST_CHIP_IDS,
    STATEWIDE_CANDIDATE_MANIFEST_FILENAME,
    STATEWIDE_CANDIDATE_SHA256,
    STATEWIDE_CANDIDATE_TILE_SIZE_PIXELS,
)
from core.pipelines.pendientes.helpers.experimental_whitebox import inspect_whitebox_backend
from core.pipelines.pendientes.helpers.methodology.statewide_candidate_qa import (
    validate_contextual_reference_manifest,
    validate_seam_manifest,
)
from core.pipelines.pendientes.helpers.statewide_conditioning import (
    condition_raster_tiled,
    streaming_global_qa,
    validate_matching_grid,
)
from core.pipelines.pendientes.helpers.tiled_conditioning import comparison_metrics
from core.utils.files import read_json, sha256_file, write_json_atomic


class PendientesStatewideCandidate:
    """Produce or finalize the buffered statewide FP2 candidate without promotion."""

    def __init__(self) -> None:
        transform_dir = Path("data") / "transform" / PIPELINE_NAME
        self.baseline_path = transform_dir / ANALYTIC_DEM_FILENAME
        self.state_dir = transform_dir / STATE_VALIDATION_DIRECTORY_NAME
        self.global_dir = transform_dir / GLOBAL_VALIDATION_DIRECTORY_NAME
        self.output_dir = transform_dir / STATEWIDE_CANDIDATE_DIRECTORY_NAME
        self.output_path = self.output_dir / STATEWIDE_CANDIDATE_FILENAME
        self.manifest_path = self.output_dir / STATEWIDE_CANDIDATE_MANIFEST_FILENAME
        self.halo_manifest_path = self.output_dir / "tile_validation" / "halo_validation.json"
        self.contextual_manifest_path = (
            self.output_dir / "contextual_reference_validation" / "contextual_reference_validation.json"
        )
        self.seam_manifest_path = self.output_dir / "seam_qa.json"

    def execute(self) -> dict[str, Any]:
        inventory, phase5d, halo_validation = self._validate_inputs()
        backend = self._backend(phase5d)
        production = condition_raster_tiled(
            self.baseline_path,
            self.output_path,
            backend,
            STATEWIDE_CANDIDATE_FP2_CONFIG,
            STATEWIDE_CANDIDATE_TILE_SIZE_PIXELS,
            int(halo_validation["selected_halo_pixels"]),
        )
        return self._finalize_candidate(inventory, phase5d, halo_validation, backend, production)

    def finalize_existing(self) -> dict[str, Any]:
        if not self.output_path.is_file():
            raise FileNotFoundError(f"Existing statewide candidate is required: {self.output_path}")
        observed_sha256 = sha256_file(self.output_path)
        if observed_sha256 != STATEWIDE_CANDIDATE_SHA256:
            raise ValueError(
                f"Statewide candidate checksum mismatch: expected {STATEWIDE_CANDIDATE_SHA256}, "
                f"observed {observed_sha256}"
            )
        inventory, phase5d, halo_validation = self._validate_inputs()
        backend = self._recorded_backend(phase5d)
        return self._finalize_candidate(inventory, phase5d, halo_validation, backend, None)

    def _finalize_candidate(
        self,
        inventory: dict[str, Any],
        phase5d: dict[str, Any],
        halo_validation: dict[str, Any],
        backend: dict[str, Any],
        production: dict[str, Any] | None,
    ) -> dict[str, Any]:
        started = time.perf_counter()
        output_sha256 = sha256_file(self.output_path)
        candidate_checksum_passed = output_sha256 == STATEWIDE_CANDIDATE_SHA256
        if not candidate_checksum_passed:
            raise ValueError("Statewide candidate changed before finalization")
        raster_contract, grid = self._raster_contract()
        global_qa = streaming_global_qa(self.baseline_path, self.output_path)
        contextual = validate_contextual_reference_manifest(
            self.contextual_manifest_path,
            STATE_VALIDATION_CHIP_COUNT_TARGET,
            int(halo_validation["selected_halo_pixels"]),
            STATEWIDE_CANDIDATE_TILE_SIZE_PIXELS,
        )
        seams = validate_seam_manifest(
            self.seam_manifest_path,
            STATEWIDE_CANDIDATE_TILE_SIZE_PIXELS,
            raster_contract["width"],
            raster_contract["height"],
        )
        historical = self._phase5d_isolated_reference_evidence(
            inventory,
            phase5d,
            int(halo_validation["selected_halo_pixels"]),
        )
        mask = global_qa["valid_pixels"]
        max_difference = global_qa["absolute_difference_m"]["maximum"]
        gates = {
            "baseline_checksum": True,
            "candidate_checksum": candidate_checksum_passed,
            "grid": grid["passed"],
            "nodata_mask": mask["mask_mismatch"] == 0,
            "max_abs_dz": max_difference
            <= float(STATEWIDE_CANDIDATE_FP2_CONFIG["max_diff_m"]) + STATEWIDE_CANDIDATE_FLOAT_TOLERANCE_M,
            "fp2_halo_validation": True,
            "contextual_equivalence_30_of_30": contextual["manifest"]["all_chips_exact"],
            "contextual_seam_crossing_equivalence": contextual["manifest"]["all_seam_crossing_chips_exact"],
        }
        gates["all_passed"] = all(gates.values())
        status = "statewide_candidate_generated_not_promoted" if gates["all_passed"] else "statewide_processing_failed"
        global_summary = {
            "bias_m": global_qa["bias_m"],
            "MAE_m": global_qa["mae_m"],
            "RMSE_m": global_qa["rmse_m"],
            "max_abs_dz_m": max_difference,
            "pct_gt_0_10_m": global_qa["threshold_percentages"]["abs_change_gt_0.10_m"],
            "pct_gt_0_25_m": global_qa["threshold_percentages"]["abs_change_gt_0.25_m"],
            "pct_gt_0_50_m": global_qa["threshold_percentages"]["abs_change_gt_0.50_m"],
            "absolute_difference_percentiles_m": global_qa["absolute_difference_m"],
            "elevation_distribution_m": global_qa["elevation_distribution_m"],
            "percentile_method": global_qa["percentile_method"],
        }
        contextual_manifest = contextual["manifest"]
        seam_manifest = seams["manifest"]
        processing = {
            "tile_size_pixels": STATEWIDE_CANDIDATE_TILE_SIZE_PIXELS,
            "halo_pixels": halo_validation["selected_halo_pixels"],
            "tile_count": 225,
            "processing_order": "row-major",
            "production_elapsed_seconds": production.get("elapsed_seconds") if production else None,
            "production_elapsed_note": (None if production else "not recovered after interactive session interruption"),
        }
        if production is not None:
            processing["production_metrics"] = production
        manifest = {
            "phase": "6A_statewide_FP2_candidate_production",
            "pipeline_version": PIPELINE_VERSION,
            "created_at": datetime.now().astimezone().isoformat(),
            "status": status,
            "decision": {"allowed": list(STATEWIDE_CANDIDATE_DECISIONS), "value": status},
            "source_baseline": {
                "path": str(self.baseline_path),
                "sha256": EXPERIMENT_BASELINE_SHA256,
                "immutable": True,
            },
            "conditioning": {
                "method": "WhiteboxTools FeaturePreservingSmoothing",
                "candidate_id": "FP2",
                "parameters": dict(STATEWIDE_CANDIDATE_FP2_CONFIG),
                "promoted": False,
            },
            "whitebox_backend": backend,
            "processing": processing,
            "raster_candidate": {
                "conceptual_id": "modelo_elevacion_acondicionado_contexto",
                "path": str(self.output_path),
                "sha256": output_sha256,
                "size_bytes": self.output_path.stat().st_size,
                "staging_with_10km_buffer": True,
                "territorial_clip_applied": False,
                "institutional_product": False,
            },
            "grid": raster_contract,
            "valid_pixels": mask,
            "global_Z_QA": global_summary,
            "halo_validation": {
                "path": str(self.halo_manifest_path),
                "sha256": sha256_file(self.halo_manifest_path),
                "controls": list(STATEWIDE_CANDIDATE_HALO_TEST_CHIP_IDS),
                "minimum_common_exact_halo_pixels": halo_validation["selected_halo_pixels"],
                "confirmation_halo_pixels": 32,
                "exact": True,
            },
            "contextual_equivalence": {
                "chips": contextual_manifest["chip_count"],
                "exact": contextual_manifest["exact_chip_count"],
                "max_abs_difference": max(
                    result["max_abs_difference"] for result in contextual_manifest["results"].values()
                ),
                "seam_crossing_chips": contextual_manifest["seam_crossing_chip_count"],
                "seam_crossing_exact": contextual_manifest["exact_seam_crossing_chip_count"],
                "artifact": {"path": contextual["path"], "sha256": contextual["sha256"]},
            },
            "seam_QA": {
                "seam_count": seam_manifest["seam_count"],
                "aggregate": seam_manifest["aggregate"],
                "descriptive_not_a_threshold_gate": True,
                "artifact": {"path": seams["path"], "sha256": seams["sha256"]},
            },
            "phase5d_isolated_reference_evidence": historical,
            "quality_gates": gates,
            "finalization_elapsed_seconds": time.perf_counter() - started,
            "final_slopes_generated": False,
            "load_executed": False,
            "institutional_products_generated": [],
        }
        write_json_atomic(manifest, self.manifest_path)
        return manifest

    def _validate_inputs(self) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
        if sha256_file(self.baseline_path) != EXPERIMENT_BASELINE_SHA256:
            raise ValueError("Frozen baseline checksum changed")
        inventory = read_json(self.state_dir / STATE_VALIDATION_INVENTORY_FILENAME)
        phase5d = read_json(self.global_dir / GLOBAL_VALIDATION_MANIFEST_FILENAME)
        halo_validation = read_json(self.halo_manifest_path)
        if inventory is None or phase5d is None or halo_validation is None:
            raise FileNotFoundError("Phase 5A, Phase 5D and FP2 halo validation are required")
        if phase5d["status"] != "completed_reviewed_no_statewide_execution":
            raise ValueError("Phase 5D is not frozen")
        if phase5d["decision"]["value"] != "FP2_recomendado_para_procesamiento_estatal":
            raise ValueError("Phase 5D did not select FP2")
        if halo_validation["selected_halo_pixels"] != 24:
            raise ValueError("FP2 halo gate did not select the empirically validated halo 24")
        for control in STATEWIDE_CANDIDATE_HALO_TEST_CHIP_IDS:
            for halo in (24, 32):
                result = halo_validation["results"][control]["halos"][str(halo)]
                if not result["comparison"]["array_identical"] or not result["seams"]["seam_free"]:
                    raise ValueError(f"FP2 halo gate failed for {control} at halo {halo}")
        return inventory, phase5d, halo_validation

    def _backend(self, phase5d: dict[str, Any]) -> dict[str, Any]:
        previous = phase5d["whitebox_backend"]
        backend = inspect_whitebox_backend(
            Path(previous["executable"]),
            previous["expected_exact_version"],
            previous["executable_sha256"],
        )
        frontend = importlib.metadata.version("whitebox")
        if frontend != "2.3.6":
            raise ValueError(f"whitebox frontend mismatch: {frontend}")
        return {
            **backend,
            "python_frontend_contract": "whitebox==2.3.6",
            "python_frontend_observed": frontend,
        }

    def _recorded_backend(self, phase5d: dict[str, Any]) -> dict[str, Any]:
        backend = dict(phase5d["whitebox_backend"])
        if backend.get("observed_version") != "WhiteboxTools v2.4.0 (c) Dr. John Lindsay 2017-2023":
            raise ValueError("Recorded WhiteboxTools engine version changed")
        if backend.get("executable_sha256") != "96bb47a9d1f0fe8a3cb46df524242c990eab9bc2ae1930e540e09328331172e4":
            raise ValueError("Recorded WhiteboxTools engine checksum changed")
        if backend.get("python_frontend_contract") != "whitebox==2.3.6":
            raise ValueError("Recorded whitebox frontend contract changed")
        return {
            **backend,
            "revalidated_during_finalization": False,
            "finalization_note": "Existing-candidate QA does not require the production executable.",
        }

    def _raster_contract(self) -> tuple[dict[str, Any], dict[str, Any]]:
        with rasterio.open(self.baseline_path) as baseline, rasterio.open(self.output_path) as output:
            grid = validate_matching_grid(baseline, output)
            output.read(1, window=Window(output.width - 1, output.height - 1, 1, 1))
            contract = {
                "crs_epsg": output.crs.to_epsg() if output.crs else None,
                "resolution_m": [abs(output.res[0]), abs(output.res[1])],
                "width": output.width,
                "height": output.height,
                "origin": [output.transform.c, output.transform.f],
                "dtype": "Float32" if output.dtypes[0] == "float32" else output.dtypes[0],
                "nodata": output.nodata,
                "block_shape": list(output.block_shapes[0]),
                "compression": output.compression.value.upper() if output.compression else None,
                "last_pixel_readable": True,
            }
        expected = {
            "crs_epsg": contract["crs_epsg"] == 6368,
            "dimensions": (contract["width"], contract["height"]) == (30533, 29255),
            "resolution": contract["resolution_m"] == [15.0, 15.0],
            "origin": contract["origin"] == [417465.0, 2525730.0],
            "block_shape": contract["block_shape"] == [256, 256],
            "compression": contract["compression"] == "DEFLATE",
        }
        grid["checks"].update(expected)
        grid["passed"] = all(grid["checks"].values())
        return contract, grid

    def _phase5d_isolated_reference_evidence(
        self,
        inventory: dict[str, Any],
        phase5d: dict[str, Any],
        halo: int,
    ) -> dict[str, Any]:
        results = {}
        with rasterio.open(self.output_path) as output:
            for chip in inventory["chips"]:
                chip_id = chip["chip_id"]
                window = Window(chip["column_offset"], chip["row_offset"], chip["width"], chip["height"])
                statewide = output.read(1, window=window)
                reference_path = Path(phase5d["results"][chip_id]["candidates"]["FP2"]["artifact"]["path"])
                with rasterio.open(reference_path) as reference_dataset:
                    reference = reference_dataset.read(1)
                core = np.s_[halo:-halo, halo:-halo]
                results[chip_id] = {
                    "complete_chip": comparison_metrics(reference, statewide),
                    "interior_excluding_24px": comparison_metrics(reference[core], statewide[core]),
                }
        return {
            "chip_count": len(results),
            "complete_exact_chip_count": sum(result["complete_chip"]["array_identical"] for result in results.values()),
            "interior_24px_exact_chip_count": sum(
                result["interior_excluding_24px"]["array_identical"] for result in results.values()
            ),
            "interior_24px_total_different_pixels": sum(
                result["interior_excluding_24px"]["n_pixels_different"] for result in results.values()
            ),
            "interior_24px_max_abs_difference": max(
                result["interior_excluding_24px"]["max_abs_difference"] for result in results.values()
            ),
            "all_complete_chips_identical": all(
                result["complete_chip"]["array_identical"] for result in results.values()
            ),
            "all_interiors_excluding_24px_identical": all(
                result["interior_excluding_24px"]["array_identical"] for result in results.values()
            ),
            "hard_gate": False,
            "interpretation": (
                "Phase-5D FP2 references were processed as isolated 1024x1024 rasters. Their edge differences are "
                "expected reference-boundary effects; only contextual references are a causal assembly gate."
            ),
            "results": results,
        }
