from __future__ import annotations

import math
import time
from pathlib import Path
from typing import Any

import numpy as np
import rasterio
from rasterio.features import geometry_mask, geometry_window
from rasterio.windows import Window, transform as window_transform
from shapely.geometry import mapping

from core.pipelines.pendientes.constants import FINAL_NODATA, RASTER_BLOCK_SIZE
from core.pipelines.pendientes.helpers.experimental_metrics import valid_mask
from core.pipelines.pendientes.helpers.tiled_conditioning import core_tile_windows


def aligned_territorial_window(
    dataset: rasterio.io.DatasetReader,
    geometry: Any,
) -> Window:
    window = geometry_window(dataset, [mapping(geometry)])
    aligned = Window(
        int(window.col_off),
        int(window.row_off),
        int(window.width),
        int(window.height),
    )
    if aligned.width <= 0 or aligned.height <= 0:
        raise ValueError("Jalisco geometry produced an empty raster window")
    if (
        aligned.col_off < 0
        or aligned.row_off < 0
        or aligned.col_off + aligned.width > dataset.width
        or aligned.row_off + aligned.height > dataset.height
    ):
        raise ValueError("Jalisco territorial window is outside the validated context DEM")
    return aligned


def territorial_profile(
    source: rasterio.io.DatasetReader,
    window: Window,
) -> dict[str, Any]:
    return {
        "driver": "GTiff",
        "width": int(window.width),
        "height": int(window.height),
        "count": 1,
        "dtype": "float32",
        "crs": source.crs,
        "transform": window_transform(window, source.transform),
        "nodata": FINAL_NODATA,
        "tiled": True,
        "blockxsize": RASTER_BLOCK_SIZE,
        "blockysize": RASTER_BLOCK_SIZE,
        "compress": "deflate",
        "BIGTIFF": "IF_SAFER",
    }


def parent_window_for_child(child_window: Window, territorial_window: Window) -> Window:
    return Window(
        int(territorial_window.col_off + child_window.col_off),
        int(territorial_window.row_off + child_window.row_off),
        int(child_window.width),
        int(child_window.height),
    )


def create_territorial_dem(
    context_path: Path,
    output_path: Path,
    geometry: Any,
    processing_window_size: int = 2048,
) -> dict[str, Any]:
    if output_path.exists():
        raise FileExistsError(f"Territorial DEM already exists: {output_path}")
    started = time.perf_counter()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    partial = output_path.with_suffix(".partial.tif")
    partial.unlink(missing_ok=True)
    with rasterio.open(context_path) as source:
        territorial_window = aligned_territorial_window(source, geometry)
        profile = territorial_profile(source, territorial_window)
        windows = core_tile_windows((profile["height"], profile["width"]), processing_window_size)
        try:
            with rasterio.open(partial, "w", **profile) as destination:
                destination.set_band_unit(1, "metre")
                for child_window in windows:
                    parent_window = parent_window_for_child(child_window, territorial_window)
                    source_values = source.read(1, window=parent_window)
                    inside = geometry_mask(
                        [mapping(geometry)],
                        out_shape=(int(child_window.height), int(child_window.width)),
                        transform=window_transform(child_window, destination.transform),
                        invert=True,
                        all_touched=False,
                    )
                    source_valid = valid_mask(source_values, source.nodata)
                    output = np.where(inside & source_valid, source_values, FINAL_NODATA).astype(np.float32)
                    destination.write(output, 1, window=child_window)
            partial.replace(output_path)
        except Exception:
            partial.unlink(missing_ok=True)
            raise
    return {
        "territorial_window": {
            "column_offset": int(territorial_window.col_off),
            "row_offset": int(territorial_window.row_off),
            "width": int(territorial_window.width),
            "height": int(territorial_window.height),
        },
        "processing_window_size_pixels": processing_window_size,
        "processing_window_count": len(windows),
        "processing_order": "row-major",
        "elapsed_seconds": time.perf_counter() - started,
    }


def _histogram_percentiles(
    histogram: np.ndarray,
    minimum: float,
    maximum: float,
    percentiles: tuple[int, ...],
) -> dict[str, float]:
    total = int(histogram.sum())
    if total <= 0:
        raise ValueError("Territorial DEM has no valid values")
    cumulative = np.cumsum(histogram)
    width = (maximum - minimum) / histogram.size if maximum > minimum else 0.0
    output = {}
    for percentile in percentiles:
        rank = max(1, math.ceil(percentile / 100 * total))
        index = int(np.searchsorted(cumulative, rank, side="left"))
        output[f"p{percentile:02d}"] = minimum + (index + 0.5) * width if width else minimum
    return output


def validate_territorial_dem(
    context_path: Path,
    territorial_path: Path,
    geometry: Any,
    vector_area_m2: float,
    processing_window_size: int = 2048,
    histogram_bins: int = 100_000,
) -> dict[str, Any]:
    compared = different = expected_inside = valid_output = 0
    mismatch = valid_outside = nodata_inside = inherited_nodata_inside = 0
    value_sum = square_sum = 0.0
    minimum = float("inf")
    maximum = float("-inf")
    max_abs_difference = 0.0
    with rasterio.open(context_path) as parent, rasterio.open(territorial_path) as child:
        territorial_window = aligned_territorial_window(parent, geometry)
        expected_transform = window_transform(territorial_window, parent.transform)
        grid_checks = {
            "crs": child.crs == parent.crs and child.crs.to_epsg() == 6368,
            "transform": child.transform == expected_transform,
            "dimensions": child.width == territorial_window.width and child.height == territorial_window.height,
            "resolution": child.res == parent.res == (15.0, 15.0),
            "dtype": child.dtypes == ("float32",),
            "nodata": child.nodata == parent.nodata == FINAL_NODATA,
            "tiled": child.profile.get("tiled") is True,
            "block_shape": child.block_shapes == [(RASTER_BLOCK_SIZE, RASTER_BLOCK_SIZE)],
            "compression": child.compression is not None and child.compression.value == "DEFLATE",
            "vertical_unit": child.units == ("metre",),
        }
        if not all(grid_checks.values()):
            raise ValueError(f"Territorial DEM grid contract failed: {grid_checks}")
        windows = core_tile_windows(child.shape, processing_window_size)
        for child_window in windows:
            parent_window = parent_window_for_child(child_window, territorial_window)
            parent_values = parent.read(1, window=parent_window)
            child_values = child.read(1, window=child_window)
            inside = geometry_mask(
                [mapping(geometry)],
                out_shape=(int(child_window.height), int(child_window.width)),
                transform=window_transform(child_window, child.transform),
                invert=True,
                all_touched=False,
            )
            parent_valid = valid_mask(parent_values, parent.nodata)
            child_valid = valid_mask(child_values, child.nodata)
            expected_valid = inside & parent_valid
            expected_inside += int(np.count_nonzero(inside))
            valid_output += int(np.count_nonzero(child_valid))
            mismatch += int(np.count_nonzero(child_valid ^ expected_valid))
            valid_outside += int(np.count_nonzero(child_valid & ~inside))
            nodata_inside += int(np.count_nonzero(inside & ~child_valid))
            inherited_nodata_inside += int(np.count_nonzero(inside & ~parent_valid))
            comparison = expected_valid & child_valid
            differences = child_values[comparison].astype(np.float64) - parent_values[comparison]
            compared += differences.size
            different += int(np.count_nonzero(differences != 0))
            max_abs_difference = max(max_abs_difference, float(np.abs(differences).max(initial=0.0)))
            values = child_values[child_valid].astype(np.float64)
            if values.size:
                value_sum += float(values.sum())
                square_sum += float(np.square(values).sum())
                minimum = min(minimum, float(values.min()))
                maximum = max(maximum, float(values.max()))
        histogram = np.zeros(histogram_bins, dtype=np.int64)
        for child_window in windows:
            values = child.read(1, window=child_window)
            selected = values[valid_mask(values, child.nodata)]
            histogram += np.histogram(selected, bins=histogram_bins, range=(minimum, maximum))[0]
        child.read(1, window=Window(child.width - 1, child.height - 1, 1, 1))
        bounds = [float(value) for value in child.bounds]
        transform = list(child.transform)
        size = child.width * child.height
    mean = value_sum / valid_output
    statistics = {
        "minimum": minimum,
        "maximum": maximum,
        "mean": mean,
        "stddev": math.sqrt(max(0.0, square_sum / valid_output - mean * mean)),
        **_histogram_percentiles(histogram, minimum, maximum, (1, 5, 25, 50, 75, 95, 99)),
        "valid_pixels": valid_output,
        "nodata_pixels": size - valid_output,
        "percentile_method": {
            "name": "all-valid-pixel fixed-width histogram",
            "bins": histogram_bins,
            "precision_m": (maximum - minimum) / histogram_bins,
        },
    }
    raster_area_m2 = valid_output * 225.0
    area_difference = raster_area_m2 - vector_area_m2
    return {
        "grid": {
            "checks": grid_checks,
            "passed": all(grid_checks.values()),
            "width": int(territorial_window.width),
            "height": int(territorial_window.height),
            "transform": transform,
            "bounds": bounds,
        },
        "value_equality": {
            "compared_valid_pixels": compared,
            "different_pixels": different,
            "max_abs_difference": max_abs_difference,
            "bitwise_equal": different == 0,
        },
        "mask": {
            "expected_inside_pixels": expected_inside,
            "valid_dem_pixels": valid_output,
            "mask_mismatch_pixels": mismatch,
            "valid_outside_jalisco_pixels": valid_outside,
            "nodata_inside_jalisco_pixels": nodata_inside,
            "inherited_parent_nodata_inside_jalisco_pixels": inherited_nodata_inside,
        },
        "area": {
            "pixel_area_m2": 225.0,
            "valid_area_m2": raster_area_m2,
            "valid_area_ha": raster_area_m2 / 10_000,
            "valid_area_km2": raster_area_m2 / 1_000_000,
            "vector_area_km2": vector_area_m2 / 1_000_000,
            "raster_area_km2": raster_area_m2 / 1_000_000,
            "difference_km2": area_difference / 1_000_000,
            "difference_percent": area_difference / vector_area_m2 * 100,
            "descriptive_not_a_standalone_gate": True,
        },
        "statistics_m": statistics,
        "rasterization": {
            "rule": "pixel_center",
            "all_touched": False,
            "antialiasing": False,
        },
    }
