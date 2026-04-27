from pathlib import Path
from typing import Any, Optional

import numpy as np
import pandas as pd

from core.db import Database
from core.pipelines.pobreza_multidimencional.config import settings
from core.pipelines.pobreza_multidimencional.consts import CATALOG_CSV_DIR, PIPELINE_NAME
from core.pipelines.pobreza_multidimencional.schemas import (
    CatEntidad,
    CatParentesco,
    PobrezaMultidimencionalBase,
    PobrezaMultidimencionalDatos,
)
from core.pipelines.stage import Stage
from core.utils.bulk_ops import insert_records, sync_id_sequence, upsert_records
from core.utils.files import clean_directory


class PobrezaMultidimencionalLoad(Stage):
    """Carga catálogos, resuelve cvegeo y persiste los microdatos MMP."""

    def __init__(self, year: int):
        super().__init__(PIPELINE_NAME, "load")
        self.year = year
        self.db: Optional[Database] = None

    def source(self, input_data: Optional[Any] = None) -> dict:
        if not input_data or "df" not in input_data:
            raise ValueError("Load no recibió datos de Transform")
        self.db = Database(PIPELINE_NAME, settings.database_url)
        self.db.connect()
        PobrezaMultidimencionalBase.metadata.create_all(self.db.engine)
        return input_data

    def action(self, input_data: Optional[Any] = None) -> dict:
        df: pd.DataFrame = input_data["df"]
        year: int = input_data["year"]

        with self.db.get_session() as session:
            # 1. Poblar catálogos desde los CSV de ENIGH (idempotente)
            self._load_catalogs(session)

            # 2. Resolver municipio_id a partir de ubica_geo (cvegeo)
            municipio_cache = self._load_cvegeo_mapping(session)
            df["municipio_id"] = df["ubica_geo"].map(municipio_cache)

            unmatched = df[df["municipio_id"].isna() & df["ubica_geo"].notna()]
            if not unmatched.empty:
                self.logger.warning(
                    f"[{year}] {len(unmatched)} registros sin match en cvegeo_municipalities"
                )

            # 3. Upsert datos principales (idempotente por llave natural)
            # replace NaN→None: df.where() no convierte NaN en columnas numéricas
            records = df.replace({np.nan: None}).to_dict("records")
            upsert_records(
                session,
                records,
                PobrezaMultidimencionalDatos,
                conflict_keys=["folioviv", "foliohog", "numren", "anio"],
                chunk_size=settings.POBREZA_MULTIDIMENCIONAL_LOAD_BATCH_SIZE,
            )
            sync_id_sequence(session, PobrezaMultidimencionalDatos)

        self.logger.info(f"[{year}] {len(df)} registros cargados")
        return {"row_count": len(df), "year": year}

    def finalization(self, input_data: Optional[Any] = None) -> dict:
        clean_directory(self.work_dir, self.logger)
        if self.db and self.db.is_connected:
            self.db.disconnect()
        return input_data

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _load_catalogs(self, session) -> None:
        """Inserta registros de catálogos desde los CSV de ENIGH."""
        self._load_catalog_csv(
            session,
            csv_file=Path(CATALOG_CSV_DIR) / "cat_entidades_federativas.csv",
            model=CatEntidad,
        )
        self._load_catalog_csv(
            session,
            csv_file=Path(CATALOG_CSV_DIR) / "cat_parentesco.csv",
            model=CatParentesco,
        )

    def _load_catalog_csv(self, session, csv_file: Path, model) -> None:
        """Lee un CSV de catálogo ENIGH e inserta sus filas en la BD."""
        if not csv_file.exists():
            self.logger.warning(f"Catálogo no encontrado: {csv_file}")
            return

        # Los CSV tienen una fila de título antes de la cabecera real
        raw = pd.read_csv(csv_file, header=None, dtype=str, encoding="utf-8")

        # Detectar fila de cabecera (la que contiene "Código")
        header_row = None
        for i, row in raw.iterrows():
            if any("digo" in str(v) for v in row.values):
                header_row = i
                break

        if header_row is None:
            self.logger.warning(f"No se encontró cabecera en {csv_file}")
            return

        df = pd.read_csv(
            csv_file,
            skiprows=header_row + 1,
            header=0,
            names=["codigo", "nombre"],
            dtype=str,
            encoding="utf-8",
        )
        df = df.dropna(subset=["codigo", "nombre"])
        df["codigo"] = pd.to_numeric(df["codigo"], errors="coerce")
        df = df.dropna(subset=["codigo"])
        df["codigo"] = df["codigo"].astype(int)
        df["nombre"] = df["nombre"].str.strip()

        records = df.to_dict("records")
        insert_records(session, records, model, conflict_keys=["codigo"])
        self.logger.info(f"Catálogo '{model.__tablename__}': {len(records)} registros")

    def _load_cvegeo_mapping(self, session) -> dict:
        """Retorna mapa {cvegeo_int → municipio_id} desde la foreign table."""
        from sqlalchemy import text

        result = session.execute(
            text("SELECT id, cvegeo FROM cvegeo_municipalities WHERE cvegeo IS NOT NULL")
        ).fetchall()
        mapping = {row.cvegeo: row.id for row in result}
        self.logger.info(f"Mapa cvegeo cargado: {len(mapping)} municipios")
        return mapping
