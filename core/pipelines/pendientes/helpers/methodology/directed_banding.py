from __future__ import annotations

from typing import Any

import numpy as np

from core.pipelines.pendientes.constants import (
    CALIBRATION_BANDING_REFERENCE_PERCENTILE,
    CALIBRATION_REPETITION_MAX_LAG_PIXELS,
    CALIBRATION_REPETITION_MIN_LAG_PIXELS,
)
from core.pipelines.pendientes.helpers.experimental_metrics import valid_mask


def second_difference_fields(
    elevation: np.ndarray,
    nodata: float | None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    if elevation.ndim != 2:
        raise ValueError("Elevation array must be two-dimensional")
    values = elevation.astype(np.float64, copy=False)
    source_valid = valid_mask(values, nodata)
    d2x = np.full(values.shape, np.nan, dtype=np.float64)
    d2y = np.full(values.shape, np.nan, dtype=np.float64)
    valid = np.zeros(values.shape, dtype=bool)
    if min(values.shape) < 3:
        return d2x, d2y, np.full(values.shape, np.nan), valid
    inner_valid = (
        source_valid[1:-1, 1:-1]
        & source_valid[1:-1, :-2]
        & source_valid[1:-1, 2:]
        & source_valid[:-2, 1:-1]
        & source_valid[2:, 1:-1]
    )
    inner_d2x = values[1:-1, 2:] - 2 * values[1:-1, 1:-1] + values[1:-1, :-2]
    inner_d2y = values[2:, 1:-1] - 2 * values[1:-1, 1:-1] + values[:-2, 1:-1]
    inner_d2x[~inner_valid] = np.nan
    inner_d2y[~inner_valid] = np.nan
    d2x[1:-1, 1:-1] = inner_d2x
    d2y[1:-1, 1:-1] = inner_d2y
    valid[1:-1, 1:-1] = inner_valid
    magnitude = np.hypot(d2x, d2y)
    return d2x, d2y, magnitude, valid


def _axial_orientation(d2x: np.ndarray, d2y: np.ndarray, selected: np.ndarray) -> dict[str, float]:
    angles = np.arctan2(d2y[selected], d2x[selected])
    cosine = float(np.mean(np.cos(2 * angles)))
    sine = float(np.mean(np.sin(2 * angles)))
    dominant = 0.5 * np.arctan2(sine, cosine)
    return {
        "coherence": float(np.hypot(cosine, sine)),
        "dominant_normal_degrees": float(np.degrees(dominant) % 180),
    }


def _shift_without_wrap(mask: np.ndarray, row_offset: int, column_offset: int) -> np.ndarray:
    shifted = np.zeros(mask.shape, dtype=bool)
    source_row_start = max(0, -row_offset)
    source_row_end = mask.shape[0] - max(0, row_offset)
    source_column_start = max(0, -column_offset)
    source_column_end = mask.shape[1] - max(0, column_offset)
    target_row_start = max(0, row_offset)
    target_row_end = target_row_start + source_row_end - source_row_start
    target_column_start = max(0, column_offset)
    target_column_end = target_column_start + source_column_end - source_column_start
    shifted[target_row_start:target_row_end, target_column_start:target_column_end] = mask[
        source_row_start:source_row_end,
        source_column_start:source_column_end,
    ]
    return shifted


def _tangent_continuity(
    d2x: np.ndarray,
    d2y: np.ndarray,
    selected: np.ndarray,
) -> dict[str, float]:
    normal_angle = np.arctan2(d2y, d2x)
    tangent_angle = np.mod(normal_angle + np.pi / 2, np.pi)
    safe_tangent_angle = np.where(np.isfinite(tangent_angle), tangent_angle, 0.0)
    direction_index = np.mod(np.rint(safe_tangent_angle / (np.pi / 4)).astype(np.int8), 4)
    supported = np.zeros(selected.shape, dtype=bool)
    directions = ((0, 1), (1, 1), (1, 0), (1, -1))
    for index, (row_offset, column_offset) in enumerate(directions):
        direction_cells = selected & (direction_index == index)
        forward = _shift_without_wrap(selected, row_offset, column_offset)
        backward = _shift_without_wrap(selected, -row_offset, -column_offset)
        supported |= direction_cells & (forward | backward)
    return {
        "supported_cells": int(np.count_nonzero(supported)),
        "support_percentage": float(np.count_nonzero(supported) / np.count_nonzero(selected) * 100),
    }


def _autocorrelation(projection: np.ndarray, minimum_lag: int, maximum_lag: int) -> dict[str, float | int]:
    values = projection.astype(np.float64, copy=False)
    values = values - values.mean()
    variance = float(np.dot(values, values))
    if variance <= np.finfo(float).eps:
        return {"maximum_positive_autocorrelation": 0.0, "lag_pixels": minimum_lag}
    available_maximum = min(maximum_lag, values.size - 2)
    correlations = []
    for lag in range(minimum_lag, available_maximum + 1):
        denominator = float(np.linalg.norm(values[:-lag]) * np.linalg.norm(values[lag:]))
        correlation = float(np.dot(values[:-lag], values[lag:]) / denominator) if denominator else 0.0
        correlations.append((correlation, lag))
    maximum = max(correlations, key=lambda item: (item[0], -item[1]))
    return {"maximum_positive_autocorrelation": maximum[0], "lag_pixels": maximum[1]}


def directed_banding_metrics(
    elevation: np.ndarray,
    nodata: float | None,
    reference_threshold_m: float | None = None,
) -> tuple[dict[str, Any], np.ndarray, np.ndarray]:
    d2x, d2y, magnitude, valid = second_difference_fields(elevation, nodata)
    values = magnitude[valid]
    if not values.size:
        raise ValueError("Banding metric has no valid second-difference cells")
    threshold = (
        float(np.percentile(values, CALIBRATION_BANDING_REFERENCE_PERCENTILE))
        if reference_threshold_m is None
        else reference_threshold_m
    )
    numerical_floor = np.finfo(np.float32).eps
    selected = valid & (magnitude >= max(threshold, numerical_floor))
    if not selected.any():
        empty = {
            "reference_threshold_m": threshold,
            "high_second_difference_percentage": 0.0,
            "orientation": {"coherence": 0.0, "dominant_normal_degrees": None},
            "tangent_continuity": {"supported_cells": 0, "support_percentage": 0.0},
            "repetition": {
                "x": {"maximum_positive_autocorrelation": 0.0, "lag_pixels": None},
                "y": {"maximum_positive_autocorrelation": 0.0, "lag_pixels": None},
                "dominant_axis": None,
            },
        }
        return empty, magnitude, valid

    selected_magnitude = np.where(selected, magnitude, 0.0)
    x_repetition = _autocorrelation(
        selected_magnitude.sum(axis=0),
        CALIBRATION_REPETITION_MIN_LAG_PIXELS,
        CALIBRATION_REPETITION_MAX_LAG_PIXELS,
    )
    y_repetition = _autocorrelation(
        selected_magnitude.sum(axis=1),
        CALIBRATION_REPETITION_MIN_LAG_PIXELS,
        CALIBRATION_REPETITION_MAX_LAG_PIXELS,
    )
    dominant_axis = (
        "x"
        if x_repetition["maximum_positive_autocorrelation"] >= y_repetition["maximum_positive_autocorrelation"]
        else "y"
    )
    return (
        {
            "reference_threshold_m": threshold,
            "reference_threshold_source": (
                f"RAW p{CALIBRATION_BANDING_REFERENCE_PERCENTILE:g} second-difference magnitude"
            ),
            "high_second_difference_cells": int(np.count_nonzero(selected)),
            "high_second_difference_percentage": float(np.count_nonzero(selected) / np.count_nonzero(valid) * 100),
            "orientation": _axial_orientation(d2x, d2y, selected),
            "tangent_continuity": _tangent_continuity(d2x, d2y, selected),
            "repetition": {
                "x": x_repetition,
                "y": y_repetition,
                "dominant_axis": dominant_axis,
            },
            "interpretation": (
                "component signature only: density, axial coherence, tangent continuity and projection "
                "autocorrelation are reported separately; no weighted score or acceptance threshold"
            ),
        },
        magnitude,
        valid,
    )
