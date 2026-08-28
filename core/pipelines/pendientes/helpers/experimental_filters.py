from __future__ import annotations

import math

import numpy as np


def _valid_mask(values: np.ndarray, nodata: float | None) -> np.ndarray:
    valid = np.isfinite(values)
    if nodata is not None:
        valid &= values != nodata
    return valid


def _shift_reflect(values: np.ndarray, row_offset: int, column_offset: int) -> np.ndarray:
    row_radius = abs(row_offset)
    column_radius = abs(column_offset)
    padded = np.pad(values, ((row_radius, row_radius), (column_radius, column_radius)), mode="reflect")
    row_start = row_radius + row_offset
    column_start = column_radius + column_offset
    return padded[row_start : row_start + values.shape[0], column_start : column_start + values.shape[1]]


def gaussian_smoothing(
    elevation: np.ndarray,
    sigma_pixels: float,
    nodata: float | None = None,
) -> np.ndarray:
    if elevation.ndim != 2:
        raise ValueError("Elevation array must be two-dimensional")
    if sigma_pixels <= 0:
        raise ValueError("Gaussian sigma must be positive")
    values = elevation.astype(np.float64, copy=False)
    valid = _valid_mask(values, nodata)
    radius = max(1, math.ceil(3 * sigma_pixels))
    offsets = np.arange(-radius, radius + 1, dtype=np.int32)
    weights = np.exp(-0.5 * np.square(offsets / sigma_pixels))
    weights /= weights.sum()

    numerator = np.where(valid, values, 0.0)
    denominator = valid.astype(np.float64)
    for axis in (1, 0):
        filtered_values = np.zeros(values.shape, dtype=np.float64)
        filtered_weights = np.zeros(values.shape, dtype=np.float64)
        for offset, weight in zip(offsets, weights, strict=True):
            row_offset = int(offset) if axis == 0 else 0
            column_offset = int(offset) if axis == 1 else 0
            filtered_values += weight * _shift_reflect(numerator, row_offset, column_offset)
            filtered_weights += weight * _shift_reflect(denominator, row_offset, column_offset)
        numerator = filtered_values
        denominator = filtered_weights

    output = np.full(values.shape, nodata if nodata is not None else np.nan, dtype=np.float32)
    output[valid] = (numerator[valid] / denominator[valid]).astype(np.float32)
    return output


def bilateral_smoothing(
    elevation: np.ndarray,
    sigma_dist_pixels: float,
    sigma_int_m: float,
    nodata: float | None = None,
) -> np.ndarray:
    if elevation.ndim != 2:
        raise ValueError("Elevation array must be two-dimensional")
    if sigma_dist_pixels <= 0 or sigma_int_m <= 0:
        raise ValueError("Bilateral sigmas must be positive")
    values = elevation.astype(np.float64, copy=False)
    valid = _valid_mask(values, nodata)
    radius = max(1, math.ceil(3 * sigma_dist_pixels))
    numerator = np.zeros(values.shape, dtype=np.float64)
    denominator = np.zeros(values.shape, dtype=np.float64)
    padded_values = np.pad(values, radius, mode="reflect")
    padded_valid = np.pad(valid, radius, mode="reflect")

    for row_offset in range(-radius, radius + 1):
        for column_offset in range(-radius, radius + 1):
            row_start = radius + row_offset
            column_start = radius + column_offset
            shifted_values = padded_values[
                row_start : row_start + values.shape[0],
                column_start : column_start + values.shape[1],
            ]
            shifted_valid = padded_valid[
                row_start : row_start + values.shape[0],
                column_start : column_start + values.shape[1],
            ]
            spatial_weight = math.exp(
                -(row_offset * row_offset + column_offset * column_offset) / (2 * sigma_dist_pixels**2)
            )
            elevation_difference = np.where(shifted_valid & valid, shifted_values - values, 0.0)
            intensity_weight = np.exp(-np.square(elevation_difference) / (2 * sigma_int_m**2))
            weights = spatial_weight * intensity_weight * shifted_valid
            numerator += weights * np.where(shifted_valid, shifted_values, 0.0)
            denominator += weights

    output = np.full(values.shape, nodata if nodata is not None else np.nan, dtype=np.float32)
    output[valid] = (numerator[valid] / denominator[valid]).astype(np.float32)
    return output
