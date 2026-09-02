from __future__ import annotations

import math
from pathlib import Path

import geopandas as gpd

from core.pipelines.pendientes.constants import (
    AOI_ANALYTIC_LAYER,
    AOI_TERRITORIAL_LAYER,
    TARGET_SRID,
)
from core.pipelines.pendientes.schemas import ProcessingGrid


def align_bounds(bounds: tuple[float, float, float, float], resolution: float) -> tuple[float, float, float, float]:
    if resolution <= 0:
        raise ValueError("Grid resolution must be positive")
    x_min, y_min, x_max, y_max = bounds
    if not all(math.isfinite(value) for value in bounds) or x_min >= x_max or y_min >= y_max:
        raise ValueError(f"Invalid AOI bounds: {bounds}")
    return (
        math.floor(x_min / resolution) * resolution,
        math.floor(y_min / resolution) * resolution,
        math.ceil(x_max / resolution) * resolution,
        math.ceil(y_max / resolution) * resolution,
    )


def processing_grid(bounds: tuple[float, float, float, float], resolution: float, srid: int) -> ProcessingGrid:
    aligned = align_bounds(bounds, resolution)
    width = round((aligned[2] - aligned[0]) / resolution)
    height = round((aligned[3] - aligned[1]) / resolution)
    return ProcessingGrid(srid, resolution, aligned, width, height)


def validate_jalisco_boundary(boundary: gpd.GeoDataFrame, target_srid: int = TARGET_SRID) -> gpd.GeoDataFrame:
    if len(boundary) != 1:
        raise ValueError(f"cvegeo state boundary must contain exactly one Jalisco feature; found {len(boundary)}")
    if boundary.crs is None:
        raise ValueError("Jalisco boundary has no CRS")
    if boundary.crs.to_epsg() != target_srid:
        boundary = boundary.to_crs(epsg=target_srid)
    geometry = boundary.geometry.iloc[0]
    if geometry is None or geometry.is_empty or not geometry.is_valid:
        raise ValueError("Jalisco boundary geometry is null, empty, or invalid")
    return boundary


def build_analytic_aoi(
    boundary: gpd.GeoDataFrame,
    buffer_m: float,
    resolution: float,
    target_srid: int = TARGET_SRID,
) -> tuple[gpd.GeoDataFrame, ProcessingGrid]:
    if buffer_m <= 0:
        raise ValueError("AOI buffer must be positive")
    territorial = validate_jalisco_boundary(boundary, target_srid)
    analytic = territorial.copy()
    analytic[analytic.geometry.name] = analytic.geometry.buffer(buffer_m)
    grid = processing_grid(tuple(float(value) for value in analytic.total_bounds), resolution, target_srid)
    return analytic, grid


def write_aoi_artifact(boundary: gpd.GeoDataFrame, analytic: gpd.GeoDataFrame, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = output_path.with_suffix(".tmp.gpkg")
    temporary_path.unlink(missing_ok=True)
    try:
        boundary.to_file(temporary_path, layer=AOI_TERRITORIAL_LAYER, driver="GPKG")
        # Fiona creates an additional GeoPackage layer when the dataset exists;
        # append mode is for features in an existing layer and is not portable
        # across the Fiona/GDAL versions used by ETL-SIEEJ.
        analytic.to_file(temporary_path, layer=AOI_ANALYTIC_LAYER, driver="GPKG")
        temporary_path.replace(output_path)
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise
    return output_path
