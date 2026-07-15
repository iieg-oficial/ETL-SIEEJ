from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import geopandas as gpd
import pandas as pd
from geoalchemy2.elements import WKBElement
from geoalchemy2.shape import from_shape

from core.pipelines.edafologia.constants import CANONICAL_SRID, MUNICIPAL_BOUNDARY_SOURCES, TRANSFORM_OUTPUT_LAYER
from core.pipelines.edafologia.helpers.download import sha256_file
from core.pipelines.edafologia.schemas import (
    CalificadoresEdafologicos,
    Edafologias,
    FuentesLimitesMunicipales,
    GruposEdafologicos,
)


REQUIRED_TRANSFORM_FIELDS: tuple[str, ...] = (
    "source_version",
    "source_objectid",
    "clave_wrb",
    "grupo1_origen",
    "califp_g1_origen",
    "califs_g1_origen",
    "source_name",
    "source_url",
    "source_file_name",
    "source_file_sha256",
    "source_downloaded_at",
    "processed_at",
    "fecha_actualizacion",
)


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


def catalog_records(mapping: dict[str, str]) -> list[dict[str, str]]:
    records = [{"clave": key, "descripcion": value} for key, value in mapping.items()]
    validate_catalog_records(records)
    return records


def boundary_source_records() -> list[dict[str, Any]]:
    records = [
        {
            "id": 1,
            "clave": "iieg",
            "nombre": "Límites municipales IIEG",
            "descripcion": "Geometría municipal geom_iieg disponible en public.cvegeo_municipalities.",
            "version": None,
            "procedencia": MUNICIPAL_BOUNDARY_SOURCES["iieg"]["geometry_column"],
        },
        {
            "id": 2,
            "clave": "inegi",
            "nombre": "Límites municipales INEGI",
            "descripcion": "Geometría municipal geom_inegi disponible en public.cvegeo_municipalities.",
            "version": None,
            "procedencia": MUNICIPAL_BOUNDARY_SOURCES["inegi"]["geometry_column"],
        },
    ]
    validate_catalog_records(records, required=("clave", "nombre", "descripcion"))
    return records


def validate_catalog_records(
    records: Iterable[dict[str, Any]], required: tuple[str, ...] = ("clave", "descripcion")
) -> None:
    seen: set[str] = set()
    for record in records:
        for field in required:
            value = record.get(field)
            if value is None or str(value).strip() == "":
                raise ValueError(f"Catalog record has empty {field}: {record}")
        clave = str(record["clave"])
        if clave in seen:
            raise ValueError(f"Duplicated catalog key: {clave}")
        seen.add(clave)


def validate_catalog_counts(
    group_records: list[dict[str, Any]], qualifier_records: list[dict[str, Any]], limit_records: list[dict[str, Any]]
) -> None:
    expected = (
        ("grupos_edafologicos", group_records, 24),
        ("calificadores_edafologicos", qualifier_records, 87),
        ("fuentes_limites_municipales", limit_records, 2),
    )
    failed = [f"{name}={len(records)}" for name, records, count in expected if len(records) != count]
    if failed:
        raise ValueError(f"Unexpected catalog counts: {failed}")


def shapely_to_wkb_element(geometry: Any) -> WKBElement:
    if geometry is None or geometry.is_empty:
        raise ValueError("Cannot convert null or empty geometry to WKBElement")
    if not geometry.is_valid:
        raise ValueError("Cannot convert invalid geometry to WKBElement")
    return from_shape(geometry, srid=CANONICAL_SRID)


def safe_none(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.to_pydatetime()
    if pd.isna(value):
        return None
    return value


def dataframe_to_nullable_records(gdf: gpd.GeoDataFrame, columns: list[str]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for row in gdf[columns].itertuples(index=False, name=None):
        records.append({column: safe_none(value) for column, value in zip(columns, row)})
    return records


def validate_version_collision(session: Any, source_version: str, source_file_sha256: str) -> None:
    existing_hashes = {
        row[0]
        for row in session.query(Edafologias.source_file_sha256)
        .filter(Edafologias.source_version == source_version)
        .distinct()
        .all()
    }
    if existing_hashes and existing_hashes != {source_file_sha256}:
        raise ValueError(f"source_version collision: {source_version} already exists with different source_file_sha256")


def resolve_catalog_ids(
    gdf: gpd.GeoDataFrame,
    grupo_id_by_clave: dict[str, int],
    calificador_id_by_clave: dict[str, int],
) -> gpd.GeoDataFrame:
    result = gdf.copy()
    result["grupo_edafologico_id"] = result["grupo1_origen"].map(grupo_id_by_clave)
    result["calificador_primario_id"] = result["califp_g1_origen"].map(calificador_id_by_clave)
    result["calificador_secundario_id"] = result["califs_g1_origen"].map(calificador_id_by_clave)
    missing = {
        column: sorted(result.loc[result[column].isna(), source_column].dropna().astype(str).unique().tolist())
        for column, source_column in (
            ("grupo_edafologico_id", "grupo1_origen"),
            ("calificador_primario_id", "califp_g1_origen"),
            ("calificador_secundario_id", "califs_g1_origen"),
        )
        if result[column].isna().any()
    }
    if missing:
        raise ValueError(f"Missing catalog ids for transformed data: {missing}")
    for column in ("grupo_edafologico_id", "calificador_primario_id", "calificador_secundario_id"):
        result[column] = result[column].astype(int)
    return result


def canonical_records(gdf: gpd.GeoDataFrame) -> list[dict[str, Any]]:
    insert_columns = [column for column in Edafologias.columns() if column != Edafologias.id.key]
    if "geom" not in insert_columns:
        raise ValueError("Edafologias schema must include geom column")
    missing_columns = [column for column in insert_columns if column != "geom" and column not in gdf.columns]
    if missing_columns:
        raise ValueError(f"Transformed data is missing columns required by Edafologias: {missing_columns}")
    records = dataframe_to_nullable_records(gdf, [column for column in insert_columns if column != "geom"])
    for record, geometry in zip(records, gdf.geometry, strict=True):
        record["geom"] = shapely_to_wkb_element(geometry)
    return records


def catalog_count_summary(
    group_records: list[dict[str, Any]], qualifier_records: list[dict[str, Any]], limit_records: list[dict[str, Any]]
) -> dict[str, int]:
    return {
        GruposEdafologicos.__tablename__: len(group_records),
        CalificadoresEdafologicos.__tablename__: len(qualifier_records),
        FuentesLimitesMunicipales.__tablename__: len(limit_records),
    }
