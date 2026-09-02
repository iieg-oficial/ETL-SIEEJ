from __future__ import annotations

import json

import numpy as np

from core.pipelines.pendientes.helpers.methodology.state_validation_qa import (
    aggregate_state_validation,
    assign_full_resolution_banding_classes,
)
from core.pipelines.pendientes.helpers.methodology.state_validation_sampling import (
    classify_candidate_pool,
    select_spatially_stratified,
)
from core.pipelines.pendientes.helpers.tiled_conditioning import (
    array_window,
    comparison_metrics,
    core_tile_windows,
    expanded_window,
    seam_metrics,
)
from core.pipelines.pendientes.helpers.methodology.state_validation import PendientesStateValidation


def _sampling_candidate(index: int, x: float, y: float) -> dict:
    return {
        "row_offset": index * 10,
        "column_offset": index * 20,
        "width": 1024,
        "height": 1024,
        "center_x": x,
        "center_y": y,
        "bbox": (x - 7680, y - 7680, x + 7680, y + 7680),
        "slope_median_degrees": float(index % 7),
        "roughness_median_abs_laplacian_m": float(index % 5),
        "valid_percentage": 100.0,
        "preliminary_elevation_m": {"minimum": 100.0, "median": 100.0 + index, "maximum": 200.0},
        "preliminary_local_relief_m": float(10 + index % 9),
        "preliminary_raw_banding": {
            "density_percentage": 10.0,
            "reference_threshold_m": 1.0,
            "axial_coherence": 0.5,
            "continuity_percentage": 50.0,
            "dominant_autocorrelation": 0.3 + index / 100,
            "dominant_axis": "x",
            "dominant_lag_pixels": 4,
        },
    }


def test_spatial_selection_is_reproducible_and_stratified():
    candidates = [
        _sampling_candidate(row * 6 + column, 500_000 + column * 20_000, 2_200_000 + row * 20_000)
        for row in range(6)
        for column in range(6)
    ]

    classified, contract = classify_candidate_pool(candidates)
    first = select_spatially_stratified(classified)
    second = select_spatially_stratified(classified)

    assert first == second
    assert len(first) == 36
    assert len({item["spatial_sector"] for item in first}) == 36
    assert set(item["raw_banding_class"] for item in classified) == {
        "banding_bajo",
        "banding_medio",
        "banding_alto",
    }
    assert len(set(item["morphology_class"] for item in classified)) >= 3
    assert contract["raw_density_interpretation"].startswith("approximately 10%")


def test_tile_halo_reconstruction_covers_each_pixel_once():
    values = np.arange(100, dtype=np.float32).reshape(10, 10)
    reconstructed = np.empty_like(values)
    cores = core_tile_windows(values.shape, tile_size=6)

    for core in cores:
        context = expanded_window(core, values.shape, halo=2)
        context_values = array_window(values, context)
        row = int(core.row_off - context.row_off)
        column = int(core.col_off - context.col_off)
        cropped = context_values[row : row + int(core.height), column : column + int(core.width)]
        reconstructed[
            int(core.row_off) : int(core.row_off + core.height),
            int(core.col_off) : int(core.col_off + core.width),
        ] = cropped

    assert comparison_metrics(values, reconstructed)["array_identical"] is True
    assert len(cores) == 4
    assert expanded_window(cores[0], values.shape, halo=2).flatten() == (0, 0, 8, 8)


def test_seam_qa_distinguishes_vertical_horizontal_corners_and_interior():
    reference = np.zeros((16, 16), dtype=np.float32)
    candidate = reference.copy()
    candidate[:, 8] = 0.25

    qa = seam_metrics(reference, candidate, tile_size=8, band_width=2)

    assert qa["seam_free"] is False
    assert qa["regions"]["vertical_borders"]["n_pixels_different"] > 0
    assert qa["regions"]["horizontal_borders"]["n_pixels_different"] == 0
    assert qa["regions"]["corners"]["n_pixels_different"] > 0
    assert qa["regions"]["interior"]["n_pixels_different"] == 0


def _qa_result(chip_id: str, autocorrelation: float, density_change: float, mae: float) -> dict:
    return {
        "chip": {"chip_id": chip_id, "morphology_class": "montana" if chip_id == "c" else "plano"},
        "qa": {
            "raw_dominant_repetition": {"autocorrelation": autocorrelation},
            "fp3_dominant_repetition": {"autocorrelation": autocorrelation - 0.02},
            "raw_banding": {"high_second_difference_percentage": 10.0},
            "fp3_banding": {"high_second_difference_percentage": 10.0 + density_change},
            "metrics": {
                "elevation": {
                    "mae_m": mae,
                    "rmse_m": mae * 1.2,
                    "absolute_difference_m": {"maximum": 0.5},
                    "threshold_percentages": {"abs_change_gt_0.25_m": 20.0},
                },
                "slope_horn_degrees": {"difference_from_raw_degrees": {"mae": 0.2, "rmse": 0.3}},
                "structure_preservation": {
                    "strong_gradient": {"candidate_to_raw_magnitude_ratio": {"p50": 1.0}},
                    "surface_normal_angular_difference_degrees": {"p95": 0.8},
                },
            },
        },
    }


def test_qa_aggregation_preserves_strata_and_outliers():
    results = {
        "a": _qa_result("a", 0.4, -4.0, 0.1),
        "b": _qa_result("b", 0.6, -2.0, 0.2),
        "c": _qa_result("c", 0.8, 1.0, 0.3),
    }

    contract = assign_full_resolution_banding_classes(results)
    aggregate = aggregate_state_validation(results)

    assert {result["raw_banding_class"] for result in results.values()} == {
        "banding_bajo",
        "banding_medio",
        "banding_alto",
    }
    assert contract["descriptive_only"] is True
    assert aggregate["mae_z_m"]["maximum"] == 0.3
    assert aggregate["outliers"]["largest_mae_z"][0]["chip_id"] == "c"
    assert aggregate["by_raw_banding_class"]["banding_alto"]["fraction_density_reduced"] == 0.0


def test_review_records_decision_without_promoting_or_generating_state_dem(tmp_path):
    stage = PendientesStateValidation()
    stage.manifest_path = tmp_path / "manifest.json"
    stage.manifest_path.write_text(json.dumps({"status": "completed_pending_review"}), encoding="utf-8")

    manifest = stage.record_review("requiere_ajuste", {"reason": "test"})

    assert manifest["status"] == "completed_reviewed_not_promoted"
    assert manifest["decision"]["value"] == "requiere_ajuste"
    assert manifest["decision"]["promoted"] is False
    assert manifest["decision"]["statewide_dem_generated"] is False
