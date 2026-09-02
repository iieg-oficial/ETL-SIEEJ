from __future__ import annotations

import csv
import json

import numpy as np
import rasterio
from affine import Affine

from core.pipelines.pendientes.constants import (
    CALIBRATION_CANDIDATE_ORDER,
    CALIBRATION_FEATURE_PRESERVING_CONFIGS,
)
from core.pipelines.pendientes.helpers.methodology.calibration_profiles import (
    profile_lines_from_raw,
    profile_records,
    write_profile_csv,
    write_profile_png,
)
from core.pipelines.pendientes.helpers.methodology.directed_banding import directed_banding_metrics
from core.pipelines.pendientes.helpers.methodology.experimental_filters import gaussian_smoothing
from core.pipelines.pendientes.helpers.methodology.calibration import PendientesCalibration


def _periodic_steps(size: int = 128, spacing: int = 8) -> np.ndarray:
    _, columns = np.indices((size, size))
    return np.floor(columns / spacing).astype(np.float32)


def test_directed_banding_detects_oriented_repetitive_steps():
    elevation = _periodic_steps()

    metrics, magnitude, valid = directed_banding_metrics(elevation, nodata=-9999)

    assert valid.any()
    assert np.nanmax(magnitude) == 1
    assert metrics["orientation"]["coherence"] > 0.99
    assert metrics["orientation"]["dominant_normal_degrees"] in (0.0, 180.0)
    assert metrics["tangent_continuity"]["support_percentage"] > 99
    assert metrics["repetition"]["dominant_axis"] == "x"
    assert metrics["repetition"]["x"]["lag_pixels"] % 8 == 0
    assert metrics["repetition"]["x"]["maximum_positive_autocorrelation"] > 0.7


def test_directed_banding_uses_raw_threshold_for_candidate_comparison():
    raw = _periodic_steps()
    smoothed = gaussian_smoothing(raw, sigma_pixels=1.0)
    raw_metrics, _, _ = directed_banding_metrics(raw, nodata=None)

    candidate_metrics, _, _ = directed_banding_metrics(
        smoothed,
        nodata=None,
        reference_threshold_m=raw_metrics["reference_threshold_m"],
    )

    assert candidate_metrics["reference_threshold_m"] == raw_metrics["reference_threshold_m"]
    assert candidate_metrics["high_second_difference_percentage"] < raw_metrics["high_second_difference_percentage"]


def test_flat_surface_does_not_create_false_linear_banding():
    metrics, _, _ = directed_banding_metrics(np.full((32, 32), 100.0), nodata=None)

    assert metrics["high_second_difference_percentage"] == 0
    assert metrics["orientation"]["coherence"] == 0
    assert metrics["repetition"]["dominant_axis"] is None


def test_profiles_are_parallel_reproducible_and_export_raw_candidate_delta(tmp_path):
    raw = _periodic_steps()
    candidates = {
        "B2": raw + 0.1,
        "FP1": raw + 0.2,
        "FP2": raw + 0.3,
        "FP3": raw + 0.4,
        "FP4": raw + 0.5,
    }
    transform = Affine(15, 0, 500_000, 0, -15, 2_300_000)

    first, first_contract = profile_lines_from_raw(raw, nodata=None, offsets=(-16, 0, 16))
    second, second_contract = profile_lines_from_raw(raw, nodata=None, offsets=(-16, 0, 16))

    assert first == second
    assert first_contract == second_contract
    assert len(first) == 3
    records = profile_records(first[1], raw, candidates, transform)
    assert np.allclose([record["delta_B2_m"] for record in records], 0.1)
    assert all(record["distance_m"] <= records[index + 1]["distance_m"] for index, record in enumerate(records[:-1]))

    csv_path = write_profile_csv(tmp_path / "profile.csv", records)
    with csv_path.open(encoding="utf-8") as source:
        exported = list(csv.DictReader(source))
    assert len(exported) == len(records)
    assert {"distance_m", "elevation_RAW_m", "elevation_FP4_m", "delta_FP4_m"} <= set(exported[0])

    plot = write_profile_png(tmp_path / "profile.png", records, CALIBRATION_CANDIDATE_ORDER)
    with rasterio.open(plot["path"]) as dataset:
        assert dataset.driver == "PNG"
        assert dataset.count == 3
    assert plot["independent_autoscaling"] is False


def test_feature_preserving_calibration_never_exceeds_half_metre_contract():
    assert [configuration["id"] for configuration in CALIBRATION_FEATURE_PRESERVING_CONFIGS] == [
        "FP1",
        "FP2",
        "FP3",
        "FP4",
    ]
    assert max(float(configuration["max_diff_m"]) for configuration in CALIBRATION_FEATURE_PRESERVING_CONFIGS) == 0.5


def test_record_review_requires_complete_allowed_classifications_and_never_promotes(tmp_path):
    stage = PendientesCalibration()
    stage.manifest_path = tmp_path / "manifest.json"
    candidates = {candidate_id: {"classification": None} for candidate_id in CALIBRATION_CANDIDATE_ORDER}
    manifest = {
        "status": "completed_pending_review",
        "results": {
            chip_id: {"candidates": json.loads(json.dumps(candidates))}
            for chip_id in ("plano", "lomerio", "montana", "problema_manual")
        },
    }
    stage.manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    classifications = {
        "B2": "descartar",
        "FP1": "mantener",
        "FP2": "mantener",
        "FP3": "recomendado_para_validacion_estatal",
        "FP4": "descartar",
    }

    reviewed = stage.record_review(classifications, {"review_scope": "synthetic test"})

    assert reviewed["status"] == "completed_reviewed_not_promoted"
    assert reviewed["decision"]["classifications"] == classifications
    assert reviewed["decision"]["winner_selected"] is False
    assert reviewed["decision"]["recommendation_is_not_promotion"] is True
    assert all(
        chip["candidates"]["FP3"]["classification"] == "recomendado_para_validacion_estatal"
        for chip in reviewed["results"].values()
    )
