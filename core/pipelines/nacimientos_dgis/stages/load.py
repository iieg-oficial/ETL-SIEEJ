import io
import pandas as pd
from pathlib import Path
from typing import Any, Optional

from core.db import Database
from core.pipelines.nacimientos_dgis.config import settings
from core.pipelines.nacimientos_dgis.constants import COPY_COLS, PIPELINE_NAME
from core.pipelines.nacimientos_dgis.queries import (
    COPY_STG,
    INSERT_NACIMIENTOS_ADOLESCENTES,
    INSERT_TASA_FECUNDIDAD,
    REFRESH_VIEWS,
    TRUNCATE_STG,
)
from core.pipelines.nacimientos_dgis.schemas import StgNacimientos
from core.pipelines.stage import Stage
from core.utils.bulk_ops import count_records
from core.utils.files import cleanup_pipeline_data
from core.utils.logger import get_logger


class NacimientosDgisLoad(Stage):
    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "load")
        self.logger = get_logger(f"{PIPELINE_NAME}.load")
        self.mode = mode
        self.db = Database(settings.DB_NAME, settings.database_url)

    def source(self, input_data: Optional[Any] = None) -> pd.DataFrame:
        pkl = Path(f"data/transform/{PIPELINE_NAME}/nacimientos.pkl")
        if pkl.exists():
            self.logger.info("[source] Loading transform pkl")
            return pd.read_pickle(pkl)
        return input_data

    def _prepare_copy_buffer(self, df: pd.DataFrame) -> io.StringIO:
        buffer = io.StringIO()
        df[COPY_COLS].to_csv(buffer, index=False, header=False)
        buffer.seek(0)
        return buffer

    def _load_stg(self, df: pd.DataFrame) -> None:
        if self.mode == "bootstrap":
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(TRUNCATE_STG)
                cursor.close()

        buffer = self._prepare_copy_buffer(df)

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.copy_expert(COPY_STG, buffer)
            cursor.close()

        self.logger.info(f"[action] {len(df):,} rows loaded into stg_nacimientos")

    def _load_calculated_tables(self) -> None:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(INSERT_TASA_FECUNDIDAD)
            self.logger.info("[action] stg_tasa_fecundidad populated")
            cursor.execute(INSERT_NACIMIENTOS_ADOLESCENTES)
            self.logger.info("[action] stg_nacimientos_adolescentes populated")
            cursor.close()

    def _refresh_views(self) -> None:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(REFRESH_VIEWS)
            cursor.close()

        self.logger.info("[action] materialized views refreshed")

    def action(self, input_data: pd.DataFrame) -> dict[str, Any]:
        if input_data is None or input_data.empty:
            self.logger.info("[action] No data to load")
            return None

        self.logger.info(f"[action] Loading {len(input_data):,} rows")

        try:
            self.db.connect()
            self._load_stg(input_data)
            self._load_calculated_tables()
            self._refresh_views()
        except Exception:
            self.db.disconnect()
            raise

        return {"rows_loaded": len(input_data)}

    def finalization(self, input_data: Any) -> Any:
        cleanup_pipeline_data(PIPELINE_NAME)
        if input_data is None:
            return None
        try:
            with self.db.get_session() as session:
                total = count_records(session, StgNacimientos)
            self.logger.info(f"[finalization] {total:,} rows in {StgNacimientos.__tablename__}")
        finally:
            self.db.disconnect()
        return input_data
