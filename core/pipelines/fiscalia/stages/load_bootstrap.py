
from core.pipelines.stage import Stage
from typing import Any, Optional

from core.utils.logger import get_logger
from core.utils.bulk_ops import insert_records
from core.db import Database
from core.pipelines.fiscalia.schemas import (
    ZonasGeograficas as ZonasGeograficasSchema,
    Municipios,
    Localidades,
    EsViolencia as EsViolenciaSchema,
    Delitos as DelitosSchema,
    BienesAfectados as BienesAfectadosSchema,
    Colonias
)
from core.pipelines.fiscalia.config import settings


class FiscaliaLoadBootstrap(Stage):
    def __init__(self, pipeline_name: str = 'fiscalia', mode: str = 'bootstrap'):
        super().__init__(pipeline_name, 'load')
        self.mode = mode
        self.logger = get_logger(f"{pipeline_name}.load")

    def source(self, input_data: Optional[Any]) -> Any:
        self.logger.info(f"📥 [source] records recibidos: {list(input_data.keys())}")
        return input_data

    def action(self, input_data: Optional[Any]) -> Any:
        self.logger.info("⚙️ [action] Insertando datos en DB")

        db = Database("fiscalia", settings.database_url)
        db.connect()

        with db.get_session() as session:
            try:
                insert_records(session, input_data["bienes_records"], BienesAfectadosSchema, conflict_keys=["id"])
                insert_records(session, input_data["delitos_records"], DelitosSchema, conflict_keys=["id"])
                insert_records(session, input_data["violencia_records"], EsViolenciaSchema, conflict_keys=["id"])
                insert_records(session, input_data["zonas_geograficas_records"], ZonasGeograficasSchema, conflict_keys=["id"])
                insert_records(session, input_data["municipios_records"], Municipios, conflict_keys=["id"])
                insert_records(session, input_data["colonias_records"], Colonias, conflict_keys=["id"])
                insert_records(session, input_data["localidades_records"], Localidades, conflict_keys=["id"])
                session.commit()
                self.logger.info("Datos insertados correctamente")
            except Exception as e:
                session.rollback()
                self.logger.error(e)
                raise

        db.disconnect()
        return input_data

    def finalization(self, input_data: Optional[Any]) -> Any:
        self.logger.info("📤 [finalization] Carga completada")
        return input_data
