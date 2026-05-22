import pandas as pd
from pathlib import Path
from typing import Any, Optional

from core.db import Database
from core.pipelines.participacion_ciudadana.config import settings
from core.pipelines.participacion_ciudadana.schemas import StgParticipacion
from core.pipelines.stage import Stage
from core.utils import df_to_records
from core.utils.bulk_ops import bulk_insert, count_records, sync_id_sequence
from core.utils.files import cleanup_pipeline_data
from core.utils.logger import get_logger


class ParticipacionCiudadanaLoad(Stage):
    def __init__(self):
        super().__init__("participacion_ciudadana", "load")
        self.logger = get_logger("participacion_ciudadana.load")
        self.db = Database(settings.DB_NAME, settings.database_url)

    def source(self, input_data: Optional[Any] = None) -> pd.DataFrame:
        pkl_path = Path("data/transform/participacion_ciudadana/participacion.pkl")

        if pkl_path.exists():
            self.logger.info("[source] Loading transform pkl")
            return pd.read_pickle(pkl_path)

        return input_data

    def action(self, input_data: pd.DataFrame) -> dict[str, Any]:
        if input_data.empty:
            self.logger.info("[action] Empty input, skipping load")
            return None

        self.logger.info(f"[action] Loading {len(input_data)} rows")

        try:
            self.db.connect()
            with self.db.get_session() as session:
                records_before = count_records(session, StgParticipacion)

                cols = [c for c in StgParticipacion.columns() if c != StgParticipacion.id.key]
                df = input_data.astype(object).where(input_data.notna(), None)

                sync_id_sequence(session, StgParticipacion)
                bulk_insert(session, df_to_records(df, cols), StgParticipacion)

        except Exception:
            self.db.disconnect()
            raise

        return {"records_before": records_before}

    def finalization(self, input_data: Any) -> Any:
        cleanup_pipeline_data("participacion_ciudadana")
        if input_data is None:
            return None
        try:
            with self.db.get_session() as session:
                total = count_records(session, StgParticipacion)
                inserted = total - input_data["records_before"]
            self.logger.info(f"[finalization] {total:,} stg_participacion in database ({inserted:,} inserted)")
        finally:
            self.db.disconnect()

        return input_data
