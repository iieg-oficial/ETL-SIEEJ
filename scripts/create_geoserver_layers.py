#!/usr/bin/env python3
"""Crea/actualiza en GeoServer un workspace + datastore PostGIS + una layer por
cada vista materializada con geometría, para cada pipeline de ETL-SIEEJ que
declare MATERIALIZED_VIEWS. Idempotente: seguro correrlo varias veces.

Uso (dentro del contenedor de Airflow, con scripts/ montado):
    PYTHONPATH=. python3 scripts/create_geoserver_layers.py [--pipeline NAME ...] [--dry-run]
"""
from __future__ import annotations

import argparse
import importlib
import sys

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

from core.db import Database
from core.utils.geoserver import GeoServerClient
from core.utils.geoserver_introspect import (
    GEOMETRY_TYPE_TO_JTS_BINDING,
    PG_TO_JAVA_BINDING,
    discover_pipelines,
    get_columns,
    get_geometry_columns,
    load_declared_matviews,
    pick_default_geometry,
    resolve_matviews,
)
from core.utils.logger import get_console_logger

logger = get_console_logger("create_geoserver_layers")


class GeoServerSettings(BaseSettings):
    GEOSERVER_URL: str
    GEOSERVER_USER: str
    GEOSERVER_PASSWORD: str
    GEOSERVER_VERIFY_SSL: bool = False


def build_geoserver_client(settings: GeoServerSettings | None = None) -> GeoServerClient:
    settings = settings or GeoServerSettings()
    return GeoServerClient(
        base_url=settings.GEOSERVER_URL,
        user=settings.GEOSERVER_USER,
        password=settings.GEOSERVER_PASSWORD,
        verify_ssl=settings.GEOSERVER_VERIFY_SSL,
    )


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pipeline",
        action="append",
        dest="pipelines",
        help="Pipeline a procesar (repetible). Default: todos los pipelines detectados automáticamente.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Solo loggea qué haría, sin llamar al REST API de GeoServer.",
    )
    return parser


def build_attribute_entry(column_name: str, binding: str) -> dict:
    return {"name": column_name, "binding": binding}


def build_featuretype_fields(
    matview: str,
    columns: list,
    geoms: list,
    default_geom,
) -> dict:
    """Construye los campos gestionados del featureType (ver
    geoserver.py::_MANAGED_FEATURETYPE_KEYS). Si hay más de una columna de
    geometría, arma una lista explícita de `attributes` con la geometría
    default primero, seguida de las demás columnas (incluyendo la(s) otra(s)
    geometría(s) como atributo normal) -- técnica 1 del plan. Si solo hay una
    geometría, no hace falta declarar `attributes`: es inambigua.
    """
    fields: dict = {
        "name": matview,
        "nativeName": matview,
        "srs": f"EPSG:{default_geom.srid}",
        "projectionPolicy": "FORCE_DECLARED",
        "enabled": True,
    }

    if len(geoms) <= 1:
        return fields

    geom_columns = {g.column for g in geoms}
    ordered_columns = [c for c in columns if c.name == default_geom.column]
    ordered_columns += [c for c in columns if c.name != default_geom.column]

    attributes = []
    for col in ordered_columns:
        if col.name in geom_columns:
            geom_info = next(g for g in geoms if g.column == col.name)
            binding = GEOMETRY_TYPE_TO_JTS_BINDING.get(geom_info.geometry_type, GEOMETRY_TYPE_TO_JTS_BINDING["GEOMETRY"])
        else:
            binding = PG_TO_JAVA_BINDING.get(col.pg_type)
            if binding is None:
                logger.warning(f"[{matview}] tipo Postgres sin mapeo conocido: {col.pg_type} (columna {col.name})")
                binding = "java.lang.String"
        attributes.append(build_attribute_entry(col.name, binding))

    fields["attributes"] = {"attribute": attributes}
    return fields


def remove_orphan_featuretypes(gs: GeoServerClient, workspace: str, kept_layers: list[str]) -> None:
    """Borra en GeoServer cualquier featuretype de `workspace` que no esté en
    `kept_layers` (lo que se acaba de crear/actualizar en esta corrida) --
    vistas renombradas, eliminadas, o que perdieron su columna de geometría.
    """
    existing = gs.list_featuretypes(workspace, workspace)
    for name in existing:
        if name not in kept_layers:
            gs.delete_featuretype(workspace, workspace, name)


def process_pipeline(gs: GeoServerClient, pipeline_name: str, dry_run: bool) -> None:
    config = importlib.import_module(f"core.pipelines.{pipeline_name}.config")
    declared = load_declared_matviews(pipeline_name)
    if declared is None:
        raise ValueError(f"{pipeline_name} no declara MATERIALIZED_VIEWS")
    settings = config.settings

    workspace = f"proxmox_{pipeline_name}"
    db = Database(pipeline_name, settings.database_url)
    db.connect()
    try:
        matviews = resolve_matviews(db, declared)
        logger.info(f"[{pipeline_name}] {len(matviews)} vistas materializadas resueltas: {matviews}")

        if not dry_run:
            gs.ensure_workspace(workspace)
            gs.ensure_postgis_datastore(
                workspace,
                workspace,
                host=settings.DB_HOST,
                port=settings.DB_PORT,
                database=settings.DB_NAME,
                schema="public",
                user=settings.DB_USER,
                password=settings.DB_PASSWORD,
                expose_primary_keys=True,
            )

        ensured_layers: list[str] = []
        for matview in matviews:
            geoms = get_geometry_columns(db, matview)
            if not geoms:
                logger.warning(f"[{pipeline_name}] {matview} no tiene columna de geometría, se omite")
                continue

            default_geom = pick_default_geometry(geoms)
            columns = get_columns(db, matview)
            fields = build_featuretype_fields(matview, columns, geoms, default_geom)

            if dry_run:
                logger.info(
                    f"[dry-run] {workspace}/{workspace}/{matview} "
                    f"(geometría default={default_geom.column}, srid={default_geom.srid})"
                )
                continue

            gs.ensure_featuretype(workspace, workspace, layer_name=matview, managed_fields=fields)
            ensured_layers.append(matview)

        if not dry_run:
            remove_orphan_featuretypes(gs, workspace, ensured_layers)
    finally:
        db.disconnect()


def main() -> int:
    load_dotenv()
    args = build_arg_parser().parse_args()
    gs = build_geoserver_client()

    targets = args.pipelines or discover_pipelines()
    if not targets:
        logger.error("No se detectó ningún pipeline con MATERIALIZED_VIEWS")
        return 1

    for name in targets:
        logger.info(f"=== {name} ===")
        try:
            process_pipeline(gs, name, dry_run=args.dry_run)
        except Exception:
            logger.error(f"[{name}] falló, se continúa con el resto del batch", exc_info=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
