import math
from pathlib import Path
from typing import Any, Optional

import pandas as pd

from core.db import Database
from core.pipelines.asg_imss.config import settings
from core.pipelines.asg_imss.consts import (
    CATALOG_RANGO_EDAD,
    CATALOG_RANGO_SALARIAL,
    CATALOG_RANGO_UMA,
    CATALOG_SEXO,
    CATALOG_TAMANIO_PATRON,
    PIPELINE_NAME,
)
from core.pipelines.asg_imss.schemas import (
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
from core.utils.bulk_ops import insert_records, upsert_records
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
        total_upserted = 0

        with self.db.get_session() as session:
            if self.mode == "bootstrap":
                self._load_static_catalogs(session)
                self._load_dynamic_catalogs(session, catalogs)

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
                    conflict_keys=["record_hash"],
                    chunk_size=settings.ASG_LOAD_BATCH_SIZE,
                )

            total_upserted += len(records)
            self.logger.info(f"  {pkl_path.name}: {len(records):,} registros upserted.")

        self.logger.info(f"Carga completa. Total upserted: {total_upserted:,}")
        return {"row_count": total_upserted}

    def finalization(self, input_data: Optional[Any] = None) -> dict:
        if self.db:
            self.db.disconnect()

        clean_directory(self.work_dir, self.logger)
        self.logger.info(f"Pipeline {PIPELINE_NAME} load finalizado.")
        return input_data

    def _load_static_catalogs(self, session) -> None:
        self.logger.info("Cargando catálogos estáticos...")

        insert_records(session, CATALOG_TAMANIO_PATRON, CatTamanioPatron, conflict_keys=["cve"])
        self.logger.info(f"  CatTamanioPatron: {len(CATALOG_TAMANIO_PATRON)} registros.")

        insert_records(session, CATALOG_SEXO, CatSexo, conflict_keys=["cve"])
        self.logger.info(f"  CatSexo: {len(CATALOG_SEXO)} registros.")

        insert_records(session, CATALOG_RANGO_EDAD, CatRangoEdad, conflict_keys=["cve"])
        self.logger.info(f"  CatRangoEdad: {len(CATALOG_RANGO_EDAD)} registros.")

        insert_records(session, CATALOG_RANGO_SALARIAL, CatRangoSalarial, conflict_keys=["cve"])
        self.logger.info(f"  CatRangoSalarial: {len(CATALOG_RANGO_SALARIAL)} registros.")

        insert_records(session, CATALOG_RANGO_UMA, CatRangoUma, conflict_keys=["cve"])
        self.logger.info(f"  CatRangoUma: {len(CATALOG_RANGO_UMA)} registros.")

        session.flush()

    def _load_dynamic_catalogs(self, session, catalogs: dict[str, list[dict]]) -> None:
        self.logger.info("Cargando catálogos dinámicos...")

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
