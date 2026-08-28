from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import rasterio
from affine import Affine
from pyproj import Transformer
from rasterio.enums import Resampling
from rasterio.transform import rowcol
from rasterio.warp import reproject, transform_bounds
from rasterio.windows import Window, bounds as window_bounds, from_bounds

from core.pipelines.pendientes.constants import FINAL_NODATA, SOURCE_EXPECTED_NODATA
from core.pipelines.pendientes.helpers.directed_banding import second_difference_fields
from core.pipelines.pendientes.helpers.experimental_artifacts import hillshade
from core.pipelines.pendientes.helpers.slope import experimental_horn_slope


def equivalent_native_window(
    source: rasterio.io.DatasetReader,
    target_bounds: tuple[float, float, float, float],
    target_crs: rasterio.crs.CRS,
) -> tuple[Window, tuple[float, float, float, float]]:
    if source.crs is None:
        raise ValueError("Native source CRS is required")
    geographic_bounds = transform_bounds(target_crs, source.crs, *target_bounds, densify_pts=21)
    fractional = from_bounds(*geographic_bounds, transform=source.transform)
    kernel_margin_pixels = 2
    left = max(0, int(np.floor(fractional.col_off)) - kernel_margin_pixels)
    top = max(0, int(np.floor(fractional.row_off)) - kernel_margin_pixels)
    right = min(source.width, int(np.ceil(fractional.col_off + fractional.width)) + kernel_margin_pixels)
    bottom = min(source.height, int(np.ceil(fractional.row_off + fractional.height)) + kernel_margin_pixels)
    window = Window(left, top, right - left, bottom - top)
    if window.width <= 0 or window.height <= 0:
        raise ValueError("Equivalent footprint does not intersect the native source")
    return window, tuple(float(value) for value in window_bounds(window, source.transform))


def warp_native_to_grid(
    source_values: np.ndarray,
    source_transform: Affine,
    source_crs: rasterio.crs.CRS,
    destination_shape: tuple[int, int],
    destination_transform: Affine,
    destination_crs: rasterio.crs.CRS,
    resampling: Resampling,
    source_nodata: float = SOURCE_EXPECTED_NODATA,
    destination_nodata: float = FINAL_NODATA,
) -> np.ndarray:
    destination = np.full(destination_shape, destination_nodata, dtype=np.float32)
    reproject(
        source=source_values,
        destination=destination,
        src_transform=source_transform,
        src_crs=source_crs,
        src_nodata=source_nodata,
        dst_transform=destination_transform,
        dst_crs=destination_crs,
        dst_nodata=destination_nodata,
        resampling=resampling,
        init_dest_nodata=True,
        num_threads=1,
    )
    return destination


def elevation_distribution(values: np.ndarray, nodata: float | None) -> dict[str, Any]:
    valid = np.isfinite(values)
    if nodata is not None:
        valid &= values != nodata
    selected = values[valid].astype(np.float64, copy=False)
    if not selected.size:
        raise ValueError("Elevation window has no valid values")
    counts, edges = np.histogram(selected, bins=32)
    return {
        "valid_count": int(selected.size),
        "nodata_count": int(values.size - selected.size),
        "valid_percentage": float(selected.size / values.size * 100),
        "minimum": float(selected.min()),
        "maximum": float(selected.max()),
        "mean": float(selected.mean()),
        "stddev": float(selected.std()),
        "percentiles": {
            f"p{percentile:02d}": float(np.percentile(selected, percentile))
            for percentile in (1, 5, 25, 50, 75, 90, 95, 99)
        },
        "histogram": {"bin_edges": edges.tolist(), "counts": counts.tolist()},
    }


def quantization_summary(values: np.ndarray, nodata: float | None) -> dict[str, Any]:
    valid = np.isfinite(values)
    if nodata is not None:
        valid &= values != nodata
    selected = values[valid].astype(np.float64, copy=False)
    integer = np.isclose(selected, np.rint(selected), atol=0.0, rtol=0.0)
    return {
        "storage_dtype": str(values.dtype),
        "integer_value_count": int(np.count_nonzero(integer)),
        "integer_value_percentage": float(np.count_nonzero(integer) / selected.size * 100),
        "unique_elevation_count": int(np.unique(selected).size),
        "vertical_increment_observed_m": 1.0,
        "interpretation": "Int16 stores whole-metre elevation levels; this confirms vertical quantization, not causality.",
    }


def native_neighbor_differences(values: np.ndarray, nodata: float | None) -> dict[str, Any]:
    valid = np.isfinite(values)
    if nodata is not None:
        valid &= values != nodata
    pairs = {
        "dz_x": (values[:, 1:] - values[:, :-1], valid[:, 1:] & valid[:, :-1]),
        "dz_y": (values[1:, :] - values[:-1, :], valid[1:, :] & valid[:-1, :]),
    }
    result: dict[str, Any] = {}
    for name, (differences, pair_valid) in pairs.items():
        absolute = np.abs(differences[pair_valid].astype(np.float64, copy=False))
        result[name] = {
            "valid_pairs": int(absolute.size),
            "percentage_abs_dz_eq_0_m": float(np.count_nonzero(absolute == 0) / absolute.size * 100),
            "percentage_abs_dz_eq_1_m": float(np.count_nonzero(absolute == 1) / absolute.size * 100),
            "percentage_abs_dz_eq_2_m": float(np.count_nonzero(absolute == 2) / absolute.size * 100),
            "percentage_abs_dz_le_1_m": float(np.count_nonzero(absolute <= 1) / absolute.size * 100),
            "percentage_abs_dz_le_2_m": float(np.count_nonzero(absolute <= 2) / absolute.size * 100),
            "percentiles_m": {
                f"p{percentile:02d}": float(np.percentile(absolute, percentile))
                for percentile in (50, 90, 95, 99)
            },
        }
    return result


def spatial_difference_metrics(
    reference: np.ndarray,
    comparison: np.ndarray,
    nodata: float | None = FINAL_NODATA,
) -> dict[str, Any]:
    if reference.shape != comparison.shape:
        raise ValueError("Spatial comparison requires a shared QA grid")
    valid = np.isfinite(reference) & np.isfinite(comparison)
    if nodata is not None:
        valid &= (reference != nodata) & (comparison != nodata)
    differences = comparison[valid].astype(np.float64) - reference[valid].astype(np.float64)
    if not differences.size:
        raise ValueError("Spatial comparison has no common valid cells")
    absolute = np.abs(differences)
    counts, edges = np.histogram(differences, bins=64)
    return {
        "common_valid_pixels": int(differences.size),
        "bias": float(differences.mean()),
        "mae": float(absolute.mean()),
        "rmse": float(np.sqrt(np.mean(np.square(differences)))),
        "absolute_difference": {
            **{
                f"p{percentile:02d}": float(np.percentile(absolute, percentile))
                for percentile in (50, 90, 95, 99)
            },
            "maximum": float(absolute.max()),
        },
        "difference_histogram": {"bin_edges": edges.tolist(), "counts": counts.tolist()},
    }


def metric_derivatives(values: np.ndarray, resolution_m: float, nodata: float | None) -> dict[str, Any]:
    slope, _, slope_valid = experimental_horn_slope(values, resolution_m, nodata)
    shade, shade_valid = hillshade(values, resolution_m, nodata, 315.0, 45.0)
    _, _, second, second_valid = second_difference_fields(values, nodata)
    return {
        "slope": slope,
        "slope_valid": slope_valid,
        "hillshade": shade,
        "hillshade_valid": shade_valid,
        "second_difference": second,
        "second_difference_valid": second_valid,
    }


def profile_coordinates(
    center_x: float,
    center_y: float,
    length_m: float,
    spacing_m: float,
    angle_degrees: float,
    tangent_offset_m: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if length_m <= 0 or spacing_m <= 0:
        raise ValueError("Profile length and spacing must be positive")
    angle = np.radians(angle_degrees)
    normal = np.array([np.cos(angle), np.sin(angle)], dtype=np.float64)
    tangent = np.array([-normal[1], normal[0]], dtype=np.float64)
    count = max(2, int(np.floor(length_m / spacing_m)) + 1)
    along = np.linspace(-length_m / 2, length_m / 2, count)
    coordinates = np.array([center_x, center_y]) + along[:, None] * normal + tangent_offset_m * tangent
    return along - along.min(), coordinates[:, 0], coordinates[:, 1]


def sample_profile(
    distances: np.ndarray,
    x_target: np.ndarray,
    y_target: np.ndarray,
    target_crs: rasterio.crs.CRS,
    native_values: np.ndarray,
    native_transform: Affine,
    native_crs: rasterio.crs.CRS,
    baseline_values: np.ndarray,
    baseline_transform: Affine,
) -> list[dict[str, float]]:
    transformer = Transformer.from_crs(target_crs, native_crs, always_xy=True)
    longitude, latitude = transformer.transform(x_target, y_target)
    native_rows, native_columns = rowcol(native_transform, longitude, latitude)
    target_rows, target_columns = rowcol(baseline_transform, x_target, y_target)
    records = []
    for index in range(distances.size):
        nr, nc = int(native_rows[index]), int(native_columns[index])
        tr, tc = int(target_rows[index]), int(target_columns[index])
        if not (0 <= nr < native_values.shape[0] and 0 <= nc < native_values.shape[1]):
            continue
        if not (0 <= tr < baseline_values.shape[0] and 0 <= tc < baseline_values.shape[1]):
            continue
        records.append(
            {
                "distance_m": float(distances[index]),
                "x_epsg6368": float(x_target[index]),
                "y_epsg6368": float(y_target[index]),
                "longitude_epsg6365": float(longitude[index]),
                "latitude_epsg6365": float(latitude[index]),
                "native_elevation_m": float(native_values[nr, nc]),
                "baseline_elevation_m": float(baseline_values[tr, tc]),
            }
        )
    return records


def profile_step_summary(records: list[dict[str, float]]) -> dict[str, Any]:
    native = np.array([record["native_elevation_m"] for record in records], dtype=np.float64)
    differences = np.abs(np.diff(native))
    nonzero = differences > 0
    return {
        "sample_count": len(records),
        "plateau_transition_percentage": float(np.count_nonzero(differences == 0) / differences.size * 100),
        "one_metre_step_percentage": float(np.count_nonzero(differences == 1) / differences.size * 100),
        "two_metre_step_percentage": float(np.count_nonzero(differences == 2) / differences.size * 100),
        "nonzero_step_count": int(np.count_nonzero(nonzero)),
        "alternating_plateau_step_sequences": int(
            np.count_nonzero((differences[:-1] == 0) & (differences[1:] > 0))
            + np.count_nonzero((differences[:-1] > 0) & (differences[1:] == 0))
        ),
    }


def write_profile_csv(path: Path, records: list[dict[str, float]]) -> Path:
    if not records:
        raise ValueError("Profile CSV requires records")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp.csv")
    with temporary.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    temporary.replace(path)
    return path


def write_native_raster(
    path: Path,
    values: np.ndarray,
    transform: Affine,
    crs: rasterio.crs.CRS,
    nodata: int = SOURCE_EXPECTED_NODATA,
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp.tif")
    with rasterio.open(
        temporary,
        "w",
        driver="GTiff",
        height=values.shape[0],
        width=values.shape[1],
        count=1,
        dtype="int16",
        crs=crs,
        transform=transform,
        nodata=nodata,
        compress="deflate",
        tiled=True,
        blockxsize=256,
        blockysize=256,
    ) as destination:
        destination.write(values.astype(np.int16, copy=False), 1)
    temporary.replace(path)
    return path


def write_profile_comparison(path: Path, profiles: list[list[dict[str, float]]]) -> Path:
    if not profiles:
        raise ValueError("Profile comparison requires profiles")
    figure, axes = plt.subplots(len(profiles), 1, figsize=(12, 3.5 * len(profiles)), constrained_layout=True)
    axes_array = np.atleast_1d(axes)
    for index, (axis, records) in enumerate(zip(axes_array, profiles, strict=True), start=1):
        distance = [record["distance_m"] for record in records]
        axis.step(distance, [record["native_elevation_m"] for record in records], where="mid", label="CEM nativo")
        axis.plot(distance, [record["baseline_elevation_m"] for record in records], label="Baseline bilinear")
        axis.set_title(f"Perfil {index}")
        axis.set_xlabel("Distancia (m)")
        axis.set_ylabel("Elevación (m)")
        axis.grid(alpha=0.2)
        axis.legend()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp.png")
    figure.savefig(temporary, dpi=120)
    plt.close(figure)
    temporary.replace(path)
    return path


def write_diagnostic_composition(
    path: Path,
    source_common: np.ndarray,
    baseline: np.ndarray,
    source_derivatives: dict[str, Any],
    baseline_derivatives: dict[str, Any],
) -> Path:
    valid = (source_common != FINAL_NODATA) & (baseline != FINAL_NODATA)
    elevation = np.concatenate((source_common[valid], baseline[valid]))
    elevation_range = np.percentile(elevation, (1, 99))
    slopes = np.concatenate(
        (
            source_derivatives["slope"][source_derivatives["slope_valid"]],
            baseline_derivatives["slope"][baseline_derivatives["slope_valid"]],
        )
    )
    slope_max = float(np.percentile(slopes, 99))
    difference = baseline - source_common
    difference_limit = float(np.percentile(np.abs(difference[valid]), 99))
    second = np.concatenate(
        (
            source_derivatives["second_difference"][source_derivatives["second_difference_valid"]],
            baseline_derivatives["second_difference"][baseline_derivatives["second_difference_valid"]],
        )
    )
    second_max = float(np.percentile(second, 99))
    panels = (
        (source_common, "CEM nativo en rejilla QA (nearest)", "terrain", *elevation_range),
        (baseline, "Baseline bilinear", "terrain", *elevation_range),
        (difference, "Baseline - fuente", "RdBu_r", -difference_limit, difference_limit),
        (source_derivatives["hillshade"], "Hillshade fuente", "gray", 0.0, 255.0),
        (baseline_derivatives["hillshade"], "Hillshade baseline", "gray", 0.0, 255.0),
        (source_derivatives["slope"], "Pendiente fuente", "magma", 0.0, slope_max),
        (baseline_derivatives["slope"], "Pendiente baseline", "magma", 0.0, slope_max),
        (source_derivatives["second_difference"], "2a diferencia fuente", "viridis", 0.0, second_max),
        (baseline_derivatives["second_difference"], "2a diferencia baseline", "viridis", 0.0, second_max),
    )
    figure, axes = plt.subplots(3, 3, figsize=(15, 14), constrained_layout=True)
    for axis, (values, title, color_map, minimum, maximum) in zip(axes.flat, panels, strict=True):
        axis.imshow(values, cmap=color_map, vmin=minimum, vmax=maximum)
        axis.set_title(title)
        axis.axis("off")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp.png")
    figure.savefig(temporary, dpi=120)
    plt.close(figure)
    temporary.replace(path)
    return path
