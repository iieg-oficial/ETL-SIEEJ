from __future__ import annotations

import math
import shlex
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any

import numpy as np
import rasterio
from rasterio.windows import Window

from core.pipelines.pendientes.constants import FINAL_NODATA, RASTER_BLOCK_SIZE
from core.pipelines.pendientes.helpers.experimental_metrics import valid_mask
from core.pipelines.pendientes.helpers.tiled_conditioning import core_tile_windows
from core.utils.files import sha256_file


def run_context_we5(
    context_dem_path: Path,
    output_path: Path,
    backend: dict[str, Any],
) -> dict[str, Any]:
    """Run the frozen GRASS Wood–Evans 5x5 estimator on the full context DEM."""
    if output_path.exists():
        raise FileExistsError(f"Context WE5 output already exists: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    partial = output_path.with_suffix(".partial.tif")
    partial.unlink(missing_ok=True)
    started = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="pendientes_we5_state_") as temporary:
        location = Path(temporary) / "location"
        commands = (
            f"r.in.gdal input={shlex.quote(str(context_dem_path.resolve()))} output=dem --overwrite",
            "g.region raster=dem",
            "r.param.scale input=dem output=we5 method=slope size=5 exponent=0 zscale=1 --overwrite",
            "r.out.gdal "
            f"input=we5 output={shlex.quote(str(partial.resolve()))} "
            "format=GTiff type=Float32 nodata=-9999 "
            f"createopt=TILED=YES,COMPRESS=DEFLATE,BLOCKXSIZE={RASTER_BLOCK_SIZE},"
            f"BLOCKYSIZE={RASTER_BLOCK_SIZE},BIGTIFF=IF_SAFER -f --overwrite",
        )
        command = [
            backend["grass_executable"],
            "-c",
            "EPSG:6368",
            str(location),
            "--exec",
            "/bin/bash",
            "-ec",
            "; ".join(commands),
        ]
        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            with rasterio.open(partial, "r+") as dataset:
                dataset.set_band_unit(1, "degree")
            partial.replace(output_path)
        except Exception:
            partial.unlink(missing_ok=True)
            raise
    return {
        "command": command,
        "method": "slope",
        "size": 5,
        "exponent": 0.0,
        "zscale": 1.0,
        "elapsed_seconds": time.perf_counter() - started,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def validate_we5_context(parent_path: Path, slope_path: Path) -> dict[str, Any]:
    valid_pixels = nodata_pixels = nonfinite = invalid_range = 0
    minimum = float("inf")
    maximum = float("-inf")
    total = total_sq = 0.0
    with rasterio.open(parent_path) as parent, rasterio.open(slope_path) as slope:
        checks = {
            "crs": slope.crs == parent.crs and slope.crs.to_epsg() == 6368,
            "resolution": slope.res == parent.res == (15.0, 15.0),
            "transform": slope.transform == parent.transform,
            "bounds": slope.bounds == parent.bounds,
            "dimensions": slope.shape == parent.shape,
            "dtype": slope.dtypes == ("float32",),
            "nodata": slope.nodata == FINAL_NODATA,
            "unit": slope.units == ("degree",),
        }
        windows = core_tile_windows(slope.shape, 2048)
        for window in windows:
            values = slope.read(1, window=window)
            selected = values[valid_mask(values, slope.nodata)].astype(np.float64)
            valid_pixels += selected.size
            nodata_pixels += values.size - selected.size
            nonfinite += int(np.count_nonzero(~np.isfinite(selected)))
            invalid_range += int(np.count_nonzero((selected < 0.0) | (selected >= 90.0)))
            minimum = min(minimum, float(selected.min(initial=float("inf"))))
            maximum = max(maximum, float(selected.max(initial=float("-inf"))))
            total += float(selected.sum())
            total_sq += float(np.square(selected).sum())
        histogram = np.zeros(100_000, dtype=np.int64)
        for window in windows:
            values = slope.read(1, window=window)
            selected = values[valid_mask(values, slope.nodata)]
            histogram += np.histogram(selected, bins=histogram.size, range=(minimum, maximum))[0]
        metadata = {
            "width": slope.width,
            "height": slope.height,
            "transform": list(slope.transform),
            "bounds": list(slope.bounds),
        }
    mean = total / valid_pixels
    cumulative = np.cumsum(histogram)
    width = (maximum - minimum) / histogram.size
    percentiles = {}
    for percentile in (1, 5, 25, 50, 75, 90, 95, 99):
        rank = max(1, math.ceil(percentile / 100 * valid_pixels))
        index = int(np.searchsorted(cumulative, rank, side="left"))
        percentiles[f"p{percentile:02d}"] = minimum + (index + 0.5) * width
    hard_gates = {
        **checks,
        "finite": nonfinite == 0,
        "valid_range": invalid_range == 0,
    }
    return {
        "metadata": metadata,
        "valid_pixels": valid_pixels,
        "nodata_pixels": nodata_pixels,
        "nonfinite_pixels": nonfinite,
        "invalid_range_pixels": invalid_range,
        "statistics": {
            "min": minimum,
            "max": maximum,
            "mean": mean,
            "std": math.sqrt(max(0.0, total_sq / valid_pixels - mean * mean)),
            **percentiles,
            "percentile_method": "100000-bin all-valid-pixel histogram",
        },
        "hard_gates": {**hard_gates, "all_passed": all(hard_gates.values())},
    }


def verify_eight_we5_chips(
    statewide_path: Path,
    phase8a1_manifest: dict[str, Any],
    phase8a1_directory: Path,
) -> dict[str, Any]:
    exact = different = compared = 0
    maximum = 0.0
    results: dict[str, Any] = {}
    with rasterio.open(statewide_path) as statewide:
        for chip in phase8a1_manifest["real_chip_sample"]:
            chip_id = chip["chip_id"]
            if "row_offset" in chip:
                row = int(chip["row_offset"])
                column = int(chip["column_offset"])
            else:
                center_row, center_column = statewide.index(chip["center_x"], chip["center_y"])
                row, column = center_row - 512, center_column - 512
            observed = statewide.read(1, window=Window(column, row, 1024, 1024))
            reference_path = phase8a1_directory / "chips" / chip_id / "WE5.tif"
            with rasterio.open(reference_path) as reference:
                expected = reference.read(1)
            mismatch = observed.view(np.uint32) != expected.view(np.uint32)
            count = int(np.count_nonzero(mismatch))
            common = valid_mask(observed, FINAL_NODATA) & valid_mask(expected, FINAL_NODATA)
            difference = np.abs(observed[common].astype(np.float64) - expected[common].astype(np.float64))
            chip_maximum = float(difference.max(initial=0.0))
            exact += int(count == 0)
            different += count
            compared += observed.size
            maximum = max(maximum, chip_maximum)
            results[chip_id] = {
                "reference_path": str(reference_path),
                "reference_sha256": sha256_file(reference_path),
                "compared_pixels": observed.size,
                "different_pixels": count,
                "max_abs_difference": chip_maximum,
                "exact": count == 0,
            }
    hard_gates = {
        "chip_count": len(results) == 8,
        "exact_chip_count": exact == 8,
        "different_pixels": different == 0,
        "max_abs_difference": maximum == 0.0,
    }
    return {
        "chip_count": len(results),
        "exact_chip_count": exact,
        "compared_pixels": compared,
        "different_pixels": different,
        "max_abs_difference": maximum,
        "chips": results,
        "hard_gates": {**hard_gates, "all_passed": all(hard_gates.values())},
    }


def compare_statewide_slopes(reference_path: Path, selected_path: Path) -> dict[str, Any]:
    count = 0
    total = total_sq = total_abs = 0.0
    maximum = 0.0
    thresholds = {value: 0 for value in (0.1, 0.5, 1.0, 2.0)}
    absolute_maximum = 0.0
    with rasterio.open(reference_path) as reference, rasterio.open(selected_path) as selected:
        if reference.shape != selected.shape or reference.transform != selected.transform:
            raise ValueError("Horn and WE5 territorial grids differ")
        windows = core_tile_windows(reference.shape, 2048)
        for window in windows:
            horn = reference.read(1, window=window)
            we5 = selected.read(1, window=window)
            common = valid_mask(horn, reference.nodata) & valid_mask(we5, selected.nodata)
            difference = we5[common].astype(np.float64) - horn[common].astype(np.float64)
            absolute = np.abs(difference)
            count += difference.size
            total += float(difference.sum())
            total_sq += float(np.square(difference).sum())
            total_abs += float(absolute.sum())
            absolute_maximum = max(absolute_maximum, float(absolute.max(initial=0.0)))
            maximum = max(maximum, float(np.abs(difference).max(initial=0.0)))
            for threshold in thresholds:
                thresholds[threshold] += int(np.count_nonzero(absolute > threshold))
        histogram = np.zeros(100_000, dtype=np.int64)
        for window in windows:
            horn = reference.read(1, window=window)
            we5 = selected.read(1, window=window)
            common = valid_mask(horn, reference.nodata) & valid_mask(we5, selected.nodata)
            absolute = np.abs(we5[common].astype(np.float64) - horn[common].astype(np.float64))
            histogram += np.histogram(absolute, bins=histogram.size, range=(0.0, absolute_maximum))[0]
    cumulative = np.cumsum(histogram)
    percentiles = {}
    width = absolute_maximum / histogram.size
    for percentile in (50, 90, 95, 99):
        rank = max(1, math.ceil(percentile / 100 * count))
        index = int(np.searchsorted(cumulative, rank, side="left"))
        percentiles[f"p{percentile}_abs_difference"] = (index + 0.5) * width
    return {
        "compared_pixels": count,
        "bias": total / count,
        "mae": total_abs / count,
        "rmse": math.sqrt(total_sq / count),
        **percentiles,
        "max_abs_difference": maximum,
        "threshold_percentages": {
            f"gt_{threshold:g}_degrees": value / count * 100 for threshold, value in thresholds.items()
        },
        "acceptance_threshold_applied": False,
    }
