import numpy as np
import pandas as pd
from pathlib import Path
from typing import Any, Optional

from core.db import Database
from core.pipelines.stage import Stage
from core.pipelines.intensidad_migratoria.config import settings
from core.pipelines.intensidad_migratoria.queries import MATERIALIZED_VIEWS
from core.pipelines.intensidad_migratoria.schemas import IimEstatal, IimMunicipal
from core.utils import df_to_records
from core.utils.bulk_ops import bulk_insert, count_records, sync_id_sequence
from core.utils.files import cleanup_pipeline_data
from core.utils.logger import get_logger
from core.utils.views import refresh_materialized_views

logger = get_logger("intensidad_migratoria.load")


class IntensidadMigratoriaLoad(Stage):
    def __init__(self):
        super().__init__("intensidad_migratoria", "load")
        self.db = Database(settings.DB_NAME, settings.database_url)

    def source(self, input_data: Optional[Any] = None) -> dict[str, pd.DataFrame]:
        pkl_municipal = Path("data/transform/intensidad_migratoria/df_municipal.pkl")
        pkl_estatal = Path("data/transform/intensidad_migratoria/df_estatal.pkl")

        if pkl_municipal.exists() and pkl_estatal.exists():
            logger.info("Loading load input from transform pkl files")
            return {
                "df_municipal": pd.read_pickle(pkl_municipal),
                "df_estatal": pd.read_pickle(pkl_estatal),
            }

        return input_data

    def action(self, input_data: dict[str, pd.DataFrame]) -> dict[str, Any]:
        df_municipal = input_data["df_municipal"]
        df_estatal = input_data["df_estatal"]

        if df_municipal.empty and df_estatal.empty:
            logger.info("Empty DataFrames, skipping load")
            return None

        try:
            self.db.connect()
            with self.db.get_session() as session:
                records_before_municipal = count_records(session, IimMunicipal)
                records_before_estatal = count_records(session, IimEstatal)

                sync_id_sequence(session, IimMunicipal)
                municipal_cols = [c for c in IimMunicipal.columns() if c != IimMunicipal.id.key]
                bulk_insert(session, df_to_records(df_municipal.replace({np.nan: None}), municipal_cols), IimMunicipal)

                sync_id_sequence(session, IimEstatal)
                estatal_cols = [c for c in IimEstatal.columns() if c != IimEstatal.id.key]
                bulk_insert(session, df_to_records(df_estatal.replace({np.nan: None}), estatal_cols), IimEstatal)

            refresh_materialized_views(self.db, MATERIALIZED_VIEWS)

        except Exception as e:
            logger.error(f"Load error: {e}")
            self.db.disconnect()
            raise

        return {
            "data": input_data,
            "records_before_municipal": records_before_municipal,
            "records_before_estatal": records_before_estatal,
        }

    def finalization(self, input_data: Any) -> Any:
        cleanup_pipeline_data("intensidad_migratoria")
        if input_data is None:
            return None
        try:
            with self.db.get_session() as session:
                total_municipal = count_records(session, IimMunicipal)
                total_estatal = count_records(session, IimEstatal)
                logger.info(
                    f"{total_municipal:,} iim_municipal records in database ({total_municipal - input_data['records_before_municipal']:,} inserted)"
                )
                logger.info(
                    f"{total_estatal:,} iim_estatal records in database ({total_estatal - input_data['records_before_estatal']:,} inserted)"
                )
        finally:
            self.db.disconnect()

        return input_data["data"]
