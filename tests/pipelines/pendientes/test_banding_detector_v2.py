from __future__ import annotations

import csv

import numpy as np
import pytest

from core.pipelines.pendientes.helpers.banding_detector_v2 import detector_v2_metrics
from core.pipelines.pendientes.helpers.banding_review import (
    evaluate_candidate_rule,
    labeled_metric_distributions,
    write_chip_atlas,
    write_review_csv,
)
from core.pipelines.pendientes.stages.banding_calibration import PendientesBandingCalibration
from core.utils.files import sha256_file


def _surfaces(size: int = 128) -> dict[str, np.ndarray]:
    rows, columns = np.indices((size, size))
    random = np.random.default_rng(20260828)
    return {
        "flat": np.zeros((size, size), dtype=np.float32),
        "periodic": np.floor(columns / 8).astype(np.float32),
        "single_crest": (20 * np.exp(-((columns - size / 2) / 4) ** 2)).astype(np.float32),
        "isotropic_noise": random.normal(size=(size, size)).astype(np.float32),
        "oriented_periodic": np.floor((rows + columns) / 12).astype(np.float32),
        "orientation_change": np.where(
            rows < size // 2,
            np.floor(columns / 8),
            np.floor(rows / 8),
        ).astype(np.float32),
    }


def test_flat_surface_has_no_false_periodicity_or_profiles():
    metrics = detector_v2_metrics(_surfaces()["flat"], nodata=None)

    assert metrics["current"]["high_second_difference_percentage"] == 0
    assert metrics["peak_prominence"]["peak_prominence"] == 0
    assert metrics["lag_stability"]["valid_subwindows"] == 0
    assert metrics["spatial_persistence"]["long_run_count_ge_4"] == 0
    assert metrics["profile_step_repetition"]["strong_step_count"] == 0


def test_periodic_bands_have_prominent_stable_lag_and_repeated_persistent_steps():
    metrics = detector_v2_metrics(_surfaces()["periodic"], nodata=None)

    assert metrics["peak_prominence"]["peak_lag_pixels"] == 8
    assert metrics["peak_prominence"]["peak_prominence"] > 1
    assert metrics["lag_stability"]["stable_fraction"] >= 0.7
    assert metrics["anisotropy"]["energy_anisotropy"] > 0.99
    assert metrics["spatial_persistence"]["long_run_count_ge_4"] > 20
    assert metrics["profile_step_repetition"]["strong_step_count"] > 80


def test_single_crest_has_far_fewer_repetitions_than_periodic_bands():
    surfaces = _surfaces()
    periodic = detector_v2_metrics(surfaces["periodic"], nodata=None)
    crest = detector_v2_metrics(surfaces["single_crest"], nodata=None)

    assert crest["spatial_persistence"]["long_run_count_ge_4"] < periodic["spatial_persistence"]["long_run_count_ge_4"]
    assert crest["profile_step_repetition"]["strong_step_count"] < periodic["profile_step_repetition"]["strong_step_count"] / 2
    assert crest["peak_prominence"]["peak_prominence"] < periodic["peak_prominence"]["peak_prominence"]


def test_isotropic_noise_has_low_anisotropy_and_unstable_lag():
    metrics = detector_v2_metrics(_surfaces()["isotropic_noise"], nodata=None)

    assert metrics["anisotropy"]["energy_anisotropy"] < 0.1
    assert metrics["lag_stability"]["stable_fraction"] < 0.25
    assert metrics["spatial_persistence"]["selected_fraction_in_runs_ge_4"] < 0.05


def test_oriented_periodicity_is_anisotropic_and_orientation_change_is_less_stable():
    surfaces = _surfaces()
    oriented = detector_v2_metrics(surfaces["oriented_periodic"], nodata=None)
    changed = detector_v2_metrics(surfaces["orientation_change"], nodata=None)

    assert oriented["anisotropy"]["energy_anisotropy"] > 0.99
    assert oriented["spatial_persistence"]["selected_fraction_in_runs_ge_4"] > 0.95
    assert changed["current"]["orientation"]["coherence"] < 0.1
    assert changed["lag_stability"]["stable_fraction"] < oriented["lag_stability"]["stable_fraction"]


def test_review_csv_and_atlas_are_reproducible_and_manual_reference_is_not_inferred(tmp_path):
    rows = [
        {
            "chip_id": "problema_manual",
            "human_label": "banding_presente",
            "human_confidence": "high",
            "human_notes": "known",
        },
        {"chip_id": "control", "human_label": "", "human_confidence": "", "human_notes": ""},
    ]
    first_csv = write_review_csv(tmp_path / "first.csv", rows)
    second_csv = write_review_csv(tmp_path / "second.csv", rows)
    with first_csv.open(encoding="utf-8") as source:
        exported = list(csv.DictReader(source))
    arrays = {
        "hillshade": np.ones((16, 16), dtype=np.float32) * 128,
        "slope": np.ones((16, 16), dtype=np.float32),
        "second_difference": np.ones((16, 16), dtype=np.float32) * 0.5,
        "directed_signature": np.eye(16, dtype=np.float32),
    }
    metadata = {
        "chip_id": "problema_manual",
        "center_x": 750968.0,
        "center_y": 2329434.0,
        "morphology_class": "plano",
        "autocorrelation": 0.7,
        "axial_coherence": 0.6,
        "continuity": 50.0,
        "dominant_axis": "y",
        "dominant_lag": 4,
    }
    first_atlas = write_chip_atlas(tmp_path / "first.png", arrays, metadata, 20.0, 2.0)
    second_atlas = write_chip_atlas(tmp_path / "second.png", arrays, metadata, 20.0, 2.0)

    assert sha256_file(first_csv) == sha256_file(second_csv)
    assert sha256_file(first_atlas) == sha256_file(second_atlas)
    assert exported[0]["human_label"] == "banding_presente"
    assert exported[1]["human_label"] == ""


def test_supervised_evaluation_waits_for_both_human_classes_then_reports_errors():
    incomplete = [{"chip_id": "positive", "human_label": "banding_presente", "metric": 0.8}]
    complete = [
        *incomplete,
        {"chip_id": "negative", "human_label": "banding_ausente", "metric": 0.2},
        {"chip_id": "false_positive", "human_label": "banding_ausente", "metric": 0.9},
    ]

    assert labeled_metric_distributions(incomplete, ("metric",))["status"] == (
        "not_executed_insufficient_human_labels"
    )
    evaluated = evaluate_candidate_rule(complete, "metric", 0.5, lambda value, threshold: value >= threshold)

    assert evaluated["status"] == "evaluated"
    assert evaluated["confusion_matrix"]["true_positive"] == 1
    assert evaluated["confusion_matrix"]["false_positive"] == 1
    assert evaluated["false_positive_chip_ids"] == ["false_positive"]


def test_manual_problem_remains_a_positive_detector_regression_reference():
    stage = PendientesBandingCalibration()
    valid = [
        {
            "chip_id": "problema_manual",
            "center_x": 750968.0,
            "center_y": 2329434.0,
            "human_label": "banding_presente",
            "human_source": "manual_known_problem",
        }
    ]

    stage._validate_manual_reference(valid)
    valid[0]["human_label"] = "banding_ausente"

    with pytest.raises(ValueError, match="regression contract"):
        stage._validate_manual_reference(valid)
