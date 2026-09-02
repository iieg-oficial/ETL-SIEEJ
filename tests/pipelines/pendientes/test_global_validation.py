import json

import numpy as np
import pytest

from core.pipelines.pendientes.helpers.methodology.global_validation_qa import (
    aggregate_candidate_metrics,
    candidate_outliers,
    comparative_candidate_qa,
    pareto_comparison,
    profile_attenuation_metrics,
)
from core.pipelines.pendientes.helpers.methodology.global_validation import PendientesGlobalConditioningValidation


def _surface() -> np.ndarray:
    y, x = np.mgrid[:32, :32]
    return (1000 + x * 2 + y + ((x % 4) == 0) * 0.4).astype(np.float32)


def test_candidate_qa_reports_limits_slope_morphology_and_second_difference_ratios():
    raw = _surface()
    candidate = raw + np.where(np.indices(raw.shape)[1] % 2, 0.2, -0.2).astype(np.float32)
    qa = comparative_candidate_qa(raw, candidate, 15.0, -9999.0)
    assert qa["elevation"]["absolute_difference_m"]["maximum"] == pytest.approx(0.2, abs=1e-4)
    assert qa["elevation"]["threshold_percentages"]["abs_change_gt_0.10_m"] == 100.0
    assert qa["slope_horn_degrees"]["exploratory_not_productive"] is True
    assert set(qa["morphology"]["strong_gradient"]["ratio_candidate_to_raw"]) == {"p05", "median", "p95"}
    assert set(qa["second_difference_magnitude_m"]["candidate_to_raw_ratio"]) == {
        "mean",
        "p50",
        "p90",
        "p95",
        "p99",
    }


def test_profile_metrics_use_identical_samples_and_preserve_trend_contract():
    raw = np.array([0, 0, 1, 1, 2, 2, 4, 4, 5, 5], dtype=np.float32)
    candidate = np.array([0.1, 0.2, 0.8, 1.2, 1.8, 2.2, 3.8, 4.2, 4.8, 5.1], dtype=np.float32)
    metrics = profile_attenuation_metrics(raw, candidate)
    assert metrics["raw_strong_step_count"] > 0
    assert 0 <= metrics["strong_step_retained_above_half_percentage"] <= 100
    assert metrics["endpoint_trend_error_m"] == pytest.approx(0.0, abs=1e-6)
    with pytest.raises(ValueError, match="share shape"):
        profile_attenuation_metrics(raw, candidate[:-1])


def test_aggregate_is_stratified_and_outliers_keep_chip_identity():
    raw = _surface()
    candidates = {
        "FP1": raw + 0.1,
        "FP2": raw + 0.2,
        "FP3": raw + 0.25,
    }
    results = {}
    for index, morphology in enumerate(("plano", "montana", "plano"), start=1):
        results[f"chip_{index}"] = {
            "chip": {"morphology_class": morphology},
            "candidates": {
                candidate_id: {"qa": comparative_candidate_qa(raw, values + index * 0.01, 15, -9999)}
                for candidate_id, values in candidates.items()
            },
        }
    aggregate = aggregate_candidate_metrics(results, "FP2", "plano")
    outliers = candidate_outliers(results, "FP2")
    assert aggregate["chip_count"] == 2
    assert outliers["worst_mae_z"]["chip_id"] == "chip_3"


def test_pareto_marks_only_strictly_dominated_candidates():
    def metrics(value: float) -> dict:
        summary = {"median": value}
        return {
            "mae_z_m": summary,
            "slope_mae_degrees": summary,
            "normal_p95_degrees": summary,
            "strong_gradient_ratio_median": {"median": 1.0 + value},
            "second_difference_p50_ratio": summary,
            "second_difference_p95_ratio": summary,
        }

    aggregate = {"FP1": metrics(0.2), "FP2": metrics(0.1), "FP3": metrics(0.3)}
    profiles = {
        candidate_id: {"strong_step_amplitude_candidate_to_raw_median": value}
        for candidate_id, value in (("FP1", 0.2), ("FP2", 0.1), ("FP3", 0.3))
    }
    pareto = pareto_comparison(aggregate, profiles)
    assert pareto["non_dominated"] == ["FP2"]
    assert pareto["dominated_by"]["FP3"] == ["FP1", "FP2"]
    assert pareto["weighted_score"] is None


def test_frozen_candidate_contract_and_representative_selection():
    stage = PendientesGlobalConditioningValidation()
    configurations = stage._candidate_configurations()
    assert tuple(configurations) == ("FP1", "FP2", "FP3")
    assert configurations["FP1"]["max_diff_m"] == 0.25
    assert configurations["FP2"]["norm_diff_degrees"] == 5.0
    assert configurations["FP3"]["norm_diff_degrees"] == 7.5

    morphologies = ["plano"] * 8 + ["valle"] * 4 + ["lomerio"] * 7 + ["montana"] * 8 + ["transicion_valle_sierra"] * 3
    chips = [
        {"chip_id": f"chip_{index:02d}", "morphology_class": morphology}
        for index, morphology in enumerate(morphologies)
    ]
    chips[0]["chip_id"] = "problema_manual"
    selected = stage._representative_chips({"chips": chips})
    assert len(selected) == 10
    assert selected[0] == "problema_manual"
    assert len(set(selected)) == 10


def test_decision_contract_requires_tile_validation_without_assuming_fp2_halo(tmp_path):
    stage = PendientesGlobalConditioningValidation()
    stage.manifest_path = tmp_path / "manifest.json"
    stage.manifest_path.write_text(
        json.dumps(
            {
                "status": "completed_pending_comparative_review",
                "candidates": stage._candidate_configurations(),
            }
        ),
        encoding="utf-8",
    )
    manifest = stage.record_decision("FP2_recomendado_para_procesamiento_estatal", {"pareto": "reviewed"})
    contract = manifest["next_phase_contract"]
    assert contract["selected_candidate_id"] == "FP2"
    assert contract["required_tile_validation"]["required"] is True
    assert contract["required_tile_validation"]["halo_pixels"] is None
    assert contract["required_tile_validation"]["phase5a_fp3_halo_24_must_not_be_assumed"] is True
