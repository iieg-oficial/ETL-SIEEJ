from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import geopandas as gpd

from core.pipelines.edafologia.constants import (
    CANONICAL_SRID,
    REQUIRED_TRANSFORM_FIELDS,
    TRANSFORM_OUTPUT_LAYER,
)
from core.utils.files import sha256_file


def read_transform_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Transform manifest not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def validate_transform_manifest(manifest: dict[str, Any], manifest_path: Path) -> None:
    required = (
        "extract_manifest_path",
        "extract_manifest_sha256",
        "output_path",
        "output_sha256",
        "output_layer",
        "final_feature_count",
        "final_crs",
        "final_geometry_types",
        "spatial_validation",
    )
    missing = [field for field in required if field not in manifest]
    if missing:
        raise ValueError(f"Transform manifest is missing required fields: {missing}")

    extract_manifest_path = Path(str(manifest["extract_manifest_path"]))
    output_path = Path(str(manifest["output_path"]))
    if not extract_manifest_path.exists():
        raise FileNotFoundError(f"Extract manifest referenced by Transform does not exist: {extract_manifest_path}")
    if not output_path.exists():
        raise FileNotFoundError(f"Transformed GeoPackage does not exist: {output_path}")
    if sha256_file(extract_manifest_path) != manifest["extract_manifest_sha256"]:
        raise ValueError("Transform manifest extract_manifest_sha256 does not match the current Extract manifest")
    if sha256_file(output_path) != manifest["output_sha256"]:
        raise ValueError("Transform manifest output_sha256 does not match the current GeoPackage")
    if manifest["output_layer"] != TRANSFORM_OUTPUT_LAYER:
        raise ValueError(f"Unexpected transform output layer: {manifest['output_layer']}")
    if int(manifest["final_feature_count"]) != 3765:
        raise ValueError(f"Unexpected transformed feature count: {manifest['final_feature_count']}")
    if int(manifest["final_crs"]) != CANONICAL_SRID:
        raise ValueError(f"Unexpected transformed CRS: {manifest['final_crs']}")
    if manifest["final_geometry_types"] != ["MultiPolygon"]:
        raise ValueError(f"Unexpected transformed geometry types: {manifest['final_geometry_types']}")

    spatial = manifest["spatial_validation"]
    failed = [
        key
        for key in ("null_geometries", "empty_geometries", "invalid_geometries", "non_positive_area")
        if int(spatial.get(key, 0)) != 0
    ]
    if failed:
        raise ValueError(f"Transform manifest reports invalid spatial counters: {failed}")
    if not spatial.get("source_objectid_unique"):
        raise ValueError("Transform manifest reports duplicated source_objectid")
    if manifest_path.exists() and sha256_file(manifest_path) == manifest.get("transform_manifest_sha256"):
        return


def read_transformed_layer(manifest: dict[str, Any]) -> gpd.GeoDataFrame:
    return gpd.read_file(manifest["output_path"], layer=manifest["output_layer"], engine="pyogrio")


def validate_transformed_frame(gdf: gpd.GeoDataFrame, manifest: dict[str, Any]) -> None:
    missing_fields = [field for field in REQUIRED_TRANSFORM_FIELDS if field not in gdf.columns]
    if missing_fields:
        raise ValueError(f"Transformed layer is missing required fields: {missing_fields}")
    if len(gdf) != int(manifest["final_feature_count"]):
        raise ValueError(f"Transformed layer count mismatch: {len(gdf)} != {manifest['final_feature_count']}")
    if gdf.crs is None or gdf.crs.to_epsg() != CANONICAL_SRID:
        raise ValueError("Transformed layer CRS is not EPSG:6368")
    if gdf.geometry.isna().any():
        raise ValueError("Transformed layer contains null geometries")
    geometry_types = sorted(gdf.geometry.geom_type.dropna().unique().tolist())
    if geometry_types != ["MultiPolygon"]:
        raise ValueError(f"Transformed layer must contain only MultiPolygon geometries: {geometry_types}")
    if gdf.geometry.is_empty.any():
        raise ValueError("Transformed layer contains empty geometries")
    if (~gdf.geometry.is_valid & gdf.geometry.notna()).any():
        raise ValueError("Transformed layer contains invalid geometries")
    if not gdf["source_objectid"].is_unique:
        raise ValueError("Transformed layer contains duplicated source_objectid")
