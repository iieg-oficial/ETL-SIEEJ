from __future__ import annotations

import json

import numpy as np
import pytest
import rasterio
from affine import Affine

from core.pipelines.pendientes.constants import (
    SLOPE_SELECTION_PARENT_MANIFEST_SHA256,
    STATEWIDE_CANDIDATE_SHA256,
)
from core.pipelines.pendientes.helpers.slope import (
    horn_gradient,
    slope_products_from_gradient,
    zevenbergen_thorne_gradient,
)
from core.pipelines.pendientes.helpers.slope_selection import (
    contextual_chip_window,
    difference_metrics,
    inspect_gdaldem_backend,
    planar_error_metrics,
    planar_surface,
    run_gdaldem_slope,
    write_single_band_raster,
)
from core.pipelines.pendientes.helpers.methodology.slope_algorithm_validation import (
    PendientesSlopeAlgorithmValidation,
)


@pytest.mark.parametrize(
    ("slope_degrees", "direction_degrees"),
    [(0.0, 0.0), (1.0, 0.0), (15.0, 90.0), (30.0, 45.0), (45.0, 135.0), (5.0, 22.5), (15.0, 67.5)],
)
def test_numpy_kernels_reproduce_analytical_planes(slope_degrees, direction_degrees):
    elevation = planar_surface(65, 15.0, slope_degrees, direction_degrees)
    for gradient in (horn_gradient, zevenbergen_thorne_gradient):
        dz_dx, dz_dy, valid = gradient(elevation, 15.0)
        degrees, _ = slope_products_from_gradient(dz_dx, dz_dy)
        assert np.allclose(degrees[valid], slope_degrees, atol=1e-3)


def test_gdaldem_backend_runs_both_algorithms_reproducibly_on_diagonal_plane(tmp_path):
    backend = inspect_gdaldem_backend()
    dem_path = write_single_band_raster(
        tmp_path / "dem.tif",
        planar_surface(65, 15.0, 30.0, 45.0),
        Affine(15, 0, 0, 0, -15, 975),
        "EPSG:6368",
        "metre",
    )
    arrays = {}
    for algorithm in ("Horn", "ZevenbergenThorne"):
        first = tmp_path / f"{algorithm}_first.tif"
        second = tmp_path / f"{algorithm}_second.tif"
        run_gdaldem_slope(backend, dem_path, first, algorithm)
        run_gdaldem_slope(backend, dem_path, second, algorithm)
        with rasterio.open(first) as first_dataset, rasterio.open(second) as second_dataset:
            arrays[algorithm] = first_dataset.read(1)
            assert np.array_equal(arrays[algorithm], second_dataset.read(1))
            assert first_dataset.nodata == -9999.0
        assert planar_error_metrics(arrays[algorithm], 30.0)["max_error_degrees"] <= 1e-3
    assert difference_metrics(arrays["Horn"], arrays["ZevenbergenThorne"])["mae_degrees"] <= 1e-3


def test_backend_freezes_equal_xy_z_dimensions_and_effective_z_factor():
    backend = inspect_gdaldem_backend()
    assert backend["parameters"]["scale_xy_to_z"] == 1.0
    assert backend["parameters"]["effective_z_factor"] == 1.0


def test_horn_and_zevenbergen_thorne_have_distinct_local_noise_response():
    clean = planar_surface(65, 15.0, 5.0, 22.5)
    noisy = clean.copy()
    noisy[32, 32] += 0.5
    outputs = {}
    for name, gradient in (("Horn", horn_gradient), ("ZevenbergenThorne", zevenbergen_thorne_gradient)):
        dz_dx, dz_dy, valid = gradient(noisy, 15.0)
        degrees, _ = slope_products_from_gradient(dz_dx, dz_dy)
        outputs[name] = degrees[valid]
    assert not np.array_equal(outputs["Horn"], outputs["ZevenbergenThorne"])


def test_gdaldem_edges_and_nodata_are_not_computed_without_full_neighborhood(tmp_path):
    backend = inspect_gdaldem_backend()
    values = planar_surface(9, 15.0, 5.0, 0.0)
    values[4, 4] = -9999.0
    dem_path = write_single_band_raster(
        tmp_path / "dem.tif", values, Affine(15, 0, 0, 0, -15, 135), "EPSG:6368", "metre"
    )
    output_path = tmp_path / "slope.tif"
    run_gdaldem_slope(backend, dem_path, output_path, "Horn")
    with rasterio.open(output_path) as dataset:
        slope = dataset.read(1)
    assert np.all(slope[0, :] == -9999)
    assert np.all(slope[-1, :] == -9999)
    assert np.all(slope[:, 0] == -9999)
    assert np.all(slope[:, -1] == -9999)
    assert np.all(slope[3:6, 3:6] == -9999)


def test_contextual_window_adds_margin_without_changing_analysis_grid():
    chip = {"column_offset": 100, "row_offset": 200, "width": 1024, "height": 1024}
    window = contextual_chip_window(chip, 32, (2000, 2000))
    assert window.flatten() == (68, 168, 1088, 1088)
    with pytest.raises(ValueError, match="outside"):
        contextual_chip_window({**chip, "column_offset": 10}, 32, (2000, 2000))


def test_selection_manifest_freezes_parent_and_percentage_relationship(tmp_path):
    stage = PendientesSlopeAlgorithmValidation()
    stage.manifest_path = tmp_path / "manifest.json"
    stage.manifest_path.write_text(
        json.dumps(
            {
                "status": "completed_pending_methodological_decision",
                "backend": {"name": "GDAL gdaldem CLI", "version": "GDAL 3.8.4"},
                "inputs": {
                    "master_territorial_grid": {"master_dem_sha256": "a" * 64},
                },
                "visual_review": {"human_review_completed": False},
            }
        ),
        encoding="utf-8",
    )
    manifest = stage.record_decision("Horn_recomendado_para_produccion", {"pareto": "reviewed"})
    contract = manifest["next_phase_contract"]
    assert contract["parent_context_dem_sha256"] == STATEWIDE_CANDIDATE_SHA256
    assert contract["selected_slope_algorithm"] == "Horn"
    assert contract["percentage_derivation"] == "tan(radians(degrees)) * 100; values are not capped at 100"
    assert SLOPE_SELECTION_PARENT_MANIFEST_SHA256 == (
        "9aed5594e044ce78ab7512812c186d088b92d955c375d3e98c60315e797c6e55"
    )
