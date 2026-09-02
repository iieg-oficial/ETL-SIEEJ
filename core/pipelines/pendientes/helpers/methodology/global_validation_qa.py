from __future__ import annotations

from typing import Any

import numpy as np

from core.pipelines.pendientes.helpers.methodology.directed_banding import second_difference_fields
from core.pipelines.pendientes.helpers.experimental_metrics import valid_mask
from core.pipelines.pendientes.helpers.slope import experimental_horn_slope, horn_gradient


def _percentiles(values: np.ndarray, percentiles: tuple[int, ...]) -> dict[str, float]:
    return {f"p{percentile:02d}": float(np.percentile(values, percentile)) for percentile in percentiles}


def _distribution(values: np.ndarray) -> dict[str, float]:
    selected = values[np.isfinite(values)].astype(np.float64, copy=False)
    if not selected.size:
        raise ValueError("Distribution has no finite values")
    return {
        "mean": float(selected.mean()),
        "stddev": float(selected.std()),
        **_percentiles(selected, (50, 75, 90, 95, 99)),
        "maximum": float(selected.max()),
    }


def comparative_candidate_qa(
    raw: np.ndarray,
    candidate: np.ndarray,
    resolution_m: float,
    nodata: float | None,
) -> dict[str, Any]:
    if raw.shape != candidate.shape:
        raise ValueError("RAW and candidate must share a grid")
    common = valid_mask(raw, nodata) & valid_mask(candidate, nodata)
    differences = candidate[common].astype(np.float64) - raw[common].astype(np.float64)
    absolute = np.abs(differences)
    if not absolute.size:
        raise ValueError("Candidate comparison has no common valid pixels")

    raw_slope, _, raw_slope_valid = experimental_horn_slope(raw, resolution_m, nodata)
    candidate_slope, _, candidate_slope_valid = experimental_horn_slope(candidate, resolution_m, nodata)
    slope_common = raw_slope_valid & candidate_slope_valid
    slope_difference = candidate_slope[slope_common].astype(np.float64) - raw_slope[slope_common].astype(np.float64)
    slope_absolute = np.abs(slope_difference)

    raw_dx, raw_dy, raw_gradient_valid = horn_gradient(raw, resolution_m, nodata)
    candidate_dx, candidate_dy, candidate_gradient_valid = horn_gradient(candidate, resolution_m, nodata)
    gradient_common = raw_gradient_valid & candidate_gradient_valid
    raw_gradient = np.hypot(raw_dx, raw_dy)
    candidate_gradient = np.hypot(candidate_dx, candidate_dy)
    strong_threshold = float(np.percentile(raw_gradient[raw_gradient_valid], 90))
    strong = gradient_common & (raw_gradient >= strong_threshold) & (raw_gradient > 0)
    gradient_ratios = candidate_gradient[strong] / raw_gradient[strong]

    raw_normals = np.stack(
        (-raw_dx[gradient_common], -raw_dy[gradient_common], np.ones(np.count_nonzero(gradient_common))),
        axis=1,
    )
    candidate_normals = np.stack(
        (
            -candidate_dx[gradient_common],
            -candidate_dy[gradient_common],
            np.ones(np.count_nonzero(gradient_common)),
        ),
        axis=1,
    )
    raw_normals /= np.linalg.norm(raw_normals, axis=1, keepdims=True)
    candidate_normals /= np.linalg.norm(candidate_normals, axis=1, keepdims=True)
    angular = np.degrees(np.arccos(np.clip(np.sum(raw_normals * candidate_normals, axis=1), -1.0, 1.0)))

    _, _, raw_second, raw_second_valid = second_difference_fields(raw, nodata)
    _, _, candidate_second, candidate_second_valid = second_difference_fields(candidate, nodata)
    raw_second_values = raw_second[raw_second_valid].astype(np.float64)
    candidate_second_values = candidate_second[candidate_second_valid].astype(np.float64)
    raw_second_summary = _distribution(raw_second_values)
    candidate_second_summary = _distribution(candidate_second_values)
    ratios = {
        key: float(candidate_second_summary[key] / raw_second_summary[key])
        for key in ("mean", "p50", "p90", "p95", "p99")
        if raw_second_summary[key] > 0
    }

    return {
        "elevation": {
            "bias_m": float(differences.mean()),
            "mae_m": float(absolute.mean()),
            "rmse_m": float(np.sqrt(np.mean(np.square(differences)))),
            "absolute_difference_m": {
                **_percentiles(absolute, (50, 90, 95, 99)),
                "maximum": float(absolute.max()),
            },
            "threshold_percentages": {
                f"abs_change_gt_{threshold:.2f}_m": float(np.count_nonzero(absolute > threshold) / absolute.size * 100)
                for threshold in (0.10, 0.25, 0.50)
            },
            "modified_pixel_percentage": float(np.count_nonzero(absolute > 1e-6) / absolute.size * 100),
        },
        "slope_horn_degrees": {
            "candidate": _distribution(candidate_slope[candidate_slope_valid]),
            "difference_from_raw": {
                "bias": float(slope_difference.mean()),
                "mae": float(slope_absolute.mean()),
                "rmse": float(np.sqrt(np.mean(np.square(slope_difference)))),
                "p95_absolute": float(np.percentile(slope_absolute, 95)),
                "p99_absolute": float(np.percentile(slope_absolute, 99)),
            },
            "exploratory_not_productive": True,
        },
        "morphology": {
            "strong_gradient": {
                "raw_p90_threshold_rise_run": strong_threshold,
                "ratio_candidate_to_raw": {
                    "p05": float(np.percentile(gradient_ratios, 5)),
                    "median": float(np.median(gradient_ratios)),
                    "p95": float(np.percentile(gradient_ratios, 95)),
                },
            },
            "surface_normal_difference_degrees": {
                **_percentiles(angular, (50, 90, 95, 99)),
                "maximum": float(angular.max()),
            },
        },
        "second_difference_magnitude_m": {
            "raw": raw_second_summary,
            "candidate": candidate_second_summary,
            "candidate_to_raw_ratio": ratios,
            "internal_p90_density_used_for_decision": False,
        },
    }


def profile_attenuation_metrics(
    raw_values: np.ndarray,
    candidate_values: np.ndarray,
) -> dict[str, float | int]:
    if raw_values.shape != candidate_values.shape or raw_values.size < 3:
        raise ValueError("Profile series must share shape and contain at least three samples")
    raw_steps = np.abs(np.diff(raw_values.astype(np.float64)))
    candidate_steps = np.abs(np.diff(candidate_values.astype(np.float64)))
    threshold = float(np.percentile(raw_steps, 90))
    strong = raw_steps >= threshold
    if not np.count_nonzero(strong):
        raise ValueError("Profile contains no strong RAW steps")
    ratios = candidate_steps[strong] / np.maximum(raw_steps[strong], np.finfo(np.float64).eps)
    delta = candidate_values.astype(np.float64) - raw_values.astype(np.float64)
    return {
        "raw_strong_step_threshold_m": threshold,
        "raw_strong_step_count": int(np.count_nonzero(strong)),
        "candidate_steps_above_raw_threshold_count": int(np.count_nonzero(candidate_steps >= threshold)),
        "strong_step_amplitude_raw_mean_m": float(raw_steps[strong].mean()),
        "strong_step_amplitude_candidate_mean_m": float(candidate_steps[strong].mean()),
        "strong_step_amplitude_candidate_to_raw_median": float(np.median(ratios)),
        "strong_step_retained_above_half_percentage": float(np.count_nonzero(ratios >= 0.5) / ratios.size * 100),
        "endpoint_trend_error_m": float(delta[-1] - delta[0]),
        "mean_z_change_m": float(delta.mean()),
        "maximum_absolute_z_change_m": float(np.abs(delta).max()),
    }


def _aggregate(values: list[float]) -> dict[str, float]:
    array = np.asarray(values, dtype=np.float64)
    return {
        "median": float(np.median(array)),
        "p95": float(np.percentile(array, 95)),
        "minimum": float(array.min()),
        "maximum": float(array.max()),
    }


def aggregate_candidate_metrics(
    chip_results: dict[str, dict[str, Any]],
    candidate_id: str,
    morphology: str | None = None,
) -> dict[str, Any]:
    selected = [
        item
        for item in chip_results.values()
        if morphology is None or item["chip"]["morphology_class"] == morphology
    ]
    if not selected:
        raise ValueError(f"No results for morphology {morphology!r}")

    def values(path: tuple[str, ...]) -> list[float]:
        output = []
        for item in selected:
            value: Any = item["candidates"][candidate_id]["qa"]
            for key in path:
                value = value[key]
            output.append(float(value))
        return output

    return {
        "chip_count": len(selected),
        "bias_z_m": _aggregate(values(("elevation", "bias_m"))),
        "mae_z_m": _aggregate(values(("elevation", "mae_m"))),
        "rmse_z_m": _aggregate(values(("elevation", "rmse_m"))),
        "absolute_difference_z_m": {
            key: _aggregate(values(("elevation", "absolute_difference_m", key)))
            for key in ("p50", "p90", "p95", "p99", "maximum")
        },
        "percentage_abs_change_gt_0.10_m": _aggregate(
            values(("elevation", "threshold_percentages", "abs_change_gt_0.10_m"))
        ),
        "slope_mae_degrees": _aggregate(values(("slope_horn_degrees", "difference_from_raw", "mae"))),
        "slope_candidate_distribution": {
            key: _aggregate(values(("slope_horn_degrees", "candidate", key)))
            for key in ("mean", "stddev", "p50", "p90", "p95", "p99", "maximum")
        },
        "slope_difference_from_raw": {
            key: _aggregate(values(("slope_horn_degrees", "difference_from_raw", key)))
            for key in ("bias", "mae", "rmse", "p95_absolute", "p99_absolute")
        },
        "normal_difference_degrees": {
            key: _aggregate(values(("morphology", "surface_normal_difference_degrees", key)))
            for key in ("p50", "p90", "p95", "p99")
        },
        "normal_p95_degrees": _aggregate(values(("morphology", "surface_normal_difference_degrees", "p95"))),
        "strong_gradient_ratio_p05": _aggregate(
            values(("morphology", "strong_gradient", "ratio_candidate_to_raw", "p05"))
        ),
        "strong_gradient_ratio_median": _aggregate(
            values(("morphology", "strong_gradient", "ratio_candidate_to_raw", "median"))
        ),
        "strong_gradient_ratio_p95": _aggregate(
            values(("morphology", "strong_gradient", "ratio_candidate_to_raw", "p95"))
        ),
        "second_difference_mean_ratio": _aggregate(
            values(("second_difference_magnitude_m", "candidate_to_raw_ratio", "mean"))
        ),
        "second_difference_p50_ratio": _aggregate(
            values(("second_difference_magnitude_m", "candidate_to_raw_ratio", "p50"))
        ),
        "second_difference_p90_ratio": _aggregate(
            values(("second_difference_magnitude_m", "candidate_to_raw_ratio", "p90"))
        ),
        "second_difference_p95_ratio": _aggregate(
            values(("second_difference_magnitude_m", "candidate_to_raw_ratio", "p95"))
        ),
        "second_difference_p99_ratio": _aggregate(
            values(("second_difference_magnitude_m", "candidate_to_raw_ratio", "p99"))
        ),
        "percentage_abs_change_gt_0.25_m": _aggregate(
            values(("elevation", "threshold_percentages", "abs_change_gt_0.25_m"))
        ),
        "percentage_abs_change_gt_0.50_m": _aggregate(
            values(("elevation", "threshold_percentages", "abs_change_gt_0.50_m"))
        ),
    }


def candidate_outliers(chip_results: dict[str, dict[str, Any]], candidate_id: str) -> dict[str, Any]:
    def ranked(path: tuple[str, ...], reverse: bool = True) -> list[dict[str, Any]]:
        output = []
        for chip_id, item in chip_results.items():
            value: Any = item["candidates"][candidate_id]["qa"]
            for key in path:
                value = value[key]
            output.append(
                {
                    "chip_id": chip_id,
                    "morphology_class": item["chip"]["morphology_class"],
                    "value": float(value),
                }
            )
        return sorted(output, key=lambda item: ((-1 if reverse else 1) * item["value"], item["chip_id"]))

    return {
        "worst_mae_z": ranked(("elevation", "mae_m"))[0],
        "worst_slope_mae": ranked(("slope_horn_degrees", "difference_from_raw", "mae"))[0],
        "worst_normal_p95": ranked(("morphology", "surface_normal_difference_degrees", "p95"))[0],
        "greatest_gradient_reduction": ranked(
            ("morphology", "strong_gradient", "ratio_candidate_to_raw", "median"), reverse=False
        )[0],
        "largest_modified_percentage": ranked(("elevation", "modified_pixel_percentage"))[0],
        "largest_second_difference_p95_ratio": ranked(
            ("second_difference_magnitude_m", "candidate_to_raw_ratio", "p95")
        )[0],
    }


def pareto_comparison(
    aggregate: dict[str, dict[str, Any]],
    profile_aggregate: dict[str, dict[str, float]],
) -> dict[str, Any]:
    dimensions = {}
    for candidate_id, metrics in aggregate.items():
        dimensions[candidate_id] = {
            "median_mae_z_m": metrics["mae_z_m"]["median"],
            "median_slope_mae_degrees": metrics["slope_mae_degrees"]["median"],
            "median_normal_p95_degrees": metrics["normal_p95_degrees"]["median"],
            "strong_gradient_ratio_deviation": abs(metrics["strong_gradient_ratio_median"]["median"] - 1.0),
            "median_second_difference_p50_ratio": metrics["second_difference_p50_ratio"]["median"],
            "median_second_difference_p95_ratio": metrics["second_difference_p95_ratio"]["median"],
            "median_profile_strong_step_amplitude_ratio": profile_aggregate[candidate_id][
                "strong_step_amplitude_candidate_to_raw_median"
            ],
        }
    dominated_by: dict[str, list[str]] = {candidate_id: [] for candidate_id in dimensions}
    for candidate_id, values in dimensions.items():
        for competitor_id, competitor in dimensions.items():
            if competitor_id == candidate_id:
                continue
            no_worse = all(competitor[key] <= values[key] for key in values)
            strictly_better = any(competitor[key] < values[key] for key in values)
            if no_worse and strictly_better:
                dominated_by[candidate_id].append(competitor_id)
    return {
        "weighted_score": None,
        "lower_is_better_dimensions": dimensions,
        "dominated_by": dominated_by,
        "non_dominated": [candidate_id for candidate_id, dominators in dominated_by.items() if not dominators],
    }
