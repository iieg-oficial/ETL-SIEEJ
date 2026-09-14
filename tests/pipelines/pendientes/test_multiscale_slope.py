from pathlib import Path

import numpy as np
import rasterio
from affine import Affine

from core.pipelines.pendientes.helpers.multiscale_slope import (
    class_fragmentation,
    error_metrics,
    inspect_grass_param_scale,
    planar_surface,
    quadratic_gradient_kernels,
    run_grass_wood_evans,
    write_single_band_raster,
    wood_evans_slope,
)


def test_quadratic_fit_reproduces_horizontal_and_inclined_planes() -> None:
    for window in (3, 5, 7):
        kernel_x, kernel_y = quadratic_gradient_kernels(window, 15.0)
        assert abs(kernel_x.sum()) < 1e-12
        assert abs(kernel_y.sum()) < 1e-12
        for slope in (0, 1, 2, 5, 15, 30, 45):
            for orientation in (0, 22.5, 45, 67.5, 90, 135):
                values = planar_surface(33, 15.0, slope, orientation)
                result, valid = wood_evans_slope(values, window, 15.0)
                metrics = error_metrics(result[valid], slope)
                assert metrics["max_error"] < 2e-4


def test_full_support_nodata_and_edge_policy() -> None:
    values = planar_surface(15, 15.0, 5.0, 45.0)
    values[7, 7] = -9999
    result, valid = wood_evans_slope(values, 5, 15.0, nodata=-9999)
    assert not valid[:2].any() and not valid[-2:].any()
    assert not valid[:, :2].any() and not valid[:, -2:].any()
    assert not valid[5:10, 5:10].any()
    assert np.isnan(result[~valid]).all()


def test_noise_is_reproducible_and_larger_windows_reduce_error() -> None:
    base = planar_surface(129, 15.0, 2.0, 22.5).astype(np.float64)
    rng = np.random.default_rng(801)
    noisy = base + rng.normal(0, 1.0, base.shape)
    errors = {}
    for window in (3, 5, 7):
        first, valid = wood_evans_slope(noisy, window, 15.0)
        second, second_valid = wood_evans_slope(noisy, window, 15.0)
        assert np.array_equal(valid, second_valid)
        assert np.array_equal(first[valid], second[valid])
        errors[window] = error_metrics(first[valid], 2.0, extended=True)
    assert errors[7]["rmse"] < errors[5]["rmse"] < errors[3]["rmse"]


def test_grass_backend_matches_explicit_unweighted_fit_on_plane(tmp_path: Path) -> None:
    backend = inspect_grass_param_scale()
    values = planar_surface(65, 15.0, 15.0, 67.5)
    dem = write_single_band_raster(tmp_path / "dem.tif", values, Affine(15, 0, 0, 0, -15, 975), "EPSG:6368", "metre")
    outputs = {window: tmp_path / f"we{window}.tif" for window in (3, 5, 7)}
    run_grass_wood_evans(dem, outputs, backend)
    for window, path in outputs.items():
        expected, valid = wood_evans_slope(values, window, 15.0)
        with rasterio.open(path) as dataset:
            observed = dataset.read(1)
        common = valid & (observed != -9999)
        assert np.max(np.abs(observed[common] - expected[common])) < 2e-5


def test_fragmentation_uses_fixed_nine_pixel_threshold() -> None:
    values = np.full((20, 20), 1.0, dtype=np.float32)
    values[10, 10] = 6.0
    report = class_fragmentation(values)
    assert report["small_component_threshold_pixels"] == 9
    assert report["number_of_connected_components"] == 2
    assert report["percent_pixels_in_components_lt_threshold"] == 0.25
