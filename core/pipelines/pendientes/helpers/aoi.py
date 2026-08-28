from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import geopandas as gpd
from shapely import wkb
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from core.pipelines.pendientes.constants import (
    ALLOWED_BOUNDARY_GEOMETRY_COLUMNS,
    AOI_ANALYTIC_LAYER,
    AOI_TERRITORIAL_LAYER,
    CVEGEO_STATE_BOUNDARY_TABLE,
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


def read_jalisco_boundary(database_url: str, geometry_column: str) -> gpd.GeoDataFrame:
    if geometry_column not in ALLOWED_BOUNDARY_GEOMETRY_COLUMNS:
        raise ValueError(f"Unsupported cvegeo boundary column: {geometry_column}")
    query = text(
        f"SELECT id, {geometry_column} AS geom FROM {CVEGEO_STATE_BOUNDARY_TABLE} ORDER BY id"  # noqa: S608
    )
    engine = create_engine(database_url)
    try:
        boundary = gpd.read_postgis(query, engine, geom_col="geom")
    except SQLAlchemyError:
        raise ConnectionError("Could not read the canonical Jalisco boundary from cvegeo") from None
    finally:
        engine.dispose()
    return validate_jalisco_boundary(boundary)


def read_jalisco_boundary_snapshot(snapshot_path: Path, geometry_column: str) -> gpd.GeoDataFrame:
    """Read a credential-free EWKB snapshot produced by a real cvegeo query."""
    payload = json.loads(snapshot_path.read_text(encoding="utf-8"))
    expected = {
        "source_database": "cvegeo",
        "source_table": CVEGEO_STATE_BOUNDARY_TABLE,
        "geometry_column": geometry_column,
        "srid": TARGET_SRID,
        "feature_count": 1,
    }
    mismatches = {
        key: (expected_value, payload.get(key))
        for key, expected_value in expected.items()
        if payload.get(key) != expected_value
    }
    if mismatches:
        raise ValueError(f"cvegeo boundary snapshot contract failed: {mismatches}")
    geometry_hex = payload.get("ewkb_hex")
    if not isinstance(geometry_hex, str) or not geometry_hex:
        raise ValueError("cvegeo boundary snapshot has no EWKB geometry")
    boundary = gpd.GeoDataFrame(
        {"id": [payload.get("id")]},
        geometry=[wkb.loads(bytes.fromhex(geometry_hex))],
        crs=f"EPSG:{TARGET_SRID}",
    )
    boundary.attrs["snapshot_query_timestamp"] = payload.get("queried_at")
    boundary.attrs["snapshot_path"] = str(snapshot_path)
    return validate_jalisco_boundary(boundary)


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


def aoi_manifest(
    boundary: gpd.GeoDataFrame,
    analytic: gpd.GeoDataFrame,
    grid: ProcessingGrid,
    geometry_column: str,
    buffer_m: float,
    access_mode: str = "direct_database_query",
) -> dict[str, Any]:
    return {
        "source_database": "cvegeo",
        "source_table": CVEGEO_STATE_BOUNDARY_TABLE,
        "source_geometry_column": geometry_column,
        "source_access_mode": access_mode,
        "territorial_crs_epsg": boundary.crs.to_epsg(),
        "territorial_bounds": [float(value) for value in boundary.total_bounds],
        "analytic_buffer_m": buffer_m,
        "analytic_bounds": [float(value) for value in analytic.total_bounds],
        "processing_grid": grid.to_dict(),
    }
