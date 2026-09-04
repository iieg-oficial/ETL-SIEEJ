from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import numpy as np
import rasterio
from rasterio.windows import Window
from scipy.ndimage import gaussian_filter

from core.pipelines.pendientes.constants import FINAL_NODATA, RASTER_BLOCK_SIZE
from core.pipelines.pendientes.helpers.experimental_metrics import valid_mask
from core.utils.files import sha256_file


def gaussian_radius(sigma_pixels: float, truncate: float) -> int:
    if sigma_pixels <= 0 or truncate <= 0:
        raise ValueError("Gaussian sigma and truncate must be positive")
    return int(truncate * sigma_pixels + 0.5)


def normalized_gaussian(
    values: np.ndarray,
    *,
    sigma_pixels: float,
    truncate: float,
    nodata: float | None,
) -> np.ndarray:
    """Filter valid elevations without allowing NoData to enter the convolution."""
    source = values.astype(np.float64, copy=False)
    source_valid = np.isfinite(source)
    if nodata is not None:
        source_valid &= source != nodata
    safe = np.where(source_valid, source, 0.0)
    weights = gaussian_filter(
        source_valid.astype(np.float64),
        sigma=sigma_pixels,
        truncate=truncate,
        mode="constant",
        cval=0.0,
    )
    weighted = gaussian_filter(
        safe,
        sigma=sigma_pixels,
        truncate=truncate,
        mode="constant",
        cval=0.0,
    )
    output = np.full(source.shape, FINAL_NODATA, dtype=np.float32)
    selected = source_valid & (weights > np.finfo(np.float64).eps)
    output[selected] = (weighted[selected] / weights[selected]).astype(np.float32)
    return output


def _core_windows(shape: tuple[int, int], tile_size: int) -> list[Window]:
    if tile_size <= 0:
        raise ValueError("Tile size must be positive")
    height, width = shape
    return [
        Window(column, row, min(tile_size, width - column), min(tile_size, height - row))
        for row in range(0, height, tile_size)
        for column in range(0, width, tile_size)
    ]


def _expanded_window(core: Window, shape: tuple[int, int], halo: int) -> Window:
    height, width = shape
    left = max(0, int(core.col_off) - halo)
    top = max(0, int(core.row_off) - halo)
    right = min(width, int(core.col_off + core.width) + halo)
    bottom = min(height, int(core.row_off + core.height) + halo)
    return Window(left, top, right - left, bottom - top)


def create_gaussian_conditioned_dem(
    source_path: Path,
    output_path: Path,
    *,
    sigma_pixels: float = 1.5,
    truncate: float = 4.0,
    tile_size: int = 2048,
) -> dict[str, Any]:
    if output_path.exists():
        raise FileExistsError(f"Conditioned DEM already exists: {output_path}")
    radius = gaussian_radius(sigma_pixels, truncate)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    partial = output_path.with_suffix(".partial.tif")
    partial.unlink(missing_ok=True)
    started = time.perf_counter()
    try:
        with rasterio.open(source_path) as source:
            profile = source.profile.copy()
            profile.update(
                driver="GTiff",
                dtype="float32",
                nodata=FINAL_NODATA,
                tiled=True,
                blockxsize=RASTER_BLOCK_SIZE,
                blockysize=RASTER_BLOCK_SIZE,
                compress="deflate",
                predictor=3,
                BIGTIFF="IF_SAFER",
            )
            windows = _core_windows(source.shape, tile_size)
            with rasterio.open(partial, "w", **profile) as destination:
                destination.set_band_unit(1, "metre")
                for core in windows:
                    context = _expanded_window(core, source.shape, radius)
                    values = source.read(1, window=context)
                    filtered = normalized_gaussian(
                        values,
                        sigma_pixels=sigma_pixels,
                        truncate=truncate,
                        nodata=source.nodata,
                    )
                    row = int(core.row_off - context.row_off)
                    column = int(core.col_off - context.col_off)
                    destination.write(
                        filtered[row : row + int(core.height), column : column + int(core.width)],
                        1,
                        window=core,
                    )
        partial.replace(output_path)
    except Exception:
        partial.unlink(missing_ok=True)
        raise
    return {
        "path": str(output_path),
        "sha256": sha256_file(output_path),
        "method": "normalized_gaussian",
        "sigma_pixels": sigma_pixels,
        "sigma_metres": sigma_pixels * 15.0,
        "truncate": truncate,
        "kernel_radius_pixels": radius,
        "nodata_policy": "normalized convolution by validity mask; source NoData remains NoData",
        "tile_size_pixels": tile_size,
        "tile_count": len(windows),
        "elapsed_seconds": time.perf_counter() - started,
    }


def validate_gaussian_conditioning(source_path: Path, output_path: Path, tile_size: int = 2048) -> dict[str, Any]:
    valid_pixels = mask_mismatch = nonfinite = 0
    with rasterio.open(source_path) as source, rasterio.open(output_path) as conditioned:
        checks = {
            "crs": conditioned.crs == source.crs and conditioned.crs.to_epsg() == 6368,
            "transform": conditioned.transform == source.transform,
            "bounds": conditioned.bounds == source.bounds,
            "dimensions": conditioned.shape == source.shape,
            "resolution": conditioned.res == source.res == (15.0, 15.0),
            "dtype": conditioned.dtypes == ("float32",),
            "nodata": conditioned.nodata == FINAL_NODATA,
            "vertical_unit": conditioned.units == ("metre",),
        }
        for window in _core_windows(source.shape, tile_size):
            raw = source.read(1, window=window)
            result = conditioned.read(1, window=window)
            raw_valid = valid_mask(raw, source.nodata)
            result_valid = valid_mask(result, conditioned.nodata)
            valid_pixels += int(np.count_nonzero(result_valid))
            mask_mismatch += int(np.count_nonzero(raw_valid ^ result_valid))
            nonfinite += int(np.count_nonzero(~np.isfinite(result[result_valid])))
    hard_gates = {
        **checks,
        "mask_preserved": mask_mismatch == 0,
        "valid_values_finite": nonfinite == 0,
    }
    return {
        "valid_pixels": valid_pixels,
        "mask_mismatch_pixels": mask_mismatch,
        "nonfinite_valid_pixels": nonfinite,
        "hard_gates": {**hard_gates, "all_passed": all(hard_gates.values())},
    }
