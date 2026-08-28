from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import rasterio

from core.pipelines.pendientes.constants import (
    BANDING_REVIEW_CSV_FILENAME,
    BANDING_REVIEW_DIRECTORY_NAME,
    BANDING_REVIEW_MANIFEST_FILENAME,
    BANDING_REVIEW_PRIORITY_COUNT,
    EXPERIMENT_BASELINE_SHA256,
    FINAL_NODATA,
    PIPELINE_NAME,
    PIPELINE_VERSION,
    STATE_VALIDATION_DIRECTORY_NAME,
    STATE_VALIDATION_INVENTORY_FILENAME,
    STATE_VALIDATION_MANIFEST_FILENAME,
    TARGET_RESOLUTION_M,
    TARGET_SRID,
)
from core.pipelines.pendientes.helpers.banding_detector_v2 import detector_v2_metrics
from core.pipelines.pendientes.helpers.banding_review import (
    labeled_metric_distributions,
    percentile_rank,
    read_review_csv,
    select_priority_review,
    write_chip_atlas,
    write_contact_sheet,
    write_review_csv,
)
from core.pipelines.pendientes.helpers.directed_banding import second_difference_fields
from core.pipelines.pendientes.helpers.experimental_artifacts import hillshade
from core.pipelines.pendientes.helpers.slope import experimental_horn_slope
from core.utils.files import read_json, sha256_file, write_json_atomic


class PendientesBandingCalibration:
    """Build a human-review dataset and provisional detector-v2 evidence."""

    def __init__(self) -> None:
        transform_dir = Path("data") / "transform" / PIPELINE_NAME
        self.state_dir = transform_dir / STATE_VALIDATION_DIRECTORY_NAME
        self.state_manifest_path = self.state_dir / STATE_VALIDATION_MANIFEST_FILENAME
        self.state_inventory_path = self.state_dir / STATE_VALIDATION_INVENTORY_FILENAME
        self.output_dir = transform_dir / BANDING_REVIEW_DIRECTORY_NAME
        self.review_csv_path = self.output_dir / BANDING_REVIEW_CSV_FILENAME
        self.manifest_path = self.output_dir / BANDING_REVIEW_MANIFEST_FILENAME
        self.priority_path = self.output_dir / "priority_review.json"

    def execute(self) -> dict[str, Any]:
        started = time.perf_counter()
        state_manifest, inventory = self._validate_sources()
        rows: list[dict[str, Any]] = []
        detailed_metrics: dict[str, Any] = {}
        raw_contracts: dict[str, Any] = {}
        slope_p99_values = []
        magnitude_p99_values = []
        for chip_id, result in sorted(state_manifest["results"].items()):
            raw_path = Path(result["artifacts"]["RAW"])
            raw, nodata = self._read_validated_raw(raw_path, result["chip"])
            metrics = detector_v2_metrics(raw, nodata)
            row = self._review_row(chip_id, result, metrics, raw_path)
            rows.append(row)
            detailed_metrics[chip_id] = metrics
            raw_contracts[chip_id] = {
                "path": str(raw_path),
                "sha256": sha256_file(raw_path),
                "reused_without_filtering": True,
            }
            slope_p99_values.append(float(result["qa"]["raw_summary"]["horn_slope_degrees"]["p99"]))
            _, _, magnitude, valid = second_difference_fields(raw, nodata)
            magnitude_p99_values.append(float(np.percentile(magnitude[valid], 99)))
        self._preserve_human_review(rows)
        self._validate_manual_reference(rows)
        write_review_csv(self.review_csv_path, rows)
        scales = {
            "hillshade": [0.0, 255.0],
            "slope_horn_degrees": [0.0, max(slope_p99_values)],
            "second_difference_magnitude_m": [0.0, max(magnitude_p99_values)],
            "common_across_all_30_chips": True,
            "independent_autoscaling": False,
        }
        atlas_paths = self._write_atlas(rows, raw_contracts, detailed_metrics, scales)
        contact_sheet = write_contact_sheet(self.output_dir / "review_atlas" / "contact_sheet.png", atlas_paths)
        priority = select_priority_review(rows, BANDING_REVIEW_PRIORITY_COUNT)
        write_json_atomic(
            {
                "created_at": datetime.now().astimezone().isoformat(),
                "count": len(priority),
                "selection_is_review_priority_not_classification": True,
                "chips": priority,
            },
            self.priority_path,
        )
        manual_rankings = self._manual_rankings(rows)
        supervised = labeled_metric_distributions(rows, self._metric_fields())
        manifest = {
            "phase": "5B_banding_detector_calibration",
            "pipeline_version": PIPELINE_VERSION,
            "created_at": datetime.now().astimezone().isoformat(),
            "status": "completed_awaiting_human_review",
            "source_phase5a": {
                "manifest_path": str(self.state_manifest_path),
                "manifest_sha256": sha256_file(self.state_manifest_path),
                "inventory_path": str(self.state_inventory_path),
                "inventory_sha256": sha256_file(self.state_inventory_path),
                "decision": state_manifest["decision"]["value"],
                "raw_artifacts_reused": 30,
                "fp3_executed": False,
            },
            "review_dataset": {
                "path": str(self.review_csv_path),
                "sha256": sha256_file(self.review_csv_path),
                "row_count": len(rows),
                "allowed_human_labels": ["banding_presente", "banding_ausente", "dudoso"],
                "prelabeled_rows": 1,
                "unlabeled_rows": len(rows) - 1,
            },
            "manual_positive_regression": {
                "chip_id": "problema_manual",
                "x": 750968.0,
                "y": 2329434.0,
                "human_reference": "banding_presente",
                "source": "manual_known_problem",
                "future_clear_absent_prediction_is_problematic": True,
                "rankings": manual_rankings,
            },
            "detector_v2": {
                "weighted_score": None,
                "classifier_trained": False,
                "new_metrics": [
                    "peak_prominence",
                    "lag_stability",
                    "second_difference_energy_anisotropy",
                    "tangent_run_persistence",
                    "profile_step_repetition",
                ],
                "metrics_by_chip": detailed_metrics,
            },
            "atlas": {
                "directory": str(self.output_dir / "review_atlas"),
                "chip_image_count": len(atlas_paths),
                "chip_images": {
                    path.stem: {"path": str(path), "sha256": sha256_file(path)} for path in atlas_paths
                },
                "contact_sheet": str(contact_sheet),
                "contact_sheet_sha256": sha256_file(contact_sheet),
                "scale_contract": scales,
            },
            "priority_review": {
                "path": str(self.priority_path),
                "sha256": sha256_file(self.priority_path),
                "count": len(priority),
                "chips": priority,
            },
            "supervised_evaluation": supervised,
            "raw_artifacts": raw_contracts,
            "filters_executed": [],
            "statewide_processing": False,
            "institutional_products_generated": [],
            "elapsed_seconds": time.perf_counter() - started,
        }
        write_json_atomic(manifest, self.manifest_path)
        return manifest

    def _validate_sources(self) -> tuple[dict[str, Any], dict[str, Any]]:
        state_manifest = read_json(self.state_manifest_path)
        inventory = read_json(self.state_inventory_path)
        if state_manifest is None or inventory is None:
            raise FileNotFoundError("Phase-5A manifest and inventory are required")
        if state_manifest.get("status") != "completed_reviewed_not_promoted":
            raise ValueError("Phase 5A must be reviewed before detector calibration")
        if state_manifest["baseline"]["sha256"] != EXPERIMENT_BASELINE_SHA256:
            raise ValueError("Phase-5A baseline checksum changed")
        if state_manifest["inventory"]["sha256"] != sha256_file(self.state_inventory_path):
            raise ValueError("Phase-5A inventory checksum changed")
        if len(state_manifest.get("results", {})) != 30 or inventory.get("chip_count") != 30:
            raise ValueError("Detector calibration requires exactly the 30 phase-5A chips")
        return state_manifest, inventory

    def _read_validated_raw(self, path: Path, chip: dict[str, Any]) -> tuple[np.ndarray, float | None]:
        if not path.is_file():
            raise FileNotFoundError(f"Phase-5A RAW chip not found: {path}")
        with rasterio.open(path) as dataset:
            if (
                dataset.crs is None
                or dataset.crs.to_epsg() != TARGET_SRID
                or dataset.res != (TARGET_RESOLUTION_M, TARGET_RESOLUTION_M)
                or dataset.shape != (1024, 1024)
                or dataset.nodata != FINAL_NODATA
                or dataset.dtypes != ("float32",)
                or list(dataset.bounds) != list(chip["bbox"])
            ):
                raise ValueError(f"Phase-5A RAW grid contract changed: {path}")
            return dataset.read(1), dataset.nodata

    def _review_row(
        self,
        chip_id: str,
        result: dict[str, Any],
        metrics: dict[str, Any],
        raw_path: Path,
    ) -> dict[str, Any]:
        chip = result["chip"]
        raw_summary = result["qa"]["raw_summary"]
        current = metrics["current"]
        axis = current["repetition"]["dominant_axis"]
        repetition = current["repetition"][axis]
        profile = metrics["profile_step_repetition"]
        manual = chip_id == "problema_manual"
        return {
            "chip_id": chip_id,
            "center_x": chip["center_x"],
            "center_y": chip["center_y"],
            "bbox": json.dumps(chip["bbox"], separators=(",", ":")),
            "morphology_class": chip["morphology_class"],
            "raw_slope_p50": raw_summary["horn_slope_degrees"]["p50"],
            "raw_ruggedness": raw_summary["absolute_laplacian_m"]["p50"],
            "raw_relief": raw_summary["local_relief_p95_minus_p5_m"],
            "second_difference_density": current["high_second_difference_percentage"],
            "axial_coherence": current["orientation"]["coherence"],
            "continuity": current["tangent_continuity"]["support_percentage"],
            "autocorrelation": repetition["maximum_positive_autocorrelation"],
            "dominant_axis": axis,
            "dominant_lag": repetition["lag_pixels"],
            "peak_prominence": metrics["peak_prominence"]["peak_prominence"],
            "peak_local_baseline": metrics["peak_prominence"]["local_baseline"],
            "lag_stable_fraction": metrics["lag_stability"]["stable_fraction"],
            "lag_valid_subwindow_fraction": (
                metrics["lag_stability"]["valid_subwindows"] / metrics["lag_stability"]["subwindow_count"]
            ),
            "lag_mad_pixels": metrics["lag_stability"]["lag_mad_pixels"],
            "energy_anisotropy": metrics["anisotropy"]["energy_anisotropy"],
            "long_run_count_ge_4": metrics["spatial_persistence"]["long_run_count_ge_4"],
            "long_runs_per_million_cells": metrics["spatial_persistence"]["long_runs_per_million_cells"],
            "long_run_selected_fraction": metrics["spatial_persistence"]["selected_fraction_in_runs_ge_4"],
            "run_length_p90_pixels": metrics["spatial_persistence"]["run_length_pixels"]["p90"],
            "run_length_max_pixels": metrics["spatial_persistence"]["run_length_pixels"]["maximum"],
            "profile_strong_step_count": profile["strong_step_count"],
            "profiles_with_three_or_more_steps": profile["profiles_with_three_or_more_steps"],
            "profile_spacing_median_pixels": profile["spacing_pixels"]["median"],
            "profile_spacing_cv": profile["spacing_pixels"]["coefficient_of_variation"],
            "profile_amplitude_cv": profile["amplitude_coefficient_of_variation"],
            "raw_path": str(raw_path),
            "raw_sha256": sha256_file(raw_path),
            "human_label": "banding_presente" if manual else "",
            "human_confidence": "high" if manual else "",
            "human_notes": "Known visually observed banding/escalonamiento" if manual else "",
            "human_source": "manual_known_problem" if manual else "",
        }

    def _atlas_arrays(self, raw: np.ndarray, nodata: float | None, threshold: float) -> dict[str, np.ndarray]:
        shade, shade_valid = hillshade(raw, TARGET_RESOLUTION_M, nodata)
        slope, _, slope_valid = experimental_horn_slope(raw, TARGET_RESOLUTION_M, nodata)
        _, _, magnitude, second_valid = second_difference_fields(raw, nodata)
        directed = np.where(second_valid & (magnitude >= threshold), magnitude, np.nan)
        return {
            "hillshade": np.where(shade_valid, shade, np.nan),
            "slope": np.where(slope_valid, slope, np.nan),
            "second_difference": np.where(second_valid, magnitude, np.nan),
            "directed_signature": directed,
        }

    def _write_atlas(
        self,
        rows: list[dict[str, Any]],
        raw_contracts: dict[str, Any],
        detailed_metrics: dict[str, Any],
        scales: dict[str, Any],
    ) -> list[Path]:
        output = []
        for row in rows:
            chip_id = row["chip_id"]
            path = Path(raw_contracts[chip_id]["path"])
            with rasterio.open(path) as dataset:
                raw = dataset.read(1)
                nodata = dataset.nodata
            arrays = self._atlas_arrays(raw, nodata, detailed_metrics[chip_id]["reference_threshold_m"])
            atlas_path = write_chip_atlas(
                self.output_dir / "review_atlas" / f"{chip_id}.png",
                arrays,
                row,
                scales["slope_horn_degrees"][1],
                scales["second_difference_magnitude_m"][1],
            )
            output.append(atlas_path)
        return output

    def _metric_fields(self) -> tuple[str, ...]:
        return (
            "second_difference_density",
            "axial_coherence",
            "continuity",
            "autocorrelation",
            "peak_prominence",
            "peak_local_baseline",
            "lag_stable_fraction",
            "lag_valid_subwindow_fraction",
            "lag_mad_pixels",
            "energy_anisotropy",
            "long_run_count_ge_4",
            "long_runs_per_million_cells",
            "long_run_selected_fraction",
            "run_length_p90_pixels",
            "run_length_max_pixels",
            "profile_strong_step_count",
            "profiles_with_three_or_more_steps",
            "profile_spacing_median_pixels",
            "profile_spacing_cv",
            "profile_amplitude_cv",
        )

    def _manual_rankings(self, rows: list[dict[str, Any]]) -> dict[str, Any]:
        manual = next(row for row in rows if row["chip_id"] == "problema_manual")
        rankings = {}
        for metric in self._metric_fields():
            available = [float(row[metric]) for row in rows if row[metric] not in (None, "")]
            if manual[metric] not in (None, ""):
                rankings[metric] = percentile_rank(available, float(manual[metric]))
        rankings["dominant_axis"] = manual["dominant_axis"]
        rankings["dominant_lag_pixels"] = manual["dominant_lag"]
        return rankings

    def _validate_manual_reference(self, rows: list[dict[str, Any]]) -> None:
        manual = [row for row in rows if row["chip_id"] == "problema_manual"]
        if len(manual) != 1:
            raise ValueError("Exactly one problema_manual regression reference is required")
        if (
            manual[0]["human_label"] != "banding_presente"
            or manual[0]["human_source"] != "manual_known_problem"
            or float(manual[0]["center_x"]) != 750968.0
            or float(manual[0]["center_y"]) != 2329434.0
        ):
            raise ValueError("Manual positive banding regression contract changed")

    def _preserve_human_review(self, rows: list[dict[str, Any]]) -> None:
        if not self.review_csv_path.is_file():
            return
        previous = {row["chip_id"]: row for row in read_review_csv(self.review_csv_path)}
        for row in rows:
            if row["chip_id"] == "problema_manual" or row["chip_id"] not in previous:
                continue
            prior = previous[row["chip_id"]]
            for field in ("human_label", "human_confidence", "human_notes", "human_source"):
                row[field] = prior.get(field, "")
