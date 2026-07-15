from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import geopandas as gpd
import pandas as pd
from shapely import make_valid
from shapely.geometry import GeometryCollection, MultiPolygon, Polygon
from shapely.ops import unary_union

from core.pipelines.edafologia.constants import CANONICAL_SRID, EXPECTED_SOURCE_COLUMNS, RENAME_HEADER
from core.pipelines.edafologia.helpers.download import sha256_file
from core.pipelines.edafologia.mappings import (
    CALIFICADORES_EDAFOLOGICOS,
    GRUPOS_EDAFOLOGICOS,
    catalog_sha256,
)


def require_manifest(manifest: dict[str, Any]) -> None:
    required = (
        "source_url",
        "source_name",
        "source_version",
        "downloaded_at",
        "zip_path",
        "source_file_sha256",
        "selected_path",
        "selected_layer",
        "selected_geometry_type",
        "selected_crs",
        "selected_feature_count",
        "selected_fields",
        "auxiliary_inputs",
        "controlled_catalogs",
        "pipeline_version",
    )
    missing = [field for field in required if field not in manifest]
    if missing:
        raise ValueError(f"Extract manifest is missing required fields: {missing}")
    boundaries = manifest["auxiliary_inputs"].get("municipal_boundaries")
    if not boundaries:
        raise ValueError("Extract manifest is missing auxiliary_inputs.municipal_boundaries")
    if "output_gpkg" not in boundaries or "layers" not in boundaries:
        raise ValueError("Extract manifest has an invalid municipal_boundaries section")


def validate_extract_manifest(manifest_path: Path) -> dict[str, Any]:
    if not manifest_path.exists():
        raise FileNotFoundError(f"Extract manifest not found: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    require_manifest(manifest)

    zip_path = Path(str(manifest["zip_path"]))
    selected_path = Path(str(manifest["selected_path"]))
    boundaries_path = Path(str(manifest["auxiliary_inputs"]["municipal_boundaries"]["output_gpkg"]))
    for path in (zip_path, selected_path, boundaries_path):
        if not path.exists():
            raise FileNotFoundError(f"Manifest references a missing file: {path}")
    if sha256_file(zip_path) != manifest["source_file_sha256"]:
        raise ValueError("Extract manifest ZIP hash does not match the referenced file")
    expected_gpkg_hash = manifest["auxiliary_inputs"]["municipal_boundaries"].get("gpkg_sha256")
    if expected_gpkg_hash and sha256_file(boundaries_path) != expected_gpkg_hash:
        raise ValueError("Municipal boundaries GPKG hash does not match the extract manifest")

    validate_catalog_manifest(manifest)
    return manifest


def validate_catalog_manifest(manifest: dict[str, Any]) -> None:
    catalogs = manifest.get("controlled_catalogs", {})
    expected = {
        "grupo1": (GRUPOS_EDAFOLOGICOS, 24),
        "calificadores": (CALIFICADORES_EDAFOLOGICOS, 87),
    }
    for name, (mapping, count) in expected.items():
        entry = catalogs.get(name)
        if not entry:
            raise ValueError(f"Extract manifest is missing controlled_catalogs.{name}")
        if entry.get("record_count") != count:
            raise ValueError(f"Catalog {name} count mismatch: {entry.get('record_count')} != {count}")
        if entry.get("sha256") != catalog_sha256(mapping):
            raise ValueError(f"Catalog {name} hash mismatch")


def read_source_layer(manifest: dict[str, Any]) -> gpd.GeoDataFrame:
    path = Path(str(manifest["selected_path"]))
    layer = str(manifest["selected_layer"]) if path.suffix.lower() == ".gpkg" else None
    gdf = gpd.read_file(path, layer=layer, engine="pyogrio")
    if gdf.crs is None:
        raise ValueError(f"Selected source layer has no CRS: {path}")
    missing_fields = [field for field in EXPECTED_SOURCE_COLUMNS if field not in gdf.columns]
    if missing_fields:
        raise ValueError(f"Selected source layer is missing required fields: {missing_fields}")
    declared_count = int(manifest["selected_feature_count"])
    if len(gdf) != declared_count:
        raise ValueError(f"Selected source feature count mismatch: {len(gdf)} != {declared_count}")
    if gdf["OBJECTID"].isna().any() or not gdf["OBJECTID"].is_unique:
        raise ValueError("Selected source layer must have a present and unique OBJECTID")
    source_geometry_types = sorted(gdf.geometry.geom_type.dropna().unique().tolist())
    if not set(source_geometry_types).issubset({"Polygon", "MultiPolygon"}):
        raise ValueError(f"Selected source layer must be polygonal: {source_geometry_types}")
    return gdf


def validate_boundary_gdf(gdf: gpd.GeoDataFrame, layer_name: str) -> dict[str, Any]:
    count = int(len(gdf))
    unique_cvegeo = int(gdf["cvegeo"].nunique(dropna=True)) if "cvegeo" in gdf else 0
    srid = gdf.crs.to_epsg() if gdf.crs is not None else None
    geometry_types = sorted(gdf.geometry.geom_type.dropna().unique().tolist())
    null_geometries = int(gdf.geometry.isna().sum())
    invalid_geometries = int((~gdf.geometry.is_valid & gdf.geometry.notna()).sum())
    validations = {
        "expected_count": count == 125,
        "unique_cvegeo": unique_cvegeo == 125,
        "srid": srid == CANONICAL_SRID,
        "multipolygon": geometry_types == ["MultiPolygon"],
        "null_geometries": null_geometries == 0,
        "invalid_geometries": invalid_geometries == 0,
    }
    failed = [name for name, passed in validations.items() if not passed]
    if failed:
        raise ValueError(f"Invalid boundary layer {layer_name}: {failed}")
    return {
        "count": count,
        "unique_cvegeo": unique_cvegeo,
        "srid": srid,
        "geometry_type": "MultiPolygon",
        "bbox": [float(value) for value in gdf.total_bounds],
        "null_geometries": null_geometries,
        "invalid_geometries": invalid_geometries,
        "validations": validations,
    }


def read_boundary_layers(manifest: dict[str, Any]) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame, dict[str, Any]]:
    boundaries = manifest["auxiliary_inputs"]["municipal_boundaries"]
    gpkg_path = Path(str(boundaries["output_gpkg"]))
    iieg = gpd.read_file(gpkg_path, layer="municipios_iieg", engine="pyogrio")
    inegi = gpd.read_file(gpkg_path, layer="municipios_inegi", engine="pyogrio")
    iieg_validation = validate_boundary_gdf(iieg, "municipios_iieg")
    inegi_validation = validate_boundary_gdf(inegi, "municipios_inegi")
    if set(iieg["cvegeo"].astype(str)) != set(inegi["cvegeo"].astype(str)):
        raise ValueError("Municipal boundary layers do not contain the same cvegeo set")
    return iieg, inegi, {"municipios_iieg": iieg_validation, "municipios_inegi": inegi_validation}


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


def validate_catalog_coverage(gdf: gpd.GeoDataFrame) -> dict[str, Any]:
    checks = {
        "grupo1_origen": GRUPOS_EDAFOLOGICOS,
        "califp_g1_origen": CALIFICADORES_EDAFOLOGICOS,
        "califs_g1_origen": CALIFICADORES_EDAFOLOGICOS,
    }
    missing: dict[str, dict[str, int]] = {}
    coverage: dict[str, dict[str, int]] = {}
    for field, mapping in checks.items():
        counts = gdf[field].astype(str).value_counts().to_dict()
        missing[field] = {key: int(value) for key, value in counts.items() if key not in mapping}
        coverage[field] = {
            "observed_codes": len(counts),
            "mapped_codes": len([key for key in counts if key in mapping]),
            "unmapped_codes": len(missing[field]),
        }
    if any(missing[field] for field in missing):
        raise ValueError(f"Unmapped edafologia catalog codes inside Jalisco: {missing}")
    return {"coverage": coverage, "unmapped_codes": missing}


def catalog_id_lookup(mapping: dict[str, str]) -> dict[str, int]:
    return {key: idx for idx, key in enumerate(mapping, start=1)}


def apply_catalog_ids(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    result = gdf.copy()
    grupo_ids = catalog_id_lookup(GRUPOS_EDAFOLOGICOS)
    calificador_ids = catalog_id_lookup(CALIFICADORES_EDAFOLOGICOS)
    result["grupo_edafologico_id"] = result["grupo1_origen"].map(grupo_ids)
    result["calificador_primario_id"] = result["califp_g1_origen"].map(calificador_ids)
    result["calificador_secundario_id"] = result["califs_g1_origen"].map(calificador_ids)
    id_columns = ["grupo_edafologico_id", "calificador_primario_id", "calificador_secundario_id"]
    if result[id_columns].isna().any().any():
        missing = {column: int(result[column].isna().sum()) for column in id_columns if result[column].isna().any()}
        raise ValueError(f"Could not resolve catalog ids after coverage validation: {missing}")
    for column in id_columns:
        result[column] = result[column].astype(int)
    return result


def add_traceability(gdf: gpd.GeoDataFrame, manifest: dict[str, Any], processed_at: datetime) -> gpd.GeoDataFrame:
    result = gdf.copy()
    downloaded_at = manifest.get("downloaded_at")
    if not downloaded_at:
        raise ValueError("Extract manifest has no downloaded_at value for traceability")
    downloaded_ts = pd.to_datetime(downloaded_at)
    result["source_name"] = manifest["source_name"]
    result["source_url"] = manifest["source_url"]
    result["source_version"] = manifest["source_version"]
    result["source_file_name"] = Path(str(manifest["zip_path"])).name
    result["source_file_sha256"] = manifest["source_file_sha256"]
    result["source_downloaded_at"] = downloaded_ts.isoformat()
    result["processed_at"] = processed_at.isoformat()
    result["fecha_actualizacion"] = downloaded_ts.date().isoformat()
    result["pipeline_version"] = manifest["pipeline_version"]
    return result


def prepare_attributes(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    result = gdf.rename(columns=RENAME_HEADER).copy()
    result["source_objectid"] = pd.to_numeric(result["source_objectid"], errors="raise").astype(int)
    for column in ("shape_leng_origen", "shape_area_origen"):
        result[column] = pd.to_numeric(result[column], errors="coerce")
    return result


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
