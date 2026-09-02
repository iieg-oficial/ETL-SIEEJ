from __future__ import annotations

import math
import subprocess
import time
from pathlib import Path
from typing import Any

import numpy as np
import rasterio
from rasterio.windows import Window, transform as window_transform

from core.pipelines.pendientes.constants import FINAL_NODATA, RASTER_BLOCK_SIZE, SLOPE_QA_CLASSES_DEGREES
from core.pipelines.pendientes.helpers.experimental_metrics import valid_mask
from core.pipelines.pendientes.helpers.tiled_conditioning import core_tile_windows
from core.utils.files import sha256_file


def validate_frozen_backend(backend: dict[str, Any]) -> dict[str, Any]:
    executable = Path(backend["executable"])
    if not executable.is_file():
        raise FileNotFoundError(f"Frozen gdaldem executable does not exist: {executable}")
    observed_sha256 = sha256_file(executable)
    if observed_sha256 != backend["executable_sha256"]:
        raise ValueError("Frozen gdaldem executable checksum changed")
    gdalinfo = executable.with_name("gdalinfo")
    result = subprocess.run([str(gdalinfo), "--version"], check=True, capture_output=True, text=True)
    observed_version = result.stdout.strip()
    if observed_version != backend["version"]:
        raise ValueError(f"Frozen GDAL version changed: {observed_version}")
    parameters = backend["parameters"]
    if parameters != {
        "output_unit": "degree",
        "scale_xy_to_z": 1.0,
        "effective_z_factor": 1.0,
        "compute_edges": False,
    }:
        raise ValueError(f"Unexpected frozen backend parameters: {parameters}")
    if backend["algorithms"]["Horn"]["cli_value"] != "Horn":
        raise ValueError("Phase 7A did not freeze the Horn CLI value")
    return {
        "executable": str(executable),
        "executable_sha256": observed_sha256,
        "version": observed_version,
        "validated": True,
    }


def run_context_horn_slope(
    backend: dict[str, Any],
    context_dem_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    if output_path.exists():
        raise FileExistsError(f"Context slope already exists: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    partial = output_path.with_suffix(".partial.tif")
    partial.unlink(missing_ok=True)
    command = [
        backend["executable"],
        "slope",
        str(context_dem_path.resolve()),
        str(partial.resolve()),
        "-s",
        "1.0",
        "-alg",
        backend["algorithms"]["Horn"]["cli_value"],
        "-of",
        "GTiff",
        "-co",
        "TILED=YES",
        "-co",
        f"BLOCKXSIZE={RASTER_BLOCK_SIZE}",
        "-co",
        f"BLOCKYSIZE={RASTER_BLOCK_SIZE}",
        "-co",
        "COMPRESS=DEFLATE",
        "-co",
        "BIGTIFF=IF_SAFER",
        "-q",
    ]
    if "-compute_edges" in command or "-p" in command:
        raise AssertionError("Forbidden gdaldem production option")
    started = time.perf_counter()
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
        "algorithm": "Horn",
        "compute_edges": False,
        "percent_mode": False,
        "elapsed_seconds": time.perf_counter() - started,
        "return_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def validate_context_slope(context_dem_path: Path, slope_path: Path) -> dict[str, Any]:
    invalid_range = nonfinite = valid_pixels = 0
    with rasterio.open(context_dem_path) as parent, rasterio.open(slope_path) as slope:
        checks = {
            "crs": slope.crs == parent.crs and slope.crs.to_epsg() == 6368,
            "transform": slope.transform == parent.transform,
            "dimensions": slope.shape == parent.shape == (29255, 30533),
            "resolution": slope.res == parent.res == (15.0, 15.0),
            "dtype": slope.dtypes == ("float32",),
            "nodata": slope.nodata == parent.nodata == FINAL_NODATA,
            "tiled": slope.profile.get("tiled") is True,
            "block_shape": slope.block_shapes == [(RASTER_BLOCK_SIZE, RASTER_BLOCK_SIZE)],
            "compression": slope.compression is not None and slope.compression.value == "DEFLATE",
            "unit": slope.units == ("degree",),
        }
        for _, window in slope.block_windows(1):
            values = slope.read(1, window=window)
            selected = values[valid_mask(values, slope.nodata)]
            valid_pixels += selected.size
            nonfinite += int(np.count_nonzero(~np.isfinite(selected)))
            invalid_range += int(np.count_nonzero((selected < 0.0) | (selected >= 90.0)))
        edge_nodata = {
            "top": bool(np.all(slope.read(1, window=Window(0, 0, slope.width, 1)) == FINAL_NODATA)),
            "bottom": bool(np.all(slope.read(1, window=Window(0, slope.height - 1, slope.width, 1)) == FINAL_NODATA)),
            "left": bool(np.all(slope.read(1, window=Window(0, 0, 1, slope.height)) == FINAL_NODATA)),
            "right": bool(np.all(slope.read(1, window=Window(slope.width - 1, 0, 1, slope.height)) == FINAL_NODATA)),
        }
        metadata = {
            "width": slope.width,
            "height": slope.height,
            "transform": list(slope.transform),
            "bounds": list(slope.bounds),
            "resolution": list(slope.res),
            "dtype": slope.dtypes[0],
            "nodata": slope.nodata,
        }
    passed = all(checks.values()) and nonfinite == 0 and invalid_range == 0 and all(edge_nodata.values())
    return {
        "checks": checks,
        "edge_nodata": edge_nodata,
        "valid_pixels": valid_pixels,
        "nonfinite_valid_pixels": nonfinite,
        "invalid_range_pixels": invalid_range,
        "metadata": metadata,
        "passed": passed,
    }


def verify_phase7a_chips(
    context_slope_path: Path,
    inventory: dict[str, Any],
    phase7a_manifest: dict[str, Any],
) -> dict[str, Any]:
    chips = {chip["chip_id"]: chip for chip in inventory["chips"]}
    different = compared = exact = 0
    maximum = 0.0
    results = {}
    with rasterio.open(context_slope_path) as statewide:
        for chip_id, reference_record in phase7a_manifest["real_chip_results"].items():
            chip = chips[chip_id]
            window = Window(chip["column_offset"], chip["row_offset"], chip["width"], chip["height"])
            statewide_values = statewide.read(1, window=window)
            reference_path = Path(reference_record["algorithms"]["Horn"]["artifact"]["path"])
            expected_sha = reference_record["algorithms"]["Horn"]["artifact"]["sha256"]
            if sha256_file(reference_path) != expected_sha:
                raise ValueError(f"Phase 7A Horn reference checksum changed: {chip_id}")
            with rasterio.open(reference_path) as reference:
                reference_values = reference.read(1)
            mismatch = statewide_values.view(np.uint32) != reference_values.view(np.uint32)
            count = int(np.count_nonzero(mismatch))
            finite = np.isfinite(statewide_values) & np.isfinite(reference_values)
            max_difference = float(
                np.max(np.abs(statewide_values[finite].astype(np.float64) - reference_values[finite]), initial=0.0)
            )
            compared += statewide_values.size
            different += count
            maximum = max(maximum, max_difference)
            exact += int(count == 0)
            results[chip_id] = {
                "compared_pixels": statewide_values.size,
                "different_float32_pixels": count,
                "maximum_absolute_difference_degrees": max_difference,
                "exact": count == 0,
            }
    return {
        "chip_count": len(results),
        "exact_chip_count": exact,
        "compared_pixels": compared,
        "different_float32_pixels": different,
        "maximum_absolute_difference_degrees": maximum,
        "passed": len(results) == exact == 30 and different == 0 and maximum == 0.0,
        "chips": results,
    }


def slope_output_profile(master: rasterio.io.DatasetReader, unit: str) -> dict[str, Any]:
    return {
        "driver": "GTiff",
        "width": master.width,
        "height": master.height,
        "count": 1,
        "dtype": "float32",
        "crs": master.crs,
        "transform": master.transform,
        "nodata": FINAL_NODATA,
        "tiled": True,
        "blockxsize": RASTER_BLOCK_SIZE,
        "blockysize": RASTER_BLOCK_SIZE,
        "compress": "deflate",
        "BIGTIFF": "IF_SAFER",
    }


def create_territorial_degrees(
    context_slope_path: Path,
    master_dem_path: Path,
    output_path: Path,
    territorial_window: dict[str, int],
    processing_window_size: int = 2048,
) -> dict[str, Any]:
    if output_path.exists():
        raise FileExistsError(f"Territorial degree slope already exists: {output_path}")
    partial = output_path.with_suffix(".partial.tif")
    partial.unlink(missing_ok=True)
    window_offset = Window(
        territorial_window["column_offset"],
        territorial_window["row_offset"],
        territorial_window["width"],
        territorial_window["height"],
    )
    missing_context = valid_pixels = 0
    started = time.perf_counter()
    with rasterio.open(context_slope_path) as context, rasterio.open(master_dem_path) as master:
        if window_transform(window_offset, context.transform) != master.transform:
            raise ValueError("Phase 6B territorial window does not reproduce the master transform")
        profile = slope_output_profile(master, "degree")
        windows = core_tile_windows(master.shape, processing_window_size)
        try:
            with rasterio.open(partial, "w", **profile) as destination:
                destination.set_band_unit(1, "degree")
                for child_window in windows:
                    context_window = Window(
                        window_offset.col_off + child_window.col_off,
                        window_offset.row_off + child_window.row_off,
                        child_window.width,
                        child_window.height,
                    )
                    degrees = context.read(1, window=context_window)
                    master_values = master.read(1, window=child_window)
                    master_valid = valid_mask(master_values, master.nodata)
                    slope_valid = valid_mask(degrees, context.nodata)
                    missing_context += int(np.count_nonzero(master_valid & ~slope_valid))
                    valid_pixels += int(np.count_nonzero(master_valid))
                    output = np.where(master_valid & slope_valid, degrees, FINAL_NODATA).astype(np.float32)
                    destination.write(output, 1, window=child_window)
            if missing_context:
                raise ValueError(f"Context slope has {missing_context} NoData pixels inside Jalisco")
            partial.replace(output_path)
        except Exception:
            partial.unlink(missing_ok=True)
            raise
    return {
        "territorial_window": territorial_window,
        "processing_window_size_pixels": processing_window_size,
        "processing_window_count": len(windows),
        "valid_pixels_written": valid_pixels,
        "missing_context_inside_master_mask": missing_context,
        "elapsed_seconds": time.perf_counter() - started,
    }


def percent_from_degrees(values: np.ndarray) -> np.ndarray:
    return (np.tan(np.radians(values.astype(np.float64))) * 100.0).astype(np.float32)


def create_territorial_percent(
    degrees_path: Path,
    output_path: Path,
    processing_window_size: int = 2048,
) -> dict[str, Any]:
    if output_path.exists():
        raise FileExistsError(f"Territorial percent slope already exists: {output_path}")
    partial = output_path.with_suffix(".partial.tif")
    partial.unlink(missing_ok=True)
    started = time.perf_counter()
    valid_pixels = 0
    with rasterio.open(degrees_path) as degrees:
        profile = slope_output_profile(degrees, "percent")
        windows = core_tile_windows(degrees.shape, processing_window_size)
        try:
            with rasterio.open(partial, "w", **profile) as destination:
                destination.set_band_unit(1, "percent")
                for window in windows:
                    values = degrees.read(1, window=window)
                    selected = valid_mask(values, degrees.nodata)
                    valid_pixels += int(np.count_nonzero(selected))
                    output = np.full(values.shape, FINAL_NODATA, dtype=np.float32)
                    output[selected] = percent_from_degrees(values[selected])
                    destination.write(output, 1, window=window)
            partial.replace(output_path)
        except Exception:
            partial.unlink(missing_ok=True)
            raise
    return {
        "source": str(degrees_path),
        "formula": "float32(tan(radians(float64(degrees))) * 100)",
        "processing_window_size_pixels": processing_window_size,
        "processing_window_count": len(windows),
        "valid_pixels_written": valid_pixels,
        "elapsed_seconds": time.perf_counter() - started,
    }


def _percentiles_from_histogram(
    histogram: np.ndarray,
    minimum: float,
    maximum: float,
    percentiles: tuple[int, ...],
) -> dict[str, float]:
    total = int(histogram.sum())
    cumulative = np.cumsum(histogram)
    width = (maximum - minimum) / histogram.size if maximum > minimum else 0.0
    output = {}
    for percentile in percentiles:
        rank = max(1, math.ceil(percentile / 100.0 * total))
        index = int(np.searchsorted(cumulative, rank, side="left"))
        output[f"p{percentile:02d}"] = minimum + (index + 0.5) * width if width else minimum
    return output


def validate_slope_family(
    master_dem_path: Path,
    degrees_path: Path,
    percent_path: Path,
    histogram_bins: int = 100_000,
    expected_valid_pixels: int = 356_528_880,
) -> dict[str, Any]:
    counts = {"valid": 0, "mask_mismatch_degrees": 0, "mask_mismatch_percent": 0}
    sums = {"degrees": 0.0, "degrees_sq": 0.0, "percent": 0.0, "percent_sq": 0.0}
    minima = {"degrees": float("inf"), "percent": float("inf")}
    maxima = {"degrees": float("-inf"), "percent": float("-inf")}
    nonfinite = invalid_degrees = pct_gt_100 = relation_different = 0
    below_45_mismatch = equal_45_mismatch = above_45_mismatch = 0
    relation_max_abs = relation_max_relative = 0.0
    class_counts = [0 for _ in SLOPE_QA_CLASSES_DEGREES]
    with (
        rasterio.open(master_dem_path) as master,
        rasterio.open(degrees_path) as degrees,
        rasterio.open(percent_path) as percent,
    ):
        expected_common = {
            "crs": degrees.crs == percent.crs == master.crs and master.crs.to_epsg() == 6368,
            "dimensions": degrees.shape == percent.shape == master.shape,
            "transform": degrees.transform == percent.transform == master.transform,
            "bounds": degrees.bounds == percent.bounds == master.bounds,
            "resolution": degrees.res == percent.res == master.res == (15.0, 15.0),
            "dtype": degrees.dtypes == percent.dtypes == master.dtypes == ("float32",),
            "nodata": degrees.nodata == percent.nodata == master.nodata == FINAL_NODATA,
            "degree_unit": degrees.units == ("degree",),
            "percent_unit": percent.units == ("percent",),
            "tiled": degrees.profile.get("tiled") is True and percent.profile.get("tiled") is True,
            "block_shape": degrees.block_shapes == percent.block_shapes == [(RASTER_BLOCK_SIZE, RASTER_BLOCK_SIZE)],
            "compression": (
                degrees.compression is not None
                and percent.compression is not None
                and degrees.compression.value == percent.compression.value == "DEFLATE"
            ),
        }
        windows = [window for _, window in master.block_windows(1)]
        for window in windows:
            dem_values = master.read(1, window=window)
            degree_values = degrees.read(1, window=window)
            percent_values = percent.read(1, window=window)
            master_valid = valid_mask(dem_values, master.nodata)
            degree_valid = valid_mask(degree_values, degrees.nodata)
            percent_valid = valid_mask(percent_values, percent.nodata)
            counts["mask_mismatch_degrees"] += int(np.count_nonzero(master_valid ^ degree_valid))
            counts["mask_mismatch_percent"] += int(np.count_nonzero(master_valid ^ percent_valid))
            selected = master_valid & degree_valid & percent_valid
            degree_selected = degree_values[selected]
            percent_selected = percent_values[selected]
            counts["valid"] += degree_selected.size
            nonfinite += int(np.count_nonzero(~np.isfinite(degree_selected)))
            nonfinite += int(np.count_nonzero(~np.isfinite(percent_selected)))
            invalid_degrees += int(np.count_nonzero((degree_selected < 0.0) | (degree_selected >= 90.0)))
            pct_gt_100 += int(np.count_nonzero(percent_selected > 100.0))
            below_45_mismatch += int(np.count_nonzero((degree_selected < 45.0) & ~(percent_selected < 100.0)))
            equal_45_mismatch += int(np.count_nonzero((degree_selected == 45.0) & (percent_selected != 100.0)))
            above_45_mismatch += int(np.count_nonzero((degree_selected > 45.0) & ~(percent_selected > 100.0)))
            expected_pct = percent_from_degrees(degree_selected)
            mismatch = expected_pct.view(np.uint32) != percent_selected.view(np.uint32)
            relation_different += int(np.count_nonzero(mismatch))
            absolute = np.abs(expected_pct.astype(np.float64) - percent_selected.astype(np.float64))
            relation_max_abs = max(relation_max_abs, float(absolute.max(initial=0.0)))
            denominator = np.maximum(np.abs(expected_pct.astype(np.float64)), np.finfo(np.float32).tiny)
            relation_max_relative = max(relation_max_relative, float((absolute / denominator).max(initial=0.0)))
            for name, values in (("degrees", degree_selected), ("percent", percent_selected)):
                as_float64 = values.astype(np.float64)
                sums[name] += float(as_float64.sum())
                sums[f"{name}_sq"] += float(np.square(as_float64).sum())
                minima[name] = min(minima[name], float(as_float64.min(initial=float("inf"))))
                maxima[name] = max(maxima[name], float(as_float64.max(initial=float("-inf"))))
            for index, (lower, upper) in enumerate(SLOPE_QA_CLASSES_DEGREES):
                mask = degree_selected > lower if upper is None else degree_selected >= lower
                if upper == 45.0:
                    mask &= degree_selected <= upper
                elif upper is not None:
                    mask &= degree_selected < upper
                class_counts[index] += int(np.count_nonzero(mask))
        histograms = {
            "degrees": np.zeros(histogram_bins, dtype=np.int64),
            "percent": np.zeros(histogram_bins, dtype=np.int64),
        }
        for window in windows:
            for name, dataset in (("degrees", degrees), ("percent", percent)):
                values = dataset.read(1, window=window)
                selected = values[valid_mask(values, dataset.nodata)]
                histograms[name] += np.histogram(selected, bins=histogram_bins, range=(minima[name], maxima[name]))[0]
        metadata = {
            "width": master.width,
            "height": master.height,
            "transform": list(master.transform),
            "bounds": list(master.bounds),
            "resolution": list(master.res),
        }
    statistics = {}
    for name in ("degrees", "percent"):
        mean = sums[name] / counts["valid"]
        statistics[name] = {
            "minimum": minima[name],
            "maximum": maxima[name],
            "mean": mean,
            "stddev": math.sqrt(max(0.0, sums[f"{name}_sq"] / counts["valid"] - mean * mean)),
            **_percentiles_from_histogram(histograms[name], minima[name], maxima[name], (1, 5, 25, 50, 75, 90, 95, 99)),
            "percentile_method": {
                "name": "all-valid-pixel fixed-width histogram",
                "bins": histogram_bins,
                "precision": (maxima[name] - minima[name]) / histogram_bins,
            },
        }
    class_labels = [
        f"{lower:g}-{upper:g}_degrees" if upper is not None else f"gt_{lower:g}_degrees"
        for lower, upper in SLOPE_QA_CLASSES_DEGREES
    ]
    hard_gates = {
        "common_grid": all(expected_common.values()),
        "valid_pixels": counts["valid"] == expected_valid_pixels,
        "degree_mask_equals_master": counts["mask_mismatch_degrees"] == 0,
        "percent_mask_equals_master": counts["mask_mismatch_percent"] == 0,
        "finite": nonfinite == 0,
        "degree_range": invalid_degrees == 0,
        "percent_relation_bitwise": relation_different == 0,
        "degree_percent_threshold_semantics": (below_45_mismatch == equal_45_mismatch == above_45_mismatch == 0),
    }
    return {
        "grid": {"checks": expected_common, "metadata": metadata},
        "mask": {
            "valid_pixels": counts["valid"],
            "degree_mask_mismatch_pixels": counts["mask_mismatch_degrees"],
            "percent_mask_mismatch_pixels": counts["mask_mismatch_percent"],
            "valid_outside_jalisco_pixels": 0 if counts["mask_mismatch_degrees"] == 0 else None,
            "nodata_inside_jalisco_pixels": 0 if counts["mask_mismatch_degrees"] == 0 else None,
        },
        "degrees_qa": {
            "nonfinite_valid_pixels": nonfinite,
            "invalid_range_pixels": invalid_degrees,
            "classes": {
                label: {"pixels": count, "percentage": count / counts["valid"] * 100.0}
                for label, count in zip(class_labels, class_counts, strict=True)
            },
        },
        "percent_qa": {
            "pixels_gt_100": pct_gt_100,
            "percentage_pixels_gt_100": pct_gt_100 / counts["valid"] * 100.0,
            "threshold_semantics": {
                "degrees_lt_45_not_percent_lt_100": below_45_mismatch,
                "degrees_eq_45_not_percent_eq_100": equal_45_mismatch,
                "degrees_gt_45_not_percent_gt_100": above_45_mismatch,
            },
        },
        "degrees_percent_relation": {
            "formula": "float32(tan(radians(float64(degrees))) * 100)",
            "compared_pixels": counts["valid"],
            "different_float32_pixels": relation_different,
            "maximum_absolute_difference": relation_max_abs,
            "maximum_relative_difference": relation_max_relative,
        },
        "statistics": statistics,
        "hard_gates": {**hard_gates, "all_passed": all(hard_gates.values())},
    }
