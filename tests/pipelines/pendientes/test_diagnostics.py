from __future__ import annotations

from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_origin

from core.pipelines.pendientes.helpers.diagnostics import (
    DiagnosticChipRequest,
    baseline_qa,
    diagnostic_chip_plan,
    source_window_summary,
    write_diagnostic_chip,
)


def _write_baseline(path: Path, values: np.ndarray) -> Path:
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        width=values.shape[1],
        height=values.shape[0],
        count=1,
        dtype="float32",
        crs="EPSG:6368",
        transform=from_origin(0, values.shape[0] * 15, 15, 15),
        nodata=-9999,
    ) as dataset:
        dataset.write(values.astype(np.float32), 1)
    return path


def test_baseline_qa_streams_statistics_and_neighbor_differences(tmp_path):
    values = np.array(
        [
            [0, 0, 1, 2],
            [0, 0, 1, 2],
            [1, 1, 2, 3],
            [2, 2, 3, -9999],
        ],
        dtype=np.float32,
    )
    path = _write_baseline(tmp_path / "baseline.tif", values)
    qa = baseline_qa(path, maximum_sample_cells=100)

    assert qa["raster"]["valid_pixels"] == 15
    assert qa["raster"]["nodata_pixels"] == 1
    assert qa["raster"]["minimum"] == 0
    assert qa["raster"]["maximum"] == 3
    assert qa["raster"]["valid_surface_m2"] == 15 * 225
    assert qa["neighbor_differences"]["dz_x"]["percentage_abs_dz_eq_0"] > 0
    assert qa["neighbor_differences"]["dz_y"]["threshold_percentages"]["abs_dz_le_1_m"] == 100


def test_source_window_summary_is_native_grid_sample_not_cross_grid_pairing(tmp_path):
    path = _write_baseline(tmp_path / "source.tif", np.arange(100, dtype=np.float32).reshape(10, 10))
    summary = source_window_summary(
        path,
        {"column_offset": 2, "row_offset": 3, "width": 4, "height": 5},
        maximum_sample_cells=20,
    )
    assert summary["source_window_cells"] == 20
    assert summary["sample_shape"] == [5, 4]
    assert "not paired by pixel index" in summary["strategy"]


def test_diagnostic_chip_preserves_crs_resolution_and_grid(tmp_path):
    baseline = _write_baseline(tmp_path / "baseline.tif", np.arange(100, dtype=np.float32).reshape(10, 10))
    result = write_diagnostic_chip(
        baseline,
        tmp_path / "chips",
        DiagnosticChipRequest(
            name="manual_test",
            terrain_class="manual_problem_area",
            center_x=75,
            center_y=75,
            size=4,
        ),
    )
    with rasterio.open(result["path"]) as chip:
        assert chip.crs.to_epsg() == 6368
        assert chip.res == (15, 15)
        assert chip.width == 4
        assert chip.height == 4


def test_diagnostic_chip_plan_does_not_choose_arbitrary_windows():
    plan = diagnostic_chip_plan()
    assert plan["default_size"] == [1024, 1024]
    assert plan["selection_status"] == "coordinates pending reproducible terrain-stratified selection"
