from __future__ import annotations

from collections import Counter
from typing import Any

import numpy as np

from core.pipelines.pendientes.constants import (
    STATE_VALIDATION_BANDING_CLASSES,
    STATE_VALIDATION_ELEVATION_THRESHOLDS_M,
    TARGET_RESOLUTION_M,
)
from core.pipelines.pendientes.helpers.directed_banding import directed_banding_metrics
from core.pipelines.pendientes.helpers.experimental_metrics import (
    absolute_laplacian,
    distribution,
    experimental_metrics,
    valid_mask,
)
from core.pipelines.pendientes.helpers.slope import experimental_horn_slope


def dominant_repetition(banding: dict[str, Any]) -> dict[str, Any]:
    axis = banding["repetition"]["dominant_axis"]
    if axis is None:
        return {"axis": None, "lag_pixels": None, "autocorrelation": 0.0}
    component = banding["repetition"][axis]
    return {
        "axis": axis,
        "lag_pixels": component["lag_pixels"],
        "autocorrelation": component["maximum_positive_autocorrelation"],
    }


def state_chip_qa(
    raw: np.ndarray,
    candidate: np.ndarray,
    nodata: float | None,
) -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    metrics, candidate_slope, candidate_slope_valid = experimental_metrics(
        raw,
        candidate,
        TARGET_RESOLUTION_M,
        nodata,
    )
    common = valid_mask(raw, nodata) & valid_mask(candidate, nodata)
    absolute = np.abs(candidate[common].astype(np.float64) - raw[common].astype(np.float64))
    metrics["elevation"]["threshold_percentages"] = {
        f"abs_change_gt_{threshold:g}_m": float(np.count_nonzero(absolute > threshold) / absolute.size * 100)
        for threshold in STATE_VALIDATION_ELEVATION_THRESHOLDS_M
    }
    raw_banding, raw_banding_raster, raw_banding_valid = directed_banding_metrics(raw, nodata)
    candidate_banding, candidate_banding_raster, candidate_banding_valid = directed_banding_metrics(
        candidate,
        nodata,
        raw_banding["reference_threshold_m"],
    )
    raw_values = raw[valid_mask(raw, nodata)].astype(np.float64)
    raw_slope, _, raw_slope_valid = experimental_horn_slope(raw, TARGET_RESOLUTION_M, nodata)
    raw_laplacian, raw_laplacian_valid = absolute_laplacian(raw, nodata)
    raw_summary = {
        "elevation_m": distribution(raw, valid_mask(raw, nodata)),
        "horn_slope_degrees": distribution(raw_slope, raw_slope_valid),
        "absolute_laplacian_m": distribution(raw_laplacian, raw_laplacian_valid),
        "local_relief_p95_minus_p5_m": float(np.percentile(raw_values, 95) - np.percentile(raw_values, 5)),
        "valid_percentage": float(np.count_nonzero(valid_mask(raw, nodata)) / raw.size * 100),
    }
    return (
        {
            "raw_summary": raw_summary,
            "metrics": metrics,
            "raw_banding": raw_banding,
            "fp3_banding": candidate_banding,
            "raw_dominant_repetition": dominant_repetition(raw_banding),
            "fp3_dominant_repetition": dominant_repetition(candidate_banding),
        },
        {
            "candidate_slope": candidate_slope,
            "candidate_slope_valid": candidate_slope_valid,
            "raw_banding_raster": raw_banding_raster,
            "raw_banding_valid": raw_banding_valid,
            "candidate_banding_raster": candidate_banding_raster,
            "candidate_banding_valid": candidate_banding_valid,
        },
    )


def assign_full_resolution_banding_classes(results: dict[str, dict[str, Any]]) -> dict[str, Any]:
    correlations = np.array(
        [result["qa"]["raw_dominant_repetition"]["autocorrelation"] for result in results.values()]
    )
    lower = float(np.percentile(correlations, 100 / 3))
    upper = float(np.percentile(correlations, 200 / 3))
    for result in results.values():
        correlation = result["qa"]["raw_dominant_repetition"]["autocorrelation"]
        if correlation <= lower:
            label = "banding_bajo"
        elif correlation >= upper:
            label = "banding_alto"
        else:
            label = "banding_medio"
        result["raw_banding_class"] = label
    return {
        "variable": "RAW dominant-axis autocorrelation",
        "lower_tercile": lower,
        "upper_tercile": upper,
        "labels": list(STATE_VALIDATION_BANDING_CLASSES),
        "descriptive_only": True,
        "density_note": "RAW density is approximately 10% because its own p90 is the frozen threshold per chip",
    }


def _numeric_summary(values: list[float]) -> dict[str, float]:
    array = np.asarray(values, dtype=np.float64)
    return {
        "minimum": float(array.min()),
        "median": float(np.median(array)),
        "p95": float(np.percentile(array, 95)),
        "maximum": float(array.max()),
    }


def aggregate_state_validation(results: dict[str, dict[str, Any]]) -> dict[str, Any]:
    def values(path: tuple[str, ...], subset: list[dict[str, Any]]) -> list[float]:
        output = []
        for item in subset:
            selected: Any = item
            for key in path:
                selected = selected[key]
            output.append(float(selected))
        return output

    all_results = list(results.values())
    elevation_path = ("qa", "metrics", "elevation")
    slope_path = ("qa", "metrics", "slope_horn_degrees", "difference_from_raw_degrees")
    structure_path = ("qa", "metrics", "structure_preservation")
    summary = {
        "chip_count": len(all_results),
        "mae_z_m": _numeric_summary(values((*elevation_path, "mae_m"), all_results)),
        "rmse_z_m": _numeric_summary(values((*elevation_path, "rmse_m"), all_results)),
        "maximum_absolute_z_m": max(
            values((*elevation_path, "absolute_difference_m", "maximum"), all_results)
        ),
        "percentage_abs_change_gt_0.25_m": _numeric_summary(
            values((*elevation_path, "threshold_percentages", "abs_change_gt_0.25_m"), all_results)
        ),
        "slope_mae_degrees": _numeric_summary(values((*slope_path, "mae"), all_results)),
        "slope_rmse_degrees": _numeric_summary(values((*slope_path, "rmse"), all_results)),
        "strong_gradient_ratio_p50": _numeric_summary(
            values(
                (*structure_path, "strong_gradient", "candidate_to_raw_magnitude_ratio", "p50"),
                all_results,
            )
        ),
        "normal_difference_p95_degrees": _numeric_summary(
            values((*structure_path, "surface_normal_angular_difference_degrees", "p95"), all_results)
        ),
    }
    strata: dict[str, Any] = {}
    for banding_class in STATE_VALIDATION_BANDING_CLASSES:
        subset = [item for item in all_results if item["raw_banding_class"] == banding_class]
        density_change = [
            item["qa"]["fp3_banding"]["high_second_difference_percentage"]
            - item["qa"]["raw_banding"]["high_second_difference_percentage"]
            for item in subset
        ]
        autocorrelation_change = [
            item["qa"]["fp3_dominant_repetition"]["autocorrelation"]
            - item["qa"]["raw_dominant_repetition"]["autocorrelation"]
            for item in subset
        ]
        strata[banding_class] = {
            "chip_count": len(subset),
            "mae_z_m": _numeric_summary(values((*elevation_path, "mae_m"), subset)),
            "density_change_percentage_points": _numeric_summary(density_change),
            "dominant_autocorrelation_change": _numeric_summary(autocorrelation_change),
            "fraction_density_reduced": float(np.count_nonzero(np.array(density_change) < 0) / len(subset)),
            "fraction_autocorrelation_reduced": float(
                np.count_nonzero(np.array(autocorrelation_change) < 0) / len(subset)
            ),
        }
    summary["by_raw_banding_class"] = strata
    summary["morphology_counts"] = dict(Counter(item["chip"]["morphology_class"] for item in all_results))
    summary["outliers"] = {
        "largest_mae_z": sorted(
            (
                {"chip_id": item["chip"]["chip_id"], "value": item["qa"]["metrics"]["elevation"]["mae_m"]}
                for item in all_results
            ),
            key=lambda item: (-item["value"], item["chip_id"]),
        )[:5],
        "largest_normal_p95": sorted(
            (
                {
                    "chip_id": item["chip"]["chip_id"],
                    "value": item["qa"]["metrics"]["structure_preservation"][
                        "surface_normal_angular_difference_degrees"
                    ]["p95"],
                }
                for item in all_results
            ),
            key=lambda item: (-item["value"], item["chip_id"]),
        )[:5],
        "largest_autocorrelation_increase": sorted(
            (
                {
                    "chip_id": item["chip"]["chip_id"],
                    "value": item["qa"]["fp3_dominant_repetition"]["autocorrelation"]
                    - item["qa"]["raw_dominant_repetition"]["autocorrelation"],
                }
                for item in all_results
            ),
            key=lambda item: (-item["value"], item["chip_id"]),
        )[:5],
    }
    return summary


def select_visual_cases(results: dict[str, dict[str, Any]], maximum: int) -> list[str]:
    ordered: list[str] = []

    def add(chip_id: str) -> None:
        if chip_id not in ordered and len(ordered) < maximum:
            ordered.append(chip_id)

    if "problema_manual" in results:
        add("problema_manual")
    items = list(results.items())
    density_change = lambda item: (
        item[1]["qa"]["fp3_banding"]["high_second_difference_percentage"]
        - item[1]["qa"]["raw_banding"]["high_second_difference_percentage"]
    )
    autocorrelation_change = lambda item: (
        item[1]["qa"]["fp3_dominant_repetition"]["autocorrelation"]
        - item[1]["qa"]["raw_dominant_repetition"]["autocorrelation"]
    )
    for ranked in (
        sorted(items, key=lambda item: (density_change(item), item[0])),
        sorted(items, key=lambda item: (-density_change(item), item[0])),
        sorted(items, key=lambda item: (autocorrelation_change(item), item[0])),
        sorted(items, key=lambda item: (-autocorrelation_change(item), item[0])),
    ):
        add(ranked[0][0])
    for morphology in ("plano", "lomerio", "montana", "valle", "transicion_valle_sierra"):
        match = next((chip_id for chip_id, item in sorted(items) if item["chip"]["morphology_class"] == morphology), None)
        if match is not None:
            add(match)
    for banding_class in STATE_VALIDATION_BANDING_CLASSES:
        match = next((chip_id for chip_id, item in sorted(items) if item["raw_banding_class"] == banding_class), None)
        if match is not None:
            add(match)
    return ordered
