from __future__ import annotations

import math
import time
from pathlib import Path
from typing import Any

import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.transform import from_origin
from rasterio.vrt import WarpedVRT
from rasterio.warp import transform_bounds
from rasterio.windows import Window, bounds as window_bounds, from_bounds

from core.pipelines.pendientes.constants import FINAL_DTYPE, FINAL_NODATA, RASTER_BLOCK_SIZE, SUPPORTED_SOURCE_DTYPES
from core.pipelines.pendientes.schemas import RasterMetadata

RASTERIO_TO_GDAL_DTYPE = {
    "uint8": "Byte",
    "int16": "Int16",
    "uint16": "UInt16",
    "int32": "Int32",
    "uint32": "UInt32",
    "float32": "Float32",
    "float64": "Float64",
}


def band_statistics(
    dataset: rasterio.io.DatasetReader,
    band_index: int,
    max_cells: int,
) -> dict[str, Any]:
    """Calculate bounded-memory sampled statistics without mutating source metadata."""
    block_height, block_width = dataset.block_shapes[band_index - 1]
    block_rows = math.ceil(dataset.height / block_height)
    block_columns = math.ceil(dataset.width / block_width)
    total_blocks = block_rows * block_columns
    maximum_blocks = max(1, max_cells // (block_width * block_height))
    block_stride = max(1, math.ceil(math.sqrt(total_blocks / maximum_blocks)))
    count = 0
    nodata_count = 0
    value_sum = 0.0
    square_sum = 0.0
    minimum = math.inf
    maximum = -math.inf
    sampled_cells = 0
    sampled_blocks = 0
    for block_row in range(0, block_rows, block_stride):
        row_offset = block_row * block_height
        rows = min(block_height, dataset.height - row_offset)
        for block_column in range(0, block_columns, block_stride):
            column_offset = block_column * block_width
            columns = min(block_width, dataset.width - column_offset)
            window = Window(column_offset, row_offset, columns, rows)
            sampled = dataset.read(band_index, window=window, masked=True)
            sampled_blocks += 1
            sampled_cells += sampled.size
            values = sampled.compressed().astype(np.float64, copy=False)
            values = values[np.isfinite(values)]
            nodata_count += int(sampled.size - values.size)
            if not values.size:
                continue
            count += int(values.size)
            value_sum += float(values.sum())
            square_sum += float(np.square(values).sum())
            minimum = min(minimum, float(values.min()))
            maximum = max(maximum, float(values.max()))
    if not count:
        return {
            "sampled": block_stride > 1,
            "sampling_strategy": "systematic native-block sample",
            "block_stride": block_stride,
            "sampled_blocks": sampled_blocks,
            "total_blocks": total_blocks,
            "sampled_cells": sampled_cells,
            "valid_count": 0,
            "nodata_count": nodata_count,
            "min": None,
            "max": None,
            "mean": None,
            "stddev": None,
        }
    mean = value_sum / count
    variance = max(0.0, square_sum / count - mean * mean)
    return {
        "sampled": block_stride > 1,
        "sampling_strategy": "systematic native-block sample",
        "block_stride": block_stride,
        "sampled_blocks": sampled_blocks,
        "total_blocks": total_blocks,
        "sampled_cells": sampled_cells,
        "valid_count": count,
        "nodata_count": nodata_count,
        "min": minimum,
        "max": maximum,
        "mean": mean,
        "stddev": math.sqrt(variance),
    }


def inspect_raster(path: Path, max_cells: int = 5_000_000) -> RasterMetadata:
    try:
        with rasterio.open(path, "r") as dataset:
            if dataset.transform.b or dataset.transform.d:
                raise ValueError("Rotated/skewed source grids are not admitted")
            crs_wkt = dataset.crs.to_wkt() if dataset.crs else ""
            return RasterMetadata(
                path=str(path),
                driver=dataset.driver,
                crs_wkt=crs_wkt,
                epsg=dataset.crs.to_epsg() if dataset.crs else None,
                pixel_size=(abs(float(dataset.transform.a)), abs(float(dataset.transform.e))),
                extent=(dataset.bounds.left, dataset.bounds.bottom, dataset.bounds.right, dataset.bounds.top),
                width=dataset.width,
                height=dataset.height,
                band_count=dataset.count,
                data_types=tuple(RASTERIO_TO_GDAL_DTYPE.get(dtype, dtype) for dtype in dataset.dtypes),
                nodata=tuple(dataset.nodatavals),
                z_units=tuple(dataset.units),
                compression=dataset.compression.name if dataset.compression else None,
                block_shapes=tuple(dataset.block_shapes),
                tiled=bool(dataset.profile.get("tiled", False)),
                statistics={
                    f"band_{index}": band_statistics(dataset, index, max_cells) for index in range(1, dataset.count + 1)
                },
            )
    except rasterio.errors.RasterioIOError as exc:
        raise ValueError(f"GDAL/rasterio could not open raster: {path}") from exc


def validate_source_contract(
    metadata: RasterMetadata,
    expected_bands: int = 1,
    allowed_srids: tuple[int, ...] = (),
    expected_dtype: str | None = None,
    expected_nodata: float | None = None,
    expected_pixel_size: float | None = None,
    pixel_size_tolerance: float = 1e-10,
) -> None:
    errors: list[str] = []
    if not metadata.crs_wkt:
        errors.append("missing CRS")
    if allowed_srids and metadata.epsg not in allowed_srids:
        errors.append(f"EPSG {metadata.epsg} is not in admitted SRIDs {allowed_srids}")
    if metadata.band_count != expected_bands:
        errors.append(f"expected {expected_bands} band(s), found {metadata.band_count}")
    if expected_dtype is not None and metadata.data_types != (expected_dtype,):
        errors.append(f"expected dtype {expected_dtype}, found {metadata.data_types}")
    if expected_nodata is not None and (
        len(metadata.nodata) != expected_bands
        or any(value is None or not math.isclose(value, expected_nodata, abs_tol=0.0) for value in metadata.nodata)
    ):
        errors.append(f"expected NoData {expected_nodata}, found {metadata.nodata}")
    unsupported = sorted(set(metadata.data_types) - set(SUPPORTED_SOURCE_DTYPES))
    if unsupported:
        errors.append(f"unsupported data types: {unsupported}")
    if metadata.width <= 0 or metadata.height <= 0:
        errors.append("non-positive raster dimensions")
    if any(not math.isfinite(value) or value <= 0 for value in metadata.pixel_size):
        errors.append(f"invalid pixel size {metadata.pixel_size}")
    if expected_pixel_size is not None and any(
        not math.isclose(value, expected_pixel_size, rel_tol=0.0, abs_tol=pixel_size_tolerance)
        for value in metadata.pixel_size
    ):
        errors.append(
            f"expected pixel size approximately {expected_pixel_size}, found {metadata.pixel_size} "
            f"(absolute tolerance {pixel_size_tolerance})"
        )
    if all(stats["valid_count"] == 0 for stats in metadata.statistics.values()):
        errors.append("raster contains no valid sampled elevation cells")
    if errors:
        raise ValueError("CEM source contract failed: " + "; ".join(errors))


def source_window_for_target_bounds(
    source: rasterio.io.DatasetReader,
    target_srid: int,
    target_bounds: tuple[float, float, float, float],
    kernel_margin_pixels: int = 2,
) -> tuple[Window, tuple[float, float, float, float]]:
    if source.crs is None:
        raise ValueError("Cannot determine a source window without CRS")
    source_bounds = transform_bounds(
        f"EPSG:{target_srid}",
        source.crs,
        *target_bounds,
        densify_pts=21,
    )
    fractional = from_bounds(*source_bounds, transform=source.transform)
    column_start = max(0, math.floor(fractional.col_off) - kernel_margin_pixels)
    row_start = max(0, math.floor(fractional.row_off) - kernel_margin_pixels)
    column_stop = min(source.width, math.ceil(fractional.col_off + fractional.width) + kernel_margin_pixels)
    row_stop = min(source.height, math.ceil(fractional.row_off + fractional.height) + kernel_margin_pixels)
    if column_start >= column_stop or row_start >= row_stop:
        raise ValueError("Target AOI does not overlap the CEM source")
    window = Window(column_start, row_start, column_stop - column_start, row_stop - row_start)
    return window, tuple(float(value) for value in window_bounds(window, source.transform))


def reproject_dem(
    source_path: Path,
    destination_path: Path,
    target_srid: int,
    resolution: float,
    aligned_bounds: tuple[float, float, float, float],
    nodata: float = FINAL_NODATA,
) -> dict[str, object]:
    started = time.perf_counter()
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = destination_path.with_suffix(".tmp.tif")
    temporary_path.unlink(missing_ok=True)
    x_min, y_min, x_max, y_max = aligned_bounds
    width = round((x_max - x_min) / resolution)
    height = round((y_max - y_min) / resolution)
    transform = from_origin(x_min, y_max, resolution, resolution)
    processing_report: dict[str, object] = {}
    try:
        with rasterio.open(source_path, "r") as source:
            if source.crs is None:
                raise ValueError("Cannot reproject a raster without CRS")
            source_window, source_window_bounds = source_window_for_target_bounds(
                source,
                target_srid,
                aligned_bounds,
            )
            profile = {
                "driver": "GTiff",
                "width": width,
                "height": height,
                "count": 1,
                "dtype": "float32",
                "crs": f"EPSG:{target_srid}",
                "transform": transform,
                "nodata": nodata,
                "tiled": True,
                "compress": "deflate",
                "predictor": 3,
                "BIGTIFF": "IF_SAFER",
                "blockxsize": RASTER_BLOCK_SIZE,
                "blockysize": RASTER_BLOCK_SIZE,
            }
            with (
                WarpedVRT(
                    source,
                    crs=f"EPSG:{target_srid}",
                    transform=transform,
                    width=width,
                    height=height,
                    src_nodata=source.nodata,
                    nodata=nodata,
                    dtype="float32",
                    resampling=Resampling.bilinear,
                    warp_mem_limit=64,
                ) as warped,
                rasterio.open(temporary_path, "w", **profile) as destination,
            ):
                destination_blocks = 0
                maximum_block_cells = 0
                for _, destination_window in destination.block_windows(1):
                    values = warped.read(1, window=destination_window, out_dtype="float32", masked=False)
                    destination.write(values, 1, window=destination_window)
                    destination_blocks += 1
                    maximum_block_cells = max(maximum_block_cells, values.size)
            source_window_cells = int(source_window.width * source_window.height)
            source_dataset_cells = int(source.width * source.height)
            processing_report = {
                "source_dataset_size": [source.width, source.height],
                "source_dataset_cells": source_dataset_cells,
                "source_window": {
                    "column_offset": int(source_window.col_off),
                    "row_offset": int(source_window.row_off),
                    "width": int(source_window.width),
                    "height": int(source_window.height),
                    "bounds": list(source_window_bounds),
                    "cells": source_window_cells,
                    "fraction_of_source": source_window_cells / source_dataset_cells,
                    "kernel_margin_pixels": 2,
                },
                "destination_size": [width, height],
                "destination_blocks_written": destination_blocks,
                "maximum_materialized_block_cells": maximum_block_cells,
                "warp_memory_limit_mb": 64,
                "full_source_array_materialized": False,
                "elapsed_seconds": time.perf_counter() - started,
            }
        temporary_path.replace(destination_path)
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise
    return processing_report


def validate_analytic_grid(
    metadata: RasterMetadata,
    target_srid: int,
    resolution: float,
    aligned_bounds: tuple[float, float, float, float],
    tolerance: float = 1e-8,
    expected_dtype: str = FINAL_DTYPE,
    expected_nodata: float = FINAL_NODATA,
) -> None:
    errors: list[str] = []
    if metadata.epsg != target_srid:
        errors.append(f"expected EPSG:{target_srid}, found {metadata.epsg}")
    if any(abs(pixel_size - resolution) > tolerance for pixel_size in metadata.pixel_size):
        errors.append(f"expected {resolution} m pixels, found {metadata.pixel_size}")
    if any(abs(actual - expected) > tolerance for actual, expected in zip(metadata.extent, aligned_bounds)):
        errors.append(f"expected aligned extent {aligned_bounds}, found {metadata.extent}")
    if metadata.data_types != (expected_dtype,):
        errors.append(f"expected dtype {expected_dtype}, found {metadata.data_types}")
    if metadata.nodata != (expected_nodata,):
        errors.append(f"expected NoData {expected_nodata}, found {metadata.nodata}")
    if errors:
        raise ValueError("Analytic grid contract failed: " + "; ".join(errors))
