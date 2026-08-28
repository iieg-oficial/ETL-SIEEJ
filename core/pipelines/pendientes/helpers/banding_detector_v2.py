from __future__ import annotations

import math
from typing import Any

import numpy as np

from core.pipelines.pendientes.constants import (
    CALIBRATION_REPETITION_MAX_LAG_PIXELS,
    CALIBRATION_REPETITION_MIN_LAG_PIXELS,
)
from core.pipelines.pendientes.helpers.calibration_profiles import profile_lines_from_raw
from core.pipelines.pendientes.helpers.directed_banding import (
    directed_banding_metrics,
    second_difference_fields,
)


def autocorrelation_curve(
    projection: np.ndarray,
    minimum_lag: int = CALIBRATION_REPETITION_MIN_LAG_PIXELS,
    maximum_lag: int = CALIBRATION_REPETITION_MAX_LAG_PIXELS,
) -> dict[int, float]:
    values = projection.astype(np.float64, copy=False)
    values = values - values.mean()
    if float(np.dot(values, values)) <= np.finfo(float).eps:
        return {lag: 0.0 for lag in range(minimum_lag, min(maximum_lag, values.size - 2) + 1)}
    output: dict[int, float] = {}
    for lag in range(minimum_lag, min(maximum_lag, values.size - 2) + 1):
        denominator = float(np.linalg.norm(values[:-lag]) * np.linalg.norm(values[lag:]))
        output[lag] = float(np.dot(values[:-lag], values[lag:]) / denominator) if denominator else 0.0
    return output


def peak_prominence(curve: dict[int, float]) -> dict[str, float | int]:
    if not curve:
        return {
            "peak_lag_pixels": CALIBRATION_REPETITION_MIN_LAG_PIXELS,
            "peak_autocorrelation": 0.0,
            "local_baseline": 0.0,
            "background_median": 0.0,
            "peak_prominence": 0.0,
        }
    peak_lag, peak = max(curve.items(), key=lambda item: (item[1], -item[0]))
    background = float(np.median(list(curve.values())))
    shoulders = [value for lag, value in curve.items() if 2 <= abs(lag - peak_lag) <= 5]
    local_baseline = float(np.median(shoulders)) if shoulders else background
    return {
        "peak_lag_pixels": peak_lag,
        "peak_autocorrelation": peak,
        "local_baseline": local_baseline,
        "background_median": background,
        "peak_prominence": float(peak - local_baseline),
    }


def _selected_magnitude(
    elevation: np.ndarray,
    nodata: float | None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, float]:
    d2x, d2y, magnitude, valid = second_difference_fields(elevation, nodata)
    threshold = float(np.percentile(magnitude[valid], 90))
    selected = valid & (magnitude >= max(threshold, np.finfo(np.float32).eps))
    return d2x, d2y, magnitude, selected, threshold


def _axis_projection(selected_magnitude: np.ndarray, axis: str) -> np.ndarray:
    return selected_magnitude.sum(axis=0 if axis == "x" else 1)


def lag_stability(
    magnitude: np.ndarray,
    selected: np.ndarray,
    dominant_axis: str | None,
    dominant_lag: int | None,
    subdivisions: int = 4,
    tolerance_pixels: int = 2,
) -> dict[str, Any]:
    if dominant_axis is None or dominant_lag is None:
        return {
            "subwindow_count": subdivisions**2,
            "valid_subwindows": 0,
            "stable_fraction": 0.0,
            "lag_median_pixels": None,
            "lag_mad_pixels": None,
            "lags_pixels": [],
            "tolerance_pixels": tolerance_pixels,
        }
    lags: list[int] = []
    height, width = magnitude.shape
    for row_index in range(subdivisions):
        row_start = row_index * height // subdivisions
        row_end = (row_index + 1) * height // subdivisions
        for column_index in range(subdivisions):
            column_start = column_index * width // subdivisions
            column_end = (column_index + 1) * width // subdivisions
            local = np.where(
                selected[row_start:row_end, column_start:column_end],
                magnitude[row_start:row_end, column_start:column_end],
                0.0,
            )
            curve = autocorrelation_curve(_axis_projection(local, dominant_axis))
            if curve and np.ptp(list(curve.values())) > np.finfo(float).eps:
                lags.append(max(curve.items(), key=lambda item: (item[1], -item[0]))[0])
    if not lags:
        return {
            "subwindow_count": subdivisions**2,
            "valid_subwindows": 0,
            "stable_fraction": 0.0,
            "lag_median_pixels": None,
            "lag_mad_pixels": None,
            "lags_pixels": [],
            "tolerance_pixels": tolerance_pixels,
        }
    lag_values = np.asarray(lags)
    median = float(np.median(lag_values))
    return {
        "subwindow_count": subdivisions**2,
        "valid_subwindows": len(lags),
        "stable_fraction": float(np.count_nonzero(np.abs(lag_values - dominant_lag) <= tolerance_pixels) / len(lags)),
        "lag_median_pixels": median,
        "lag_mad_pixels": float(np.median(np.abs(lag_values - median))),
        "lags_pixels": lags,
        "tolerance_pixels": tolerance_pixels,
    }


def second_difference_anisotropy(
    elevation: np.ndarray,
    nodata: float | None,
    selected: np.ndarray,
) -> dict[str, float]:
    if not selected.any():
        return {"energy_anisotropy": 0.0, "principal_axis_degrees": 0.0, "selected_hessian_cells": 0}
    values = elevation.astype(np.float64, copy=False)
    source_valid = np.isfinite(values)
    if nodata is not None:
        source_valid &= values != nodata
    valid = np.zeros(values.shape, dtype=bool)
    valid[1:-1, 1:-1] = (
        source_valid[1:-1, 1:-1]
        & source_valid[:-2, :-2]
        & source_valid[:-2, 1:-1]
        & source_valid[:-2, 2:]
        & source_valid[1:-1, :-2]
        & source_valid[1:-1, 2:]
        & source_valid[2:, :-2]
        & source_valid[2:, 1:-1]
        & source_valid[2:, 2:]
    )
    cells = selected & valid
    dxx = values[1:-1, 2:] - 2 * values[1:-1, 1:-1] + values[1:-1, :-2]
    dyy = values[2:, 1:-1] - 2 * values[1:-1, 1:-1] + values[:-2, 1:-1]
    dxy = (values[2:, 2:] - values[2:, :-2] - values[:-2, 2:] + values[:-2, :-2]) / 4
    inner_cells = cells[1:-1, 1:-1]
    a = dxx[inner_cells]
    c = dyy[inner_cells]
    b = dxy[inner_cells]
    delta = np.hypot(a - c, 2 * b)
    trace = a + c
    eigenvalue_plus = (trace + delta) / 2
    eigenvalue_minus = (trace - delta) / 2
    angles = 0.5 * np.arctan2(2 * b, a - c)
    use_minus = np.abs(eigenvalue_minus) > np.abs(eigenvalue_plus)
    angles = np.where(use_minus, angles + np.pi / 2, angles)
    weights = np.maximum(np.abs(eigenvalue_plus), np.abs(eigenvalue_minus))
    total = float(weights.sum())
    cosine = float(np.sum(weights * np.cos(2 * angles)) / total) if total else 0.0
    sine = float(np.sum(weights * np.sin(2 * angles)) / total) if total else 0.0
    return {
        "energy_anisotropy": float(np.hypot(cosine, sine)),
        "principal_axis_degrees": float(0.5 * math.degrees(math.atan2(sine, cosine)) % 180),
        "selected_hessian_cells": int(weights.size),
    }


def _line_starts(shape: tuple[int, int], direction: tuple[int, int]) -> list[tuple[int, int]]:
    height, width = shape
    if direction == (0, 1):
        return [(row, 0) for row in range(height)]
    if direction == (1, 0):
        return [(0, column) for column in range(width)]
    if direction == (1, 1):
        return [(0, column) for column in range(width)] + [(row, 0) for row in range(1, height)]
    if direction == (1, -1):
        return [(0, column) for column in range(width)] + [(row, width - 1) for row in range(1, height)]
    raise ValueError(f"Unsupported run direction: {direction}")


def _run_lengths(mask: np.ndarray, direction: tuple[int, int]) -> np.ndarray:
    lengths: list[int] = []
    row_step, column_step = direction
    for start_row, start_column in _line_starts(mask.shape, direction):
        values = []
        row, column = start_row, start_column
        while 0 <= row < mask.shape[0] and 0 <= column < mask.shape[1]:
            values.append(mask[row, column])
            row += row_step
            column += column_step
        line = np.asarray(values, dtype=np.int8)
        padded = np.pad(line, 1)
        changes = np.diff(padded)
        starts = np.flatnonzero(changes == 1)
        ends = np.flatnonzero(changes == -1)
        lengths.extend((ends - starts).tolist())
    return np.asarray(lengths, dtype=np.int32)


def spatial_persistence(selected: np.ndarray, dominant_normal_degrees: float | None) -> dict[str, Any]:
    if dominant_normal_degrees is None or not selected.any():
        return {
            "tangent_direction": None,
            "run_count": 0,
            "long_run_count_ge_4": 0,
            "long_runs_per_million_cells": 0.0,
            "selected_fraction_in_runs_ge_4": 0.0,
            "run_length_pixels": {"p50": 0.0, "p90": 0.0, "p99": 0.0, "maximum": 0},
        }
    tangent = math.radians((dominant_normal_degrees + 90) % 180)
    direction_index = int(round(tangent / (math.pi / 4))) % 4
    directions = ((0, 1), (1, 1), (1, 0), (1, -1))
    direction = directions[direction_index]
    lengths = _run_lengths(selected, direction)
    long = lengths[lengths >= 4]
    selected_count = int(np.count_nonzero(selected))
    return {
        "tangent_direction": list(direction),
        "run_count": int(lengths.size),
        "long_run_count_ge_4": int(long.size),
        "long_runs_per_million_cells": float(long.size / selected.size * 1_000_000),
        "selected_fraction_in_runs_ge_4": float(long.sum() / selected_count) if selected_count else 0.0,
        "run_length_pixels": {
            "p50": float(np.percentile(lengths, 50)),
            "p90": float(np.percentile(lengths, 90)),
            "p99": float(np.percentile(lengths, 99)),
            "maximum": int(lengths.max(initial=0)),
        },
    }


def _local_peak_indices(values: np.ndarray, threshold: float) -> np.ndarray:
    if values.size < 3 or threshold <= np.finfo(float).eps:
        return np.array([], dtype=np.int64)
    return np.flatnonzero(
        (values[1:-1] >= threshold)
        & (values[1:-1] >= values[:-2])
        & (values[1:-1] > values[2:])
    ) + 1


def profile_step_repetition(
    elevation: np.ndarray,
    nodata: float | None,
    offsets: tuple[int, ...] | None = None,
) -> dict[str, Any]:
    if offsets is None:
        spacing = max(1, min(elevation.shape) // 8)
        offsets = tuple(multiplier * spacing for multiplier in (-3, -2, -1, 0, 1, 2, 3))
    try:
        lines, contract = profile_lines_from_raw(elevation, nodata, offsets)
    except ValueError:
        return {
            "profile_count": 0,
            "profiles_with_three_or_more_steps": 0,
            "strong_step_threshold_m": 0.0,
            "strong_step_count": 0,
            "spacing_pixels": {"median": None, "iqr": None, "coefficient_of_variation": None},
            "amplitude_coefficient_of_variation": None,
            "profiles": [],
        }
    differences = []
    per_profile = []
    for line in lines:
        values = elevation[np.asarray(line.rows), np.asarray(line.columns)].astype(np.float64)
        absolute = np.abs(np.diff(values))
        differences.append(absolute)
        per_profile.append((line.profile_id, absolute))
    threshold = float(np.percentile(np.concatenate(differences), 90))
    all_spacings: list[float] = []
    all_amplitudes: list[float] = []
    profiles = []
    for profile_id, absolute in per_profile:
        peaks = _local_peak_indices(absolute, threshold)
        spacings = np.diff(peaks).astype(np.float64)
        amplitudes = absolute[peaks]
        all_spacings.extend(spacings.tolist())
        all_amplitudes.extend(amplitudes.tolist())
        profiles.append(
            {
                "profile_id": profile_id,
                "strong_step_count": int(peaks.size),
                "median_spacing_pixels": float(np.median(spacings)) if spacings.size else None,
            }
        )
    spacing = np.asarray(all_spacings)
    amplitude = np.asarray(all_amplitudes)
    spacing_mean = float(spacing.mean()) if spacing.size else 0.0
    amplitude_mean = float(amplitude.mean()) if amplitude.size else 0.0
    return {
        "profile_count": len(lines),
        "profile_contract": contract,
        "profiles_with_three_or_more_steps": sum(item["strong_step_count"] >= 3 for item in profiles),
        "strong_step_threshold_m": threshold,
        "strong_step_count": int(amplitude.size),
        "spacing_pixels": {
            "median": float(np.median(spacing)) if spacing.size else None,
            "iqr": float(np.percentile(spacing, 75) - np.percentile(spacing, 25)) if spacing.size else None,
            "coefficient_of_variation": float(spacing.std() / spacing_mean) if spacing_mean else None,
        },
        "amplitude_coefficient_of_variation": float(amplitude.std() / amplitude_mean) if amplitude_mean else None,
        "profiles": profiles,
    }


def detector_v2_metrics(elevation: np.ndarray, nodata: float | None) -> dict[str, Any]:
    current, magnitude, valid = directed_banding_metrics(elevation, nodata)
    _, _, _, selected, threshold = _selected_magnitude(elevation, nodata)
    selected_magnitude = np.where(selected, magnitude, 0.0)
    curves = {
        axis: autocorrelation_curve(_axis_projection(selected_magnitude, axis)) for axis in ("x", "y")
    }
    prominences = {axis: peak_prominence(curve) for axis, curve in curves.items()}
    dominant_axis = max(
        prominences,
        key=lambda axis: (prominences[axis]["peak_autocorrelation"], axis == "x"),
    )
    dominant = prominences[dominant_axis]
    normal = current["orientation"]["dominant_normal_degrees"]
    return {
        "current": current,
        "peak_prominence": {"dominant_axis": dominant_axis, **dominant, "by_axis": prominences},
        "lag_stability": lag_stability(
            magnitude,
            selected,
            dominant_axis,
            int(dominant["peak_lag_pixels"]),
        ),
        "anisotropy": second_difference_anisotropy(elevation, nodata, selected),
        "spatial_persistence": spatial_persistence(selected, normal),
        "profile_step_repetition": profile_step_repetition(elevation, nodata),
        "reference_threshold_m": threshold,
        "valid_second_difference_cells": int(np.count_nonzero(valid)),
        "no_weighted_score": True,
    }
