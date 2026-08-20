from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from core.pipelines.edafologia.constants import MUNICIPAL_BOUNDARY_SOURCES
from core.pipelines.edafologia.schemas import (
    CalificadoresEdafologicos,
    FuentesLimitesMunicipales,
    GruposEdafologicos,
)


def catalog_records(mapping: dict[str, str]) -> list[dict[str, str]]:
    records = [{"clave": key, "descripcion": value} for key, value in mapping.items()]
    validate_catalog_records(records)
    return records


def boundary_source_records() -> list[dict[str, Any]]:
    records = [
        {
            "id": 1,
            "clave": "iieg",
            "nombre_fuente": "Límites municipales IIEG",
            "descripcion": "Geometría municipal geom_iieg disponible en public.cvegeo_municipalities.",
            "version": MUNICIPAL_BOUNDARY_SOURCES["iieg"]["version"],
            "procedencia": f"public.cvegeo_municipalities.{MUNICIPAL_BOUNDARY_SOURCES['iieg']['geometry_column']}",
        },
        {
            "id": 2,
            "clave": "inegi",
            "nombre_fuente": "Límites municipales INEGI",
            "descripcion": "Geometría municipal geom_inegi disponible en public.cvegeo_municipalities.",
            "version": MUNICIPAL_BOUNDARY_SOURCES["inegi"]["version"],
            "procedencia": f"public.cvegeo_municipalities.{MUNICIPAL_BOUNDARY_SOURCES['inegi']['geometry_column']}",
        },
    ]
    validate_catalog_records(records, required=("clave", "nombre_fuente", "descripcion", "version", "procedencia"))
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


def catalog_count_summary(
    group_records: list[dict[str, Any]], qualifier_records: list[dict[str, Any]], limit_records: list[dict[str, Any]]
) -> dict[str, int]:
    return {
        GruposEdafologicos.__tablename__: len(group_records),
        CalificadoresEdafologicos.__tablename__: len(qualifier_records),
        FuentesLimitesMunicipales.__tablename__: len(limit_records),
    }
