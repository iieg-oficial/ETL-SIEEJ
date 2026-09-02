from __future__ import annotations

import shlex
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any

import numpy as np
from scipy import ndimage

from core.pipelines.pendientes.constants import (
    DEGREES_CLASSIFICATION,
    FINAL_NODATA,
    MULTISCALE_SMALL_COMPONENT_PIXELS,
    MULTISCALE_SLOPE_WINDOWS,
)
from core.pipelines.pendientes.helpers.classification import classify_values
from core.utils.files import sha256_file


def inspect_grass_param_scale() -> dict[str, Any]:
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
        raise ValueError("Installed r.param.scale does not expose the frozen parameters")
    return {
        "name": "GRASS GIS r.param.scale",
        "version": version,
        "grass_executable": grass,
        "grass_executable_sha256": sha256_file(Path(grass)),
        "module_executable": str(module),
        "module_sha256": sha256_file(module),
        "method": "slope",
        "windows": list(MULTISCALE_SLOPE_WINDOWS),
        "distance_weighting_exponent": 0.0,
        "zscale": 1.0,
        "central_cell_constraint": False,
        "fit": "unweighted bivariate quadratic polynomial by least squares",
        "edge_policy": "full odd-window support required; evaluation uses a common 32-pixel context and crops center",
        "nodata_policy": "a cell is excluded when its complete fitting window is not valid",
    }


def quadratic_gradient_kernels(window: int, pixel_size: float) -> tuple[np.ndarray, np.ndarray]:
    if window not in MULTISCALE_SLOPE_WINDOWS or window % 2 != 1:
        raise ValueError(f"Window must be one of {MULTISCALE_SLOPE_WINDOWS}")
    if pixel_size <= 0:
        raise ValueError("Pixel size must be positive")
    radius = window // 2
    coordinates = np.arange(-radius, radius + 1, dtype=np.float64) * pixel_size
    x, y = np.meshgrid(coordinates, coordinates)
    design = np.column_stack((x.ravel() ** 2, y.ravel() ** 2, (x * y).ravel(), x.ravel(), y.ravel(), np.ones(x.size)))
    inverse = np.linalg.pinv(design)
    return inverse[3].reshape(window, window), inverse[4].reshape(window, window)


def wood_evans_slope(
    elevation: np.ndarray,
    window: int,
    pixel_size: float,
    nodata: float | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Unweighted six-coefficient local quadratic fit, evaluated at each center."""
    if elevation.ndim != 2:
        raise ValueError("Elevation array must be two-dimensional")
    values = elevation.astype(np.float64, copy=False)
    valid = np.isfinite(values)
    if nodata is not None:
        valid &= values != nodata
    kernel_x, kernel_y = quadratic_gradient_kernels(window, pixel_size)
    safe = np.where(valid, values, 0.0)
    dz_dx = ndimage.correlate(safe, kernel_x, mode="constant", cval=0.0)
    dz_dy = ndimage.correlate(safe, kernel_y, mode="constant", cval=0.0)
    support = ndimage.correlate(valid.astype(np.int16), np.ones((window, window), dtype=np.int16), mode="constant")
    output_valid = support == window * window
    slope = np.full(values.shape, np.nan, dtype=np.float64)
    slope[output_valid] = np.degrees(np.arctan(np.hypot(dz_dx[output_valid], dz_dy[output_valid])))
    return slope.astype(np.float32), output_valid


def run_grass_wood_evans(input_path: Path, output_paths: dict[int, Path], backend: dict[str, Any]) -> dict[str, Any]:
    if set(output_paths) != set(MULTISCALE_SLOPE_WINDOWS):
        raise ValueError("GRASS execution requires WE3, WE5 and WE7 outputs together")
    for path in output_paths.values():
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            raise FileExistsError(f"Multiscale slope output exists: {path}")
    started = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="pendientes_we_") as temporary:
        location = Path(temporary) / "location"
        commands = [
            f"r.in.gdal input={shlex.quote(str(input_path.resolve()))} output=dem --overwrite",
            "g.region raster=dem",
        ]
        for window, output in output_paths.items():
            map_name = f"we{window}"
            partial = output.with_suffix(".partial.tif")
            partial.unlink(missing_ok=True)
            commands.extend(
                (
                    f"r.param.scale input=dem output={map_name} method=slope size={window} exponent=0 zscale=1 --overwrite",
                    "r.out.gdal "
                    f"input={map_name} output={shlex.quote(str(partial.resolve()))} "
                    "format=GTiff type=Float32 nodata=-9999 createopt=COMPRESS=DEFLATE -f --overwrite",
                )
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
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"GRASS r.param.scale execution failed: {result.stderr}")
        for output in output_paths.values():
            output.with_suffix(".partial.tif").replace(output)
    return {
        "command": command,
        "elapsed_seconds": time.perf_counter() - started,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def error_metrics(values: np.ndarray, expected: float, extended: bool = False) -> dict[str, float]:
    selected = values[np.isfinite(values)].astype(np.float64)
    error = selected - expected
    absolute = np.abs(error)
    result = {
        "bias": float(error.mean()),
        "mae": float(absolute.mean()),
        "rmse": float(np.sqrt(np.mean(np.square(error)))),
        "max_error": float(absolute.max(initial=0.0)),
    }
    if extended:
        result.update(
            p95_abs_error=float(np.percentile(absolute, 95)),
            p99_abs_error=float(np.percentile(absolute, 99)),
            max_abs_error=float(absolute.max(initial=0.0)),
        )
    return result


def distribution_metrics(values: np.ndarray) -> dict[str, float]:
    selected = values[np.isfinite(values) & (values != FINAL_NODATA)].astype(np.float64)
    return {
        "min": float(selected.min()),
        "mean": float(selected.mean()),
        "std": float(selected.std()),
        **{f"p{p:02d}": float(np.percentile(selected, p)) for p in (1, 5, 25, 50, 75, 90, 95, 99)},
        "max": float(selected.max()),
    }


def neighbor_variation(values: np.ndarray) -> dict[str, float]:
    valid = np.isfinite(values) & (values != FINAL_NODATA)
    differences = []
    for row_shift, column_shift in ((0, 1), (1, 0)):
        left = values[: values.shape[0] - row_shift or None, : values.shape[1] - column_shift or None]
        right = values[row_shift:, column_shift:]
        common = valid[: valid.shape[0] - row_shift or None, : valid.shape[1] - column_shift or None] & valid[row_shift:, column_shift:]
        differences.append(np.abs(right[common].astype(np.float64) - left[common].astype(np.float64)))
    combined = np.concatenate(differences)
    return {f"p{p:02d}": float(np.percentile(combined, p)) for p in (50, 95, 99)}


def difference_metrics(reference: np.ndarray, candidate: np.ndarray) -> dict[str, Any]:
    common = np.isfinite(reference) & np.isfinite(candidate) & (reference != FINAL_NODATA) & (candidate != FINAL_NODATA)
    difference = candidate[common].astype(np.float64) - reference[common].astype(np.float64)
    absolute = np.abs(difference)
    return {
        "bias": float(difference.mean()),
        "mae": float(absolute.mean()),
        "rmse": float(np.sqrt(np.mean(np.square(difference)))),
        **{f"p{p:02d}_abs_difference": float(np.percentile(absolute, p)) for p in (50, 90, 95, 99)},
        "max_abs_difference": float(absolute.max()),
        "threshold_percentages": {
            f"gt_{threshold:g}_degrees": float(np.count_nonzero(absolute > threshold) / absolute.size * 100)
            for threshold in (0.1, 0.5, 1.0, 2.0)
        },
    }


def class_fragmentation(values: np.ndarray) -> dict[str, Any]:
    valid = np.isfinite(values) & (values != FINAL_NODATA)
    classes = np.full(values.shape, 255, dtype=np.uint8)
    classes[valid] = classify_values(values[valid], DEGREES_CLASSIFICATION)
    component_sizes = []
    for code in range(1, 8):
        labels, count = ndimage.label(classes == code, structure=np.ones((3, 3), dtype=np.uint8))
        sizes = np.bincount(labels.ravel())[1:] if count else np.asarray([], dtype=np.int64)
        component_sizes.extend(sizes.tolist())
    sizes = np.asarray(component_sizes, dtype=np.int64)
    small_pixels = int(sizes[sizes < MULTISCALE_SMALL_COMPONENT_PIXELS].sum())
    return {
        "number_of_connected_components": int(sizes.size),
        "median_component_area_pixels": float(np.median(sizes)) if sizes.size else 0.0,
        "small_component_threshold_pixels": MULTISCALE_SMALL_COMPONENT_PIXELS,
        "percent_pixels_in_components_lt_threshold": float(small_pixels / np.count_nonzero(valid) * 100),
        "classes": classes,
    }
