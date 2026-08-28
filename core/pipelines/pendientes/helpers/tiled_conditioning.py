from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import rasterio
from affine import Affine
from rasterio.windows import Window, transform as window_transform

from core.pipelines.pendientes.helpers.experimental_artifacts import write_float_raster
from core.pipelines.pendientes.helpers.experimental_metrics import valid_mask
from core.pipelines.pendientes.helpers.experimental_whitebox import run_feature_preserving_smoothing


def core_tile_windows(shape: tuple[int, int], tile_size: int) -> list[Window]:
    if tile_size <= 0:
        raise ValueError("Tile size must be positive")
    height, width = shape
    return [
        Window(column, row, min(tile_size, width - column), min(tile_size, height - row))
        for row in range(0, height, tile_size)
        for column in range(0, width, tile_size)
    ]


def expanded_window(core: Window, shape: tuple[int, int], halo: int) -> Window:
    if halo < 0:
        raise ValueError("Tile halo cannot be negative")
    height, width = shape
    row_start = max(0, int(core.row_off) - halo)
    column_start = max(0, int(core.col_off) - halo)
    row_end = min(height, int(core.row_off + core.height) + halo)
    column_end = min(width, int(core.col_off + core.width) + halo)
    return Window(column_start, row_start, column_end - column_start, row_end - row_start)


def array_window(values: np.ndarray, window: Window) -> np.ndarray:
    row_start = int(window.row_off)
    column_start = int(window.col_off)
    return values[
        row_start : row_start + int(window.height),
        column_start : column_start + int(window.width),
    ]


def comparison_metrics(reference: np.ndarray, candidate: np.ndarray) -> dict[str, Any]:
    if reference.shape != candidate.shape:
        raise ValueError("Tile comparison arrays must share a grid")
    difference = candidate.astype(np.float64) - reference.astype(np.float64)
    absolute = np.abs(difference)
    return {
        "max_abs_difference": float(absolute.max(initial=0.0)),
        "mae": float(absolute.mean()),
        "rmse": float(np.sqrt(np.mean(np.square(difference)))),
        "n_pixels_different": int(np.count_nonzero(difference != 0)),
        "array_identical": bool(np.array_equal(reference, candidate)),
    }


def seam_region_masks(shape: tuple[int, int], tile_size: int, band_width: int) -> dict[str, np.ndarray]:
    if band_width <= 0:
        raise ValueError("Seam band width must be positive")
    height, width = shape
    rows, columns = np.indices(shape)
    vertical = np.zeros(shape, dtype=bool)
    horizontal = np.zeros(shape, dtype=bool)
    for boundary in range(tile_size, width, tile_size):
        vertical |= np.abs(columns - boundary) < band_width
    for boundary in range(tile_size, height, tile_size):
        horizontal |= np.abs(rows - boundary) < band_width
    corners = vertical & horizontal
    return {
        "interior": ~(vertical | horizontal),
        "vertical_borders": vertical & ~horizontal,
        "horizontal_borders": horizontal & ~vertical,
        "corners": corners,
    }


def seam_metrics(
    reference: np.ndarray,
    candidate: np.ndarray,
    tile_size: int,
    band_width: int,
) -> dict[str, Any]:
    difference = candidate.astype(np.float64) - reference.astype(np.float64)
    masks = seam_region_masks(reference.shape, tile_size, band_width)
    output: dict[str, Any] = {"band_width_pixels": band_width, "regions": {}}
    for name, mask in masks.items():
        values = difference[mask]
        absolute = np.abs(values)
        output["regions"][name] = {
            "pixel_count": int(values.size),
            "max_abs_difference": float(absolute.max(initial=0.0)),
            "mae": float(absolute.mean()) if values.size else 0.0,
            "rmse": float(np.sqrt(np.mean(np.square(values)))) if values.size else 0.0,
            "n_pixels_different": int(np.count_nonzero(values != 0)),
        }
    output["seam_free"] = all(
        region["n_pixels_different"] == 0
        for name, region in output["regions"].items()
        if name != "interior"
    )
    return output


def run_full_reference(
    backend: dict[str, Any],
    values: np.ndarray,
    transform: Affine,
    crs: rasterio.crs.CRS,
    nodata: float | None,
    configuration: dict[str, float | int | str],
    output_dir: Path,
) -> tuple[np.ndarray, dict[str, Any]]:
    input_path = write_float_raster(output_dir / "full_input.tif", values, valid_mask(values, nodata), transform, crs)
    output_path = output_dir / "full_output.tif"
    execution = run_feature_preserving_smoothing(backend, input_path, output_path, configuration)
    with rasterio.open(output_path) as dataset:
        result = dataset.read(1)
    return result, execution


def run_tiled_reference(
    backend: dict[str, Any],
    values: np.ndarray,
    transform: Affine,
    crs: rasterio.crs.CRS,
    nodata: float | None,
    configuration: dict[str, float | int | str],
    output_dir: Path,
    tile_size: int,
    halo: int,
) -> tuple[np.ndarray, dict[str, Any]]:
    reconstructed = np.empty(values.shape, dtype=np.float32)
    executions: list[dict[str, Any]] = []
    for index, core in enumerate(core_tile_windows(values.shape, tile_size)):
        context = expanded_window(core, values.shape, halo)
        context_values = array_window(values, context)
        context_transform = window_transform(context, transform)
        tile_dir = output_dir / f"tile_{index:02d}"
        input_path = write_float_raster(
            tile_dir / "input_with_halo.tif",
            context_values,
            valid_mask(context_values, nodata),
            context_transform,
            crs,
        )
        output_path = tile_dir / "output_with_halo.tif"
        execution = run_feature_preserving_smoothing(backend, input_path, output_path, configuration)
        with rasterio.open(output_path) as dataset:
            filtered = dataset.read(1)
        row_start = int(core.row_off - context.row_off)
        column_start = int(core.col_off - context.col_off)
        core_values = filtered[
            row_start : row_start + int(core.height),
            column_start : column_start + int(core.width),
        ]
        output_row = int(core.row_off)
        output_column = int(core.col_off)
        reconstructed[
            output_row : output_row + int(core.height),
            output_column : output_column + int(core.width),
        ] = core_values
        executions.append(execution)
    return reconstructed, {
        "tile_size_pixels": tile_size,
        "halo_pixels": halo,
        "tile_count": len(executions),
        "elapsed_seconds": float(sum(item["elapsed_seconds"] for item in executions)),
        "executions": executions,
    }
