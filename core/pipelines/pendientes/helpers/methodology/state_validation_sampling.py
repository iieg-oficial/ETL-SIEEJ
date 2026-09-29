from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.windows import Window

from core.pipelines.pendientes.constants import (
    EXPERIMENT_SELECTION_DECIMATION,
    STATE_VALIDATION_BANDING_CLASSES,
    STATE_VALIDATION_MORPHOLOGY_CLASSES,
    STATE_VALIDATION_SECTOR_COLUMNS,
    STATE_VALIDATION_SECTOR_ROWS,
)
from core.pipelines.pendientes.helpers.methodology.directed_banding import directed_banding_metrics
from core.pipelines.pendientes.helpers.methodology.experimental_chips import ChipWindow
from core.pipelines.pendientes.helpers.experimental_metrics import valid_mask


def _dominant_repetition(banding: dict[str, Any]) -> tuple[float, int | None, str | None]:
    axis = banding["repetition"]["dominant_axis"]
    if axis is None:
        return 0.0, None, None
    component = banding["repetition"][axis]
    return float(component["maximum_positive_autocorrelation"]), component["lag_pixels"], axis


def enrich_candidate_pool(
    baseline_path: Path,
    candidates: list[dict[str, Any]],
    decimation: int = EXPERIMENT_SELECTION_DECIMATION,
) -> list[dict[str, Any]]:
    enriched: list[dict[str, Any]] = []
    with rasterio.open(baseline_path) as dataset:
        for candidate in candidates:
            sample_height = max(3, int(candidate["height"]) // decimation)
            sample_width = max(3, int(candidate["width"]) // decimation)
            values = dataset.read(
                1,
                window=Window(
                    candidate["column_offset"],
                    candidate["row_offset"],
                    candidate["width"],
                    candidate["height"],
                ),
                out_shape=(sample_height, sample_width),
                resampling=Resampling.nearest,
            )
            valid = valid_mask(values, dataset.nodata)
            selected = values[valid].astype(np.float64)
            banding, _, _ = directed_banding_metrics(values, dataset.nodata)
            correlation, lag, axis = _dominant_repetition(banding)
            enriched.append(
                {
                    **candidate,
                    "preliminary_elevation_m": {
                        "minimum": float(selected.min()),
                        "median": float(np.median(selected)),
                        "maximum": float(selected.max()),
                    },
                    "preliminary_local_relief_m": float(np.percentile(selected, 95) - np.percentile(selected, 5)),
                    "preliminary_raw_banding": {
                        "density_percentage": banding["high_second_difference_percentage"],
                        "reference_threshold_m": banding["reference_threshold_m"],
                        "axial_coherence": banding["orientation"]["coherence"],
                        "continuity_percentage": banding["tangent_continuity"]["support_percentage"],
                        "dominant_autocorrelation": correlation,
                        "dominant_axis": axis,
                        "dominant_lag_pixels": lag,
                    },
                }
            )
    return enriched


def _quantiles(candidates: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    fields = {
        "slope": np.array([item["slope_median_degrees"] for item in candidates]),
        "relief": np.array([item["preliminary_local_relief_m"] for item in candidates]),
        "elevation": np.array([item["preliminary_elevation_m"]["median"] for item in candidates]),
        "banding_autocorrelation": np.array(
            [item["preliminary_raw_banding"]["dominant_autocorrelation"] for item in candidates]
        ),
    }
    return {
        name: {"p33": float(np.percentile(values, 100 / 3)), "p67": float(np.percentile(values, 200 / 3))}
        for name, values in fields.items()
    }


def _morphology(candidate: dict[str, Any], quantiles: dict[str, dict[str, float]]) -> str:
    slope = candidate["slope_median_degrees"]
    relief = candidate["preliminary_local_relief_m"]
    elevation = candidate["preliminary_elevation_m"]["median"]
    if slope <= quantiles["slope"]["p33"] and relief <= quantiles["relief"]["p33"]:
        return "plano"
    if slope >= quantiles["slope"]["p67"] and relief >= quantiles["relief"]["p67"]:
        return "montana"
    if elevation <= quantiles["elevation"]["p33"] and relief >= quantiles["relief"]["p33"]:
        return "valle"
    if relief >= quantiles["relief"]["p67"] or slope >= quantiles["slope"]["p67"]:
        return "transicion_valle_sierra"
    return "lomerio"


def _banding_class(candidate: dict[str, Any], quantiles: dict[str, dict[str, float]]) -> str:
    correlation = candidate["preliminary_raw_banding"]["dominant_autocorrelation"]
    if correlation <= quantiles["banding_autocorrelation"]["p33"]:
        return "banding_bajo"
    if correlation >= quantiles["banding_autocorrelation"]["p67"]:
        return "banding_alto"
    return "banding_medio"


def _sector_indices(
    candidate: dict[str, Any],
    bounds: tuple[float, float, float, float],
    columns: int,
    rows: int,
) -> tuple[int, int]:
    minimum_x, minimum_y, maximum_x, maximum_y = bounds
    column = min(int((candidate["center_x"] - minimum_x) / (maximum_x - minimum_x) * columns), columns - 1)
    row_from_south = min(int((candidate["center_y"] - minimum_y) / (maximum_y - minimum_y) * rows), rows - 1)
    return rows - row_from_south, column + 1


def classify_candidate_pool(
    candidates: list[dict[str, Any]],
    sector_columns: int = STATE_VALIDATION_SECTOR_COLUMNS,
    sector_rows: int = STATE_VALIDATION_SECTOR_ROWS,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if not candidates:
        raise ValueError("State validation candidate pool cannot be empty")
    quantiles = _quantiles(candidates)
    xs = [candidate["center_x"] for candidate in candidates]
    ys = [candidate["center_y"] for candidate in candidates]
    bounds = (min(xs), min(ys), max(xs), max(ys))
    classified = []
    for candidate in candidates:
        sector_row, sector_column = _sector_indices(candidate, bounds, sector_columns, sector_rows)
        classified.append(
            {
                **candidate,
                "spatial_sector": f"N{sector_row:02d}_E{sector_column:02d}",
                "morphology_class": _morphology(candidate, quantiles),
                "raw_banding_class": _banding_class(candidate, quantiles),
            }
        )
    return classified, {
        "pool_count": len(classified),
        "sector_grid": {"columns": sector_columns, "rows": sector_rows, "bounds": list(bounds)},
        "quantiles": quantiles,
        "banding_class_variable": "RAW dominant-axis autocorrelation",
        "banding_class_rule": "validation-set terciles; descriptive, not institutional",
        "raw_density_interpretation": "approximately 10% by construction because each RAW threshold is its p90",
    }


def select_spatially_stratified(
    candidates: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    by_sector: dict[str, list[dict[str, Any]]] = {}
    for candidate in candidates:
        by_sector.setdefault(candidate["spatial_sector"], []).append(candidate)
    selected: list[dict[str, Any]] = []
    morphology_order = STATE_VALIDATION_MORPHOLOGY_CLASSES
    banding_order = STATE_VALIDATION_BANDING_CLASSES
    for index, sector in enumerate(sorted(by_sector)):
        group = by_sector[sector]
        target_morphology = morphology_order[index % len(morphology_order)]
        target_banding = banding_order[index % len(banding_order)]
        eligible = [
            item
            for item in group
            if item["morphology_class"] == target_morphology and item["raw_banding_class"] == target_banding
        ]
        relaxation = "morphology_and_banding"
        if not eligible:
            eligible = [item for item in group if item["morphology_class"] == target_morphology]
            relaxation = "morphology_only"
        if not eligible:
            eligible = [item for item in group if item["raw_banding_class"] == target_banding]
            relaxation = "banding_only"
        if not eligible:
            eligible = group
            relaxation = "sector_only"
        center_x = float(np.mean([item["center_x"] for item in group]))
        center_y = float(np.mean([item["center_y"] for item in group]))
        chosen = min(
            eligible,
            key=lambda item: (
                math.hypot(item["center_x"] - center_x, item["center_y"] - center_y),
                item["row_offset"],
                item["column_offset"],
            ),
        )
        selected.append(
            {
                **chosen,
                "selection_criterion": (
                    f"one reproducible chip for occupied 6x6 sector; target={target_morphology}/"
                    f"{target_banding}; matched={relaxation}"
                ),
            }
        )
    return selected


def chip_window_from_inventory(item: dict[str, Any], chip_id: str) -> ChipWindow:
    return ChipWindow(
        chip_id=chip_id,
        terrain_class=item["morphology_class"],
        row_offset=int(item["row_offset"]),
        column_offset=int(item["column_offset"]),
        width=int(item["width"]),
        height=int(item["height"]),
        center_x=float(item["center_x"]),
        center_y=float(item["center_y"]),
        bbox=tuple(item["bbox"]),
        selection_criterion=item["selection_criterion"],
        preliminary_slope_median_degrees=float(item["slope_median_degrees"]),
        preliminary_roughness_median_abs_laplacian_m=float(item["roughness_median_abs_laplacian_m"]),
        preliminary_valid_percentage=float(item["valid_percentage"]),
    )
