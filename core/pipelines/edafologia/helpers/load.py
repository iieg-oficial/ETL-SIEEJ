from __future__ import annotations

from typing import Any

import geopandas as gpd
import pandas as pd
from geoalchemy2.elements import WKBElement
from geoalchemy2.shape import from_shape

from core.pipelines.edafologia.constants import CANONICAL_SRID
from core.pipelines.edafologia.schemas import Edafologias


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


def source_identity(gdf: gpd.GeoDataFrame) -> tuple[str, str]:
    source_versions = gdf["version_fuente"].dropna().astype(str).unique().tolist()
    source_hashes = gdf["sha256_archivo_fuente"].dropna().astype(str).unique().tolist()
    if len(source_versions) != 1 or len(source_hashes) != 1:
        raise ValueError("Transformed data must contain exactly one version_fuente and sha256_archivo_fuente")
    return source_versions[0], source_hashes[0]


def validate_version_collision(session: Any, version_fuente: str, sha256_archivo_fuente: str) -> None:
    existing_hashes = {
        row[0]
        for row in session.query(Edafologias.sha256_archivo_fuente)
        .filter(Edafologias.version_fuente == version_fuente)
        .distinct()
        .all()
    }
    if existing_hashes and existing_hashes != {sha256_archivo_fuente}:
        raise ValueError(
            f"version_fuente collision: {version_fuente} already exists with different sha256_archivo_fuente"
        )


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
    if "geometria" not in insert_columns:
        raise ValueError("Edafologias schema must include geometria column")
    missing_columns = [column for column in insert_columns if column != "geometria" and column not in gdf.columns]
    if missing_columns:
        raise ValueError(f"Transformed data is missing columns required by Edafologias: {missing_columns}")
    records = dataframe_to_nullable_records(gdf, [column for column in insert_columns if column != "geometria"])
    for record, geometry in zip(records, gdf.geometry, strict=True):
        record["geometria"] = shapely_to_wkb_element(geometry)
    return records
