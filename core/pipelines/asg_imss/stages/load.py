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

        unknown_static_values = self._detect_unknown_static_values(files)

        with self.db.get_session() as session:
            if self.mode == "bootstrap":
                self._load_static_catalogs(session, unknown_static_values)
                self._load_dynamic_catalogs(session, catalogs)
            elif unknown_static_values:
                self._insert_placeholder_catalog_values(session, unknown_static_values)

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

        if unknown_static_values:
            self.logger.warning("=" * 60)
            self.logger.warning("NUEVOS VALORES SIN DESCRIPCIÓN DETECTADOS EN CATÁLOGOS ESTÁTICOS:")
            for catalog, values in unknown_static_values.items():
                self.logger.warning(f"  {catalog}: {values}")
            self.logger.warning("Actualizar los CATALOG_* correspondientes en consts.py.")
            self.logger.warning("=" * 60)

        self.logger.info(f"Carga completa. Total upserted: {total_upserted:,}")
        return {"row_count": total_upserted, "unknown_catalog_values": unknown_static_values}

    def finalization(self, input_data: Optional[Any] = None) -> dict:
        if self.db:
            self.db.disconnect()

        clean_directory(self.work_dir, self.logger)
        self.logger.info(f"Pipeline {PIPELINE_NAME} load finalizado.")
        return input_data

    def _load_static_catalogs(self, session, unknown_values: dict[str, list] | None = None) -> None:
        self.logger.info("Cargando catálogos estáticos...")
        extra = unknown_values or {}

        tamanio_patron = list(CATALOG_TAMANIO_PATRON) + [
            {"cve": str(v), "descripcion": "[SIN DESCRIPCIÓN]"} for v in extra.get("tamanio_patron", [])
        ]
        insert_records(session, tamanio_patron, CatTamanioPatron, conflict_keys=["cve"])
        self.logger.info(f"  CatTamanioPatron: {len(tamanio_patron)} registros.")

        sexo = list(CATALOG_SEXO) + [{"cve": int(v), "descripcion": "[SIN DESCRIPCIÓN]"} for v in extra.get("sexo", [])]
        insert_records(session, sexo, CatSexo, conflict_keys=["cve"])
        self.logger.info(f"  CatSexo: {len(sexo)} registros.")

        rango_edad = list(CATALOG_RANGO_EDAD) + [
            {"cve": str(v), "descripcion": "[SIN DESCRIPCIÓN]"} for v in extra.get("rango_edad", [])
        ]
        insert_records(session, rango_edad, CatRangoEdad, conflict_keys=["cve"])
        self.logger.info(f"  CatRangoEdad: {len(rango_edad)} registros.")

        rango_salarial = list(CATALOG_RANGO_SALARIAL) + [
            {"cve": str(v), "descripcion": "[SIN DESCRIPCIÓN]"} for v in extra.get("rango_salarial", [])
        ]
        insert_records(session, rango_salarial, CatRangoSalarial, conflict_keys=["cve"])
        self.logger.info(f"  CatRangoSalarial: {len(rango_salarial)} registros.")

        rango_uma = list(CATALOG_RANGO_UMA) + [
            {"cve": str(v), "descripcion": "[SIN DESCRIPCIÓN]"} for v in extra.get("rango_uma", [])
        ]
        insert_records(session, rango_uma, CatRangoUma, conflict_keys=["cve"])
        self.logger.info(f"  CatRangoUma: {len(rango_uma)} registros.")

        session.flush()

    def _detect_unknown_static_values(self, files: list[dict]) -> dict[str, list]:
        """Scans transformed pickles for static catalog values not present in consts."""
        _CVE_CAST: dict[str, type] = {
            "tamanio_patron": str,
            "sexo": int,
            "rango_edad": str,
            "rango_salarial": str,
            "rango_uma": str,
        }
        known: dict[str, set] = {
            "tamanio_patron": {str(r["cve"]) for r in CATALOG_TAMANIO_PATRON},
            "sexo": {int(r["cve"]) for r in CATALOG_SEXO},
            "rango_edad": {str(r["cve"]) for r in CATALOG_RANGO_EDAD},
            "rango_salarial": {str(r["cve"]) for r in CATALOG_RANGO_SALARIAL},
            "rango_uma": {str(r["cve"]) for r in CATALOG_RANGO_UMA},
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
        """Inserts placeholder entries for newly discovered static catalog values (update mode)."""
        self.logger.info("Insertando valores nuevos en catálogos estáticos (sin descripción)...")
        _catalog_map: dict[str, tuple] = {
            "tamanio_patron": (CatTamanioPatron, str),
            "sexo": (CatSexo, int),
            "rango_edad": (CatRangoEdad, str),
            "rango_salarial": (CatRangoSalarial, str),
            "rango_uma": (CatRangoUma, str),
        }
        for col, values in unknown_values.items():
            model, cve_cast = _catalog_map[col]
            records = [{"cve": cve_cast(v), "descripcion": "[SIN DESCRIPCIÓN]"} for v in values]
            insert_records(session, records, model, conflict_keys=["cve"])
            self.logger.info(f"  {model.__tablename__}: {len(records)} nuevos valores insertados.")
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
