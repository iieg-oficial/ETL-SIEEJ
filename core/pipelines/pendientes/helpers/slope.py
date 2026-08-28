from __future__ import annotations

import numpy as np


def slope_products_from_gradient(
    dz_dx: np.ndarray,
    dz_dy: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Derive both canonical units from one gradient magnitude."""
    rise_run = np.hypot(dz_dx, dz_dy)
    degrees = np.degrees(np.arctan(rise_run))
    percentage = rise_run * 100.0
    return degrees.astype(np.float32), percentage.astype(np.float32)


def horn_gradient(
    elevation: np.ndarray,
    resolution: float,
    nodata: float | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Evaluate the initial Horn candidate on an in-memory synthetic/sampled DEM.

    It is intentionally not wired into the production Transform stage in phase 1.
    """
    if elevation.ndim != 2:
        raise ValueError("Elevation array must be two-dimensional")
    if resolution <= 0:
        raise ValueError("Resolution must be positive")
    values = elevation.astype(np.float64, copy=False)
    valid = np.isfinite(values)
    if nodata is not None:
        valid &= values != nodata

    dz_dx = np.full(values.shape, np.nan, dtype=np.float64)
    dz_dy = np.full(values.shape, np.nan, dtype=np.float64)
    output_valid = np.zeros(values.shape, dtype=bool)
    if values.shape[0] < 3 or values.shape[1] < 3:
        return dz_dx, dz_dy, output_valid

    windows_valid = np.ones((values.shape[0] - 2, values.shape[1] - 2), dtype=bool)
    for row_offset in range(3):
        for column_offset in range(3):
            windows_valid &= valid[
                row_offset : row_offset + windows_valid.shape[0],
                column_offset : column_offset + windows_valid.shape[1],
            ]

    z1, z2, z3 = values[:-2, :-2], values[:-2, 1:-1], values[:-2, 2:]
    z4, z6 = values[1:-1, :-2], values[1:-1, 2:]
    z7, z8, z9 = values[2:, :-2], values[2:, 1:-1], values[2:, 2:]
    inner_dx = ((z3 + 2 * z6 + z9) - (z1 + 2 * z4 + z7)) / (8 * resolution)
    inner_dy = ((z7 + 2 * z8 + z9) - (z1 + 2 * z2 + z3)) / (8 * resolution)
    inner_dx[~windows_valid] = np.nan
    inner_dy[~windows_valid] = np.nan
    dz_dx[1:-1, 1:-1] = inner_dx
    dz_dy[1:-1, 1:-1] = inner_dy
    output_valid[1:-1, 1:-1] = windows_valid
    return dz_dx, dz_dy, output_valid


def experimental_horn_slope(
    elevation: np.ndarray,
    resolution: float,
    nodata: float | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    dz_dx, dz_dy, valid = horn_gradient(elevation, resolution, nodata)
    degrees, percentage = slope_products_from_gradient(dz_dx, dz_dy)
    return degrees, percentage, valid
