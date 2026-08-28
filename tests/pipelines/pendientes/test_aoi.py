from __future__ import annotations

import geopandas as gpd
import pytest
from fiona import listlayers
from shapely.geometry import MultiPolygon, Polygon

from core.pipelines.pendientes.helpers.aoi import (
    align_bounds,
    build_analytic_aoi,
    processing_grid,
    write_aoi_artifact,
)


def _boundary() -> gpd.GeoDataFrame:
    polygon = Polygon([(100, 100), (200, 100), (200, 200), (100, 200), (100, 100)])
    return gpd.GeoDataFrame({"id": [1]}, geometry=[MultiPolygon([polygon])], crs="EPSG:6368")


def test_align_bounds_expands_outward_to_15_m_grid():
    assert align_bounds((1.0, 16.0, 44.0, 61.0), 15.0) == (0.0, 15.0, 45.0, 75.0)


def test_processing_grid_has_integral_dimensions():
    grid = processing_grid((1.0, 16.0, 44.0, 61.0), 15.0, 6368)
    assert grid.crs_epsg == 6368
    assert grid.resolution_m == 15.0
    assert grid.width == 3
    assert grid.height == 4


def test_analytic_aoi_uses_configured_buffer_and_aligned_bbox():
    analytic, grid = build_analytic_aoi(_boundary(), buffer_m=10_000, resolution=15)
    assert analytic.crs.to_epsg() == 6368
    assert tuple(analytic.total_bounds) == pytest.approx((-9900, -9900, 10200, 10200))
    assert all(value % 15 == 0 for value in grid.bounds)


def test_align_bounds_rejects_invalid_extent():
    with pytest.raises(ValueError, match="Invalid AOI bounds"):
        align_bounds((10, 0, 0, 10), 15)


def test_write_aoi_artifact_creates_two_distinct_layers(tmp_path):
    boundary = _boundary()
    analytic, _ = build_analytic_aoi(boundary, buffer_m=10_000, resolution=15)
    output_path = tmp_path / "aoi.gpkg"

    write_aoi_artifact(boundary, analytic, output_path)

    assert set(listlayers(output_path)) == {"jalisco", "jalisco_buffer"}
