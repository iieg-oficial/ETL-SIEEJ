from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path
from typing import Any

import numpy as np
import rasterio

from core.pipelines.pendientes.constants import (
    COG_BLOCK_SIZE,
    COG_CLASSIFIED_OPTIONS,
    COG_COMPRESSION,
    COG_CONTINUOUS_OPTIONS,
    COG_ELEVATION_Q10_OPTIONS,
    ELEVATION_Q10_NODATA,
)
from core.pipelines.pendientes.helpers.experimental_metrics import valid_mask
from core.pipelines.pendientes.helpers.windows import core_tile_windows
from core.utils.files import sha256_file


def inspect_cog_driver() -> dict[str, Any]:
    version = subprocess.run(["gdalinfo", "--version"], check=True, capture_output=True, text=True).stdout.strip()
    result = subprocess.run(["gdalinfo", "--format", "COG"], check=True, capture_output=True, text=True)
    text = result.stdout
    supported = {name for name in (*COG_CONTINUOUS_OPTIONS, *COG_CLASSIFIED_OPTIONS) if f'name="{name}"' in text}
    required = set(COG_CONTINUOUS_OPTIONS) | set(COG_CLASSIFIED_OPTIONS) | set(COG_ELEVATION_Q10_OPTIONS)
    if supported != required:
        raise ValueError(f"GDAL COG driver lacks required creation options: {sorted(required - supported)}")
    return {
        "driver": "COG",
        "gdal_version": version,
        "creation_options_supported": sorted(supported),
        "continuous_options": COG_CONTINUOUS_OPTIONS,
        "classified_options": COG_CLASSIFIED_OPTIONS,
        "elevation_q10_options": COG_ELEVATION_Q10_OPTIONS,
    }


def create_cog(
    source_path: Path,
    output_path: Path,
    *,
    classified: bool,
    elevation_q10: bool = False,
) -> dict[str, Any]:
    if output_path.exists():
        raise FileExistsError(f"COG output already exists: {output_path}")
    inspect_cog_driver()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    partial = output_path.with_suffix(".partial.tif")
    partial.unlink(missing_ok=True)
    if classified and elevation_q10:
        raise ValueError("A COG cannot be both classified and Q10 elevation")
    options = (
        COG_ELEVATION_Q10_OPTIONS if elevation_q10 else COG_CLASSIFIED_OPTIONS if classified else COG_CONTINUOUS_OPTIONS
    )
    output_type = "Int16" if elevation_q10 else "Byte" if classified else "Float32"
    command = [
        "gdal_translate",
        "-of",
        "COG",
        "-ot",
        output_type,
        str(source_path.resolve()),
        str(partial.resolve()),
    ]
    for name, value in options.items():
        command.extend(("-co", f"{name}={value}"))
    started = time.perf_counter()
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        partial.replace(output_path)
    except Exception:
        partial.unlink(missing_ok=True)
        raise
    return {
        "command": command,
        "source_path": str(source_path),
        "source_sha256": sha256_file(source_path),
        "output_path": str(output_path),
        "output_sha256": sha256_file(output_path),
        "creation_options": options,
        "elapsed_seconds": time.perf_counter() - started,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def gdalinfo_json(path: Path) -> dict[str, Any]:
    result = subprocess.run(
        ["gdalinfo", "-json", str(path.resolve())],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def _same_float32_bits(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return left.astype(np.float32, copy=False).view(np.uint32) == right.astype(np.float32, copy=False).view(np.uint32)


def validate_lossless_cog(
    source_path: Path,
    cog_path: Path,
    *,
    classified: bool,
    elevation_q10: bool = False,
    processing_window_size: int = 2048,
) -> dict[str, Any]:
    info = gdalinfo_json(cog_path)
    image_structure = info.get("metadata", {}).get("IMAGE_STRUCTURE", {})
    layout = image_structure.get("LAYOUT")
    compression = image_structure.get("COMPRESSION")
    different = mask_mismatch = base_valid = cog_valid = 0
    maximum = 0.0
    with rasterio.open(source_path) as source, rasterio.open(cog_path) as cog:
        if classified and elevation_q10:
            raise ValueError("A COG cannot be both classified and Q10 elevation")
        expected_dtype = "int16" if elevation_q10 else "uint8" if classified else "float32"
        expected_nodata = float(ELEVATION_Q10_NODATA) if elevation_q10 else 255.0 if classified else -9999.0
        overviews = cog.overviews(1)
        checks = {
            "layout_cog": layout == "COG",
            "compression": compression == COG_COMPRESSION,
            "block_size": cog.block_shapes == [(COG_BLOCK_SIZE, COG_BLOCK_SIZE)],
            "overviews_present": len(overviews) > 0,
            "dtype": cog.dtypes == (expected_dtype,),
            "nodata": cog.nodata == expected_nodata,
            "crs": cog.crs == source.crs,
            "resolution": cog.res == source.res,
            "transform": cog.transform == source.transform,
            "bounds": cog.bounds == source.bounds,
            "dimensions": cog.shape == source.shape,
            "unit": cog.units == source.units,
        }
        windows = core_tile_windows(source.shape, processing_window_size)
        for window in windows:
            base = source.read(1, window=window)
            packaged = cog.read(1, window=window)
            base_mask = valid_mask(base, source.nodata)
            cog_mask = valid_mask(packaged, cog.nodata)
            base_valid += int(np.count_nonzero(base_mask))
            cog_valid += int(np.count_nonzero(cog_mask))
            mask_mismatch += int(np.count_nonzero(base_mask ^ cog_mask))
            comparison = base_mask & cog_mask
            if classified or elevation_q10:
                unequal = base[comparison] != packaged[comparison]
            else:
                unequal = ~_same_float32_bits(base[comparison], packaged[comparison])
            different += int(np.count_nonzero(unequal))
            differences = np.abs(base[comparison].astype(np.float64) - packaged[comparison].astype(np.float64))
            maximum = max(maximum, float(differences.max(initial=0.0)))
    hard_gates = {
        **checks,
        "mask_equality": mask_mismatch == 0,
        "base_value_bitwise_equality": different == 0,
        "maximum_absolute_difference_zero": maximum == 0.0,
    }
    return {
        "format": "COG",
        "cloud_optimized": layout == "COG",
        "compression": compression,
        "lossless": different == 0 and mask_mismatch == 0,
        "block_size": COG_BLOCK_SIZE,
        "overview_levels": overviews,
        "overview_resampling": (
            COG_ELEVATION_Q10_OPTIONS["OVERVIEW_RESAMPLING"]
            if elevation_q10
            else COG_CLASSIFIED_OPTIONS["OVERVIEW_RESAMPLING"]
            if classified
            else COG_CONTINUOUS_OPTIONS["OVERVIEW_RESAMPLING"]
        ),
        "base_valid_pixels": base_valid,
        "cog_valid_pixels": cog_valid,
        "mask_mismatch_pixels": mask_mismatch,
        "different_base_pixels": different,
        "max_abs_difference": maximum,
        "hard_gates": {**hard_gates, "all_passed": all(hard_gates.values())},
        "sha256": sha256_file(cog_path),
    }


def validate_cog_structure(path: Path) -> dict[str, Any]:
    try:
        info = gdalinfo_json(path)
    except (subprocess.CalledProcessError, json.JSONDecodeError) as error:
        raise ValueError(f"Invalid or corrupt COG: {path}") from error
    image_structure = info.get("metadata", {}).get("IMAGE_STRUCTURE", {})
    if image_structure.get("LAYOUT") != "COG":
        raise ValueError(f"Raster is not a valid COG layout: {path}")
    with rasterio.open(path) as dataset:
        if not dataset.overviews(1):
            raise ValueError(f"COG has no overviews: {path}")
        return {
            "driver": info.get("driverShortName"),
            "layout": "COG",
            "compression": image_structure.get("COMPRESSION"),
            "block_shape": list(dataset.block_shapes[0]),
            "overviews": dataset.overviews(1),
            "dtype": dataset.dtypes[0],
            "nodata": dataset.nodata,
            "crs_epsg": dataset.crs.to_epsg() if dataset.crs else None,
            "resolution": list(dataset.res),
            "transform": list(dataset.transform),
            "bounds": list(dataset.bounds),
        }
