from typing import Any, Optional

import pandas as pd

from core.db import Database
from core.pipelines.pobreza_multidimensional.config import settings
from core.pipelines.pobreza_multidimensional.consts import PIPELINE_NAME
from core.pipelines.pobreza_multidimensional.schemas import (
    CatEntidad,
    PobrezaMultidimensionalBase,
    PobrezaMultidimensionalDatos,
)
from core.pipelines.stage import Stage
from core.utils.bulk_ops import bulk_insert, get_mapping, insert_records, sync_id_sequence
from core.utils.files import clean_directory


class PobrezaMultidimensionalLoad(Stage):
    """Carga catálogo de entidades y datos tidy de pobreza municipal en la BD."""

    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "load")
        self.mode = mode
        self.db: Optional[Database] = None

    def source(self, input_data: Optional[Any] = None) -> dict:
        if not input_data:
            raise ValueError("Load no recibió datos de Transform")
        self.db = Database(PIPELINE_NAME, settings.database_url)
        self.db.connect()
        PobrezaMultidimensionalBase.metadata.create_all(self.db.engine)
        return input_data

    def action(self, input_data: Optional[Any] = None) -> dict:
        df: pd.DataFrame = input_data["df"]
        catalogs: dict = input_data["catalogs"]

        with self.db.get_session() as session:
            # 1) Sincronizar catálogo de entidades
            insert_records(
                session,
                catalogs["entidad"],
                CatEntidad,
                conflict_keys=["cve_ent"],
            )
            sync_id_sequence(session, CatEntidad)

            # 2) Construir mapa cve_ent → cat_entidad_id
            entidad_map: dict[str, int] = get_mapping(session, CatEntidad, "cve_ent", "id")

            # 3) Resolver cat_entidad_id en el DataFrame
            df["cat_entidad_id"] = df["cve_ent"].map(entidad_map)
            missing = df["cat_entidad_id"].isna().sum()
            if missing > 0:
                self.logger.warning(f"{missing} filas sin cat_entidad_id — se omitirán")
                df = df.dropna(subset=["cat_entidad_id"])

            df["cat_entidad_id"] = df["cat_entidad_id"].astype(int)

            # 4) Preparar registros para la tabla principal
            cols_db = [c.key for c in PobrezaMultidimensionalDatos.__table__.columns if c.key != "id"]
            # Seleccionar solo las columnas que existen en el DataFrame
            available = [c for c in cols_db if c in df.columns]
            records = df[available].to_dict("records")

            # 5) Bulk insert
            bulk_insert(
                session,
                records,
                PobrezaMultidimensionalDatos,
                chunk_size=settings.POBREZA_MULTIDIMENSIONAL_LOAD_BATCH_SIZE,
            )
            sync_id_sequence(session, PobrezaMultidimensionalDatos)

        row_count = len(df)
        self.logger.info(f"Cargados {row_count} registros en {PobrezaMultidimensionalDatos.__tablename__}")
        return {"row_count": row_count}

    def finalization(self, input_data: Optional[Any] = None) -> dict:
        clean_directory(self.work_dir, self.logger)
        if self.db:
            self.db.disconnect()
        return input_data
