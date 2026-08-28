from __future__ import annotations

from typing import Any

import numpy as np
from affine import Affine
from pyproj import CRS

from core.pipelines.pendientes.constants import EXPERIMENT_METRICS


def _valid_values(values: np.ndarray, nodata: float | None) -> tuple[np.ndarray, int]:
    valid = np.isfinite(values)
    if nodata is not None:
        valid &= values != nodata
    return values[valid].astype(np.float64, copy=False), int(values.size - np.count_nonzero(valid))


def distribution_summary(values: np.ndarray, nodata: float | None = None, histogram_bins: int = 32) -> dict[str, Any]:
    if histogram_bins < 2:
        raise ValueError("Histogram requires at least two bins")
    valid, nodata_count = _valid_values(values, nodata)
    if not valid.size:
        raise ValueError("Distribution has no valid values")
    counts, edges = np.histogram(valid, bins=histogram_bins)
    return {
        "valid_count": int(valid.size),
        "nodata_count": nodata_count,
        "minimum": float(valid.min()),
        "maximum": float(valid.max()),
        "mean": float(valid.mean()),
        "stddev": float(valid.std()),
        "p50": float(np.percentile(valid, 50)),
        "p90": float(np.percentile(valid, 90)),
        "p95": float(np.percentile(valid, 95)),
        "p99": float(np.percentile(valid, 99)),
        "histogram": {"bin_edges": edges.tolist(), "counts": counts.tolist()},
    }


def valid_surface_area_m2(
    values: np.ndarray,
    nodata: float | None,
    transform: Affine,
    crs: str | CRS,
) -> float:
    valid = np.isfinite(values)
    if nodata is not None:
        valid &= values != nodata
    reference = CRS.from_user_input(crs)
    if transform.b or transform.d:
        raise ValueError("Valid-surface QA requires a north-up grid")
    if reference.is_projected:
        conversion_factors = [axis.unit_conversion_factor or 1.0 for axis in reference.axis_info[:2]]
        pixel_area_m2 = abs(transform.a * transform.e) * conversion_factors[0] * conversion_factors[1]
        return float(np.count_nonzero(valid) * pixel_area_m2)
    if not reference.is_geographic:
        raise ValueError("Valid-surface QA requires a geographic or projected CRS")

    geod = reference.get_geod()
    total_area = 0.0
    left = transform.c
    right = transform.c + transform.a
    for row in range(values.shape[0]):
        valid_columns = int(np.count_nonzero(valid[row]))
        if not valid_columns:
            continue
        top = transform.f + row * transform.e
        bottom = top + transform.e
        area, _ = geod.polygon_area_perimeter(
            [left, right, right, left],
            [top, top, bottom, bottom],
        )
        total_area += abs(area) * valid_columns
    return float(total_area)


def reprojection_surface_metrics(
    source_window: np.ndarray,
    target_window: np.ndarray,
    source_transform: Affine,
    source_crs: str | CRS,
    target_transform: Affine,
    target_crs: str | CRS,
    source_nodata: float | None,
    target_nodata: float | None,
    histogram_bins: int = 32,
) -> dict[str, Any]:
    """Compare distributions over one footprint without pairing different grids by index."""
    source_summary = distribution_summary(source_window, source_nodata, histogram_bins)
    target_summary = distribution_summary(target_window, target_nodata, histogram_bins)
    return {
        "comparison_strategy": (
            "independent native-grid summaries over the same geospatial footprint; "
            "no direct pixel-index comparison between EPSG:6365 and EPSG:6368"
        ),
        "source": {
            **source_summary,
            "valid_surface_m2": valid_surface_area_m2(
                source_window,
                source_nodata,
                source_transform,
                source_crs,
            ),
            "area_method": "geodesic for geographic CRS; CRS unit conversion for projected CRS",
        },
        "target": {
            **target_summary,
            "valid_surface_m2": valid_surface_area_m2(
                target_window,
                target_nodata,
                target_transform,
                target_crs,
            ),
        },
        "visual_review": {
            "flat_terrain": None,
            "mountain_terrain": None,
            "status": "requires reproducible real-CEM test windows",
        },
        "controlled_future_resampling_comparison": None,
    }


def conditioning_metrics(
    baseline_elevation: np.ndarray,
    candidate_elevation: np.ndarray,
    candidate_slope: np.ndarray,
    nodata: float | None = None,
    histogram_bins: int = 32,
) -> dict[str, Any]:
    if baseline_elevation.shape != candidate_elevation.shape or baseline_elevation.shape != candidate_slope.shape:
        raise ValueError("Experimental arrays must share a grid")
    valid = np.isfinite(baseline_elevation) & np.isfinite(candidate_elevation) & np.isfinite(candidate_slope)
    if nodata is not None:
        valid &= (baseline_elevation != nodata) & (candidate_elevation != nodata) & (candidate_slope != nodata)
    if not valid.any():
        raise ValueError("Experiment has no common valid pixels")
    differences = candidate_elevation[valid].astype(np.float64) - baseline_elevation[valid].astype(np.float64)
    absolute_differences = np.abs(differences)
    slopes = candidate_slope[valid].astype(np.float64)
    slope_counts, slope_edges = np.histogram(slopes, bins=histogram_bins)
    rmse = float(np.sqrt(np.mean(np.square(differences))))
    return {
        "elevation_difference": {
            "min": float(differences.min()),
            "max": float(differences.max()),
            "mean": float(differences.mean()),
        },
        "mae": float(absolute_differences.mean()),
        "rmse": rmse,
        "rmse_against_reprojected_dem": rmse,
        "bias": float(differences.mean()),
        "maximum_absolute": float(absolute_differences.max()),
        "absolute_difference_percentiles": {
            "p50": float(np.percentile(absolute_differences, 50)),
            "p90": float(np.percentile(absolute_differences, 90)),
            "p95": float(np.percentile(absolute_differences, 95)),
            "p99": float(np.percentile(absolute_differences, 99)),
            "maximum": float(absolute_differences.max()),
        },
        "slope_distribution": {
            "p50": float(np.percentile(slopes, 50)),
            "p90": float(np.percentile(slopes, 90)),
            "p95": float(np.percentile(slopes, 95)),
            "p99": float(np.percentile(slopes, 99)),
            "maximum": float(slopes.max()),
            "mean": float(slopes.mean()),
            "stddev": float(slopes.std()),
            "histogram": {"bin_edges": slope_edges.tolist(), "counts": slope_counts.tolist()},
        },
        "modified_pixel_percentage": float(np.count_nonzero(differences) / differences.size * 100),
        "ridge_preservation": None,
        "gully_preservation": None,
        "banding_reduction": None,
        "flat_terrain_behavior": None,
        "mountain_terrain_behavior": None,
        "pending_metric_definitions": [
            metric
            for metric in EXPERIMENT_METRICS
            if metric in {"ridge_preservation", "gully_preservation", "banding_reduction"}
        ],
    }


def validate_slope_pair(degrees: np.ndarray, percentage: np.ndarray, valid: np.ndarray, atol: float = 1e-5) -> None:
    if degrees.shape != percentage.shape or degrees.shape != valid.shape:
        raise ValueError("Slope products and valid mask must share a grid")
    expected_percentage = np.tan(np.radians(degrees[valid].astype(np.float64))) * 100.0
    if not np.allclose(percentage[valid], expected_percentage, atol=atol, rtol=atol):
        raise ValueError("Degree and percent slope products are not mathematically consistent")
