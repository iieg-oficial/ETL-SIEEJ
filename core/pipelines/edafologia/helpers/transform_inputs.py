from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import geopandas as gpd

from core.pipelines.edafologia.constants import CANONICAL_SRID, EXPECTED_SOURCE_COLUMNS
from core.pipelines.edafologia.helpers.boundaries import validate_municipal_keys
from core.pipelines.edafologia.mappings import (
    CALIFICADORES_EDAFOLOGICOS,
    GRUPOS_EDAFOLOGICOS,
    catalog_sha256,
)
from core.utils.files import sha256_file


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
    municipal_keys = validate_municipal_keys(gdf)
    count = municipal_keys["count"]
    unique_cvegeo = municipal_keys["unique_cvegeo"]
    srid = gdf.crs.to_epsg() if gdf.crs is not None else None
    geometry_types = sorted(gdf.geometry.geom_type.dropna().unique().tolist())
    null_geometries = int(gdf.geometry.isna().sum())
    invalid_geometries = int((~gdf.geometry.is_valid & gdf.geometry.notna()).sum())
    validations = {
        **municipal_keys["validations"],
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
        "unique_cve_mun": municipal_keys["unique_cve_mun"],
        "municipal_keys": {key: value for key, value in municipal_keys.items() if key != "validations"},
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
