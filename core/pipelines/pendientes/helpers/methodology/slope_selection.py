from __future__ import annotations

import math
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import rasterio
from affine import Affine
from rasterio.windows import Window

from core.pipelines.pendientes.constants import FINAL_NODATA, SLOPE_QA_CLASSES_DEGREES
from core.pipelines.pendientes.helpers.methodology.directed_banding import second_difference_fields
from core.pipelines.pendientes.helpers.experimental_metrics import valid_mask
from core.utils.files import sha256_file


def contextual_chip_window(
    chip: dict[str, Any],
    margin: int,
    raster_shape: tuple[int, int],
) -> Window:
    if margin < 1:
        raise ValueError("Slope chip context margin must be positive")
    window = Window(
        int(chip["column_offset"]) - margin,
        int(chip["row_offset"]) - margin,
        int(chip["width"]) + 2 * margin,
        int(chip["height"]) + 2 * margin,
    )
    height, width = raster_shape
    if (
        window.col_off < 0
        or window.row_off < 0
        or window.col_off + window.width > width
        or window.row_off + window.height > height
    ):
        raise ValueError("Slope chip context falls outside the validated context DEM")
    return window


def inspect_gdaldem_backend() -> dict[str, Any]:
    executable = shutil.which("gdaldem")
    version_executable = shutil.which("gdalinfo")
    if executable is None or version_executable is None:
        raise FileNotFoundError("gdaldem and gdalinfo are required")
    version = subprocess.run(
        [version_executable, "--version"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    help_result = subprocess.run([executable], capture_output=True, text=True)
    help_text = help_result.stdout + help_result.stderr
    if "-alg ZevenbergenThorne" not in help_text or "gdaldem slope" not in help_text:
        raise ValueError("Installed gdaldem does not expose both slope algorithms")
    return {
        "name": "GDAL gdaldem CLI",
        "version": version,
        "executable": executable,
        "executable_sha256": sha256_file(Path(executable)),
        "algorithms": {
            "Horn": {"cli_value": "Horn", "default_in_gdal": True},
            "ZevenbergenThorne": {"cli_value": "ZevenbergenThorne", "default_in_gdal": False},
        },
        "parameters": {
            "output_unit": "degree",
            "scale_xy_to_z": 1.0,
            "effective_z_factor": 1.0,
            "compute_edges": False,
        },
        "edge_policy": "outer one-pixel border is NoData; evaluation crops a 32-pixel real-context margin",
        "nodata_policy": "without -compute_edges, any incomplete 3x3 neighborhood is NoData",
    }


def run_gdaldem_slope(
    backend: dict[str, Any],
    input_path: Path,
    output_path: Path,
    algorithm: str,
) -> dict[str, Any]:
    if algorithm not in backend["algorithms"]:
        raise ValueError(f"Unsupported slope algorithm: {algorithm}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_suffix(".tmp.tif")
    temporary.unlink(missing_ok=True)
    command = [
        backend["executable"],
        "slope",
        str(input_path.resolve()),
        str(temporary.resolve()),
        "-s",
        "1.0",
        "-alg",
        backend["algorithms"][algorithm]["cli_value"],
        "-of",
        "GTiff",
        "-co",
        "COMPRESS=DEFLATE",
        "-q",
    ]
    started = time.perf_counter()
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        temporary.replace(output_path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    return {
        "command": command,
        "elapsed_seconds": time.perf_counter() - started,
        "return_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def write_single_band_raster(
    path: Path,
    values: np.ndarray,
    transform: Affine,
    crs: Any,
    unit: str,
    nodata: float = FINAL_NODATA,
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp.tif")
    output = np.where(np.isfinite(values) & (values != nodata), values, nodata).astype(np.float32)
    tiled = output.shape[0] >= 256 and output.shape[1] >= 256
    profile = {
        "driver": "GTiff",
        "width": output.shape[1],
        "height": output.shape[0],
        "count": 1,
        "dtype": "float32",
        "crs": crs,
        "transform": transform,
        "nodata": nodata,
        "tiled": tiled,
        "compress": "deflate",
    }
    if tiled:
        profile.update(blockxsize=256, blockysize=256)
    with rasterio.open(temporary, "w", **profile) as destination:
        destination.write(output, 1)
        destination.set_band_unit(1, unit)
    temporary.replace(path)
    return path


def planar_surface(
    size: int,
    resolution_m: float,
    slope_degrees: float,
    direction_degrees: float,
) -> np.ndarray:
    coordinates = (np.arange(size, dtype=np.float64) - (size - 1) / 2) * resolution_m
    x, y = np.meshgrid(coordinates, coordinates)
    magnitude = math.tan(math.radians(slope_degrees))
    direction = math.radians(direction_degrees)
    return (1000.0 + magnitude * (math.cos(direction) * x + math.sin(direction) * y)).astype(np.float32)


def synthetic_geomorphic_surfaces(
    size: int = 257,
    resolution_m: float = 15.0,
) -> dict[str, np.ndarray]:
    coordinates = (np.arange(size, dtype=np.float64) - (size - 1) / 2) * resolution_m
    x, y = np.meshgrid(coordinates, coordinates)
    rng = np.random.default_rng(257)
    trend = math.tan(math.radians(5.0)) * x
    return {
        "paraboloide_suave": (1000 + 0.00005 * (x * x + y * y)).astype(np.float32),
        "cono_suave": (1000 + 0.08 * np.hypot(x, y)).astype(np.float32),
        "cresta": (1200 - 0.12 * np.abs(x)).astype(np.float32),
        "valle": (800 + 0.12 * np.abs(x)).astype(np.float32),
        "escalon_unico": (1000 + np.where(x >= 0, 10.0, 0.0)).astype(np.float32),
        "ondulada": (1000 + 8 * np.sin(x / 180) + 5 * np.cos(y / 240)).astype(np.float32),
        "tendencia_sin_ruido": (1000 + trend).astype(np.float32),
        "tendencia_con_ruido": (1000 + trend + rng.normal(0, 0.1, x.shape)).astype(np.float32),
    }


def distribution(values: np.ndarray) -> dict[str, float]:
    selected = values[np.isfinite(values) & (values != FINAL_NODATA)].astype(np.float64)
    if not selected.size:
        raise ValueError("Slope distribution has no valid values")
    return {
        "minimum": float(selected.min()),
        "mean": float(selected.mean()),
        "stddev": float(selected.std()),
        **{
            f"p{percentile:02d}": float(np.percentile(selected, percentile))
            for percentile in (1, 5, 25, 50, 75, 90, 95, 99)
        },
        "maximum": float(selected.max()),
    }


def slope_class_distribution(values: np.ndarray) -> dict[str, float]:
    selected = values[np.isfinite(values) & (values != FINAL_NODATA)].astype(np.float64)
    output = {}
    for lower, upper in SLOPE_QA_CLASSES_DEGREES:
        label = f"{lower:g}-{upper:g}_degrees" if upper is not None else f"gt_{lower:g}_degrees"
        membership = selected >= lower if upper is None else (selected >= lower) & (selected < upper)
        output[label] = float(np.count_nonzero(membership) / selected.size * 100)
    return output


def difference_metrics(horn: np.ndarray, zt: np.ndarray) -> dict[str, Any]:
    common = valid_mask(horn, FINAL_NODATA) & valid_mask(zt, FINAL_NODATA)
    difference = zt[common].astype(np.float64) - horn[common].astype(np.float64)
    absolute = np.abs(difference)
    if not difference.size:
        raise ValueError("Slope algorithms have no common valid values")
    return {
        "valid_pixels": difference.size,
        "bias_degrees": float(difference.mean()),
        "mae_degrees": float(absolute.mean()),
        "rmse_degrees": float(np.sqrt(np.mean(np.square(difference)))),
        "absolute_difference_degrees": {
            **{f"p{percentile:02d}": float(np.percentile(absolute, percentile)) for percentile in (50, 90, 95, 99)},
            "maximum": float(absolute.max()),
        },
        "threshold_percentages": {
            f"abs_difference_gt_{threshold:g}_degrees": float(
                np.count_nonzero(absolute > threshold) / absolute.size * 100
            )
            for threshold in (0.1, 0.5, 1.0, 2.0)
        },
    }


def planar_error_metrics(values: np.ndarray, expected_degrees: float) -> dict[str, float]:
    selected = values[np.isfinite(values) & (values != FINAL_NODATA)].astype(np.float64)
    error = selected - expected_degrees
    absolute = np.abs(error)
    return {
        "bias_degrees": float(error.mean()),
        "mae_degrees": float(absolute.mean()),
        "rmse_degrees": float(np.sqrt(np.mean(np.square(error)))),
        "max_error_degrees": float(absolute.max()),
    }


def stability_metrics(values: np.ndarray) -> dict[str, float]:
    valid = valid_mask(values, FINAL_NODATA)
    horizontal_valid = valid[:, 1:] & valid[:, :-1]
    vertical_valid = valid[1:, :] & valid[:-1, :]
    neighbor_differences = np.concatenate(
        (
            np.abs(values[:, 1:][horizontal_valid] - values[:, :-1][horizontal_valid]),
            np.abs(values[1:, :][vertical_valid] - values[:-1, :][vertical_valid]),
        )
    ).astype(np.float64)
    return {
        "neighbor_abs_difference_mean_degrees": float(neighbor_differences.mean()),
        "neighbor_abs_difference_p95_degrees": float(np.percentile(neighbor_differences, 95)),
        "neighbor_continuity_le_0.1_degrees_percentage": float(
            np.count_nonzero(neighbor_differences <= 0.1) / neighbor_differences.size * 100
        ),
    }


def roughness_difference_relationship(
    elevation: np.ndarray,
    horn: np.ndarray,
    zt: np.ndarray,
    nodata: float,
) -> dict[str, float]:
    _, _, roughness, roughness_valid = second_difference_fields(elevation, nodata)
    common = roughness_valid & valid_mask(horn, FINAL_NODATA) & valid_mask(zt, FINAL_NODATA)
    rough = roughness[common].astype(np.float64)
    absolute = np.abs(zt[common].astype(np.float64) - horn[common].astype(np.float64))
    low_threshold, high_threshold = np.percentile(rough, (25, 75))
    return {
        "roughness_p25_m": float(low_threshold),
        "roughness_p75_m": float(high_threshold),
        "mean_abs_difference_low_roughness_degrees": float(absolute[rough <= low_threshold].mean()),
        "mean_abs_difference_high_roughness_degrees": float(absolute[rough >= high_threshold].mean()),
        "pearson_abs_difference_vs_roughness": float(np.corrcoef(absolute, rough)[0, 1]),
    }


def write_comparison_figure(
    path: Path,
    dem: np.ndarray,
    horn: np.ndarray,
    zt: np.ndarray,
    slope_max: float,
    difference_limit: float,
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    valid_dem = valid_mask(dem, FINAL_NODATA)
    valid_slope = valid_mask(horn, FINAL_NODATA) & valid_mask(zt, FINAL_NODATA)
    dem_display = np.where(valid_dem, dem, np.nan)
    horn_display = np.where(valid_slope, horn, np.nan)
    zt_display = np.where(valid_slope, zt, np.nan)
    difference = np.where(valid_slope, zt - horn, np.nan)
    figure, axes = plt.subplots(1, 4, figsize=(16, 4), constrained_layout=True)
    panels = (
        (
            dem_display,
            "DEM acondicionado",
            "terrain",
            float(np.nanpercentile(dem_display, 1)),
            float(np.nanpercentile(dem_display, 99)),
        ),
        (horn_display, "Horn (°)", "viridis", 0.0, slope_max),
        (zt_display, "Zevenbergen–Thorne (°)", "viridis", 0.0, slope_max),
        (difference, "ZT - Horn (°)", "coolwarm", -difference_limit, difference_limit),
    )
    for axis, (values, title, colour_map, minimum, maximum) in zip(axes, panels, strict=True):
        image = axis.imshow(values, cmap=colour_map, vmin=minimum, vmax=maximum)
        axis.set_title(title)
        axis.set_axis_off()
        figure.colorbar(image, ax=axis, fraction=0.046, pad=0.02)
    temporary = path.with_suffix(".tmp.png")
    figure.savefig(temporary, dpi=150)
    plt.close(figure)
    temporary.replace(path)
    return path


def write_profile_figure(
    path: Path,
    dem: np.ndarray,
    horn: np.ndarray,
    zt: np.ndarray,
    row_offsets: tuple[int, ...] = (-256, 0, 256),
) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    center = dem.shape[0] // 2
    figure, axes = plt.subplots(len(row_offsets), 1, figsize=(12, 8), constrained_layout=True)
    records = []
    for axis, offset in zip(np.atleast_1d(axes), row_offsets, strict=True):
        row = center + offset
        x = np.arange(dem.shape[1]) * 15.0
        axis.plot(x, horn[row], label="Horn", linewidth=0.8)
        axis.plot(x, zt[row], label="Zevenbergen–Thorne", linewidth=0.8, alpha=0.8)
        axis.set_ylabel("Pendiente (°)")
        axis.set_title(f"Transecto fila {row}")
        axis.grid(alpha=0.2)
        records.append(
            {
                "row": row,
                "horn_neighbor_variation": stability_metrics(horn[row : row + 1]),
                "zt_neighbor_variation": stability_metrics(zt[row : row + 1]),
            }
        )
    axes[-1].set_xlabel("Distancia (m)")
    axes[0].legend()
    temporary = path.with_suffix(".tmp.png")
    figure.savefig(temporary, dpi=150)
    plt.close(figure)
    temporary.replace(path)
    return {"path": str(path), "transects": records}
