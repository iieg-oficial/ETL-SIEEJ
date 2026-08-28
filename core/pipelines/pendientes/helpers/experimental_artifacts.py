from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import rasterio
from affine import Affine

from core.pipelines.pendientes.constants import (
    EXPERIMENT_HILLSHADE_ALTITUDE_DEGREES,
    EXPERIMENT_HILLSHADE_AZIMUTH_DEGREES,
    FINAL_NODATA,
    RASTER_BLOCK_SIZE,
)
from core.pipelines.pendientes.helpers.slope import horn_gradient


def hillshade(
    elevation: np.ndarray,
    resolution: float,
    nodata: float | None,
    azimuth_degrees: float = EXPERIMENT_HILLSHADE_AZIMUTH_DEGREES,
    altitude_degrees: float = EXPERIMENT_HILLSHADE_ALTITUDE_DEGREES,
) -> tuple[np.ndarray, np.ndarray]:
    dz_dx, dz_dy, valid = horn_gradient(elevation, resolution, nodata)
    slope = np.arctan(np.hypot(dz_dx, dz_dy))
    aspect = np.arctan2(dz_dy, -dz_dx)
    azimuth = np.radians(azimuth_degrees)
    zenith = np.radians(90.0 - altitude_degrees)
    illumination = 255.0 * (np.cos(zenith) * np.cos(slope) + np.sin(zenith) * np.sin(slope) * np.cos(azimuth - aspect))
    illumination = np.clip(illumination, 0, 255)
    illumination[~valid] = np.nan
    return illumination.astype(np.float32), valid


def write_float_raster(
    path: Path,
    values: np.ndarray,
    valid: np.ndarray,
    transform: Affine,
    crs: rasterio.crs.CRS,
    nodata: float = FINAL_NODATA,
) -> Path:
    if values.shape != valid.shape:
        raise ValueError("Raster values and valid mask must share a grid")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp.tif")
    output = np.where(valid, values, nodata).astype(np.float32)
    tiled = output.shape[0] >= RASTER_BLOCK_SIZE and output.shape[1] >= RASTER_BLOCK_SIZE
    profile = {
        "driver": "GTiff",
        "height": output.shape[0],
        "width": output.shape[1],
        "count": 1,
        "dtype": "float32",
        "crs": crs,
        "transform": transform,
        "nodata": nodata,
        "tiled": tiled,
        "compress": "deflate",
    }
    if tiled:
        profile.update(blockxsize=RASTER_BLOCK_SIZE, blockysize=RASTER_BLOCK_SIZE)
    with rasterio.open(temporary, "w", **profile) as destination:
        destination.write(output, 1)
    temporary.replace(path)
    return path


def _scale_panel(values: np.ndarray, valid: np.ndarray, minimum: float, maximum: float) -> np.ndarray:
    if maximum <= minimum:
        maximum = minimum + 1.0
    scaled = np.clip((values - minimum) / (maximum - minimum), 0, 1) * 254 + 1
    return np.where(valid & np.isfinite(values), scaled, 0).astype(np.uint8)


def write_comparison_png(
    path: Path,
    panels: list[tuple[str, np.ndarray, np.ndarray]],
    minimum: float,
    maximum: float,
) -> dict[str, Any]:
    if not panels:
        raise ValueError("Comparison composition requires at least one panel")
    shapes = {values.shape for _, values, _ in panels}
    if len(shapes) != 1:
        raise ValueError("Comparison panels must share dimensions")
    arrays = [_scale_panel(values, valid, minimum, maximum) for _, values, valid in panels]
    composite = np.concatenate(arrays, axis=1)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp.png")
    with rasterio.open(
        temporary,
        "w",
        driver="PNG",
        height=composite.shape[0],
        width=composite.shape[1],
        count=1,
        dtype="uint8",
    ) as destination:
        destination.write(composite, 1)
    temporary.replace(path)
    return {
        "path": str(path),
        "panel_order": [name for name, _, _ in panels],
        "shared_display_range": [minimum, maximum],
        "nodata_display_value": 0,
        "data_display_range": [1, 255],
        "independent_autoscaling": False,
    }
