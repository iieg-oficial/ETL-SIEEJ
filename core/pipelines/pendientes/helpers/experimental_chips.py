from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.windows import Window, bounds as window_bounds
from shapely.geometry import box

from core.pipelines.pendientes.constants import (
    AOI_TERRITORIAL_LAYER,
    DIAGNOSTIC_CHIP_SIZE,
    EXPERIMENT_CHIP_STRIDE,
    EXPERIMENT_FILTER_HALO_PIXELS,
    EXPERIMENT_MIN_VALID_PERCENTAGE,
    EXPERIMENT_SELECTION_DECIMATION,
    EXPERIMENT_SELECTION_PERCENTILES,
    TARGET_RESOLUTION_M,
)
from core.pipelines.pendientes.helpers.experimental_metrics import absolute_laplacian, valid_mask
from core.pipelines.pendientes.helpers.slope import experimental_horn_slope


@dataclass(frozen=True)
class ChipWindow:
    chip_id: str
    terrain_class: str
    row_offset: int
    column_offset: int
    width: int
    height: int
    center_x: float
    center_y: float
    bbox: tuple[float, float, float, float]
    selection_criterion: str
    preliminary_slope_median_degrees: float
    preliminary_roughness_median_abs_laplacian_m: float
    preliminary_valid_percentage: float

    @property
    def window(self) -> Window:
        return Window(self.column_offset, self.row_offset, self.width, self.height)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _terrain_statistics(values: np.ndarray, resolution: float, nodata: float | None) -> tuple[float, float, float]:
    valid = valid_mask(values, nodata)
    valid_percentage = float(np.count_nonzero(valid) / valid.size * 100)
    slope, _, slope_valid = experimental_horn_slope(values, resolution, nodata)
    laplacian, laplacian_valid = absolute_laplacian(values, nodata)
    if not slope_valid.any() or not laplacian_valid.any():
        raise ValueError("Terrain sample has insufficient valid neighborhood")
    return (
        float(np.median(slope[slope_valid])),
        float(np.median(laplacian[laplacian_valid])),
        valid_percentage,
    )


def scan_chip_candidates(
    baseline_path: Path,
    aoi_path: Path,
    chip_size: int = DIAGNOSTIC_CHIP_SIZE,
    stride: int = EXPERIMENT_CHIP_STRIDE,
    decimation: int = EXPERIMENT_SELECTION_DECIMATION,
    minimum_valid_percentage: float = EXPERIMENT_MIN_VALID_PERCENTAGE,
) -> list[dict[str, Any]]:
    if chip_size <= 0 or stride <= 0 or decimation <= 0:
        raise ValueError("Chip scan dimensions must be positive")
    boundary_frame = gpd.read_file(aoi_path, layer=AOI_TERRITORIAL_LAYER)
    if len(boundary_frame) != 1:
        raise ValueError("Experimental selection requires exactly one Jalisco boundary")
    boundary = boundary_frame.geometry.iloc[0]
    candidates: list[dict[str, Any]] = []
    with rasterio.open(baseline_path, "r") as dataset:
        if dataset.crs is None or dataset.crs.to_epsg() != 6368:
            raise ValueError("Experimental baseline must use EPSG:6368")
        start = math.ceil(EXPERIMENT_FILTER_HALO_PIXELS / stride) * stride
        row_limit = dataset.height - chip_size - EXPERIMENT_FILTER_HALO_PIXELS
        column_limit = dataset.width - chip_size - EXPERIMENT_FILTER_HALO_PIXELS
        sample_size = max(3, chip_size // decimation)
        for row_offset in range(start, row_limit + 1, stride):
            for column_offset in range(start, column_limit + 1, stride):
                window = Window(column_offset, row_offset, chip_size, chip_size)
                bbox = tuple(float(value) for value in window_bounds(window, dataset.transform))
                if not boundary.covers(box(*bbox)):
                    continue
                values = dataset.read(
                    1,
                    window=window,
                    out_shape=(sample_size, sample_size),
                    masked=False,
                    resampling=Resampling.nearest,
                )
                slope, roughness, valid_percentage = _terrain_statistics(
                    values,
                    TARGET_RESOLUTION_M * decimation,
                    dataset.nodata,
                )
                if valid_percentage < minimum_valid_percentage:
                    continue
                center_x, center_y = dataset.xy(
                    row_offset + chip_size // 2,
                    column_offset + chip_size // 2,
                )
                candidates.append(
                    {
                        "row_offset": row_offset,
                        "column_offset": column_offset,
                        "width": chip_size,
                        "height": chip_size,
                        "center_x": float(center_x),
                        "center_y": float(center_y),
                        "bbox": bbox,
                        "slope_median_degrees": slope,
                        "roughness_median_abs_laplacian_m": roughness,
                        "valid_percentage": valid_percentage,
                    }
                )
    if len(candidates) < 3:
        raise ValueError(f"Terrain-stratified selection requires at least three candidates; found {len(candidates)}")
    return candidates


def _selection_percentiles(candidates: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    slope = np.array([candidate["slope_median_degrees"] for candidate in candidates])
    roughness = np.array([candidate["roughness_median_abs_laplacian_m"] for candidate in candidates])
    return {
        "slope_median_degrees": {
            f"p{percentile}": float(np.percentile(slope, percentile)) for percentile in EXPERIMENT_SELECTION_PERCENTILES
        },
        "roughness_median_abs_laplacian_m": {
            f"p{percentile}": float(np.percentile(roughness, percentile))
            for percentile in EXPERIMENT_SELECTION_PERCENTILES
        },
    }


def _choose_candidate(
    candidates: list[dict[str, Any]],
    percentiles: dict[str, dict[str, float]],
    terrain_class: str,
    used: set[tuple[int, int]],
) -> tuple[dict[str, Any], str]:
    slope_percentiles = percentiles["slope_median_degrees"]
    roughness_percentiles = percentiles["roughness_median_abs_laplacian_m"]
    targets = {"plano": "p10", "lomerio": "p50", "montana": "p90"}
    constraints = {
        "plano": lambda candidate: candidate["slope_median_degrees"] <= slope_percentiles["p25"]
        and candidate["roughness_median_abs_laplacian_m"] <= roughness_percentiles["p25"],
        "lomerio": lambda candidate: slope_percentiles["p40"]
        <= candidate["slope_median_degrees"]
        <= slope_percentiles["p60"]
        and roughness_percentiles["p40"]
        <= candidate["roughness_median_abs_laplacian_m"]
        <= roughness_percentiles["p60"],
        "montana": lambda candidate: candidate["slope_median_degrees"] >= slope_percentiles["p75"]
        and candidate["roughness_median_abs_laplacian_m"] >= roughness_percentiles["p75"],
    }
    eligible = [
        candidate
        for candidate in candidates
        if (candidate["row_offset"], candidate["column_offset"]) not in used and constraints[terrain_class](candidate)
    ]
    relaxed = False
    if not eligible:
        eligible = [
            candidate for candidate in candidates if (candidate["row_offset"], candidate["column_offset"]) not in used
        ]
        relaxed = True
    target = targets[terrain_class]
    slope_scale = max(slope_percentiles["p75"] - slope_percentiles["p25"], np.finfo(float).eps)
    roughness_scale = max(
        roughness_percentiles["p75"] - roughness_percentiles["p25"],
        np.finfo(float).eps,
    )

    def distance(candidate: dict[str, Any]) -> tuple[float, int, int]:
        slope_distance = (candidate["slope_median_degrees"] - slope_percentiles[target]) / slope_scale
        roughness_distance = (
            candidate["roughness_median_abs_laplacian_m"] - roughness_percentiles[target]
        ) / roughness_scale
        return (
            float(math.hypot(slope_distance, roughness_distance)),
            candidate["row_offset"],
            candidate["column_offset"],
        )

    selected = min(eligible, key=distance)
    criterion = (
        f"nearest joint slope/roughness {target}; class constraint "
        f"{'relaxed because no joint candidate existed' if relaxed else 'satisfied'}"
    )
    return selected, criterion


def select_representative_chips(
    candidates: list[dict[str, Any]],
) -> tuple[list[ChipWindow], dict[str, Any]]:
    percentiles = _selection_percentiles(candidates)
    selected: list[ChipWindow] = []
    used: set[tuple[int, int]] = set()
    for chip_id, terrain_class in (("plano", "plano"), ("lomerio", "lomerio"), ("montana", "montana")):
        candidate, criterion = _choose_candidate(candidates, percentiles, terrain_class, used)
        used.add((candidate["row_offset"], candidate["column_offset"]))
        selected.append(
            ChipWindow(
                chip_id=chip_id,
                terrain_class=terrain_class,
                row_offset=candidate["row_offset"],
                column_offset=candidate["column_offset"],
                width=candidate["width"],
                height=candidate["height"],
                center_x=candidate["center_x"],
                center_y=candidate["center_y"],
                bbox=candidate["bbox"],
                selection_criterion=criterion,
                preliminary_slope_median_degrees=candidate["slope_median_degrees"],
                preliminary_roughness_median_abs_laplacian_m=candidate["roughness_median_abs_laplacian_m"],
                preliminary_valid_percentage=candidate["valid_percentage"],
            )
        )
    return selected, {
        "candidate_count": len(candidates),
        "chip_size_pixels": DIAGNOSTIC_CHIP_SIZE,
        "stride_pixels": EXPERIMENT_CHIP_STRIDE,
        "selection_decimation": EXPERIMENT_SELECTION_DECIMATION,
        "minimum_valid_percentage": EXPERIMENT_MIN_VALID_PERCENTAGE,
        "boundary_rule": "entire chip bbox covered by canonical Jalisco geometry",
        "terrain_variables": ["Horn slope median", "median absolute four-neighbor Laplacian"],
        "percentiles": percentiles,
    }


def manual_chip(
    baseline_path: Path,
    center_x: float,
    center_y: float,
    chip_size: int = DIAGNOSTIC_CHIP_SIZE,
) -> ChipWindow:
    with rasterio.open(baseline_path, "r") as dataset:
        center_row, center_column = dataset.index(center_x, center_y)
        row_offset = center_row - chip_size // 2
        column_offset = center_column - chip_size // 2
        window = Window(column_offset, row_offset, chip_size, chip_size)
        if row_offset < 0 or column_offset < 0 or window.bottom > dataset.height or window.right > dataset.width:
            raise ValueError("Manual problem chip falls outside the baseline")
        values = dataset.read(1, window=window)
        slope, roughness, valid_percentage = _terrain_statistics(values, TARGET_RESOLUTION_M, dataset.nodata)
        bbox = tuple(float(value) for value in window_bounds(window, dataset.transform))
    return ChipWindow(
        chip_id="problema_manual",
        terrain_class="problema_manual",
        row_offset=row_offset,
        column_offset=column_offset,
        width=chip_size,
        height=chip_size,
        center_x=center_x,
        center_y=center_y,
        bbox=bbox,
        selection_criterion="user-supplied EPSG:6368 coordinate snapped to the baseline pixel grid",
        preliminary_slope_median_degrees=slope,
        preliminary_roughness_median_abs_laplacian_m=roughness,
        preliminary_valid_percentage=valid_percentage,
    )
