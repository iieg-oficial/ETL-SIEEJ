from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any

import geopandas as gpd
from geoalchemy2.shape import from_shape
from sqlalchemy import delete, text
from sqlalchemy.dialects.postgresql import insert

from core.pipelines.edafologia.constants import CANONICAL_SRID, LIMIT_SOURCE_KEYS
from core.pipelines.edafologia.helpers.municipal_overlay import (
    read_overlay_layer,
    read_overlay_manifest,
    validate_overlay_manifest,
)
from core.pipelines.edafologia.schemas import (
    EdafologiaFragmentosMunicipales,
    Edafologias,
    FuentesLimitesMunicipales,
)
from core.utils.bulk_ops import get_mapping


def read_validated_overlay(manifest_path: Path) -> tuple[dict[str, Any], gpd.GeoDataFrame]:
    manifest = read_overlay_manifest(manifest_path)
    validate_overlay_manifest(manifest)
    frame = read_overlay_layer(manifest)
    return manifest, frame


def resolve_boundary_source_ids(session: Any) -> dict[str, int]:
    mapping = get_mapping(
        session, FuentesLimitesMunicipales, FuentesLimitesMunicipales.clave.key, FuentesLimitesMunicipales.id.key
    )
    missing = sorted(set(LIMIT_SOURCE_KEYS) - set(mapping))
    if missing:
        raise ValueError(f"Missing fuentes_limites_municipales records: {missing}")
    return {key: int(mapping[key]) for key in LIMIT_SOURCE_KEYS}


def resolve_edafologia_ids(session: Any, frame: gpd.GeoDataFrame) -> dict[tuple[str, int], int]:
    versions = sorted(frame["version_fuente"].dropna().astype(str).unique().tolist())
    objectids = sorted(frame["identificador_objeto_fuente"].dropna().astype(int).unique().tolist())
    rows = (
        session.query(Edafologias.version_fuente, Edafologias.identificador_objeto_fuente, Edafologias.id)
        .filter(Edafologias.version_fuente.in_(versions), Edafologias.identificador_objeto_fuente.in_(objectids))
        .all()
    )
    mapping = {(str(version), int(objectid)): int(row_id) for version, objectid, row_id in rows}
    expected = {(str(row.version_fuente), int(row.identificador_objeto_fuente)) for row in frame.itertuples()}
    missing = sorted(expected - set(mapping))
    if missing:
        raise ValueError(f"Missing edafologias ids for overlay fragments: {missing[:10]}")
    return mapping


def overlay_records(
    frame: gpd.GeoDataFrame,
    edafologia_ids: dict[tuple[str, int], int],
    source_ids: dict[str, int],
) -> list[dict[str, Any]]:
    key_columns = ["version_fuente", "identificador_objeto_fuente", "fuente_limite_clave", "municipality_id"]
    if frame.duplicated(key_columns).any():
        raise ValueError("Overlay artifact contains duplicated logical keys")
    records: list[dict[str, Any]] = []
    for row in frame.itertuples():
        version_fuente = str(row.version_fuente)
        identificador_objeto_fuente = int(row.identificador_objeto_fuente)
        fuente_clave = str(row.fuente_limite_clave)
        if fuente_clave not in source_ids:
            raise ValueError(f"Unknown fuente_limite_clave in overlay artifact: {fuente_clave}")
        geometry = row.geometry
        if geometry is None or geometry.is_empty or not geometry.is_valid or geometry.area <= 0:
            raise ValueError("Overlay artifact contains invalid geometry during load preparation")
        records.append(
            {
                "edafologia_id": edafologia_ids[(version_fuente, identificador_objeto_fuente)],
                "municipality_id": int(row.municipality_id),
                "version_fuente": version_fuente,
                "fuente_limite_municipal_id": source_ids[fuente_clave],
                "superficie_m2": float(row.superficie_m2),
                "superficie_ha": float(row.superficie_ha),
                "porcentaje_poligono_fuente": float(row.porcentaje_poligono_fuente),
                "porcentaje_municipio_total": float(row.porcentaje_municipio_total),
                "porcentaje_cobertura_edafologica": float(row.porcentaje_cobertura_edafologica),
                "es_fragmento_pequenio": False,
                "geometria": from_shape(geometry, srid=CANONICAL_SRID),
            }
        )
    validate_records(records)
    return records


def validate_records(records: list[dict[str, Any]]) -> None:
    if not records:
        raise ValueError("Overlay load received no records")
    logical_keys = [
        (record["edafologia_id"], record["municipality_id"], record["fuente_limite_municipal_id"]) for record in records
    ]
    if len(logical_keys) != len(set(logical_keys)):
        raise ValueError("Prepared overlay records contain duplicate database logical keys")
    for record in records:
        if record["superficie_m2"] <= 0 or record["superficie_ha"] <= 0:
            raise ValueError("Prepared overlay records contain non-positive area")
        if record["porcentaje_poligono_fuente"] < 0 or record["porcentaje_municipio_total"] < 0:
            raise ValueError("Prepared overlay records contain negative percentages")
        if abs(record["superficie_ha"] - (record["superficie_m2"] / 10_000)) > 1e-9:
            raise ValueError("Prepared overlay records have inconsistent hectares")


def validate_municipality_ids(session: Any, records: list[dict[str, Any]]) -> None:
    rows = session.execute(
        text(
            """
            SELECT cve_mun, cvegeo
            FROM cvegeo_municipalities
            WHERE cve_ent = 14
            ORDER BY cve_mun
            """
        )
    ).all()
    mapping: dict[int, int] = {}
    for cve_mun, cvegeo in rows:
        municipality_id = int(cve_mun)
        expected_cvegeo = 14_000 + municipality_id
        if municipality_id in mapping or int(cvegeo) != expected_cvegeo:
            raise ValueError("cvegeo Jalisco municipality mapping is ambiguous or incoherent")
        mapping[municipality_id] = int(cvegeo)
    if len(mapping) != 125:
        raise ValueError(f"cvegeo Jalisco municipality catalog must contain 125 unique cve_mun values: {len(mapping)}")

    requested = {int(record["municipality_id"]) for record in records}
    missing = sorted(requested - set(mapping))
    if missing:
        raise ValueError(f"Overlay records reference municipality_id values outside Jalisco: {missing}")


def scopes(records: Iterable[dict[str, Any]]) -> list[tuple[str, int]]:
    return sorted({(str(record["version_fuente"]), int(record["fuente_limite_municipal_id"])) for record in records})


def replace_overlay_scope(session: Any, records: list[dict[str, Any]], chunk_size: int = 10_000) -> dict[str, Any]:
    validate_records(records)
    validate_municipality_ids(session, records)
    scope_values = scopes(records)
    before_counts = count_fragment_scopes(session, scope_values)
    for version_fuente, fuente_id in scope_values:
        session.execute(
            delete(EdafologiaFragmentosMunicipales).where(
                EdafologiaFragmentosMunicipales.version_fuente == version_fuente,
                EdafologiaFragmentosMunicipales.fuente_limite_municipal_id == fuente_id,
            )
        )
    total = len(records)
    for start in range(0, total, chunk_size):
        chunk = records[start : start + chunk_size]
        session.execute(insert(EdafologiaFragmentosMunicipales).values(chunk))
    session.flush()
    after_counts = count_fragment_scopes(session, scope_values)
    expected_after = {
        scope_value: sum(
            1 for record in records if (record["version_fuente"], record["fuente_limite_municipal_id"]) == scope_value
        )
        for scope_value in scope_values
    }
    if after_counts != expected_after:
        raise ValueError(f"Overlay scope replacement count mismatch: {after_counts} != {expected_after}")
    return {
        "scopes": [
            {"version_fuente": version, "fuente_limite_municipal_id": fuente_id} for version, fuente_id in scope_values
        ],
        "records": total,
        "before_counts": {f"{version}|{fuente_id}": count for (version, fuente_id), count in before_counts.items()},
        "after_counts": {f"{version}|{fuente_id}": count for (version, fuente_id), count in after_counts.items()},
    }


def count_fragment_scopes(session: Any, scope_values: list[tuple[str, int]]) -> dict[tuple[str, int], int]:
    result: dict[tuple[str, int], int] = {}
    for version_fuente, fuente_id in scope_values:
        count = session.execute(
            text(
                """
                SELECT count(*)::integer
                FROM edafologia_fragmentos_municipales
                WHERE version_fuente = :version_fuente
                  AND fuente_limite_municipal_id = :fuente_id
                """
            ),
            {"version_fuente": version_fuente, "fuente_id": fuente_id},
        ).scalar_one()
        result[(version_fuente, fuente_id)] = int(count)
    return result


def analyze_overlay_tables(session: Any) -> None:
    session.execute(text("ANALYZE edafologia_fragmentos_municipales"))
