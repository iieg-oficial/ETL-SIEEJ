
import numpy as np
from datetime import date
from typing import Any, Optional

from core.db import Database
from core.pipelines.stage import Stage
from sqlalchemy import text
from core.utils import normalize_col, normalize_text, df_to_records, records_to_map
from core.utils.logger import get_logger
from core.utils.bulk_ops import (insert_records, bulk_insert, count_records, get_mapping, sync_id_sequence)
from core.pipelines.fiscalia.schemas import (Casos, Calles, Cruces, Colonias)
from core.pipelines.fiscalia.config import settings
from core.pipelines.fiscalia.mappings import (map_bienes_to_delitos, map_municipios_to_zonas_geo,  Delitos, EsViolencia)
from core.pipelines.fiscalia.attributes.fiscalia import FiscaliaColumns


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
        self.logger.info("⚙️ [action] Loading update data")
        df = input_data["df"]

        self.db.connect()

        with self.db.get_session() as session:
            try:
                for model in [Calles, Cruces, Colonias]:
                    sync_id_sequence(session, model)

                insert_records(session, input_data["calles_records"], Calles, conflict_keys=["calle"])
                insert_records(session, input_data["cruces_records"], Cruces, conflict_keys=["cruce"])
                insert_records(session, input_data["colonias_records"], Colonias, conflict_keys=["colonia"])

                calles_map = get_mapping(session, Calles, 'calle', 'id', is_normalize=True)
                cruces_map = get_mapping(session, Cruces, 'cruce', 'id', is_normalize=True)
                colonias_map = get_mapping(session, Colonias, 'colonia', 'id', is_normalize=True)
                municipios_rows = session.execute(text("SELECT nomgeo, id FROM cvegeo_municipalities")).all()
                municipios_map = {normalize_text(row[0]): row[1] for row in municipios_rows}

                bienes_delitos_map = map_bienes_to_delitos()
                delitos_map = records_to_map(
                    [{**d, "bien_afectado_id": bienes_delitos_map.get(d[FiscaliaColumns.DELITO])}
                     for d in Delitos.to_records(FiscaliaColumns.DELITO)],
                    FiscaliaColumns.DELITO
                )
                violencia_map = records_to_map(
                    EsViolencia.to_records(FiscaliaColumns.VIOLENCIA),
                    FiscaliaColumns.VIOLENCIA
                )
                zonas_geo_map = map_municipios_to_zonas_geo(df)

                df["delitos_id"] = normalize_col(df, "delito").map(delitos_map)
                df["violencia_id"] = normalize_col(df, "violencia").map(violencia_map)
                df["zonas_geograficas_id"] = df["municipio"].map(zonas_geo_map)
                df["municipios_id"] = normalize_col(df, "municipio").map(municipios_map)
                df["calles_id"] = normalize_col(df, "calle").map(calles_map)
                df["cruces_id"] = normalize_col(df, "cruce").map(cruces_map)
                df["colonias_id"] = normalize_col(df, "colonia").map(colonias_map)
                df["fecha_actualizacion"] = date.today()

                df = df.replace({np.nan: None})

                casos_records = df_to_records(df, [
                    "delitos_id", "violencia_id", "zonas_geograficas_id", "municipios_id",
                    "colonias_id", "calles_id", "cruces_id",
                    "hora", "longitud", "latitud",
                    "fecha_denuncia", "fecha_actualizacion"
                ])

                bulk_insert(session, casos_records, Casos, chunk_size=50_000)

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
