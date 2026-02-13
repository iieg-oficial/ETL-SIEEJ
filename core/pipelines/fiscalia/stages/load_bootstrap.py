
from core.pipelines.stage import Stage
from typing import Any, Optional
from sqlalchemy import text

from core.utils import normalize_text
from core.utils.logger import get_logger
from core.utils.bulk_ops import insert_records, bulk_insert, count_records
from core.db import Database
from core.pipelines.fiscalia.schemas import (
    ZonasGeograficas as ZonasGeograficasSchema,
    EsViolencia as EsViolenciaSchema,
    Delitos as DelitosSchema,
    BienesAfectados as BienesAfectadosSchema,
    Colonias as ColoniasSchema,
    Casos as CasosSchema
)
from core.pipelines.fiscalia.config import settings


class FiscaliaLoadBootstrap(Stage):
    def __init__(self, pipeline_name: str = 'fiscalia', mode: str = 'bootstrap'):
        super().__init__(pipeline_name, 'load')
        self.mode = mode
        self.logger = get_logger(f"{pipeline_name}.load")
        self.db = Database("fiscalia", settings.database_url)

    def source(self, input_data: Optional[Any]) -> Any:
        self.logger.info(f"📥 [source] records received: {list(input_data.keys())}")
        return input_data

    def action(self, input_data: Optional[Any]) -> Any:
        self.logger.info("⚙️ [action] Inserting data into DB")

        self.db.connect()

        with self.db.get_session() as session:
            try:
                insert_records(session, input_data["bienes_records"], BienesAfectadosSchema, conflict_keys=["id"])
                insert_records(session, input_data["delitos_records"], DelitosSchema, conflict_keys=["id"])
                insert_records(session, input_data["violencia_records"], EsViolenciaSchema, conflict_keys=["id"])
                insert_records(session, input_data["zonas_geograficas_records"], ZonasGeograficasSchema, conflict_keys=["id"])
                insert_records(session, input_data["colonias_records"], ColoniasSchema, conflict_keys=["id"])

                municipios_rows = session.execute(text("SELECT nomgeo, id FROM cvegeo_municipalities")).all()
                municipios_map = {normalize_text(row[0]): row[1] for row in municipios_rows}

                for record in input_data["casos_records"]:
                    municipio = record.pop("municipio", None)
                    record["municipios_id"] = municipios_map.get(normalize_text(municipio)) if municipio else None

                bulk_insert(session, input_data["casos_records"], CasosSchema, chunk_size=50_000)

                session.commit()
                self.logger.info("Data inserted successfully!")
            except Exception as e:
                session.rollback()
                self.logger.error(e)
                raise

        return input_data

    def finalization(self, input_data: Optional[Any]) -> Any:
        with self.db.get_session() as session:
            total_cases = count_records(session, CasosSchema)
            total_crimes = count_records(session, DelitosSchema)

        self.db.disconnect()

        self.logger.info(f"📤 [finalization] Load completed: {format(total_cases, ",")} cases, {total_crimes} crimes")
        return input_data
