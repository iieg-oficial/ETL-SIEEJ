from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import rasterio
from rasterio.windows import Window, transform as window_transform

from core.pipelines.pendientes.config import settings
from core.pipelines.pendientes.constants import (
    ANALYTIC_DEM_FILENAME,
    AOI_FILENAME,
    CALIBRATION_FP_LIMIT_TOLERANCE_M,
    DIAGNOSTIC_CHIP_SIZE,
    EXPERIMENT_BASELINE_SHA256,
    FINAL_NODATA,
    PIPELINE_NAME,
    PIPELINE_VERSION,
    STATE_VALIDATION_CHIP_COUNT_TARGET,
    STATE_VALIDATION_DECISION_LABELS,
    STATE_VALIDATION_DIRECTORY_NAME,
    STATE_VALIDATION_FP3_CONFIG,
    STATE_VALIDATION_HALO_CANDIDATES_PIXELS,
    STATE_VALIDATION_INVENTORY_FILENAME,
    STATE_VALIDATION_MANIFEST_FILENAME,
    STATE_VALIDATION_TILE_SIZE_PIXELS,
    STATE_VALIDATION_TILE_TEST_CHIP_COUNT,
    STATE_VALIDATION_VISUAL_CHIP_COUNT,
    TARGET_RESOLUTION_M,
    TARGET_SRID,
)
from core.pipelines.pendientes.helpers.methodology.calibration_profiles import (
    profile_lines_from_raw,
    profile_records,
    write_profile_csv,
    write_profile_png,
)
from core.pipelines.pendientes.helpers.experimental_artifacts import (
    hillshade,
    write_comparison_png,
    write_float_raster,
)
from core.pipelines.pendientes.helpers.methodology.experimental_chips import ChipWindow, manual_chip, scan_chip_candidates
from core.pipelines.pendientes.helpers.experimental_metrics import valid_mask
from core.pipelines.pendientes.helpers.experimental_whitebox import (
    inspect_whitebox_backend,
    run_feature_preserving_smoothing,
)
from core.pipelines.pendientes.helpers.slope import experimental_horn_slope
from core.pipelines.pendientes.helpers.methodology.state_validation_qa import (
    aggregate_state_validation,
    assign_full_resolution_banding_classes,
    select_visual_cases,
    state_chip_qa,
)
from core.pipelines.pendientes.helpers.methodology.state_validation_sampling import (
    chip_window_from_inventory,
    classify_candidate_pool,
    enrich_candidate_pool,
    select_spatially_stratified,
)
from core.pipelines.pendientes.helpers.tiled_conditioning import (
    comparison_metrics,
    run_full_reference,
    run_tiled_reference,
    seam_metrics,
)
from core.utils.files import read_json, sha256_file, write_json_atomic


class PendientesStateValidation:
    """Validate FP3 spatially and empirically prove a tiled execution contract."""

    def __init__(self) -> None:
        transform_dir = Path("data") / "transform" / PIPELINE_NAME
        self.baseline_path = transform_dir / ANALYTIC_DEM_FILENAME
        self.aoi_path = transform_dir / AOI_FILENAME
        self.output_dir = transform_dir / STATE_VALIDATION_DIRECTORY_NAME
        self.inventory_path = self.output_dir / STATE_VALIDATION_INVENTORY_FILENAME
        self.manifest_path = self.output_dir / STATE_VALIDATION_MANIFEST_FILENAME

    def execute(self) -> dict[str, Any]:
        started = time.perf_counter()
        baseline = self._validate_baseline()
        backend = self._whitebox_backend()
        inventory, chips = self._build_inventory()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        write_json_atomic(inventory, self.inventory_path)
        tile_validation = self._validate_tiling(chips, backend)
        if tile_validation["selected_halo_pixels"] is None:
            manifest = self._base_manifest(baseline, backend, inventory, tile_validation)
            manifest.update(
                {
                    "status": "blocked_no_exact_tiled_equivalence",
                    "results": {},
                    "aggregate_qa": {},
                    "decision": {
                        "status": "requires_design_stop",
                        "allowed": list(STATE_VALIDATION_DECISION_LABELS),
                        "value": "requiere_ajuste",
                        "promoted": False,
                    },
                    "elapsed_seconds": time.perf_counter() - started,
                }
            )
            write_json_atomic(manifest, self.manifest_path)
            return manifest

        results: dict[str, dict[str, Any]] = {}
        selected_halo = int(tile_validation["selected_halo_pixels"])
        for chip in chips:
            metadata = next(item for item in inventory["chips"] if item["chip_id"] == chip.chip_id)
            results[chip.chip_id] = self._run_chip(chip, metadata, backend, selected_halo)
        banding_classification = assign_full_resolution_banding_classes(results)
        aggregate = aggregate_state_validation(results)
        visual_chip_ids = select_visual_cases(results, STATE_VALIDATION_VISUAL_CHIP_COUNT)
        visualizations = {
            chip_id: self._write_visualizations(results[chip_id]) for chip_id in visual_chip_ids
        }
        profile_chip_ids = self._profile_chip_ids(results)
        profiles = {chip_id: self._write_profiles(results[chip_id]) for chip_id in profile_chip_ids}
        inventory["full_resolution_results"] = {
            chip_id: {
                "raw_summary": result["qa"]["raw_summary"],
                "raw_banding": result["qa"]["raw_banding"],
                "raw_banding_class": result["raw_banding_class"],
            }
            for chip_id, result in results.items()
        }
        write_json_atomic(inventory, self.inventory_path)
        performance = self._performance(results, baseline)
        manifest = self._base_manifest(baseline, backend, inventory, tile_validation)
        manifest.update(
            {
                "status": "completed_pending_review",
                "results": results,
                "banding_classification": banding_classification,
                "aggregate_qa": aggregate,
                "visualizations": visualizations,
                "profiles": profiles,
                "performance": performance,
                "decision": {
                    "status": "awaiting_quantitative_and_visual_review",
                    "allowed": list(STATE_VALIDATION_DECISION_LABELS),
                    "value": None,
                    "promoted": False,
                    "statewide_dem_generated": False,
                },
                "elapsed_seconds": time.perf_counter() - started,
            }
        )
        write_json_atomic(manifest, self.manifest_path)
        return manifest

    def record_review(self, decision: str, evidence: dict[str, Any]) -> dict[str, Any]:
        if decision not in STATE_VALIDATION_DECISION_LABELS:
            raise ValueError(f"Invalid state-validation decision: {decision}")
        manifest = read_json(self.manifest_path)
        if manifest is None:
            raise FileNotFoundError(f"State-validation manifest not found: {self.manifest_path}")
        if manifest.get("status") != "completed_pending_review":
            raise ValueError("A completed quantitative validation is required before review")
        manifest["decision"] = {
            "status": "reviewed_without_promotion",
            "allowed": list(STATE_VALIDATION_DECISION_LABELS),
            "value": decision,
            "evidence": evidence,
            "promoted": False,
            "statewide_dem_generated": False,
            "recommendation_is_not_promotion": decision == "recomendado_para_promocion",
            "reviewed_at": datetime.now().astimezone().isoformat(),
        }
        manifest["status"] = "completed_reviewed_not_promoted"
        write_json_atomic(manifest, self.manifest_path)
        return manifest

    def _validate_baseline(self) -> dict[str, Any]:
        checksum = sha256_file(self.baseline_path)
        if checksum != EXPERIMENT_BASELINE_SHA256:
            raise ValueError("Frozen phase-3 baseline checksum changed")
        with rasterio.open(self.baseline_path) as dataset:
            if (
                dataset.crs is None
                or dataset.crs.to_epsg() != TARGET_SRID
                or dataset.res != (TARGET_RESOLUTION_M, TARGET_RESOLUTION_M)
                or dataset.dtypes != ("float32",)
                or dataset.nodata != FINAL_NODATA
            ):
                raise ValueError("Frozen phase-3 baseline raster contract changed")
            return {
                "path": str(self.baseline_path),
                "sha256": checksum,
                "shape": list(dataset.shape),
                "bounds": list(dataset.bounds),
                "pixel_count": dataset.width * dataset.height,
                "crs_epsg": dataset.crs.to_epsg(),
                "resolution_m": list(dataset.res),
                "dtype": dataset.dtypes[0],
                "nodata": dataset.nodata,
                "immutable": True,
            }

    def _whitebox_backend(self) -> dict[str, Any]:
        if (
            settings.WHITEBOX_TOOLS_EXECUTABLE is None
            or settings.WHITEBOX_TOOLS_EXPECTED_VERSION is None
            or settings.WHITEBOX_TOOLS_EXPECTED_SHA256 is None
        ):
            raise ValueError("Whitebox executable, exact version and checksum are required for phase 5A")
        backend = inspect_whitebox_backend(
            settings.WHITEBOX_TOOLS_EXECUTABLE.expanduser().resolve(),
            settings.WHITEBOX_TOOLS_EXPECTED_VERSION,
            settings.WHITEBOX_TOOLS_EXPECTED_SHA256,
        )
        return {
            **backend,
            "python_frontend_contract": "whitebox==2.3.6",
            "validated_before_batch_execution": True,
            "binary_packaged_in_git": False,
        }

    def _build_inventory(self) -> tuple[dict[str, Any], list[ChipWindow]]:
        candidates = scan_chip_candidates(self.baseline_path, self.aoi_path)
        problem = manual_chip(self.baseline_path, 750968.0, 2329434.0)
        problem_item = {
            **problem.to_dict(),
            "slope_median_degrees": problem.preliminary_slope_median_degrees,
            "roughness_median_abs_laplacian_m": problem.preliminary_roughness_median_abs_laplacian_m,
            "valid_percentage": problem.preliminary_valid_percentage,
            "mandatory_manual": True,
        }
        enriched = enrich_candidate_pool(self.baseline_path, [*candidates, problem_item])
        classified, selection_contract = classify_candidate_pool(enriched)
        regular = [item for item in classified if not item.get("mandatory_manual")]
        problem_classified = next(item for item in classified if item.get("mandatory_manual"))
        selected = select_spatially_stratified(regular)
        problem_classified = {
            **problem_classified,
            "selection_criterion": "mandatory known problem coordinate from phase 4B",
        }
        selected.append(problem_classified)
        if len(selected) != STATE_VALIDATION_CHIP_COUNT_TARGET:
            raise ValueError(
                f"State validation expected {STATE_VALIDATION_CHIP_COUNT_TARGET} chips; selected {len(selected)}"
            )
        selected = sorted(selected, key=lambda item: (item.get("mandatory_manual") is True, item["spatial_sector"]))
        chips: list[ChipWindow] = []
        inventory_chips: list[dict[str, Any]] = []
        for index, item in enumerate(selected, start=1):
            chip_id = "problema_manual" if item.get("mandatory_manual") else f"sv_{index:02d}_{item['spatial_sector']}"
            chips.append(chip_window_from_inventory(item, chip_id))
            inventory_chips.append(
                {
                    "chip_id": chip_id,
                    "center_x": item["center_x"],
                    "center_y": item["center_y"],
                    "bbox": item["bbox"],
                    "row_offset": item["row_offset"],
                    "column_offset": item["column_offset"],
                    "width": item["width"],
                    "height": item["height"],
                    "spatial_sector": item["spatial_sector"],
                    "morphology_class": item["morphology_class"],
                    "preliminary_elevation_m": item["preliminary_elevation_m"],
                    "preliminary_slope_median_degrees": item["slope_median_degrees"],
                    "preliminary_roughness_median_abs_laplacian_m": item[
                        "roughness_median_abs_laplacian_m"
                    ],
                    "preliminary_local_relief_m": item["preliminary_local_relief_m"],
                    "preliminary_raw_banding": item["preliminary_raw_banding"],
                    "preliminary_raw_banding_class": item["raw_banding_class"],
                    "valid_percentage": item["valid_percentage"],
                    "selection_criterion": item["selection_criterion"],
                    "mandatory_manual": bool(item.get("mandatory_manual")),
                    "grid_aligned": True,
                }
            )
        inventory = {
            "phase": "5A_state_spatial_validation_FP3",
            "created_at": datetime.now().astimezone().isoformat(),
            "baseline_path": str(self.baseline_path),
            "baseline_sha256": EXPERIMENT_BASELINE_SHA256,
            "chip_count": len(inventory_chips),
            "chip_size_pixels": DIAGNOSTIC_CHIP_SIZE,
            "chip_size_metres": DIAGNOSTIC_CHIP_SIZE * TARGET_RESOLUTION_M,
            "selection_contract": selection_contract,
            "chips": inventory_chips,
        }
        return inventory, chips

    def _tile_test_chips(self, chips: list[ChipWindow]) -> list[ChipWindow]:
        problem = next(chip for chip in chips if chip.chip_id == "problema_manual")
        candidates = [chip for chip in chips if chip.chip_id != "problema_manual"]
        selected = [problem]
        for morphology in ("plano", "montana"):
            match = next(chip for chip in candidates if chip.terrain_class == morphology)
            selected.append(match)
        remaining = next(chip for chip in candidates if chip not in selected)
        selected.append(remaining)
        return selected[:STATE_VALIDATION_TILE_TEST_CHIP_COUNT]

    def _read_chip(self, chip: ChipWindow) -> tuple[np.ndarray, Any, rasterio.crs.CRS, float | None]:
        with rasterio.open(self.baseline_path) as dataset:
            return (
                dataset.read(1, window=chip.window),
                window_transform(chip.window, dataset.transform),
                dataset.crs,
                dataset.nodata,
            )

    def _validate_tiling(self, chips: list[ChipWindow], backend: dict[str, Any]) -> dict[str, Any]:
        chip_results: dict[str, Any] = {}
        for chip in self._tile_test_chips(chips):
            raw, transform, crs, nodata = self._read_chip(chip)
            chip_dir = self.output_dir / "tile_validation" / chip.chip_id
            reference, reference_execution = run_full_reference(
                backend,
                raw,
                transform,
                crs,
                nodata,
                STATE_VALIDATION_FP3_CONFIG,
                chip_dir / "full_reference",
            )
            halo_results: dict[str, Any] = {}
            for halo in STATE_VALIDATION_HALO_CANDIDATES_PIXELS:
                reconstructed, execution = run_tiled_reference(
                    backend,
                    raw,
                    transform,
                    crs,
                    nodata,
                    STATE_VALIDATION_FP3_CONFIG,
                    chip_dir / f"halo_{halo}",
                    STATE_VALIDATION_TILE_SIZE_PIXELS,
                    halo,
                )
                halo_results[str(halo)] = {
                    "comparison": comparison_metrics(reference, reconstructed),
                    "seams": seam_metrics(
                        reference,
                        reconstructed,
                        STATE_VALIDATION_TILE_SIZE_PIXELS,
                        halo,
                    ),
                    "execution": execution,
                }
            chip_results[chip.chip_id] = {
                "full_reference_execution": reference_execution,
                "halos": halo_results,
            }
        selected_halo = next(
            (
                halo
                for halo in STATE_VALIDATION_HALO_CANDIDATES_PIXELS
                if all(
                    item["halos"][str(halo)]["comparison"]["array_identical"]
                    and item["halos"][str(halo)]["seams"]["seam_free"]
                    for item in chip_results.values()
                )
            ),
            None,
        )
        return {
            "reference": "complete 1024x1024 chip processed by WhiteboxTools FP3",
            "tile_size_pixels": STATE_VALIDATION_TILE_SIZE_PIXELS,
            "halo_candidates_pixels": list(STATE_VALIDATION_HALO_CANDIDATES_PIXELS),
            "test_chip_count": len(chip_results),
            "chips": chip_results,
            "selected_halo_pixels": selected_halo,
            "selection_rule": "minimum candidate bitwise-identical in every test chip and seam region",
            "float32_exact_required": True,
        }

    def _run_chip(
        self,
        chip: ChipWindow,
        metadata: dict[str, Any],
        backend: dict[str, Any],
        halo: int,
    ) -> dict[str, Any]:
        context_window = Window(
            chip.column_offset - halo,
            chip.row_offset - halo,
            chip.width + 2 * halo,
            chip.height + 2 * halo,
        )
        with rasterio.open(self.baseline_path) as dataset:
            context = dataset.read(1, window=context_window)
            context_transform = window_transform(context_window, dataset.transform)
            transform = window_transform(chip.window, dataset.transform)
            crs = dataset.crs
            nodata = dataset.nodata
        chip_dir = self.output_dir / "chips" / chip.chip_id
        input_path = write_float_raster(
            chip_dir / "backend" / "input_with_halo.tif",
            context,
            valid_mask(context, nodata),
            context_transform,
            crs,
        )
        backend_output = chip_dir / "backend" / "fp3_with_halo.tif"
        execution = run_feature_preserving_smoothing(
            backend,
            input_path,
            backend_output,
            STATE_VALIDATION_FP3_CONFIG,
        )
        with rasterio.open(backend_output) as dataset:
            filtered_context = dataset.read(1)
        core = np.s_[halo : halo + chip.height, halo : halo + chip.width]
        raw = context[core].astype(np.float32)
        fp3 = filtered_context[core].astype(np.float32)
        qa, _ = state_chip_qa(raw, fp3, nodata)
        observed_maximum = qa["metrics"]["elevation"]["absolute_difference_m"]["maximum"]
        limit = float(STATE_VALIDATION_FP3_CONFIG["max_diff_m"])
        if observed_maximum > limit + CALIBRATION_FP_LIMIT_TOLERANCE_M:
            raise ValueError(f"FP3 exceeded max_diff in {chip.chip_id}")
        raw_path = write_float_raster(
            chip_dir / "RAW.tif",
            raw,
            valid_mask(raw, nodata),
            transform,
            crs,
        )
        fp3_path = write_float_raster(
            chip_dir / "FP3.tif",
            fp3,
            valid_mask(fp3, nodata),
            transform,
            crs,
        )
        return {
            "chip": {**metadata, "chip_id": chip.chip_id},
            "qa": qa,
            "max_diff_verification": {
                "configured_m": limit,
                "tolerance_m": CALIBRATION_FP_LIMIT_TOLERANCE_M,
                "observed_m": observed_maximum,
                "passed": True,
            },
            "execution": execution,
            "artifacts": {"RAW": str(raw_path), "FP3": str(fp3_path)},
        }

    def _write_visualizations(self, result: dict[str, Any]) -> dict[str, Any]:
        with rasterio.open(result["artifacts"]["RAW"]) as dataset:
            raw = dataset.read(1)
            nodata = dataset.nodata
        with rasterio.open(result["artifacts"]["FP3"]) as dataset:
            fp3 = dataset.read(1)
        raw_valid = valid_mask(raw, nodata)
        fp3_valid = valid_mask(fp3, nodata)
        raw_hillshade, raw_hillshade_valid = hillshade(raw, TARGET_RESOLUTION_M, nodata)
        fp3_hillshade, fp3_hillshade_valid = hillshade(fp3, TARGET_RESOLUTION_M, nodata)
        raw_slope, _, raw_slope_valid = experimental_horn_slope(raw, TARGET_RESOLUTION_M, nodata)
        fp3_slope, _, fp3_slope_valid = experimental_horn_slope(fp3, TARGET_RESOLUTION_M, nodata)
        qa, arrays = state_chip_qa(raw, fp3, nodata)
        difference = fp3.astype(np.float64) - raw.astype(np.float64)
        output_dir = self.output_dir / "visualizations" / result["chip"]["chip_id"]
        slope_maximum = max(
            float(np.percentile(raw_slope[raw_slope_valid], 99)),
            float(np.percentile(fp3_slope[fp3_slope_valid], 99)),
        )
        banding_maximum = max(
            float(np.percentile(arrays["raw_banding_raster"][arrays["raw_banding_valid"]], 99)),
            float(np.percentile(arrays["candidate_banding_raster"][arrays["candidate_banding_valid"]], 99)),
        )
        return {
            "selection_context": {
                "morphology_class": result["chip"]["morphology_class"],
                "raw_banding_class": result["raw_banding_class"],
                "mae_z_m": qa["metrics"]["elevation"]["mae_m"],
            },
            "hillshade": write_comparison_png(
                output_dir / "hillshade.png",
                [("RAW", raw_hillshade, raw_hillshade_valid), ("FP3", fp3_hillshade, fp3_hillshade_valid)],
                0.0,
                255.0,
            ),
            "slope_horn_degrees": write_comparison_png(
                output_dir / "slope_horn_degrees.png",
                [("RAW", raw_slope, raw_slope_valid), ("FP3", fp3_slope, fp3_slope_valid)],
                0.0,
                slope_maximum,
            ),
            "difference_z": write_comparison_png(
                output_dir / "difference_z.png",
                [("FP3_minus_RAW", difference, raw_valid & fp3_valid)],
                -float(STATE_VALIDATION_FP3_CONFIG["max_diff_m"]),
                float(STATE_VALIDATION_FP3_CONFIG["max_diff_m"]),
            ),
            "directed_banding": write_comparison_png(
                output_dir / "directed_banding.png",
                [
                    ("RAW", arrays["raw_banding_raster"], arrays["raw_banding_valid"]),
                    ("FP3", arrays["candidate_banding_raster"], arrays["candidate_banding_valid"]),
                ],
                0.0,
                banding_maximum,
            ),
        }

    def _profile_chip_ids(self, results: dict[str, dict[str, Any]]) -> list[str]:
        high = sorted(
            (
                (chip_id, result["qa"]["raw_dominant_repetition"]["autocorrelation"])
                for chip_id, result in results.items()
                if result["raw_banding_class"] == "banding_alto" and chip_id != "problema_manual"
            ),
            key=lambda item: (-item[1], item[0]),
        )[:3]
        worst = max(
            results.items(),
            key=lambda item: (
                item[1]["qa"]["fp3_dominant_repetition"]["autocorrelation"]
                - item[1]["qa"]["raw_dominant_repetition"]["autocorrelation"],
                item[0],
            ),
        )[0]
        selected = ["problema_manual", *(item[0] for item in high)]
        if worst not in selected:
            selected.append(worst)
        return selected

    def _write_profiles(self, result: dict[str, Any]) -> dict[str, Any]:
        with rasterio.open(result["artifacts"]["RAW"]) as dataset:
            raw = dataset.read(1)
            transform = dataset.transform
            nodata = dataset.nodata
        with rasterio.open(result["artifacts"]["FP3"]) as dataset:
            fp3 = dataset.read(1)
        lines, contract = profile_lines_from_raw(raw, nodata)
        output: dict[str, Any] = {"contract": contract, "transects": {}}
        output_dir = self.output_dir / "profiles" / result["chip"]["chip_id"]
        for line in lines:
            records = profile_records(line, raw, {"FP3": fp3}, transform)
            csv_path = write_profile_csv(output_dir / f"{line.profile_id}.csv", records)
            png = write_profile_png(output_dir / f"{line.profile_id}.png", records, ("RAW", "FP3"))
            output["transects"][line.profile_id] = {
                "line": {
                    "normal_angle_degrees": line.normal_angle_degrees,
                    "tangent_offset_pixels": line.tangent_offset_pixels,
                    "sample_count": len(line.rows),
                },
                "csv_path": str(csv_path),
                "csv_sha256": sha256_file(csv_path),
                "plot": png,
            }
        return output

    def _performance(self, results: dict[str, dict[str, Any]], baseline: dict[str, Any]) -> dict[str, Any]:
        seconds = np.array([result["execution"]["elapsed_seconds"] for result in results.values()])
        equivalent_chip_count = baseline["pixel_count"] / (DIAGNOSTIC_CHIP_SIZE**2)
        return {
            "observed_execution_seconds_per_validation_chip": {
                "minimum": float(seconds.min()),
                "median": float(np.median(seconds)),
                "maximum": float(seconds.max()),
            },
            "baseline_equivalent_1024_pixel_tiles": float(equivalent_chip_count),
            "technical_serial_estimate_seconds": float(equivalent_chip_count * np.median(seconds)),
            "estimate_scope": "engine time extrapolation only; excludes masking, I/O orchestration and publication",
            "duration_promise": False,
        }

    def _base_manifest(
        self,
        baseline: dict[str, Any],
        backend: dict[str, Any],
        inventory: dict[str, Any],
        tile_validation: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "phase": "5A_state_spatial_validation_FP3",
            "pipeline_version": PIPELINE_VERSION,
            "created_at": datetime.now().astimezone().isoformat(),
            "baseline": baseline,
            "candidate": {
                "method": "WhiteboxTools FeaturePreservingSmoothing",
                **STATE_VALIDATION_FP3_CONFIG,
                "zfactor": 1.0,
                "phase4b_classification": "recomendado_para_validacion_estatal",
                "promoted": False,
            },
            "interpretive_controls": ["RAW", "FP1", "FP2"],
            "methods_not_executed": ["Gaussian", "bilateral", "FP4"],
            "inventory": {
                "path": str(self.inventory_path),
                "sha256": sha256_file(self.inventory_path),
                "chip_count": inventory["chip_count"],
            },
            "whitebox_backend": backend,
            "tile_validation": tile_validation,
            "statewide_processing": False,
            "statewide_dem_generated": False,
            "final_slopes_generated": False,
            "load_executed": False,
            "institutional_products_generated": [],
        }
