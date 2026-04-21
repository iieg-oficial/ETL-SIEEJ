from pathlib import Path
from typing import Any, Optional

import numpy as np
import pandas as pd

from core.db import Database
from core.pipelines.stage import Stage
from core.pipelines.censo_poblacion.attributes.censo_poblacion import CensoPoblacionTables as T
from core.pipelines.censo_poblacion.config import settings
from core.pipelines.censo_poblacion.schemas import Fuentes, Localidades, Poblacion
from core.utils import df_to_records
from core.utils.bulk_ops import bulk_insert, count_records, insert_records, sync_id_sequence
from core.utils.files import cleanup_pipeline_data
from core.utils.logger import get_logger

logger = get_logger("censo_poblacion.load")


class CensoPoblacionLoad(Stage):
    def __init__(self):
        super().__init__("censo_poblacion", "load")
        self.db = Database(settings.DB_NAME, settings.database_url)

    def source(self, input_data: Optional[Any] = None) -> dict[str, Any]:
        pkl_df = Path("data/transform/censo_poblacion/poblacion_df.pkl")
        pkl_catalogs = Path("data/transform/censo_poblacion/poblacion_catalogs.pkl")

        if pkl_df.exists() and pkl_catalogs.exists():
            logger.info("Loading load input from transform pkl files")
            return {
                "df": pd.read_pickle(pkl_df),
                "catalogs": pd.read_pickle(pkl_catalogs).to_dict(),
            }

        return input_data

    def _load_catalogs(self, session, catalogs: dict) -> None:
        logger.info(f"Loading {len(catalogs[T.FUENTES])} fuentes")
        insert_records(session, catalogs[T.FUENTES], Fuentes, conflict_keys=[Fuentes.id.key])

        logger.info(f"Loading {len(catalogs[T.LOCALIDADES])} localidades")
        insert_records(session, catalogs[T.LOCALIDADES], Localidades, conflict_keys=[Localidades.id.key])

    def action(self, input_data: dict[str, Any]) -> dict[str, Any]:
        df = input_data["df"]
        if df.empty:
            logger.info("Empty DataFrame, skipping load")
            return None

        logger.info(f"Loading {len(df)} poblacion rows")

        try:
            self.db.connect()
            with self.db.get_session() as session:
                records_before = count_records(session, Poblacion)

                self._load_catalogs(session, input_data["catalogs"])

                sync_id_sequence(session, Poblacion)
                cols = [c for c in Poblacion.columns() if c != Poblacion.id.key]
                records = df_to_records(df.replace({np.nan: None}), cols)
                bulk_insert(session, records, Poblacion)

        except Exception as e:
            logger.error(f"Load error: {e}")
            self.db.disconnect()
            raise

        return {"data": input_data, "records_before": records_before}

    def finalization(self, input_data: Any) -> Any:
        cleanup_pipeline_data("censo_poblacion")
        if input_data is None:
            return None
        try:
            with self.db.get_session() as session:
                total = count_records(session, Poblacion)
                inserted = total - input_data["records_before"]
            logger.info(f"{total:,} poblacion records in database")
            logger.info(f"{inserted:,} poblacion records inserted")
        finally:
            self.db.disconnect()

        return input_data["data"]
