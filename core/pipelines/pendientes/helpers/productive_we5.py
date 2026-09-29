from __future__ import annotations

import math
import shlex
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any

import numpy as np
import rasterio

from core.pipelines.pendientes.constants import FINAL_NODATA, RASTER_BLOCK_SIZE
from core.pipelines.pendientes.helpers.experimental_metrics import valid_mask
from core.pipelines.pendientes.helpers.windows import core_tile_windows
from core.utils.files import sha256_file


def inspect_productive_we5_backend() -> dict[str, Any]:
    grass = shutil.which("grass")
    module = Path("/usr/lib/grass83/bin/r.param.scale")
    if grass is None or not module.is_file():
        raise FileNotFoundError("GRASS GIS and r.param.scale are required")
    version = subprocess.run([grass, "--version"], check=True, capture_output=True, text=True).stdout.splitlines()[0]
    help_result = subprocess.run(
        [grass, "--tmp-location", "EPSG:6368", "--exec", "r.param.scale", "--help"],
        check=True,
        capture_output=True,
        text=True,
    )
    help_text = help_result.stdout + help_result.stderr
    if "exponent" not in help_text or "size" not in help_text:
        raise ValueError("Installed r.param.scale does not expose the productive parameters")
    return {
        "name": "GRASS GIS r.param.scale",
        "version": version,
        "grass_executable": grass,
        "grass_executable_sha256": sha256_file(Path(grass)),
        "module_executable": str(module),
        "module_sha256": sha256_file(module),
        "method": "slope",
        "size": 5,
        "exponent": 0.0,
        "zscale": 1.0,
    }


def wood_evans_module_commands(context_dem_path: Path, output_path: Path) -> tuple[str, ...]:
    """Build the exact GRASS module sequence for the productive WE5 estimator."""
    return (
        f"r.in.gdal input={shlex.quote(str(context_dem_path.resolve()))} output=dem --overwrite",
        "g.region raster=dem",
        "r.param.scale input=dem output=we5 method=slope size=5 exponent=0 zscale=1 --overwrite",
        "r.out.gdal "
        f"input=we5 output={shlex.quote(str(output_path.resolve()))} "
        "format=GTiff type=Float32 nodata=-9999 "
        f"createopt=TILED=YES,COMPRESS=DEFLATE,BLOCKXSIZE={RASTER_BLOCK_SIZE},"
        f"BLOCKYSIZE={RASTER_BLOCK_SIZE},BIGTIFF=IF_SAFER -f --overwrite",
    )


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
        commands = wood_evans_module_commands(context_dem_path, partial)
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
