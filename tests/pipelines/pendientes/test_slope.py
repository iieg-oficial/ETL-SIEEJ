from __future__ import annotations

import numpy as np
import pytest

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
    assert np.allclose(percentage, np.tan(np.radians(degrees)) * 100)


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


def test_slope_rejects_non_positive_resolution():
    with pytest.raises(ValueError, match="positive"):
        experimental_horn_slope(np.ones((3, 3)), resolution=0)
