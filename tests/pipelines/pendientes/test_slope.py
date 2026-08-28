from __future__ import annotations

import numpy as np
import pytest
from rasterio.transform import from_origin

from core.pipelines.pendientes.helpers.conditioning import ConditioningExperiment
from core.pipelines.pendientes.helpers.qa import (
    conditioning_metrics,
    reprojection_surface_metrics,
    valid_surface_area_m2,
    validate_slope_pair,
)
from core.pipelines.pendientes.helpers.slope import experimental_horn_slope, slope_products_from_gradient


def test_flat_surface_has_zero_slope():
    elevation = np.full((5, 5), 1200.0)
    degrees, percentage, valid = experimental_horn_slope(elevation, resolution=15)
    assert np.all(degrees[valid] == 0)
    assert np.all(percentage[valid] == 0)


def test_known_planar_gradient_matches_expected_slope():
    elevation = np.tile(np.arange(7, dtype=float) * 3.0, (7, 1))
    degrees, percentage, valid = experimental_horn_slope(elevation, resolution=15)
    assert np.allclose(percentage[valid], 20.0)
    assert np.allclose(degrees[valid], np.degrees(np.arctan(0.2)))


def test_degree_and_percentage_products_share_one_gradient():
    dz_dx = np.array([[0.0, 0.25], [1.0, 2.0]])
    dz_dy = np.array([[0.0, 0.0], [0.0, 1.0]])
    degrees, percentage = slope_products_from_gradient(dz_dx, dz_dy)
    validate_slope_pair(degrees, percentage, np.ones(degrees.shape, dtype=bool))


def test_nodata_invalidates_only_windows_that_touch_it():
    elevation = np.tile(np.arange(9, dtype=float), (9, 1))
    elevation[4, 4] = -9999
    _, _, valid = experimental_horn_slope(elevation, resolution=15, nodata=-9999)
    assert not valid[3:6, 3:6].any()
    assert valid[1, 1]
    assert valid[7, 7]


def test_edges_are_invalid_for_three_by_three_gradient():
    elevation = np.arange(25, dtype=float).reshape(5, 5)
    _, _, valid = experimental_horn_slope(elevation, resolution=15)
    assert not valid[0, :].any()
    assert not valid[-1, :].any()
    assert not valid[:, 0].any()
    assert not valid[:, -1].any()
    assert valid[1:-1, 1:-1].all()


def test_small_raster_has_no_valid_horn_cells():
    _, _, valid = experimental_horn_slope(np.ones((2, 2)), resolution=15)
    assert not valid.any()


def test_conditioning_metrics_report_no_change_for_raw():
    elevation = np.arange(9, dtype=np.float32).reshape(3, 3)
    metrics = conditioning_metrics(elevation, elevation.copy(), np.ones_like(elevation))
    assert metrics["rmse_against_reprojected_dem"] == 0
    assert metrics["modified_pixel_percentage"] == 0
    assert metrics["mae"] == 0
    assert metrics["bias"] == 0
    assert metrics["absolute_difference_percentiles"]["p99"] == 0
    assert metrics["slope_distribution"]["mean"] == 1
    assert sum(metrics["slope_distribution"]["histogram"]["counts"]) == elevation.size
    assert metrics["ridge_preservation"] is None


def test_reprojection_qa_compares_different_grids_by_footprint_not_pixel_index():
    metrics = reprojection_surface_metrics(
        np.arange(16, dtype=float).reshape(4, 4),
        np.arange(9, dtype=float).reshape(3, 3),
        source_transform=from_origin(0, 4, 1, 1),
        source_crs="EPSG:6368",
        target_transform=from_origin(0, 45, 15, 15),
        target_crs="EPSG:6368",
        source_nodata=None,
        target_nodata=None,
        histogram_bins=4,
    )
    assert metrics["source"]["valid_count"] == 16
    assert metrics["target"]["valid_surface_m2"] == 9 * 225
    assert "no direct pixel-index comparison" in metrics["comparison_strategy"]


def test_conditioning_design_reserves_three_candidates_without_selecting_methods():
    design = ConditioningExperiment().comparison_design()
    assert design["registered_candidates"] == ["raw"]
    assert design["required_future_slots"] == ["candidate_a", "candidate_b", "candidate_c"]
    assert design["winner_selected"] is False


def test_source_valid_surface_uses_geodesic_area_not_square_degrees():
    area_m2 = valid_surface_area_m2(
        np.ones((1, 1)),
        nodata=None,
        transform=from_origin(-104, 20, 1 / 7200, 1 / 7200),
        crs="EPSG:6365",
    )
    assert 100 < area_m2 < 300


def test_slope_rejects_non_positive_resolution():
    with pytest.raises(ValueError, match="positive"):
        experimental_horn_slope(np.ones((3, 3)), resolution=0)
