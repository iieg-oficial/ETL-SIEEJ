from pathlib import Path
from typing import Any, Optional

import pandas as pd

from core.db import Database
from core.pipelines.scian.config import settings
from core.pipelines.scian.constants import MODELOS, NIVELES, PADRE_FK
from core.pipelines.stage import Stage
from core.utils import df_to_records
from core.utils.bulk_ops import bulk_insert, count_records, get_mapping, sync_id_sequence
from core.utils.files import cleanup_pipeline_data
from core.utils.logger import get_logger

logger = get_logger("scian.load")


class ScianLoad(Stage):
    def __init__(self):
        super().__init__("scian", "load")
        self.db = Database(settings.DB_NAME, settings.database_url)

    def source(self, input_data: Optional[Any] = None) -> dict[str, pd.DataFrame]:
        transform_dir = Path("data/transform/scian")
        pkl_paths = {f"df_{nivel}": transform_dir / f"df_{nivel}.pkl" for nivel in NIVELES}

        if all(path.exists() for path in pkl_paths.values()):
            logger.info("Loading load input from transform pkl files")
            return {key: pd.read_pickle(path) for key, path in pkl_paths.items()}

        return input_data

    def _map_padre(self, session, df: pd.DataFrame, model, padre_model) -> pd.DataFrame:
        fk_col = PADRE_FK[model]
        padre_map = get_mapping(session, padre_model, padre_model.codigo.key, padre_model.id.key)

        df[fk_col] = df["padre"].map(padre_map)
        huerfanos = int(df[fk_col].isna().sum())
        if huerfanos:
            raise ValueError(
                f"{huerfanos} {model.__tablename__} rows without a parent in '{padre_model.__tablename__}'"
            )

        df[fk_col] = df[fk_col].astype(int)
        return df

    def action(self, input_data: dict[str, pd.DataFrame]) -> dict[str, Any] | None:
        if all(df.empty for df in input_data.values()):
            logger.info("Empty DataFrames, skipping load")
            return None

        try:
            self.db.connect()
            with self.db.get_session() as session:
                records_before = {model.__tablename__: count_records(session, model) for model in MODELOS}

                for posicion, model in enumerate(MODELOS):
                    sync_id_sequence(session, model)

                    df = input_data[f"df_{model.__tablename__}"].copy()
                    if posicion > 0:
                        df = self._map_padre(session, df, model, MODELOS[posicion - 1])

                    cols = [c for c in model.columns() if c != model.id.key]
                    bulk_insert(session, df_to_records(df.astype(object).where(df.notna(), None), cols), model)

        except Exception as e:
            logger.error(f"Load error: {e}")
            self.db.disconnect()
            raise

        return {"data": input_data, "records_before": records_before}

    def finalization(self, input_data: Any) -> Any:
        cleanup_pipeline_data("scian")
        if input_data is None:
            return None

        try:
            with self.db.get_session() as session:
                for model in MODELOS:
                    total = count_records(session, model)
                    insertados = total - input_data["records_before"][model.__tablename__]
                    logger.info(f"{total:,} {model.__tablename__} records in database ({insertados:,} inserted)")
        finally:
            self.db.disconnect()

        return input_data["data"]
