from __future__ import annotations

import math
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.windows import Window, transform as window_transform

from core.pipelines.pendientes.constants import (
    DIAGNOSTIC_CHIP_SIZE,
    NEAR_FLAT_DIFFERENCE_TOLERANCE_M,
    RASTER_BLOCK_SIZE,
)

BASELINE_PERCENTILES = (1, 5, 25, 50, 75, 95, 99)
NEIGHBOR_PERCENTILES = (50, 90, 95, 99)
NEIGHBOR_THRESHOLDS_M = (0.25, 0.5, 1.0, 2.0)
DIAGNOSTIC_TERRAIN_CLASSES = ("flat", "rolling_hills", "mountain", "manual_problem_area")


def _sample_stride(total_cells: int, maximum_sample_cells: int) -> int:
    return max(1, math.ceil(math.sqrt(total_cells / maximum_sample_cells)))


def _summary_from_values(values: np.ndarray, percentiles: tuple[int, ...]) -> dict[str, Any]:
    if not values.size:
        raise ValueError("Diagnostic sample has no valid pixels")
    return {
        "minimum": float(values.min()),
        "maximum": float(values.max()),
        "mean": float(values.mean()),
        "stddev": float(values.std()),
        "percentiles": {f"p{percentile:02d}": float(np.percentile(values, percentile)) for percentile in percentiles},
    }


def _neighbor_accumulator() -> dict[str, Any]:
    return {
        "count": 0,
        "zero_count": 0,
        "near_flat_count": 0,
        "threshold_counts": {threshold: 0 for threshold in NEIGHBOR_THRESHOLDS_M},
        "samples": [],
    }


def _accumulate_neighbors(
    accumulator: dict[str, Any],
    differences: np.ma.MaskedArray,
    sample_stride: int,
    near_flat_tolerance: float,
) -> None:
    absolute = np.ma.abs(differences)
    valid = absolute.compressed().astype(np.float64, copy=False)
    if not valid.size:
        return
    accumulator["count"] += int(valid.size)
    accumulator["zero_count"] += int(np.count_nonzero(valid == 0))
    accumulator["near_flat_count"] += int(np.count_nonzero(valid <= near_flat_tolerance))
    for threshold in NEIGHBOR_THRESHOLDS_M:
        accumulator["threshold_counts"][threshold] += int(np.count_nonzero(valid <= threshold))
    sampled = absolute[::sample_stride, ::sample_stride].compressed().astype(np.float64, copy=False)
    if not sampled.size:
        sampled = valid[: min(1024, valid.size)]
    if sampled.size:
        accumulator["samples"].append(sampled)


def _finalize_neighbors(
    accumulator: dict[str, Any],
    near_flat_tolerance: float,
) -> dict[str, Any]:
    count = accumulator["count"]
    if not count:
        raise ValueError("Baseline has no valid neighboring pixel pairs")
    samples = np.concatenate(accumulator["samples"]) if accumulator["samples"] else np.array([], dtype=float)
    return {
        "valid_pairs": count,
        "percentage_abs_dz_eq_0": accumulator["zero_count"] / count * 100,
        "near_flat_tolerance_m": near_flat_tolerance,
        "near_flat_percentage": accumulator["near_flat_count"] / count * 100,
        "threshold_percentages": {
            f"abs_dz_le_{threshold:g}_m": accumulator["threshold_counts"][threshold] / count * 100
            for threshold in NEIGHBOR_THRESHOLDS_M
        },
        "absolute_difference_percentiles": {
            f"p{percentile}": float(np.percentile(samples, percentile)) for percentile in NEIGHBOR_PERCENTILES
        },
        "percentile_sample_cells": int(samples.size),
        "percentiles_are_sampled": True,
    }


def baseline_qa(
    path: Path,
    maximum_sample_cells: int,
    near_flat_tolerance: float = NEAR_FLAT_DIFFERENCE_TOLERANCE_M,
) -> dict[str, Any]:
    """Exact streaming counts/moments and bounded deterministic percentile samples."""
    started = time.perf_counter()
    with rasterio.open(path, "r") as dataset:
        stride = _sample_stride(dataset.width * dataset.height, maximum_sample_cells)
        valid_count = 0
        nodata_count = 0
        value_sum = 0.0
        square_sum = 0.0
        minimum = math.inf
        maximum = -math.inf
        value_samples: list[np.ndarray] = []
        neighbors_x = _neighbor_accumulator()
        neighbors_y = _neighbor_accumulator()

        for _, core_window in dataset.block_windows(1):
            core = dataset.read(1, window=core_window, masked=True)
            values = core.compressed().astype(np.float64, copy=False)
            valid_count += int(values.size)
            nodata_count += int(core.size - values.size)
            if values.size:
                value_sum += float(values.sum())
                square_sum += float(np.square(values).sum())
                minimum = min(minimum, float(values.min()))
                maximum = max(maximum, float(values.max()))
                sampled = core[::stride, ::stride].compressed().astype(np.float64, copy=False)
                if not sampled.size:
                    sampled = values[: min(1024, values.size)]
                if sampled.size:
                    value_samples.append(sampled)

            row_offset = int(core_window.row_off)
            column_offset = int(core_window.col_off)
            core_height = int(core_window.height)
            core_width = int(core_window.width)
            extended_width = min(core_width + 1, dataset.width - column_offset)
            extended_height = min(core_height + 1, dataset.height - row_offset)
            extended = dataset.read(
                1,
                window=Window(column_offset, row_offset, extended_width, extended_height),
                masked=True,
            )
            horizontal_columns = min(core_width, dataset.width - column_offset - 1)
            if horizontal_columns > 0:
                differences_x = (
                    extended[:core_height, 1 : horizontal_columns + 1] - extended[:core_height, :horizontal_columns]
                )
                _accumulate_neighbors(neighbors_x, differences_x, stride, near_flat_tolerance)
            vertical_rows = min(core_height, dataset.height - row_offset - 1)
            if vertical_rows > 0:
                differences_y = extended[1 : vertical_rows + 1, :core_width] - extended[:vertical_rows, :core_width]
                _accumulate_neighbors(neighbors_y, differences_y, stride, near_flat_tolerance)

        if not valid_count:
            raise ValueError("Baseline raster has no valid pixels")
        mean = value_sum / valid_count
        variance = max(0.0, square_sum / valid_count - mean * mean)
        samples = np.concatenate(value_samples) if value_samples else np.array([], dtype=float)
        pixel_area_m2 = abs(dataset.transform.a * dataset.transform.e)
        return {
            "raster": {
                "valid_pixels": valid_count,
                "nodata_pixels": nodata_count,
                "minimum": minimum,
                "maximum": maximum,
                "mean": mean,
                "stddev": math.sqrt(variance),
                "percentiles": {
                    f"p{percentile:02d}": float(np.percentile(samples, percentile))
                    for percentile in BASELINE_PERCENTILES
                },
                "percentile_sample_cells": int(samples.size),
                "percentiles_are_sampled": True,
                "sample_stride": stride,
                "valid_surface_m2": valid_count * pixel_area_m2,
            },
            "neighbor_differences": {
                "dz_x": _finalize_neighbors(neighbors_x, near_flat_tolerance),
                "dz_y": _finalize_neighbors(neighbors_y, near_flat_tolerance),
                "interpretation": "surface characterization only; no banding threshold or causality selected",
            },
            "elapsed_seconds": time.perf_counter() - started,
        }


def source_window_summary(
    source_path: Path,
    source_window: dict[str, Any],
    maximum_sample_cells: int,
) -> dict[str, Any]:
    """Summarize the matching source footprint on its native grid without cross-grid pairing."""
    window = Window(
        source_window["column_offset"],
        source_window["row_offset"],
        source_window["width"],
        source_window["height"],
    )
    total_cells = int(window.width * window.height)
    scale = min(1.0, math.sqrt(maximum_sample_cells / total_cells))
    sample_height = max(1, round(window.height * scale))
    sample_width = max(1, round(window.width * scale))
    with rasterio.open(source_path, "r") as dataset:
        sample = dataset.read(
            1,
            window=window,
            out_shape=(sample_height, sample_width),
            masked=True,
            resampling=Resampling.nearest,
        )
    values = sample.compressed().astype(np.float64, copy=False)
    return {
        "strategy": (
            "deterministic native-grid sample over the source window covering the same geographic footprint; "
            "not paired by pixel index with the target grid"
        ),
        "source_window_cells": total_cells,
        "sample_shape": [sample_height, sample_width],
        "sample_valid_pixels": int(values.size),
        "sample_nodata_pixels": int(sample.size - values.size),
        **_summary_from_values(values, BASELINE_PERCENTILES),
    }


@dataclass(frozen=True)
class DiagnosticChipRequest:
    name: str
    terrain_class: str
    center_x: float
    center_y: float
    size: int = DIAGNOSTIC_CHIP_SIZE


def diagnostic_chip_plan() -> dict[str, Any]:
    return {
        "default_size": [DIAGNOSTIC_CHIP_SIZE, DIAGNOSTIC_CHIP_SIZE],
        "terrain_classes": list(DIAGNOSTIC_TERRAIN_CLASSES),
        "selection_status": "coordinates pending reproducible terrain-stratified selection",
        "outputs_are_qa_artifacts": True,
        "outputs_must_remain_under_ignored_data_directory": True,
    }


def write_diagnostic_chip(baseline_path: Path, output_dir: Path, request: DiagnosticChipRequest) -> dict[str, Any]:
    if request.terrain_class not in DIAGNOSTIC_TERRAIN_CLASSES:
        raise ValueError(f"Unsupported terrain class: {request.terrain_class}")
    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / f"{request.name}.tif"
    temporary = destination.with_suffix(".tmp.tif")
    with rasterio.open(baseline_path, "r") as source:
        center_row, center_column = source.index(request.center_x, request.center_y)
        window = Window(
            center_column - request.size // 2,
            center_row - request.size // 2,
            request.size,
            request.size,
        )
        if (
            window.col_off < 0
            or window.row_off < 0
            or window.col_off + window.width > source.width
            or window.row_off + window.height > source.height
        ):
            raise ValueError("Diagnostic chip window falls outside the baseline")
        values = source.read(1, window=window)
        profile = source.profile.copy()
        profile.update(
            width=request.size,
            height=request.size,
            transform=window_transform(window, source.transform),
            tiled=True,
            blockxsize=RASTER_BLOCK_SIZE,
            blockysize=RASTER_BLOCK_SIZE,
            compress="deflate",
            BIGTIFF="IF_SAFER",
        )
        with rasterio.open(temporary, "w", **profile) as target:
            target.write(values, 1)
    temporary.replace(destination)
    return {
        "request": asdict(request),
        "path": str(destination),
        "crs": "EPSG:6368",
        "resolution_m": 15,
        "window": {
            "column_offset": int(window.col_off),
            "row_offset": int(window.row_off),
            "width": int(window.width),
            "height": int(window.height),
        },
    }
