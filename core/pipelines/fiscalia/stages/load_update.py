
from core.pipelines.stage import Stage
from typing import Any, Optional

from core.utils.logger import get_logger
from core.utils.bulk_ops import insert_records, bulk_insert, count_records
from core.db import Database
from core.pipelines.fiscalia.schemas import Casos, Calles, Cruces, Colonias
from core.pipelines.fiscalia.config import settings


class FiscaliaLoadUpdate(Stage):
    def __init__(self, pipeline_name: str = 'fiscalia', mode: str = 'update'):
        super().__init__(pipeline_name, 'load')
        self.mode = mode
        self.logger = get_logger(f"{pipeline_name}.load")
        self.db = Database("fiscalia", settings.database_url)

    def source(self, input_data: Optional[Any]) -> Any:
        self.logger.info(f"📥 [source] Records received: {list(input_data.keys())}")
        return input_data

    def action(self, input_data: Any) -> Any:
        self.logger.info("⚙️ [action] Inserting update data into DB")

        self.db.connect()

        with self.db.get_session() as session:
            try:
                insert_records(session, input_data["calles_records"], Calles, conflict_keys=["id"])
                insert_records(session, input_data["cruces_records"], Cruces, conflict_keys=["id"])
                insert_records(session, input_data["colonias_records"], Colonias, conflict_keys=["id"])

                bulk_insert(session, input_data["casos_records"], Casos, chunk_size=50_000)

                session.commit()
                self.logger.info("Data inserted successfully!")
            except Exception as e:
                session.rollback()
                self.logger.error(e)
                raise

        return input_data

    def finalization(self, input_data: Any) -> Any:
        with self.db.get_session() as session:
            total_cases = count_records(session, Casos)

        self.db.disconnect()

        self.logger.info(f"📤 [finalization] Load completed: {format(total_cases, ',')} total cases in DB")
        return input_data

