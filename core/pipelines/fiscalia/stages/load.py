import numpy as np
from datetime import date
from typing import Any, Optional

from core.db import Database
from core.pipelines.stage import Stage
from core.utils import normalize_col, normalize_text, df_to_records, records_to_map
from core.utils.files import cleanup_pipeline_data
from core.utils.logger import get_logger
from core.utils.bulk_ops import (
    insert_records, upsert_records, count_records, get_mapping, get_cvegeo_mapping, sync_id_sequence,
)
from core.pipelines.fiscalia.schemas import (
    ZonasGeograficas as ZonasGeograficasSchema,
    EsViolencia as EsViolenciaSchema,
    Delitos as DelitosSchema,
    BienesAfectados as BienesAfectadosSchema,
    Colonias as ColoniasSchema,
    Calles as CallesSchema,
    Cruces as CrucesSchema,
    Casos as CasosSchema,
)
from core.pipelines.fiscalia.config import settings
from core.pipelines.fiscalia.mappings import (
    map_bienes_to_delitos,
    map_municipios_to_zonas_geo,
    Delitos,
    EsViolencia,
    ZonasGeograficas,
    BienesAfectados,
)
from core.pipelines.fiscalia.attributes.fiscalia import FiscaliaColumns


class FiscaliaLoad(Stage):
    def __init__(self, pipeline_name: str = 'fiscalia', mode: str = 'bootstrap'):
        super().__init__(pipeline_name, 'load')
        self.mode = mode
        self.logger = get_logger(f"{pipeline_name}.load")
        self.db = Database("fiscalia", settings.database_url)

    def _load_catalogs(self, session, input_data):
        bienes_records = BienesAfectados.to_records(FiscaliaColumns.BIEN_AFECTADO)
        bienes_delitos_map = map_bienes_to_delitos()
        delitos_records = [
            {**d, "bien_afectado_id": bienes_delitos_map.get(d[FiscaliaColumns.DELITO])}
            for d in Delitos.to_records(FiscaliaColumns.DELITO)
        ]
        violencia_records = EsViolencia.to_records(FiscaliaColumns.VIOLENCIA)
        zonas_geograficas_records = ZonasGeograficas.to_records(FiscaliaColumns.ZONA_GEOGRAFICA)

        insert_records(session, bienes_records, BienesAfectadosSchema, conflict_keys=["id"])
        insert_records(session, delitos_records, DelitosSchema, conflict_keys=["id"])
        insert_records(session, violencia_records, EsViolenciaSchema, conflict_keys=["id"])
        insert_records(session, zonas_geograficas_records, ZonasGeograficasSchema, conflict_keys=["id"])

        for model in [ColoniasSchema, CallesSchema, CrucesSchema]:
            sync_id_sequence(session, model)

        insert_records(session, input_data["colonias_records"], ColoniasSchema, conflict_keys=["colonia"])
        insert_records(session, input_data["calles_records"], CallesSchema, conflict_keys=["calle"])
        insert_records(session, input_data["cruces_records"], CrucesSchema, conflict_keys=["cruce"])

        return delitos_records, violencia_records

    def _map_foreign_keys(self, session, df, delitos_records, violencia_records):
        colonias_map = get_mapping(session, ColoniasSchema, 'colonia', 'id', is_normalize=True)
        calles_map = get_mapping(session, CallesSchema, 'calle', 'id', is_normalize=True)
        cruces_map = get_mapping(session, CrucesSchema, 'cruce', 'id', is_normalize=True)

        delitos_map = records_to_map(delitos_records, FiscaliaColumns.DELITO)
        violencia_map = records_to_map(violencia_records, FiscaliaColumns.VIOLENCIA)
        zonas_geo_map = map_municipios_to_zonas_geo(df)

        municipios_map = get_cvegeo_mapping(session, cve_ent=14, is_normalize=True)

        df["delitos_id"] = normalize_col(df, "delito").map(delitos_map)
        df["violencia_id"] = normalize_col(df, "violencia").map(violencia_map)
        df["zonas_geograficas_id"] = df["municipio"].map(zonas_geo_map)
        df["municipios_id"] = normalize_col(df, "municipio").map(municipios_map)
        df["colonias_id"] = normalize_col(df, "colonia").map(colonias_map)
        df["calles_id"] = normalize_col(df, "calle").map(calles_map)
        df["cruces_id"] = normalize_col(df, "cruce").map(cruces_map)
        df["fecha_actualizacion"] = date.today()

        return df.replace({np.nan: None})

    def _upsert_casos(self, session, df):
        casos_records = df_to_records(df, [
            "delitos_id", "violencia_id", "zonas_geograficas_id", "municipios_id",
            "colonias_id", "calles_id", "cruces_id",
            "hora", "longitud", "latitud",
            "fecha_denuncia", "fecha_actualizacion",
        ])
        records_before = count_records(session, CasosSchema)
        upsert_records(
            session, casos_records, CasosSchema,
            conflict_keys=["delitos_id", "fecha_denuncia", "hora", "longitud", "latitud"],
            update_keys=["violencia_id", "zonas_geograficas_id", "municipios_id",
                         "colonias_id", "calles_id", "cruces_id", "fecha_actualizacion"],
            chunk_size=50_000 if self.mode == "bootstrap" else 10_000
        )
        return records_before

    def source(self, input_data: Optional[Any]) -> Any:
        self.logger.info(f"[source] Records received: {list(input_data.keys())}")
        self.logger.info(f"[source] with {len(input_data['df'])} values")
        return input_data

    def action(self, input_data: Any) -> Any:
        self.logger.info("[action] Loading data into DB")
        df = input_data["df"]

        self.db.connect()

        with self.db.get_session() as session:
            try:
                delitos_records, violencia_records = self._load_catalogs(session, input_data)
                df = self._map_foreign_keys(session, df, delitos_records, violencia_records)
                records_before_upsert = self._upsert_casos(session, df)

                session.commit()
                self.logger.info("Data inserted successfully!")
            except Exception as e:
                session.rollback()
                self.logger.error(e)
                raise

        return {
            "data": input_data,
            "records_before_upsert": records_before_upsert
        }

    def finalization(self, input_data: Any) -> Any:
        with self.db.get_session() as session:
            total_cases = count_records(session, CasosSchema)
            total_cases_upsert = abs(input_data['records_before_upsert'] - total_cases)
        self.db.disconnect()

        cleanup_pipeline_data(self.pipeline_name)

        self.logger.info(f"[finalization]: {format(total_cases, ',')} cases in database")
        self.logger.info(f"[finalization]: {format(total_cases_upsert, ',')} cases upserted")
        return input_data["data"]
