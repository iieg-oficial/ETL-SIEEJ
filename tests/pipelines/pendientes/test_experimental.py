from __future__ import annotations

import numpy as np
import pytest
import rasterio
from affine import Affine

from core.pipelines.pendientes.helpers.experimental_artifacts import write_float_raster
from core.pipelines.pendientes.helpers.experimental_chips import select_representative_chips
from core.pipelines.pendientes.helpers.experimental_filters import bilateral_smoothing, gaussian_smoothing
from core.pipelines.pendientes.helpers.experimental_metrics import experimental_metrics


def test_gaussian_and_bilateral_preserve_constant_surface_and_nodata():
    elevation = np.full((21, 21), 100.0, dtype=np.float32)
    elevation[0, 0] = -9999

    gaussian = gaussian_smoothing(elevation, sigma_pixels=0.75, nodata=-9999)
    bilateral = bilateral_smoothing(elevation, sigma_dist_pixels=1.0, sigma_int_m=1.0, nodata=-9999)

    assert gaussian[0, 0] == -9999
    assert bilateral[0, 0] == -9999
    assert np.allclose(gaussian[1:, 1:], 100.0)
    assert np.allclose(bilateral[1:, 1:], 100.0)


def test_bilateral_preserves_isolated_break_more_than_gaussian():
    elevation = np.zeros((31, 31), dtype=np.float32)
    elevation[:, 16:] = 10.0

    gaussian = gaussian_smoothing(elevation, sigma_pixels=1.0)
    bilateral = bilateral_smoothing(elevation, sigma_dist_pixels=1.0, sigma_int_m=0.5)

    assert abs(bilateral[15, 15] - elevation[15, 15]) < abs(gaussian[15, 15] - elevation[15, 15])
    assert abs(bilateral[15, 16] - elevation[15, 16]) < abs(gaussian[15, 16] - elevation[15, 16])


def test_experimental_metrics_report_elevation_slope_banding_and_structure():
    rows, columns = np.indices((21, 21))
    raw = (rows * 2 + columns * 3).astype(np.float32)
    candidate = raw + 0.5

    metrics, slope, slope_valid = experimental_metrics(raw, candidate, resolution=15, nodata=-9999)

    assert metrics["elevation"]["bias_m"] == pytest.approx(0.5)
    assert metrics["elevation"]["mae_m"] == pytest.approx(0.5)
    assert metrics["elevation"]["rmse_m"] == pytest.approx(0.5)
    assert metrics["elevation"]["threshold_percentages"]["abs_change_gt_0.25_m"] == 100
    assert metrics["slope_horn_degrees"]["difference_from_raw_degrees"]["mae"] == pytest.approx(0)
    assert metrics["neighbor_differences"]["dz_x"]["p50"] == pytest.approx(3)
    assert metrics["absolute_laplacian_m"]["p99"] == pytest.approx(0)
    assert metrics["structure_preservation"]["strong_gradient"]["candidate_to_raw_magnitude_ratio"][
        "p50"
    ] == pytest.approx(1)
    assert slope_valid.any()
    assert np.isfinite(slope[slope_valid]).all()


def test_chip_selection_is_reproducible_and_uses_joint_terrain_variables():
    candidates = []
    for index in range(20):
        candidates.append(
            {
                "row_offset": index * 1024,
                "column_offset": index * 2048,
                "width": 1024,
                "height": 1024,
                "center_x": float(index),
                "center_y": float(index + 1),
                "bbox": (float(index), 0.0, float(index + 1), 1.0),
                "slope_median_degrees": float(index),
                "roughness_median_abs_laplacian_m": float(index * 2),
                "valid_percentage": 100.0,
            }
        )

    first, first_contract = select_representative_chips(candidates)
    second, second_contract = select_representative_chips(candidates)

    assert first == second
    assert first_contract == second_contract
    assert [chip.terrain_class for chip in first] == ["plano", "lomerio", "montana"]
    assert len({(chip.row_offset, chip.column_offset) for chip in first}) == 3
    assert first_contract["terrain_variables"] == [
        "Horn slope median",
        "median absolute four-neighbor Laplacian",
    ]


def test_experimental_raster_preserves_grid_and_nodata(tmp_path):
    values = np.arange(64, dtype=np.float32).reshape(8, 8)
    valid = np.ones(values.shape, dtype=bool)
    valid[3, 4] = False
    transform = Affine(15, 0, 500_000, 0, -15, 2_300_000)
    path = tmp_path / "qa.tif"

    write_float_raster(path, values, valid, transform, rasterio.crs.CRS.from_epsg(6368))

    with rasterio.open(path) as dataset:
        assert dataset.crs.to_epsg() == 6368
        assert dataset.transform == transform
        assert dataset.res == (15, 15)
        assert dataset.dtypes == ("float32",)
        assert dataset.nodata == -9999
        assert dataset.read(1)[3, 4] == -9999
