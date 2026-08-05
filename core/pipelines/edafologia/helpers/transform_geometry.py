from __future__ import annotations

from pathlib import Path
from typing import Any

import geopandas as gpd
from shapely import make_valid
from shapely.geometry import GeometryCollection, MultiPolygon, Polygon
from shapely.ops import unary_union

from core.pipelines.edafologia.constants import CANONICAL_SRID


def build_canonical_mask(iieg: gpd.GeoDataFrame, inegi: gpd.GeoDataFrame) -> tuple[Any, dict[str, float]]:
    coverage_iieg = iieg.geometry.union_all()
    coverage_inegi = inegi.geometry.union_all()
    coverage_canonical = unary_union([coverage_iieg, coverage_inegi])
    common = coverage_iieg.intersection(coverage_inegi)
    exclusive_iieg = coverage_iieg.difference(coverage_inegi)
    exclusive_inegi = coverage_inegi.difference(coverage_iieg)
    symmetric_difference = coverage_iieg.symmetric_difference(coverage_inegi)
    stats = {
        "area_iieg_m2": float(coverage_iieg.area),
        "area_inegi_m2": float(coverage_inegi.area),
        "area_canonical_m2": float(coverage_canonical.area),
        "area_common_m2": float(common.area),
        "area_exclusive_iieg_m2": float(exclusive_iieg.area),
        "area_exclusive_inegi_m2": float(exclusive_inegi.area),
        "area_symmetric_difference_m2": float(symmetric_difference.area),
    }
    return coverage_canonical, stats


def polygonal_part(geometry: Any) -> MultiPolygon | None:
    if geometry is None or geometry.is_empty:
        return None
    if isinstance(geometry, Polygon):
        return MultiPolygon([geometry]) if geometry.area > 0 else None
    if isinstance(geometry, MultiPolygon):
        parts = [part for part in geometry.geoms if not part.is_empty and part.area > 0]
        return MultiPolygon(parts) if parts else None
    if isinstance(geometry, GeometryCollection):
        parts = []
        for child in geometry.geoms:
            polygonal = polygonal_part(child)
            if polygonal is not None:
                parts.extend(list(polygonal.geoms))
        return MultiPolygon(parts) if parts else None
    return None


def repair_and_polygonize(
    gdf: gpd.GeoDataFrame,
    id_column: str,
    stage_name: str,
) -> tuple[gpd.GeoDataFrame, dict[str, Any]]:
    result = gdf.copy()
    empty_before = result.geometry.isna() | result.geometry.is_empty
    invalid_before = ~result.geometry.is_valid & ~empty_before
    repaired_ids = result.loc[invalid_before, id_column].astype(int).tolist() if id_column in result else []
    if invalid_before.any():
        result.loc[invalid_before, result.geometry.name] = result.loc[invalid_before, result.geometry.name].map(
            make_valid
        )
    result[result.geometry.name] = result.geometry.map(polygonal_part)
    empty_after = result.geometry.isna() | result.geometry.is_empty
    removed_ids = result.loc[empty_after, id_column].astype(int).tolist() if id_column in result else []
    result = result.loc[~empty_after].copy()
    invalid_after = ~result.geometry.is_valid
    if invalid_after.any():
        raise ValueError(f"{stage_name} has invalid geometries after repair")
    return result, {
        "stage": stage_name,
        "empty_before": int(empty_before.sum()),
        "invalid_before": int(invalid_before.sum()),
        "repaired_count": len(repaired_ids),
        "repaired_source_objectids": repaired_ids,
        "empty_removed_count": len(removed_ids),
        "empty_removed_source_objectids": removed_ids,
        "invalid_after": int(invalid_after.sum()),
    }


def clip_to_mask(gdf: gpd.GeoDataFrame, mask: Any) -> tuple[gpd.GeoDataFrame, int]:
    if gdf.empty:
        return gdf.copy(), 0
    candidate_index = gdf.sindex.query(mask, predicate="intersects")
    selected = gdf.iloc[candidate_index].copy()
    selected_count = int(len(selected))
    if selected.empty:
        return selected, selected_count
    selected[selected.geometry.name] = selected.geometry.intersection(mask)
    selected = selected.loc[~(selected.geometry.isna() | selected.geometry.is_empty)].copy()
    return selected, selected_count


def dissolve_by_source_objectid(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    if gdf.empty:
        return gdf
    columns = [column for column in gdf.columns if column != gdf.geometry.name and column != "source_objectid"]
    dissolved = gdf.dissolve(by="source_objectid", as_index=False, aggfunc={column: "first" for column in columns})
    dissolved[dissolved.geometry.name] = dissolved.geometry.map(polygonal_part)
    dissolved = dissolved.loc[~(dissolved.geometry.isna() | dissolved.geometry.is_empty)].copy()
    return dissolved


def final_spatial_validation(
    gdf: gpd.GeoDataFrame,
    coverage_canonical: Any,
    coverage_iieg: Any,
    coverage_inegi: Any,
) -> dict[str, Any]:
    if gdf.crs is None or gdf.crs.to_epsg() != CANONICAL_SRID:
        raise ValueError("Transformed product CRS is not EPSG:6368")
    geometry_types = sorted(gdf.geometry.geom_type.dropna().unique().tolist())
    null_geometries = int(gdf.geometry.isna().sum())
    empty_geometries = int(gdf.geometry.is_empty.sum())
    invalid_geometries = int((~gdf.geometry.is_valid & gdf.geometry.notna()).sum())
    non_positive_area = int((gdf.geometry.area <= 0).sum())
    intersects_mask = bool(gdf.geometry.intersects(coverage_canonical).all())
    if geometry_types != ["MultiPolygon"]:
        raise ValueError(f"Transformed product must contain only MultiPolygon geometries: {geometry_types}")
    if null_geometries or empty_geometries or invalid_geometries or non_positive_area:
        raise ValueError("Transformed product has null, empty, invalid, or non-positive-area geometries")
    if not gdf["source_objectid"].is_unique:
        raise ValueError("Transformed product has duplicated source_objectid")
    if not intersects_mask:
        raise ValueError("Transformed product contains geometries outside the canonical coverage")

    union = gdf.geometry.union_all()
    area_by_entity = gdf.set_index("source_objectid").geometry.area
    sum_area = float(area_by_entity.sum())
    union_area = float(union.area)
    return {
        "crs": CANONICAL_SRID,
        "geometry_types": geometry_types,
        "null_geometries": null_geometries,
        "empty_geometries": empty_geometries,
        "invalid_geometries": invalid_geometries,
        "non_positive_area": non_positive_area,
        "source_objectid_unique": True,
        "all_intersect_canonical_coverage": intersects_mask,
        "area_sum_m2": sum_area,
        "area_union_m2": union_area,
        "area_overlap_delta_m2": float(sum_area - union_area),
        "area_by_entity": {
            "count": int(area_by_entity.count()),
            "min_m2": float(area_by_entity.min()),
            "max_m2": float(area_by_entity.max()),
            "sum_m2": sum_area,
        },
        "coverage_iieg_pct": float(union.intersection(coverage_iieg).area / coverage_iieg.area * 100),
        "coverage_inegi_pct": float(union.intersection(coverage_inegi).area / coverage_inegi.area * 100),
        "small_geometry_area_min_m2": float(area_by_entity.min()),
    }


def write_gpkg_atomic(gdf: gpd.GeoDataFrame, output_path: Path, layer_name: str) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_suffix(".tmp.gpkg")
    temporary.unlink(missing_ok=True)
    try:
        gdf.to_file(temporary, layer=layer_name, driver="GPKG")
        temporary.replace(output_path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    return output_path
