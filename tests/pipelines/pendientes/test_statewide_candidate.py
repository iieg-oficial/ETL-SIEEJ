from __future__ import annotations

import json
import shutil
from pathlib import Path

import numpy as np
import rasterio
from affine import Affine
from rasterio.windows import Window

from core.pipelines.pendientes.constants import (
    EXPERIMENT_BASELINE_SHA256,
    STATEWIDE_CANDIDATE_DECISIONS,
    STATEWIDE_CANDIDATE_FP2_CONFIG,
    STATEWIDE_CANDIDATE_SHA256,
)
from core.pipelines.pendientes.helpers.statewide_candidate_qa import (
    validate_contextual_reference_manifest,
)
from core.pipelines.pendientes.helpers.statewide_conditioning import (
    condition_raster_tiled,
    mask_preserving_core,
    output_raster_profile,
    seam_qa,
    streaming_global_qa,
)
from core.pipelines.pendientes.stages.statewide_candidate import PendientesStatewideCandidate


def _write_raster(path: Path, values: np.ndarray) -> Path:
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        height=values.shape[0],
        width=values.shape[1],
        count=1,
        dtype="float32",
        crs="EPSG:6368",
        transform=Affine(15, 0, 400000, 0, -15, 2500000),
        nodata=-9999.0,
    ) as dataset:
        dataset.write(values.astype(np.float32), 1)
    return path


def test_fp2_and_decision_contracts_are_frozen():
    assert STATEWIDE_CANDIDATE_FP2_CONFIG == {
        "id": "FP2",
        "filter": 11,
        "norm_diff_degrees": 5.0,
        "num_iter": 1,
        "max_diff_m": 0.5,
        "zfactor": 1.0,
    }
    assert EXPERIMENT_BASELINE_SHA256 == "1461f63298509f045476b9e6e0597ee8eba3138af82e033eb232ddef3bf50fcd"
    assert STATEWIDE_CANDIDATE_DECISIONS == (
        "tile_validation_failed",
        "statewide_processing_failed",
        "statewide_candidate_generated_not_promoted",
    )


def test_mask_preserving_core_does_not_create_valid_pixels_from_nodata():
    source = np.arange(36, dtype=np.float32).reshape(6, 6)
    source[2, 2] = -9999
    filtered = source.copy()
    filtered[2, 2] = 123
    filtered[3, 3] = -9999
    core = Window(1, 1, 4, 4)
    output, counts = mask_preserving_core(source, filtered, core, Window(0, 0, 6, 6), -9999)
    assert output[1, 1] == -9999
    assert output[2, 2] == -9999
    assert counts["mask_mismatch_pixels_before_enforcement"] == 2
    assert counts["valid_pixels_conditioned"] == counts["valid_pixels_baseline"] - 1


def test_tiled_assembly_writes_each_core_once_and_preserves_grid(tmp_path, monkeypatch):
    source_values = np.arange(143, dtype=np.float32).reshape(11, 13)
    source_values[0, 0] = -9999
    source_path = _write_raster(tmp_path / "source.tif", source_values)
    output_path = tmp_path / "candidate.tif"

    def copy_backend(backend, input_path, output_path, configuration):
        shutil.copyfile(input_path, output_path)
        return {"elapsed_seconds": 0.0}

    monkeypatch.setattr(
        "core.pipelines.pendientes.helpers.statewide_conditioning.run_feature_preserving_smoothing",
        copy_backend,
    )
    result = condition_raster_tiled(source_path, output_path, {}, STATEWIDE_CANDIDATE_FP2_CONFIG, 5, 2)
    with rasterio.open(source_path) as source, rasterio.open(output_path) as candidate:
        assert np.array_equal(source.read(1), candidate.read(1))
        assert source.transform == candidate.transform
        assert source.crs == candidate.crs
        assert output_raster_profile(source)["BIGTIFF"] == "IF_SAFER"
    assert result["tile_count"] == 9
    assert result["mask"]["mask_mismatch_pixels"] == 0


def test_streaming_global_qa_checks_max_diff_grid_and_distribution(tmp_path):
    raw = np.arange(100, dtype=np.float32).reshape(10, 10)
    candidate = raw + 0.25
    source_path = _write_raster(tmp_path / "raw.tif", raw)
    candidate_path = _write_raster(tmp_path / "conditioned.tif", candidate)
    qa = streaming_global_qa(source_path, candidate_path, histogram_bins=1000)
    assert qa["bias_m"] == 0.25
    assert qa["mae_m"] == 0.25
    assert qa["rmse_m"] == 0.25
    assert qa["absolute_difference_m"]["maximum"] == 0.25
    assert qa["threshold_percentages"]["abs_change_gt_0.10_m"] == 100.0
    assert qa["elevation_distribution_m"]["conditioned"]["mean"] == 49.75


def test_seam_qa_visits_every_real_vertical_and_horizontal_boundary(tmp_path):
    raw = np.zeros((12, 14), dtype=np.float32)
    candidate = raw.copy()
    candidate[:, 7:] = 0.2
    source_path = _write_raster(tmp_path / "raw.tif", raw)
    candidate_path = _write_raster(tmp_path / "conditioned.tif", candidate)
    qa = seam_qa(source_path, candidate_path, tile_size=7)
    assert qa["seam_count"] == 2
    vertical = next(record for record in qa["records"] if record["orientation"] == "vertical")
    assert vertical["max_abs_difference_across_expected_continuity"] > 0
    assert vertical["gradient_discontinuity"]["maximum"] > 0


def test_contextual_equivalence_validator_is_the_exact_hard_gate(tmp_path):
    path = tmp_path / "contextual.json"
    result = {
        "array_identical": True,
        "max_abs_difference": 0.0,
        "n_pixels_different": 0,
        "mask_mismatch_pixels": 0,
    }
    path.write_text(
        json.dumps(
            {
                "candidate_id": "FP2",
                "halo_pixels": 24,
                "production_tile_size_pixels": 2048,
                "chip_count": 2,
                "exact_chip_count": 2,
                "all_chips_exact": True,
                "seam_crossing_chip_count": 1,
                "exact_seam_crossing_chip_count": 1,
                "all_seam_crossing_chips_exact": True,
                "results": {"a": result, "b": result},
            }
        ),
        encoding="utf-8",
    )
    validation = validate_contextual_reference_manifest(path, 2, 24, 2048)
    assert validation["checks"]["all_chips_exact"] is True
    modified = json.loads(path.read_text(encoding="utf-8"))
    modified["exact_chip_count"] = 1
    path.write_text(json.dumps(modified), encoding="utf-8")
    with np.testing.assert_raises_regex(ValueError, "Contextual reference validation failed"):
        validate_contextual_reference_manifest(path, 2, 24, 2048)


def test_finalize_existing_never_invokes_statewide_conditioning(tmp_path, monkeypatch):
    stage = PendientesStatewideCandidate()
    stage.output_path = tmp_path / "candidate.tif"
    stage.output_path.write_bytes(b"existing")
    monkeypatch.setattr(
        "core.pipelines.pendientes.stages.statewide_candidate.sha256_file",
        lambda path: STATEWIDE_CANDIDATE_SHA256,
    )
    monkeypatch.setattr(stage, "_validate_inputs", lambda: ({}, {}, {"selected_halo_pixels": 24}))
    monkeypatch.setattr(stage, "_recorded_backend", lambda phase5d: {})
    monkeypatch.setattr(stage, "_finalize_candidate", lambda *args: {"status": "finalized"})
    called = False

    def forbidden(*args, **kwargs):
        nonlocal called
        called = True
        raise AssertionError("statewide conditioning must not run")

    monkeypatch.setattr(
        "core.pipelines.pendientes.stages.statewide_candidate.condition_raster_tiled",
        forbidden,
    )
    assert stage.finalize_existing()["status"] == "finalized"
    assert called is False


def test_finalize_existing_rejects_wrong_candidate_checksum(tmp_path, monkeypatch):
    stage = PendientesStatewideCandidate()
    stage.output_path = tmp_path / "candidate.tif"
    stage.output_path.write_bytes(b"wrong")
    monkeypatch.setattr(
        "core.pipelines.pendientes.stages.statewide_candidate.sha256_file",
        lambda path: "0" * 64,
    )
    with np.testing.assert_raises_regex(ValueError, "checksum mismatch"):
        stage.finalize_existing()


def test_isolated_phase5d_complete_equality_is_not_a_quality_gate():
    isolated = {
        "all_complete_chips_identical": False,
        "all_interiors_excluding_24px_identical": True,
        "hard_gate": False,
    }
    contextual = {"all_chips_exact": True}
    assert isolated["hard_gate"] is False
    assert isolated["all_interiors_excluding_24px_identical"] is True
    assert contextual["all_chips_exact"] is True


def test_final_manifest_records_external_qa_and_not_promoted_status(tmp_path, monkeypatch):
    stage = PendientesStatewideCandidate()
    stage.output_path = tmp_path / "candidate.tif"
    stage.output_path.write_bytes(b"candidate")
    stage.manifest_path = tmp_path / "manifest.json"
    stage.halo_manifest_path = tmp_path / "halo.json"
    stage.contextual_manifest_path = tmp_path / "contextual.json"
    stage.seam_manifest_path = tmp_path / "seam.json"
    monkeypatch.setattr(
        "core.pipelines.pendientes.stages.statewide_candidate.sha256_file",
        lambda path: STATEWIDE_CANDIDATE_SHA256,
    )
    monkeypatch.setattr(
        stage,
        "_raster_contract",
        lambda: (
            {"width": 30533, "height": 29255},
            {"passed": True},
        ),
    )
    global_qa = {
        "bias_m": 0.0,
        "mae_m": 0.1,
        "rmse_m": 0.2,
        "absolute_difference_m": {"p50": 0.1, "maximum": 0.5},
        "threshold_percentages": {
            "abs_change_gt_0.10_m": 50.0,
            "abs_change_gt_0.25_m": 20.0,
            "abs_change_gt_0.50_m": 0.0,
        },
        "elevation_distribution_m": {},
        "percentile_method": {},
        "valid_pixels": {"baseline": 10, "candidate": 10, "mask_mismatch": 0},
    }
    monkeypatch.setattr(
        "core.pipelines.pendientes.stages.statewide_candidate.streaming_global_qa",
        lambda *args: global_qa,
    )
    contextual = {
        "chip_count": 30,
        "exact_chip_count": 30,
        "all_chips_exact": True,
        "seam_crossing_chip_count": 1,
        "exact_seam_crossing_chip_count": 1,
        "all_seam_crossing_chips_exact": True,
        "results": {"a": {"max_abs_difference": 0.0}},
    }
    monkeypatch.setattr(
        "core.pipelines.pendientes.stages.statewide_candidate.validate_contextual_reference_manifest",
        lambda *args: {"path": "contextual.json", "sha256": "c" * 64, "manifest": contextual},
    )
    monkeypatch.setattr(
        "core.pipelines.pendientes.stages.statewide_candidate.validate_seam_manifest",
        lambda *args: {
            "path": "seam.json",
            "sha256": "s" * 64,
            "manifest": {"seam_count": 28, "aggregate": {}},
        },
    )
    monkeypatch.setattr(
        stage,
        "_phase5d_isolated_reference_evidence",
        lambda *args: {"hard_gate": False, "all_interiors_excluding_24px_identical": True},
    )
    manifest = stage._finalize_candidate({}, {}, {"selected_halo_pixels": 24}, {}, None)
    assert manifest["status"] == "statewide_candidate_generated_not_promoted"
    assert manifest["contextual_equivalence"]["artifact"]["sha256"] == "c" * 64
    assert manifest["seam_QA"]["artifact"]["sha256"] == "s" * 64
    assert manifest["phase5d_isolated_reference_evidence"]["hard_gate"] is False
