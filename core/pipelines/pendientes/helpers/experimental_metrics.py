from __future__ import annotations

from typing import Any

import numpy as np

from core.pipelines.pendientes.constants import (
    EXPERIMENT_ELEVATION_CHANGE_THRESHOLDS_M,
    EXPERIMENT_MODIFIED_TOLERANCE_M,
    EXPERIMENT_STRONG_GRADIENT_PERCENTILE,
    NEAR_FLAT_DIFFERENCE_TOLERANCE_M,
)
from core.pipelines.pendientes.helpers.slope import experimental_horn_slope, horn_gradient


def valid_mask(values: np.ndarray, nodata: float | None) -> np.ndarray:
    valid = np.isfinite(values)
    if nodata is not None:
        valid &= values != nodata
    return valid


def absolute_laplacian(elevation: np.ndarray, nodata: float | None = None) -> tuple[np.ndarray, np.ndarray]:
    values = elevation.astype(np.float64, copy=False)
    source_valid = valid_mask(values, nodata)
    output = np.full(values.shape, np.nan, dtype=np.float64)
    valid = np.zeros(values.shape, dtype=bool)
    if min(values.shape) < 3:
        return output, valid
    inner_valid = (
        source_valid[1:-1, 1:-1]
        & source_valid[:-2, 1:-1]
        & source_valid[2:, 1:-1]
        & source_valid[1:-1, :-2]
        & source_valid[1:-1, 2:]
    )
    laplacian = np.abs(
        values[:-2, 1:-1] + values[2:, 1:-1] + values[1:-1, :-2] + values[1:-1, 2:] - 4 * values[1:-1, 1:-1]
    )
    laplacian[~inner_valid] = np.nan
    output[1:-1, 1:-1] = laplacian
    valid[1:-1, 1:-1] = inner_valid
    return output, valid


def local_neighbor_magnitude(elevation: np.ndarray, nodata: float | None = None) -> tuple[np.ndarray, np.ndarray]:
    values = elevation.astype(np.float64, copy=False)
    source_valid = valid_mask(values, nodata)
    output = np.full(values.shape, np.nan, dtype=np.float64)
    valid = np.zeros(values.shape, dtype=bool)
    if min(values.shape) < 2:
        return output, valid
    inner_valid = source_valid[:-1, :-1] & source_valid[:-1, 1:] & source_valid[1:, :-1]
    magnitude = np.hypot(values[:-1, 1:] - values[:-1, :-1], values[1:, :-1] - values[:-1, :-1])
    magnitude[~inner_valid] = np.nan
    output[:-1, :-1] = magnitude
    valid[:-1, :-1] = inner_valid
    return output, valid


def _percentiles(values: np.ndarray, percentiles: tuple[int, ...]) -> dict[str, float]:
    return {f"p{percentile}": float(np.percentile(values, percentile)) for percentile in percentiles}


def distribution(values: np.ndarray, valid: np.ndarray) -> dict[str, Any]:
    selected = values[valid].astype(np.float64, copy=False)
    if not selected.size:
        raise ValueError("Metric has no valid values")
    return {
        "count": int(selected.size),
        "minimum": float(selected.min()),
        "maximum": float(selected.max()),
        "mean": float(selected.mean()),
        "stddev": float(selected.std()),
        **_percentiles(selected, (50, 90, 95, 99)),
    }


def elevation_change_metrics(
    raw: np.ndarray,
    candidate: np.ndarray,
    nodata: float | None,
) -> dict[str, Any]:
    if raw.shape != candidate.shape:
        raise ValueError("RAW and candidate elevation must share a grid")
    valid = valid_mask(raw, nodata) & valid_mask(candidate, nodata)
    differences = candidate[valid].astype(np.float64) - raw[valid].astype(np.float64)
    if not differences.size:
        raise ValueError("Elevation comparison has no common valid pixels")
    absolute = np.abs(differences)
    return {
        "common_valid_pixels": int(differences.size),
        "bias_m": float(differences.mean()),
        "mae_m": float(absolute.mean()),
        "rmse_m": float(np.sqrt(np.mean(np.square(differences)))),
        "absolute_difference_m": {
            **_percentiles(absolute, (50, 90, 95, 99)),
            "maximum": float(absolute.max()),
        },
        "modified_tolerance_m": EXPERIMENT_MODIFIED_TOLERANCE_M,
        "modified_pixel_percentage": float(
            np.count_nonzero(absolute > EXPERIMENT_MODIFIED_TOLERANCE_M) / absolute.size * 100
        ),
        "threshold_percentages": {
            f"abs_change_gt_{threshold:g}_m": float(np.count_nonzero(absolute > threshold) / absolute.size * 100)
            for threshold in EXPERIMENT_ELEVATION_CHANGE_THRESHOLDS_M
        },
    }


def slope_metrics(
    raw: np.ndarray,
    candidate: np.ndarray,
    resolution: float,
    nodata: float | None,
) -> tuple[dict[str, Any], np.ndarray, np.ndarray]:
    raw_slope, _, raw_valid = experimental_horn_slope(raw, resolution, nodata)
    candidate_slope, _, candidate_valid = experimental_horn_slope(candidate, resolution, nodata)
    common = raw_valid & candidate_valid
    summary = distribution(candidate_slope, candidate_valid)
    differences = candidate_slope[common].astype(np.float64) - raw_slope[common].astype(np.float64)
    absolute = np.abs(differences)
    summary["difference_from_raw_degrees"] = {
        "count": int(differences.size),
        "bias": float(differences.mean()),
        "mae": float(absolute.mean()),
        "rmse": float(np.sqrt(np.mean(np.square(differences)))),
        "p95_absolute": float(np.percentile(absolute, 95)),
        "p99_absolute": float(np.percentile(absolute, 99)),
    }
    return summary, candidate_slope, candidate_valid


def neighbor_metrics(elevation: np.ndarray, nodata: float | None) -> dict[str, Any]:
    values = elevation.astype(np.float64, copy=False)
    source_valid = valid_mask(values, nodata)
    directions = {
        "dz_x": (values[:, 1:] - values[:, :-1], source_valid[:, 1:] & source_valid[:, :-1]),
        "dz_y": (values[1:, :] - values[:-1, :], source_valid[1:, :] & source_valid[:-1, :]),
    }
    result: dict[str, Any] = {"near_flat_tolerance_m": NEAR_FLAT_DIFFERENCE_TOLERANCE_M}
    for name, (differences, valid) in directions.items():
        absolute = np.abs(differences[valid].astype(np.float64, copy=False))
        result[name] = {
            "valid_pairs": int(absolute.size),
            "percentage_abs_dz_eq_0": float(np.count_nonzero(absolute == 0) / absolute.size * 100),
            "near_flat_percentage": float(
                np.count_nonzero(absolute <= NEAR_FLAT_DIFFERENCE_TOLERANCE_M) / absolute.size * 100
            ),
            "threshold_percentages": {
                f"abs_dz_le_{threshold:g}_m": float(np.count_nonzero(absolute <= threshold) / absolute.size * 100)
                for threshold in EXPERIMENT_ELEVATION_CHANGE_THRESHOLDS_M
            },
            **_percentiles(absolute, (50, 90, 95, 99)),
        }
    return result


def structure_preservation_metrics(
    raw: np.ndarray,
    candidate: np.ndarray,
    resolution: float,
    nodata: float | None,
) -> dict[str, Any]:
    raw_dx, raw_dy, raw_valid = horn_gradient(raw, resolution, nodata)
    candidate_dx, candidate_dy, candidate_valid = horn_gradient(candidate, resolution, nodata)
    common = raw_valid & candidate_valid
    raw_gradient = np.hypot(raw_dx, raw_dy)
    candidate_gradient = np.hypot(candidate_dx, candidate_dy)
    threshold = float(np.percentile(raw_gradient[raw_valid], EXPERIMENT_STRONG_GRADIENT_PERCENTILE))
    strong = common & (raw_gradient >= threshold)
    ratios = candidate_gradient[strong] / raw_gradient[strong]

    raw_normal = np.stack((-raw_dx[common], -raw_dy[common], np.ones(np.count_nonzero(common))), axis=1)
    candidate_normal = np.stack(
        (-candidate_dx[common], -candidate_dy[common], np.ones(np.count_nonzero(common))),
        axis=1,
    )
    raw_normal /= np.linalg.norm(raw_normal, axis=1, keepdims=True)
    candidate_normal /= np.linalg.norm(candidate_normal, axis=1, keepdims=True)
    angular = np.degrees(np.arccos(np.clip(np.sum(raw_normal * candidate_normal, axis=1), -1.0, 1.0)))
    return {
        "strong_gradient": {
            "raw_percentile": EXPERIMENT_STRONG_GRADIENT_PERCENTILE,
            "raw_threshold_rise_run": threshold,
            "pixel_count": int(ratios.size),
            "candidate_to_raw_magnitude_ratio": {
                "mean": float(ratios.mean()),
                **_percentiles(ratios, (10, 50, 90)),
            },
        },
        "surface_normal_angular_difference_degrees": {
            "mean": float(angular.mean()),
            **_percentiles(angular, (50, 90, 95, 99)),
            "maximum": float(angular.max()),
        },
        "ridge_preservation": None,
        "gully_preservation": None,
        "interpretation": "exploratory metrics without promotion thresholds",
    }


def experimental_metrics(
    raw: np.ndarray,
    candidate: np.ndarray,
    resolution: float,
    nodata: float | None,
) -> tuple[dict[str, Any], np.ndarray, np.ndarray]:
    slope_summary, slope, slope_valid = slope_metrics(raw, candidate, resolution, nodata)
    laplacian, laplacian_valid = absolute_laplacian(candidate, nodata)
    return (
        {
            "elevation": elevation_change_metrics(raw, candidate, nodata),
            "slope_horn_degrees": slope_summary,
            "neighbor_differences": neighbor_metrics(candidate, nodata),
            "absolute_laplacian_m": distribution(laplacian, laplacian_valid),
            "structure_preservation": structure_preservation_metrics(raw, candidate, resolution, nodata),
        },
        slope,
        slope_valid,
    )
