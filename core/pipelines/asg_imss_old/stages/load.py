import math
from pathlib import Path
from typing import Any, Optional

import pandas as pd
from sqlalchemy import select

from core.db import Database
from core.pipelines.asg_imss_old.config import settings
from core.pipelines.asg_imss_old.consts import PIPELINE_NAME
from core.pipelines.asg_imss_old.schemas import (
    AsgImssBase,
    AsgImssDatos,
    CatDelegacion,
    CatEntidadMunicipio,
    CatRangoEdad,
    CatRangoSalarial,
    CatRangoUma,
    CatSector1,
    CatSector2,
    CatSector4,
    CatSexo,
    CatSubdelegacion,
    CatTamanioPatron,
)
from core.pipelines.stage import Stage
from core.utils.bulk_ops import insert_records, sync_id_sequence, upsert_records
from core.utils.files import clean_directory


class AsgImssLoader(Stage):
    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "load")
        self.mode = mode
        self.db: Optional[Database] = None

    def source(self, input_data: Optional[Any] = None) -> dict:
        if not input_data:
            raise ValueError("Load no recibió datos de Transform.")

        self.db = Database(PIPELINE_NAME, settings.database_url)
        self.db.connect()
        AsgImssBase.metadata.create_all(self.db.engine)
        self.logger.info("Tablas verificadas/creadas.")
        return input_data

    def action(self, input_data: Optional[Any] = None) -> dict:
        files: list[dict] = input_data.get("files", [])
        catalogs: dict[str, list[dict]] = input_data.get("catalogs", {})
        unknown_catalog_values: dict[str, list] = input_data.get("unknown_catalog_values", {})
        total_upserted = 0

        with self.db.get_session() as session:
            if self.mode == "bootstrap":
                self._load_all_catalogs(session, catalogs)
            else:
                # Update mode: detect and insert placeholder entries for new static catalog values
                detected_unknowns = self._detect_unknown_static_values(session, files)
                if detected_unknowns:
                    self._insert_placeholder_catalog_values(session, detected_unknowns)
                    unknown_catalog_values = detected_unknowns

        for item in files:
            pkl_path = Path(item["file_path"])
            if not pkl_path.exists():
                self.logger.warning(f"Pickle no encontrado: {pkl_path}")
                continue

            self.logger.info(f"Cargando: {pkl_path.name}")
            df: pd.DataFrame = pd.read_pickle(pkl_path)

            records = [
                {k: (None if isinstance(v, float) and math.isnan(v) else v) for k, v in r.items()}
                for r in df.to_dict("records")
            ]

            with self.db.get_session() as session:
                upsert_records(
                    session,
                    records,
                    AsgImssDatos,
                    conflict_keys=[
                        "fecha_corte",
                        "cve_delegacion",
                        "cve_subdelegacion",
                        "cve_entidad",
                        "cve_municipio",
                        "sector_economico_1",
                        "sector_economico_2",
                        "sector_economico_4",
                        "tamanio_patron",
                        "sexo",
                        "rango_edad",
                        "rango_salarial",
                        "rango_uma",
                    ],
                    chunk_size=settings.ASG_LOAD_BATCH_SIZE,
                )

            total_upserted += len(records)
            self.logger.info(f"  {pkl_path.name}: {len(records):,} registros upserted.")

        with self.db.get_session() as session:
            sync_id_sequence(session, AsgImssDatos)
            for model in [
                CatDelegacion,
                CatSubdelegacion,
                CatEntidadMunicipio,
                CatSector1,
                CatSector2,
                CatSector4,
                CatTamanioPatron,
                CatSexo,
                CatRangoEdad,
                CatRangoSalarial,
                CatRangoUma,
            ]:
                sync_id_sequence(session, model)

        self.logger.info(f"Carga completa. Total upserted: {total_upserted:,}")
        return {"row_count": total_upserted, "unknown_catalog_values": unknown_catalog_values}

    def finalization(self, input_data: Optional[Any] = None) -> dict:
        if self.db:
            self.db.disconnect()

        unknown_catalog_values = input_data.get("unknown_catalog_values", {}) if input_data else {}
        if unknown_catalog_values:
            self.logger.warning("=" * 60)
            self.logger.warning("VALORES SIN DESCRIPCIÓN EN CATÁLOGOS:")
            for catalog, values in unknown_catalog_values.items():
                self.logger.warning(f"  {catalog}: {values}")
            if self.mode == "update":
                self.logger.warning("Actualizar los CATALOG_* correspondientes en consts.py.")
            self.logger.warning("=" * 60)

        transform_dir = Path(f"data/transform/{PIPELINE_NAME}")
        clean_directory(transform_dir, self.logger)

        self.logger.info(f"Pipeline {PIPELINE_NAME} load finalizado.")
        return input_data

    def _load_all_catalogs(self, session, catalogs: dict[str, list[dict]]) -> None:
        """Load all catalog tables from catalog data produced by the transform stage."""
        self.logger.info("Cargando catálogos...")

        tamanio_patron = catalogs.get("tamanio_patron", [])
        if tamanio_patron:
            insert_records(session, tamanio_patron, CatTamanioPatron, conflict_keys=["cve"])
            self.logger.info(f"  CatTamanioPatron: {len(tamanio_patron)} registros.")

        sexo = catalogs.get("sexo", [])
        if sexo:
            insert_records(session, sexo, CatSexo, conflict_keys=["cve"])
            self.logger.info(f"  CatSexo: {len(sexo)} registros.")

        rango_edad = catalogs.get("rango_edad", [])
        if rango_edad:
            insert_records(session, rango_edad, CatRangoEdad, conflict_keys=["cve"])
            self.logger.info(f"  CatRangoEdad: {len(rango_edad)} registros.")

        rango_salarial = catalogs.get("rango_salarial", [])
        if rango_salarial:
            insert_records(session, rango_salarial, CatRangoSalarial, conflict_keys=["cve"])
            self.logger.info(f"  CatRangoSalarial: {len(rango_salarial)} registros.")

        rango_uma = catalogs.get("rango_uma", [])
        if rango_uma:
            insert_records(session, rango_uma, CatRangoUma, conflict_keys=["cve"])
            self.logger.info(f"  CatRangoUma: {len(rango_uma)} registros.")

        delegaciones = catalogs.get("delegacion", [])
        if delegaciones:
            insert_records(session, delegaciones, CatDelegacion, conflict_keys=["cve_delegacion"])
            self.logger.info(f"  CatDelegacion: {len(delegaciones)} registros.")

        subdelegaciones = catalogs.get("subdelegacion", [])
        if subdelegaciones:
            insert_records(
                session, subdelegaciones, CatSubdelegacion, conflict_keys=["cve_delegacion", "cve_subdelegacion"]
            )
            self.logger.info(f"  CatSubdelegacion: {len(subdelegaciones)} registros.")

        entidades_municipio = catalogs.get("entidad_municipio", [])
        if entidades_municipio:
            insert_records(session, entidades_municipio, CatEntidadMunicipio, conflict_keys=["cve_municipio"])
            self.logger.info(f"  CatEntidadMunicipio: {len(entidades_municipio)} registros.")

        sectores_1 = catalogs.get("sector_1", [])
        if sectores_1:
            insert_records(session, sectores_1, CatSector1, conflict_keys=["cve_sector_1"])
            self.logger.info(f"  CatSector1: {len(sectores_1)} registros.")

        sectores_2 = catalogs.get("sector_2", [])
        if sectores_2:
            insert_records(session, sectores_2, CatSector2, conflict_keys=["cve_sector_1", "cve_sector_2"])
            self.logger.info(f"  CatSector2: {len(sectores_2)} registros.")

        sectores_4 = catalogs.get("sector_4", [])
        if sectores_4:
            insert_records(session, sectores_4, CatSector4, conflict_keys=["cve_sector_2", "cve_sector_4"])
            self.logger.info(f"  CatSector4: {len(sectores_4)} registros.")

        session.flush()

    def _detect_unknown_static_values(self, session, files: list[dict]) -> dict[str, list]:
        """Scans transformed pickles for static catalog values not present in the DB."""
        _CVE_CAST: dict[str, type] = {
            "tamanio_patron": str,
            "sexo": int,
            "rango_edad": str,
            "rango_salarial": str,
            "rango_uma": str,
        }
        _catalog_model = {
            "tamanio_patron": CatTamanioPatron,
            "sexo": CatSexo,
            "rango_edad": CatRangoEdad,
            "rango_salarial": CatRangoSalarial,
            "rango_uma": CatRangoUma,
        }
        known: dict[str, set] = {
            col: set(session.scalars(select(model.cve)).all()) for col, model in _catalog_model.items()
        }
        found: dict[str, set] = {k: set() for k in known}

        for item in files:
            pkl_path = Path(item["file_path"])
            if not pkl_path.exists():
                continue
            df: pd.DataFrame = pd.read_pickle(pkl_path)
            for col, cast in _CVE_CAST.items():
                if col in df.columns:
                    for raw_val in df[col].dropna().unique():
                        try:
                            val = cast(raw_val)
                        except (ValueError, TypeError):
                            continue
                        if val not in known[col]:
                            found[col].add(val)

        return {k: sorted(v, key=str) for k, v in found.items() if v}

    def _insert_placeholder_catalog_values(self, session, unknown_values: dict[str, list]) -> None:
        """Insert placeholder entries for newly discovered static catalog values (update mode)."""
        self.logger.info("Insertando valores nuevos en catálogos estáticos (sin descripción)...")
        _catalog_map: dict[str, tuple] = {
            "tamanio_patron": (CatTamanioPatron, str),
            "sexo": (CatSexo, int),
            "rango_edad": (CatRangoEdad, str),
            "rango_salarial": (CatRangoSalarial, str),
            "rango_uma": (CatRangoUma, str),
        }
        for col, values in unknown_values.items():
            if col not in _catalog_map:
                continue
            model, cve_cast = _catalog_map[col]
            records = [{"cve": cve_cast(v), "descripcion": "[SIN DESCRIPCIÓN]"} for v in values]
            insert_records(session, records, model, conflict_keys=["cve"])
            self.logger.info(f"  {model.__tablename__}: {len(records)} nuevos valores insertados.")
        session.flush()
