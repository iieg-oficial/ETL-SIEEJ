from __future__ import annotations

import importlib
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from sqlalchemy import text

import core.pipelines as pipelines_pkg
from core.db import Database
from core.utils.logger import get_console_logger

logger = get_console_logger(__name__)

# Postgres -> Java binding, para la lista explícita de `attributes` de un
# featureType con más de una columna de geometría (ver geoserver.py).
PG_TO_JAVA_BINDING = {
    "integer": "java.lang.Integer",
    "bigint": "java.lang.Long",
    "smallint": "java.lang.Integer",
    "double precision": "java.lang.Double",
    "real": "java.lang.Float",
    "numeric": "java.math.BigDecimal",
    "character varying": "java.lang.String",
    "character": "java.lang.String",
    "text": "java.lang.String",
    "boolean": "java.lang.Boolean",
    "date": "java.sql.Date",
    "timestamp without time zone": "java.sql.Timestamp",
    "timestamp with time zone": "java.sql.Timestamp",
}

GEOMETRY_TYPE_TO_JTS_BINDING = {
    "POINT": "org.locationtech.jts.geom.Point",
    "MULTIPOINT": "org.locationtech.jts.geom.MultiPoint",
    "POLYGON": "org.locationtech.jts.geom.Polygon",
    "MULTIPOLYGON": "org.locationtech.jts.geom.MultiPolygon",
    "LINESTRING": "org.locationtech.jts.geom.LineString",
    "MULTILINESTRING": "org.locationtech.jts.geom.MultiLineString",
    "GEOMETRY": "org.locationtech.jts.geom.Geometry",
}

# Nombre de geometría preferido cuando una vista trae más de una (ver decisión
# del plan: geom_iieg es la geometría default de las capas).
PREFERRED_DEFAULT_GEOMETRY_COLUMN = "geom_iieg"


@dataclass
class GeometryColumnInfo:
    column: str
    geometry_type: str  # ej. "MULTIPOLYGON", "POINT" (mayúsculas)
    srid: int


@dataclass
class ColumnInfo:
    name: str
    pg_type: str
    ordinal_position: int


def resolve_matviews(db: Database, declared: Iterable[str]) -> list[str]:
    """Intersecta el MATERIALIZED_VIEWS declarado por el pipeline con lo que
    de verdad existe en pg_matviews. Loggea warning por cada nombre declarado
    que no exista en la BD (constante desactualizada / migración pendiente).
    NO agrega vistas que existan en la BD pero no estén declaradas -- así se
    excluye automáticamente cualquier vista ajena al ETL (ej. vw_mapalab_fiscalia
    en la base de fiscalia).
    """
    declared = list(declared)
    with db.engine.connect() as conn:
        rows = conn.execute(text("SELECT matviewname FROM pg_matviews WHERE schemaname = 'public'")).fetchall()
    existing = {row[0] for row in rows}

    missing = [name for name in declared if name not in existing]
    for name in missing:
        logger.warning(f"[resolve_matviews] {name} está en MATERIALIZED_VIEWS pero no existe en pg_matviews")

    return [name for name in declared if name in existing]


def get_geometry_columns(db: Database, matview: str) -> list[GeometryColumnInfo]:
    """Consulta geometry_columns para `matview`. Lista vacía = sin geometría =
    señal para que el caller la omita (loggeando warning), sin fallar el script.
    """
    with db.engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT f_geometry_column, type, srid FROM geometry_columns "
                "WHERE f_table_schema = 'public' AND f_table_name = :matview"
            ),
            {"matview": matview},
        ).fetchall()
    return [GeometryColumnInfo(column=row[0], geometry_type=row[1].upper(), srid=row[2]) for row in rows]


def get_columns(db: Database, matview: str) -> list[ColumnInfo]:
    """Todas las columnas de `matview` en orden ordinal, para construir la
    lista explícita de `attributes` del featureType.

    NO se usa information_schema.columns: esa vista del estándar SQL no
    incluye vistas materializadas (relkind 'm') en Postgres, solo tablas y
    vistas normales -- devuelve 0 filas para cualquier matview. Se consulta
    pg_attribute/pg_class directamente, que sí las ve.
    """
    with db.engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT a.attname, format_type(a.atttypid, a.atttypmod), a.attnum "
                "FROM pg_attribute a "
                "JOIN pg_class c ON c.oid = a.attrelid "
                "JOIN pg_namespace n ON n.oid = c.relnamespace "
                "WHERE n.nspname = 'public' AND c.relname = :matview "
                "AND a.attnum > 0 AND NOT a.attisdropped "
                "ORDER BY a.attnum"
            ),
            {"matview": matview},
        ).fetchall()
    # format_type() devuelve modificadores de longitud/precision, ej.
    # "character varying(2)" o "numeric(12,2)" -- se normaliza al tipo base
    # para que calce con las claves de PG_TO_JAVA_BINDING. Las columnas de
    # geometria (ej. "geometry(MultiPolygon,6368)") no necesitan normalizarse
    # bien porque nunca pasan por ese diccionario (se resuelven aparte via
    # geometry_columns/pick_default_geometry).
    return [
        ColumnInfo(name=row[0], pg_type=row[1].split("(")[0].strip(), ordinal_position=row[2]) for row in rows
    ]


def pick_default_geometry(geoms: list[GeometryColumnInfo]) -> GeometryColumnInfo:
    """geom_iieg si está presente (caso de doble geometría); si no, la única
    geometría disponible (caso fiscalia, columna `geom`).
    """
    by_name = {g.column: g for g in geoms}
    if PREFERRED_DEFAULT_GEOMETRY_COLUMN in by_name:
        return by_name[PREFERRED_DEFAULT_GEOMETRY_COLUMN]
    return geoms[0]


def load_declared_matviews(pipeline_name: str) -> list[str] | None:
    """Intenta importar MATERIALIZED_VIEWS del pipeline. Algunos pipelines
    (ej. asg_imss) no re-exportan la constante en queries/__init__.py; vive
    directo en queries/views.py. Devuelve None si el pipeline no la declara
    (no es un pipeline geo) o ni siquiera existe como paquete -- señal para
    que el caller lo excluya sin error.
    """
    try:
        queries = importlib.import_module(f"core.pipelines.{pipeline_name}.queries")
        return queries.MATERIALIZED_VIEWS
    except ModuleNotFoundError:
        return None
    except AttributeError:
        pass

    try:
        queries = importlib.import_module(f"core.pipelines.{pipeline_name}.queries.views")
        return queries.MATERIALIZED_VIEWS
    except (ModuleNotFoundError, AttributeError):
        return None


def discover_pipelines() -> list[str]:
    """Descubre automáticamente qué pipelines declaran MATERIALIZED_VIEWS,
    iterando core/pipelines/* en vez de mantener una lista fija a mano. Un
    pipeline nuevo con vistas geográficas (ej. participacion_ciudadana) queda
    incluido sin tener que tocar este módulo.
    """
    pipelines_dir = Path(pipelines_pkg.__file__).parent
    candidates = sorted(p.name for p in pipelines_dir.iterdir() if p.is_dir() and not p.name.startswith("_"))
    return [name for name in candidates if load_declared_matviews(name)]
