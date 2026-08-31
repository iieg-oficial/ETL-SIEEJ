from __future__ import annotations

import math
import resource
import tempfile
import time
from pathlib import Path
from typing import Any

import numpy as np
import rasterio
from rasterio.windows import Window, transform as window_transform

from core.pipelines.pendientes.constants import FINAL_NODATA, RASTER_BLOCK_SIZE
from core.pipelines.pendientes.helpers.experimental_artifacts import write_float_raster
from core.pipelines.pendientes.helpers.experimental_metrics import valid_mask
from core.pipelines.pendientes.helpers.experimental_whitebox import run_feature_preserving_smoothing
from core.pipelines.pendientes.helpers.tiled_conditioning import core_tile_windows, expanded_window


def output_raster_profile(source: rasterio.io.DatasetReader) -> dict[str, Any]:
    return {
        "driver": "GTiff",
        "width": source.width,
        "height": source.height,
        "count": 1,
        "dtype": "float32",
        "crs": source.crs,
        "transform": source.transform,
        "nodata": FINAL_NODATA,
        "tiled": True,
        "blockxsize": RASTER_BLOCK_SIZE,
        "blockysize": RASTER_BLOCK_SIZE,
        "compress": "deflate",
        "BIGTIFF": "IF_SAFER",
    }


def mask_preserving_core(
    source_context: np.ndarray,
    filtered_context: np.ndarray,
    core: Window,
    context: Window,
    nodata: float,
) -> tuple[np.ndarray, dict[str, int]]:
    row = int(core.row_off - context.row_off)
    column = int(core.col_off - context.col_off)
    height = int(core.height)
    width = int(core.width)
    source = source_context[row : row + height, column : column + width]
    filtered = filtered_context[row : row + height, column : column + width]
    source_valid = valid_mask(source, nodata)
    filtered_valid = valid_mask(filtered, nodata)
    mismatch = source_valid ^ filtered_valid
    output = np.where(source_valid & filtered_valid, filtered, nodata).astype(np.float32)
    return output, {
        "valid_pixels_baseline": int(np.count_nonzero(source_valid)),
        "valid_pixels_whitebox": int(np.count_nonzero(filtered_valid)),
        "mask_mismatch_pixels_before_enforcement": int(np.count_nonzero(mismatch)),
        "valid_pixels_conditioned": int(np.count_nonzero(valid_mask(output, nodata))),
    }


def condition_raster_tiled(
    source_path: Path,
    output_path: Path,
    backend: dict[str, Any],
    configuration: dict[str, Any],
    tile_size: int,
    halo: int,
) -> dict[str, Any]:
    started = time.perf_counter()
    partial = output_path.with_suffix(".partial.tif")
    partial.unlink(missing_ok=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    counts = {
        "valid_pixels_baseline": 0,
        "valid_pixels_whitebox": 0,
        "mask_mismatch_pixels_before_enforcement": 0,
        "valid_pixels_conditioned": 0,
    }
    whitebox_seconds = 0.0
    with rasterio.open(source_path) as source:
        windows = core_tile_windows(source.shape, tile_size)
        with rasterio.open(partial, "w", **output_raster_profile(source)) as destination:
            with tempfile.TemporaryDirectory(prefix="pendientes_6a_tile_", dir=output_path.parent) as temporary:
                work = Path(temporary)
                for index, core in enumerate(windows):
                    context = expanded_window(core, source.shape, halo)
                    source_context = source.read(1, window=context)
                    tile_input = write_float_raster(
                        work / "input.tif",
                        source_context,
                        valid_mask(source_context, source.nodata),
                        window_transform(context, source.transform),
                        source.crs,
                    )
                    tile_output = work / "output.tif"
                    execution = run_feature_preserving_smoothing(
                        backend,
                        tile_input,
                        tile_output,
                        configuration,
                    )
                    whitebox_seconds += float(execution["elapsed_seconds"])
                    with rasterio.open(tile_output) as filtered_dataset:
                        filtered_context = filtered_dataset.read(1)
                    core_values, tile_counts = mask_preserving_core(
                        source_context,
                        filtered_context,
                        core,
                        context,
                        float(source.nodata),
                    )
                    destination.write(core_values, 1, window=core)
                    for key, value in tile_counts.items():
                        counts[key] += value
                    if index == 0 or (index + 1) % 10 == 0 or index + 1 == len(windows):
                        print(f"Phase 6A tile {index + 1}/{len(windows)}", flush=True)
        partial.replace(output_path)
    total_pixels = sum(int(window.width * window.height) for window in windows)
    counts["nodata_pixels_baseline"] = total_pixels - counts["valid_pixels_baseline"]
    counts["nodata_pixels_conditioned"] = total_pixels - counts["valid_pixels_conditioned"]
    counts["mask_mismatch_pixels"] = (
        counts["valid_pixels_baseline"] - counts["valid_pixels_conditioned"]
    )
    return {
        "tile_width_pixels": tile_size,
        "tile_height_pixels": tile_size,
        "halo_pixels": halo,
        "tile_count": len(windows),
        "processing_order": "row_major_top_to_bottom_left_to_right",
        "whitebox_elapsed_seconds": whitebox_seconds,
        "elapsed_seconds": time.perf_counter() - started,
        "max_rss_kib": int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss),
        "mask": counts,
    }


def validate_matching_grid(source: rasterio.io.DatasetReader, candidate: rasterio.io.DatasetReader) -> dict[str, Any]:
    checks = {
        "shape": source.shape == candidate.shape,
        "transform": source.transform == candidate.transform,
        "crs": source.crs == candidate.crs,
        "resolution": source.res == candidate.res,
        "dtype": candidate.dtypes == ("float32",),
        "nodata": candidate.nodata == FINAL_NODATA,
    }
    return {"checks": checks, "passed": all(checks.values())}


def _moments(values: np.ndarray) -> tuple[int, float, float, float, float]:
    selected = values.astype(np.float64, copy=False)
    return selected.size, float(selected.sum()), float(np.square(selected).sum()), float(selected.min()), float(selected.max())


def _percentiles_from_histogram(
    counts: np.ndarray,
    minimum: float,
    maximum: float,
    percentiles: tuple[int, ...],
) -> dict[str, float]:
    total = int(counts.sum())
    if total == 0:
        raise ValueError("Cannot calculate percentiles from an empty histogram")
    cumulative = np.cumsum(counts)
    width = (maximum - minimum) / counts.size if maximum > minimum else 0.0
    result = {}
    for percentile in percentiles:
        rank = max(1, math.ceil(percentile / 100 * total))
        index = int(np.searchsorted(cumulative, rank, side="left"))
        result[f"p{percentile:02d}"] = float(minimum + (index + 0.5) * width) if width else minimum
    return result


def streaming_global_qa(
    source_path: Path,
    candidate_path: Path,
    histogram_bins: int = 100_000,
    analysis_window_size: int = 2048,
) -> dict[str, Any]:
    count = 0
    delta_sum = delta_square_sum = abs_sum = 0.0
    source_sum = source_square_sum = candidate_sum = candidate_square_sum = 0.0
    source_min = candidate_min = float("inf")
    source_max = candidate_max = float("-inf")
    maximum_absolute = 0.0
    thresholds = {0.10: 0, 0.25: 0, 0.50: 0}
    valid_baseline = valid_candidate = mask_mismatch = 0
    with rasterio.open(source_path) as source, rasterio.open(candidate_path) as candidate:
        grid = validate_matching_grid(source, candidate)
        if not grid["passed"]:
            raise ValueError("Statewide candidate grid differs from baseline")
        for window in core_tile_windows(source.shape, analysis_window_size):
            raw = source.read(1, window=window)
            conditioned = candidate.read(1, window=window)
            raw_valid = valid_mask(raw, source.nodata)
            candidate_valid = valid_mask(conditioned, candidate.nodata)
            common = raw_valid & candidate_valid
            valid_baseline += int(np.count_nonzero(raw_valid))
            valid_candidate += int(np.count_nonzero(candidate_valid))
            mask_mismatch += int(np.count_nonzero(raw_valid ^ candidate_valid))
            raw_values = raw[common].astype(np.float64)
            candidate_values = conditioned[common].astype(np.float64)
            difference = candidate_values - raw_values
            absolute = np.abs(difference)
            if difference.size == 0:
                continue
            count += difference.size
            delta_sum += float(difference.sum())
            delta_square_sum += float(np.square(difference).sum())
            abs_sum += float(absolute.sum())
            source_sum += float(raw_values.sum())
            source_square_sum += float(np.square(raw_values).sum())
            candidate_sum += float(candidate_values.sum())
            candidate_square_sum += float(np.square(candidate_values).sum())
            source_min = min(source_min, float(raw_values.min()))
            source_max = max(source_max, float(raw_values.max()))
            candidate_min = min(candidate_min, float(candidate_values.min()))
            candidate_max = max(candidate_max, float(candidate_values.max()))
            maximum_absolute = max(maximum_absolute, float(absolute.max(initial=0.0)))
            for threshold in thresholds:
                thresholds[threshold] += int(np.count_nonzero(absolute > threshold))
    abs_hist = np.zeros(histogram_bins, dtype=np.int64)
    source_hist = np.zeros(histogram_bins, dtype=np.int64)
    candidate_hist = np.zeros(histogram_bins, dtype=np.int64)
    abs_range_max = max(maximum_absolute, np.finfo(np.float32).eps)
    elevation_min = min(source_min, candidate_min)
    elevation_max = max(source_max, candidate_max)
    with rasterio.open(source_path) as source, rasterio.open(candidate_path) as candidate:
        for window in core_tile_windows(source.shape, analysis_window_size):
            raw = source.read(1, window=window)
            conditioned = candidate.read(1, window=window)
            common = valid_mask(raw, source.nodata) & valid_mask(conditioned, candidate.nodata)
            raw_values = raw[common]
            candidate_values = conditioned[common]
            abs_hist += np.histogram(np.abs(candidate_values.astype(np.float64) - raw_values), bins=histogram_bins, range=(0, abs_range_max))[0]
            source_hist += np.histogram(raw_values, bins=histogram_bins, range=(elevation_min, elevation_max))[0]
            candidate_hist += np.histogram(candidate_values, bins=histogram_bins, range=(elevation_min, elevation_max))[0]

    def distribution(total: float, squares: float, minimum: float, maximum: float, histogram: np.ndarray) -> dict[str, float]:
        mean = total / count
        return {
            "minimum": minimum,
            "maximum": maximum,
            "mean": mean,
            "stddev": float(math.sqrt(max(0.0, squares / count - mean * mean))),
            **_percentiles_from_histogram(histogram, elevation_min, elevation_max, (1, 5, 25, 50, 75, 95, 99)),
        }

    return {
        "common_valid_pixels": count,
        "valid_pixels": {
            "baseline": valid_baseline,
            "candidate": valid_candidate,
            "mask_mismatch": mask_mismatch,
        },
        "bias_m": delta_sum / count,
        "mae_m": abs_sum / count,
        "rmse_m": math.sqrt(delta_square_sum / count),
        "absolute_difference_m": {
            **_percentiles_from_histogram(abs_hist, 0.0, abs_range_max, (50, 75, 90, 95, 99)),
            "maximum": maximum_absolute,
        },
        "threshold_percentages": {
            f"abs_change_gt_{threshold:.2f}_m": value / count * 100 for threshold, value in thresholds.items()
        },
        "elevation_distribution_m": {
            "baseline": distribution(source_sum, source_square_sum, source_min, source_max, source_hist),
            "conditioned": distribution(candidate_sum, candidate_square_sum, candidate_min, candidate_max, candidate_hist),
        },
        "percentile_method": {
            "name": "all-valid-pixel fixed-width histogram",
            "bins": histogram_bins,
            "absolute_precision_m": abs_range_max / histogram_bins,
            "elevation_precision_m": (elevation_max - elevation_min) / histogram_bins,
        },
    }


def seam_qa(source_path: Path, candidate_path: Path, tile_size: int) -> dict[str, Any]:
    records = []
    with rasterio.open(source_path) as source, rasterio.open(candidate_path) as candidate:
        specifications = [
            *(('vertical', position) for position in range(tile_size, source.width, tile_size)),
            *(('horizontal', position) for position in range(tile_size, source.height, tile_size)),
        ]
        for orientation, position in specifications:
            window = (
                Window(position - 2, 0, 4, source.height)
                if orientation == "vertical"
                else Window(0, position - 2, source.width, 4)
            )
            raw = source.read(1, window=window).astype(np.float64)
            conditioned = candidate.read(1, window=window).astype(np.float64)
            raw_valid = valid_mask(raw, source.nodata)
            candidate_valid = valid_mask(conditioned, candidate.nodata)
            if orientation == "horizontal":
                raw = raw.T
                conditioned = conditioned.T
                raw_valid = raw_valid.T
                candidate_valid = candidate_valid.T
            valid = raw_valid & candidate_valid
            pair = valid[:, 1] & valid[:, 2]
            triplet = valid[:, 0] & valid[:, 1] & valid[:, 2]
            delta = conditioned - raw
            continuity = np.abs(delta[:, 2] - delta[:, 1])[pair]
            gradient = np.abs((conditioned[:, 2] - conditioned[:, 1]) - (raw[:, 2] - raw[:, 1]))[pair]
            second = np.abs(
                (conditioned[:, 2] - 2 * conditioned[:, 1] + conditioned[:, 0])
                - (raw[:, 2] - 2 * raw[:, 1] + raw[:, 0])
            )[triplet]
            records.append(
                {
                    "orientation": orientation,
                    "pixel_position": position,
                    "valid_pairs": int(pair.sum()),
                    "max_abs_difference_across_expected_continuity": float(continuity.max(initial=0.0)),
                    "gradient_discontinuity": {
                        "mean": float(gradient.mean()) if gradient.size else 0.0,
                        "p95": float(np.percentile(gradient, 95)) if gradient.size else 0.0,
                        "maximum": float(gradient.max(initial=0.0)),
                    },
                    "second_difference_anomaly": {
                        "mean": float(second.mean()) if second.size else 0.0,
                        "p95": float(np.percentile(second, 95)) if second.size else 0.0,
                        "maximum": float(second.max(initial=0.0)),
                    },
                }
            )
    return {
        "seam_count": len(records),
        "records": records,
        "aggregate": {
            key: {
                "median": float(np.median([record[key]["mean"] for record in records])),
                "p95": float(np.percentile([record[key]["p95"] for record in records], 95)),
                "maximum": float(max(record[key]["maximum"] for record in records)),
            }
            for key in ("gradient_discontinuity", "second_difference_anomaly")
        },
        "interpretation": "Metrics are changes relative to baseline across every real tile boundary; chip equivalence is the causal seam test.",
    }
