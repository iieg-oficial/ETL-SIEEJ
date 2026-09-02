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
    CALIBRATION_BILATERAL_CONFIG,
    CALIBRATION_CANDIDATE_ORDER,
    CALIBRATION_DECISION_LABELS,
    CALIBRATION_DIRECTORY_NAME,
    CALIBRATION_FEATURE_PRESERVING_CONFIGS,
    CALIBRATION_FP_LIMIT_TOLERANCE_M,
    CALIBRATION_MANIFEST_FILENAME,
    EXPERIMENT_BASELINE_SHA256,
    EXPERIMENT_DIRECTORY_NAME,
    EXPERIMENT_FILTER_HALO_PIXELS,
    EXPERIMENT_MANIFEST_FILENAME,
    FINAL_NODATA,
    PIPELINE_NAME,
    PIPELINE_VERSION,
    TARGET_RESOLUTION_M,
    TARGET_SRID,
)
from core.pipelines.pendientes.helpers.methodology.calibration_profiles import (
    profile_lines_from_raw,
    profile_records,
    write_profile_csv,
    write_profile_png,
)
from core.pipelines.pendientes.helpers.methodology.directed_banding import directed_banding_metrics
from core.pipelines.pendientes.helpers.experimental_artifacts import (
    hillshade,
    write_comparison_png,
    write_float_raster,
)
from core.pipelines.pendientes.helpers.methodology.experimental_chips import ChipWindow, manual_chip
from core.pipelines.pendientes.helpers.methodology.experimental_filters import bilateral_smoothing
from core.pipelines.pendientes.helpers.experimental_metrics import (
    experimental_metrics,
    local_neighbor_magnitude,
    valid_mask,
)
from core.pipelines.pendientes.helpers.experimental_whitebox import (
    inspect_whitebox_backend,
    run_feature_preserving_smoothing,
)
from core.utils.files import read_json, sha256_file, write_json_atomic


class PendientesCalibration:
    """Run directed phase-4B calibration only when a manual problem window exists."""

    def __init__(self) -> None:
        transform_dir = Path("data") / "transform" / PIPELINE_NAME
        self.baseline_path = transform_dir / ANALYTIC_DEM_FILENAME
        self.phase4_dir = transform_dir / EXPERIMENT_DIRECTORY_NAME
        self.phase4_manifest_path = self.phase4_dir / EXPERIMENT_MANIFEST_FILENAME
        self.output_dir = transform_dir / CALIBRATION_DIRECTORY_NAME
        self.manifest_path = self.output_dir / CALIBRATION_MANIFEST_FILENAME

    def execute(self) -> dict[str, Any]:
        started = time.perf_counter()
        baseline = self._validate_baseline()
        phase4_manifest = read_json(self.phase4_manifest_path)
        if phase4_manifest is None:
            raise FileNotFoundError(f"Phase-4 manifest not found: {self.phase4_manifest_path}")
        controls = self._control_chips(phase4_manifest)
        manifest = self._manifest_contract(baseline, controls)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        if settings.EXPERIMENT_MANUAL_X is None or settings.EXPERIMENT_MANUAL_Y is None:
            manifest.update(
                {
                    "status": "pending_manual_problem_coordinate",
                    "missing_configuration": ["EXPERIMENT_MANUAL_X", "EXPERIMENT_MANUAL_Y"],
                    "results": {},
                    "profiles": {},
                    "decision": {
                        "status": "not_evaluated",
                        "classifications": {},
                        "winner_selected": False,
                        "reason": "directed calibration requires evidence from problema_manual and all controls",
                    },
                    "elapsed_seconds": time.perf_counter() - started,
                }
            )
            write_json_atomic(manifest, self.manifest_path)
            return manifest

        backend = self._whitebox_backend()
        problem_chip = manual_chip(
            self.baseline_path,
            settings.EXPERIMENT_MANUAL_X,
            settings.EXPERIMENT_MANUAL_Y,
        )
        if problem_chip.preliminary_valid_percentage < 99.5:
            raise ValueError("Manual problem chip must have at least 99.5% valid baseline coverage")
        chips = [*controls, problem_chip]
        results: dict[str, Any] = {}
        profiles: dict[str, Any] = {}
        for chip in chips:
            chip_results, candidate_arrays, transform = self._run_chip(chip, backend, phase4_manifest)
            results[chip.chip_id] = chip_results
            if chip.chip_id == "problema_manual":
                profiles = self._write_profiles(candidate_arrays, transform, chip_results["raw_banding"])
        backend["executed"] = True
        manifest.update(
            {
                "status": "completed_pending_review",
                "manual_problem_coordinate": {
                    "x": settings.EXPERIMENT_MANUAL_X,
                    "y": settings.EXPERIMENT_MANUAL_Y,
                    "crs": f"EPSG:{TARGET_SRID}",
                    "chip": problem_chip.to_dict(),
                },
                "whitebox_backend": backend,
                "results": results,
                "profiles": profiles,
                "decision": {
                    "status": "awaiting_quantitative_and_visual_review",
                    "allowed_classifications": list(CALIBRATION_DECISION_LABELS),
                    "classifications": {},
                    "winner_selected": False,
                    "weighted_score": None,
                },
                "elapsed_seconds": time.perf_counter() - started,
            }
        )
        write_json_atomic(manifest, self.manifest_path)
        return manifest

    def record_review(
        self,
        classifications: dict[str, str],
        evidence: dict[str, Any],
    ) -> dict[str, Any]:
        """Attach a complete human/analytical review without promoting a candidate."""
        manifest = read_json(self.manifest_path)
        if manifest is None:
            raise FileNotFoundError(f"Phase-4B manifest not found: {self.manifest_path}")
        expected = set(CALIBRATION_CANDIDATE_ORDER) - {"RAW"}
        if set(classifications) != expected:
            raise ValueError(f"Classifications must cover exactly: {sorted(expected)}")
        invalid = {
            candidate_id: label
            for candidate_id, label in classifications.items()
            if label not in CALIBRATION_DECISION_LABELS
        }
        if invalid:
            raise ValueError(f"Invalid calibration classifications: {invalid}")
        if set(manifest.get("results", {})) != {"plano", "lomerio", "montana", "problema_manual"}:
            raise ValueError("Review requires problema_manual and all three control chips")

        for chip_result in manifest["results"].values():
            for candidate_id, label in classifications.items():
                chip_result["candidates"][candidate_id]["classification"] = label
        manifest["decision"] = {
            "status": "reviewed_no_promotion",
            "allowed_classifications": list(CALIBRATION_DECISION_LABELS),
            "classifications": classifications,
            "evidence": evidence,
            "winner_selected": False,
            "weighted_score": None,
            "recommendation_is_not_promotion": True,
            "reviewed_at": datetime.now().astimezone().isoformat(),
        }
        manifest["status"] = "completed_reviewed_not_promoted"
        write_json_atomic(manifest, self.manifest_path)
        return manifest

    def _validate_baseline(self) -> dict[str, Any]:
        if not self.baseline_path.is_file():
            raise FileNotFoundError(f"Baseline not found: {self.baseline_path}")
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
                "crs_epsg": dataset.crs.to_epsg(),
                "resolution_m": list(dataset.res),
                "shape": list(dataset.shape),
                "dtype": dataset.dtypes[0],
                "nodata": dataset.nodata,
                "immutable": True,
            }

    def _control_chips(self, phase4_manifest: dict[str, Any]) -> list[ChipWindow]:
        inventory_path = Path(str(phase4_manifest["chip_inventory_path"]))
        inventory = read_json(inventory_path)
        if inventory is None:
            raise FileNotFoundError(f"Phase-4 chip inventory not found: {inventory_path}")
        selected: list[ChipWindow] = []
        for chip_id in ("plano", "lomerio", "montana"):
            item = next((chip for chip in inventory["chips"] if chip["chip_id"] == chip_id), None)
            if item is None:
                raise ValueError(f"Phase-4 control chip missing: {chip_id}")
            selected.append(
                ChipWindow(
                    chip_id=item["chip_id"],
                    terrain_class=item["terrain_class"],
                    row_offset=item["row_offset"],
                    column_offset=item["column_offset"],
                    width=item["width"],
                    height=item["height"],
                    center_x=item["center_x"],
                    center_y=item["center_y"],
                    bbox=tuple(item["bbox"]),
                    selection_criterion="phase-4 frozen statistical control",
                    preliminary_slope_median_degrees=item["preliminary_slope_median_degrees"],
                    preliminary_roughness_median_abs_laplacian_m=item["preliminary_roughness_median_abs_laplacian_m"],
                    preliminary_valid_percentage=item["preliminary_valid_percentage"],
                )
            )
        return selected

    def _manifest_contract(self, baseline: dict[str, Any], controls: list[ChipWindow]) -> dict[str, Any]:
        return {
            "phase": "4B_directed_conditioning_calibration",
            "pipeline_version": PIPELINE_VERSION,
            "created_at": datetime.now().astimezone().isoformat(),
            "baseline": baseline,
            "phase4_manifest": {
                "path": str(self.phase4_manifest_path),
                "sha256": sha256_file(self.phase4_manifest_path),
            },
            "controls": [chip.to_dict() for chip in controls],
            "candidate_order": list(CALIBRATION_CANDIDATE_ORDER),
            "candidates": {
                "RAW": {"method": "unmodified baseline"},
                "B2": {"method": "bilateral", **CALIBRATION_BILATERAL_CONFIG},
                "feature_preserving": {
                    "method": "WhiteboxTools FeaturePreservingSmoothing",
                    "configurations": list(CALIBRATION_FEATURE_PRESERVING_CONFIGS),
                    "z_factor": 1.0,
                },
            },
            "discarded_from_new_tests": ["A2", "A3", "B1", "B3", "C2", "C3"],
            "A1_role": "optional visual reference only; not executed by default",
            "banding_metric_contract": {
                "components": [
                    "second-difference magnitude density above the RAW p90 threshold",
                    "axial coherence of second-difference normal orientations",
                    "immediate tangent-neighbor continuity of high-second-difference cells",
                    "maximum positive autocorrelation and lag of x/y high-magnitude projections",
                ],
                "same_raw_threshold_for_all_candidates_in_each_chip": True,
                "weighted_score": None,
                "acceptance_threshold": None,
                "target": "linear/repetitive abrupt gradient changes rather than flatness alone",
            },
            "profile_contract": {
                "scope": "problema_manual only",
                "orientation": "RAW dominant second-difference normal",
                "parallel_tangent_offsets_pixels": [-256, 0, 256],
                "columns": [
                    "distance_m",
                    "elevation_RAW_m",
                    "elevation_candidate_m",
                    "delta_candidate_m",
                ],
                "outputs": ["CSV", "PNG"],
            },
            "outputs_are_experimental": True,
            "institutional_products_generated": [],
            "statewide_processing": False,
        }

    def _whitebox_backend(self) -> dict[str, Any]:
        if (
            settings.WHITEBOX_TOOLS_EXECUTABLE is None
            or settings.WHITEBOX_TOOLS_EXPECTED_VERSION is None
            or settings.WHITEBOX_TOOLS_EXPECTED_SHA256 is None
        ):
            raise ValueError("Whitebox executable, exact version and checksum are required for phase 4B")
        backend = inspect_whitebox_backend(
            settings.WHITEBOX_TOOLS_EXECUTABLE.expanduser().resolve(),
            settings.WHITEBOX_TOOLS_EXPECTED_VERSION,
            settings.WHITEBOX_TOOLS_EXPECTED_SHA256,
        )
        return {
            **backend,
            "python_frontend_contract": "whitebox==2.3.6",
            "binary_packaged_in_git": False,
            "executed": False,
        }

    def _read_context(
        self,
        dataset: rasterio.io.DatasetReader,
        chip: ChipWindow,
    ) -> tuple[np.ndarray, Window]:
        halo = EXPERIMENT_FILTER_HALO_PIXELS
        window = Window(
            chip.column_offset - halo,
            chip.row_offset - halo,
            chip.width + 2 * halo,
            chip.height + 2 * halo,
        )
        return dataset.read(1, window=window), window

    def _condition(
        self,
        chip: ChipWindow,
        backend: dict[str, Any],
        context: np.ndarray,
        context_transform,
        crs: rasterio.crs.CRS,
        nodata: float | None,
    ) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
        halo = EXPERIMENT_FILTER_HALO_PIXELS
        core = np.s_[halo:-halo, halo:-halo]
        outputs = {"RAW": context[core].astype(np.float32, copy=True)}
        execution: dict[str, Any] = {"RAW": {"elapsed_seconds": 0.0}}
        started = time.perf_counter()
        bilateral = bilateral_smoothing(
            context,
            float(CALIBRATION_BILATERAL_CONFIG["sigma_dist_pixels"]),
            float(CALIBRATION_BILATERAL_CONFIG["sigma_int_m"]),
            nodata,
        )
        outputs["B2"] = bilateral[core]
        execution["B2"] = {"elapsed_seconds": time.perf_counter() - started}

        backend_dir = self.output_dir / "chips" / chip.chip_id / "whitebox_backend"
        context_path = backend_dir / "context_with_halo.tif"
        write_float_raster(
            context_path,
            context,
            valid_mask(context, nodata),
            context_transform,
            crs,
        )
        for configuration in CALIBRATION_FEATURE_PRESERVING_CONFIGS:
            candidate_id = str(configuration["id"])
            output_path = backend_dir / f"{candidate_id}.tif"
            result = run_feature_preserving_smoothing(
                backend,
                context_path,
                output_path,
                configuration,
            )
            with rasterio.open(output_path) as dataset:
                if dataset.shape != context.shape or dataset.crs != crs or dataset.transform != context_transform:
                    raise ValueError(f"Whitebox changed the grid for {candidate_id}")
                filtered = dataset.read(1)
            outputs[candidate_id] = filtered[core].astype(np.float32)
            execution[candidate_id] = result
        return outputs, execution

    def _run_chip(
        self,
        chip: ChipWindow,
        backend: dict[str, Any],
        phase4_manifest: dict[str, Any],
    ) -> tuple[dict[str, Any], dict[str, np.ndarray], Any]:
        with rasterio.open(self.baseline_path) as dataset:
            context, context_window = self._read_context(dataset, chip)
            transform = window_transform(chip.window, dataset.transform)
            context_transform = window_transform(context_window, dataset.transform)
            crs = dataset.crs
            nodata = dataset.nodata
        candidates, execution = self._condition(
            chip,
            backend,
            context,
            context_transform,
            crs,
            nodata,
        )
        raw = candidates["RAW"]
        raw_banding, raw_banding_raster, raw_banding_valid = directed_banding_metrics(raw, nodata)
        reference_threshold = raw_banding["reference_threshold_m"]
        candidate_results: dict[str, Any] = {}
        panels: dict[str, list[tuple[str, np.ndarray, np.ndarray]]] = {
            "hillshade": [],
            "slope": [],
            "difference": [],
            "banding": [],
        }
        visual_maximum = {"slope": 0.0, "difference": 0.0, "banding": 0.0}
        for candidate_id in CALIBRATION_CANDIDATE_ORDER:
            values = candidates[candidate_id]
            metrics, slope, slope_valid = experimental_metrics(raw, values, TARGET_RESOLUTION_M, nodata)
            banding, banding_raster, banding_valid = directed_banding_metrics(
                values,
                nodata,
                reference_threshold,
            )
            shade, shade_valid = hillshade(values, TARGET_RESOLUTION_M, nodata)
            difference = values.astype(np.float64) - raw.astype(np.float64)
            difference_valid = valid_mask(values, nodata) & valid_mask(raw, nodata)
            neighbor, neighbor_valid = local_neighbor_magnitude(values, nodata)
            candidate_dir = self.output_dir / "chips" / chip.chip_id / candidate_id
            artifacts = {
                "dem": str(
                    write_float_raster(candidate_dir / "dem.tif", values, valid_mask(values, nodata), transform, crs)
                ),
                "hillshade": str(
                    write_float_raster(candidate_dir / "hillshade.tif", shade, shade_valid, transform, crs)
                ),
                "slope_horn_degrees": str(
                    write_float_raster(candidate_dir / "slope_horn_degrees.tif", slope, slope_valid, transform, crs)
                ),
                "difference_from_raw": str(
                    write_float_raster(
                        candidate_dir / "difference_from_raw.tif",
                        difference,
                        difference_valid,
                        transform,
                        crs,
                    )
                ),
                "directed_banding_magnitude": str(
                    write_float_raster(
                        candidate_dir / "directed_banding_magnitude.tif",
                        banding_raster,
                        banding_valid,
                        transform,
                        crs,
                    )
                ),
                "neighbor_magnitude": str(
                    write_float_raster(
                        candidate_dir / "neighbor_magnitude.tif",
                        neighbor,
                        neighbor_valid,
                        transform,
                        crs,
                    )
                ),
            }
            limit_verification = None
            if candidate_id.startswith("FP"):
                configured_limit = float(
                    next(
                        configuration["max_diff_m"]
                        for configuration in CALIBRATION_FEATURE_PRESERVING_CONFIGS
                        if configuration["id"] == candidate_id
                    )
                )
                observed_maximum = metrics["elevation"]["absolute_difference_m"]["maximum"]
                if observed_maximum > configured_limit + CALIBRATION_FP_LIMIT_TOLERANCE_M:
                    raise ValueError(f"{candidate_id} violated its configured max_diff")
                limit_verification = {
                    "configured_max_diff_m": configured_limit,
                    "tolerance_m": CALIBRATION_FP_LIMIT_TOLERANCE_M,
                    "observed_maximum_m": observed_maximum,
                    "passed": True,
                }
            reproducibility = self._fp2_reproducibility(chip, candidate_id, values, phase4_manifest)
            candidate_results[candidate_id] = {
                "execution": execution[candidate_id],
                "metrics": metrics,
                "directed_banding": banding,
                "max_diff_verification": limit_verification,
                "phase4_c1_reproducibility": reproducibility,
                "artifacts": artifacts,
                "classification": None,
            }
            panels["hillshade"].append((candidate_id, shade, shade_valid))
            panels["slope"].append((candidate_id, slope, slope_valid))
            panels["difference"].append((candidate_id, difference, difference_valid))
            panels["banding"].append((candidate_id, banding_raster, banding_valid))
            visual_maximum["slope"] = max(visual_maximum["slope"], float(np.percentile(slope[slope_valid], 99)))
            visual_maximum["difference"] = max(
                visual_maximum["difference"],
                float(np.percentile(np.abs(difference[difference_valid]), 99)),
            )
            visual_maximum["banding"] = max(
                visual_maximum["banding"],
                float(np.percentile(banding_raster[banding_valid], 99)),
            )

        comparison_dir = self.output_dir / "chips" / chip.chip_id / "comparisons"
        visualizations = {
            "hillshade": write_comparison_png(comparison_dir / "hillshade.png", panels["hillshade"], 0.0, 255.0),
            "slope_horn_degrees": write_comparison_png(
                comparison_dir / "slope_horn_degrees.png",
                panels["slope"],
                0.0,
                visual_maximum["slope"],
            ),
            "difference_from_raw": write_comparison_png(
                comparison_dir / "difference_from_raw.png",
                panels["difference"],
                -visual_maximum["difference"],
                visual_maximum["difference"],
            ),
            "directed_banding": write_comparison_png(
                comparison_dir / "directed_banding.png",
                panels["banding"],
                0.0,
                visual_maximum["banding"],
            ),
        }
        return (
            {
                "chip": chip.to_dict(),
                "raw_banding": raw_banding,
                "candidates": candidate_results,
                "visualizations": visualizations,
            },
            candidates,
            transform,
        )

    def _fp2_reproducibility(
        self,
        chip: ChipWindow,
        candidate_id: str,
        values: np.ndarray,
        phase4_manifest: dict[str, Any],
    ) -> dict[str, Any] | None:
        if candidate_id != "FP2" or chip.chip_id == "problema_manual":
            return None
        c1_path = Path(phase4_manifest["comparisons"][chip.chip_id]["results"]["C1"]["artifacts"]["dem"])
        with rasterio.open(c1_path) as dataset:
            previous = dataset.read(1)
        difference = np.abs(values.astype(np.float64) - previous.astype(np.float64))
        return {
            "phase4_candidate": "C1",
            "maximum_absolute_difference_m": float(difference.max()),
            "identical_pixel_percentage": float(np.count_nonzero(difference == 0) / difference.size * 100),
            "array_identical": bool(np.array_equal(values, previous)),
        }

    def _write_profiles(
        self,
        candidates: dict[str, np.ndarray],
        transform,
        raw_banding: dict[str, Any],
    ) -> dict[str, Any]:
        raw = candidates["RAW"]
        lines, contract = profile_lines_from_raw(raw, FINAL_NODATA)
        output: dict[str, Any] = {"contract": contract, "raw_banding": raw_banding, "transects": {}}
        candidate_values = {candidate_id: candidates[candidate_id] for candidate_id in CALIBRATION_CANDIDATE_ORDER[1:]}
        for line in lines:
            records = profile_records(line, raw, candidate_values, transform)
            profile_dir = self.output_dir / "chips" / "problema_manual" / "profiles"
            csv_path = write_profile_csv(profile_dir / f"{line.profile_id}.csv", records)
            png = write_profile_png(
                profile_dir / f"{line.profile_id}.png",
                records,
                CALIBRATION_CANDIDATE_ORDER,
            )
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
