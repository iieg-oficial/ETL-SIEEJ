
import numpy as np
from datetime import date
from typing import Any, Optional, Dict, List, Tuple

from core.pipelines.stage import Stage
from core.db import Database
from core.utils.logger import get_logger
from core.pipelines.fiscalia.config import settings
from core.pipelines.fiscalia.mappings.delitos import map_bienes_to_delitos
from core.pipelines.fiscalia.helpers.records import df_to_records, records_to_map
from core.pipelines.fiscalia.helpers.normalize import (
    list_values_to_null, titlecase_df, normalize_col
)
from core.pipelines.fiscalia.helpers.catalog import get_catalog_mapping, get_new_catalog_records
from core.pipelines.fiscalia.helpers.format_datetime import parse_hour, parse_date
from core.pipelines.fiscalia.helpers.geo import utm13n_to_latlon
from core.pipelines.fiscalia.attributes.fiscalia import FiscaliaColumns
from core.pipelines.fiscalia.schemas import (Cruces, Colonias, Calles, Municipios)
from core.pipelines.fiscalia.mappings.schemas import (
    BienesAfectados,
    Delitos,
    EsViolencia,
)
from core.pipelines.fiscalia.mappings.zonas_geograficas import map_municipios_to_zonas_geo

NULL_VALUES = ["Nan", "Desconocido", "N.D", "N.D.", "No Disponible", "N.A"]


class FiscaliaTransformUpdate(Stage):
    def __init__(self, pipeline_name: str = 'fiscalia', mode: str = 'update'):
        super().__init__(pipeline_name, 'transform')
        self.mode = mode
        self.logger = get_logger(f"{pipeline_name}.transform")
        self.bienes_delitos_map = map_bienes_to_delitos()
        self.db = Database("fiscalia", settings.database_url)

    def source(self, input_data: Optional[Any]) -> Any:
        self.logger.info(f"📥 [source] fiscalia={len(input_data)} rows")
        return input_data

    def _get_attributes_records(self, df, session) -> Tuple[Dict, Dict]:
        calles_map, max_calle_id = get_catalog_mapping(session, Calles, 'calle')
        cruces_map, max_cruce_id = get_catalog_mapping(session, Cruces, 'cruce')
        colonias_map, max_colonia_id = get_catalog_mapping(session, Colonias, 'colonia')

        new_calles, calles_map = get_new_catalog_records(df, 'calle', calles_map, max_calle_id)
        new_cruces, cruces_map = get_new_catalog_records(df, 'cruce', cruces_map, max_cruce_id)
        new_colonias, colonias_map = get_new_catalog_records(df, 'colonia', colonias_map, max_colonia_id)

        municipios_map, _ = get_catalog_mapping(session, Municipios, 'municipio')

        delitos_map = records_to_map(
            [{**d, "bien_afectado_id": self.bienes_delitos_map.get(d[FiscaliaColumns.DELITO])}
             for d in Delitos.to_records(FiscaliaColumns.DELITO)],
            FiscaliaColumns.DELITO
        )
        violencia_map = records_to_map(
            EsViolencia.to_records(FiscaliaColumns.VIOLENCIA),
            FiscaliaColumns.VIOLENCIA
        )
        zonas_geo_map = map_municipios_to_zonas_geo(df)

        new_records = {
            "calles_records": new_calles,
            "cruces_records": new_cruces,
            "colonias_records": new_colonias,
        }
        mappings = {
            "calles": calles_map,
            "cruces": cruces_map,
            "colonias": colonias_map,
            "municipios": municipios_map,
            "delitos": delitos_map,
            "violencia": violencia_map,
            "zonas_geo": zonas_geo_map,
        }
        return new_records, mappings

    def _get_casos_records(self, df, mappings: Dict) -> List[Dict]:
        df["delitos_id"] = normalize_col(df, "delito").map(mappings["delitos"])
        df["violencia_id"] = normalize_col(df, "violencia").map(mappings["violencia"])
        df["zonas_geograficas_id"] = df["municipio"].map(mappings["zonas_geo"])
        df["municipios_id"] = normalize_col(df, "municipio").map(mappings["municipios"])
        df["calles_id"] = normalize_col(df, "calle").map(mappings["calles"])
        df["cruces_id"] = normalize_col(df, "cruce").map(mappings["cruces"])
        df["colonias_id"] = normalize_col(df, "colonia").map(mappings["colonias"])
        df["fecha_actualizacion"] = date.today()

        df = df.replace({np.nan: None})

        return df_to_records(df, [
            "delitos_id", "violencia_id", "zonas_geograficas_id", "municipios_id",
            "colonias_id", "calles_id", "cruces_id",
            "hora", "longitud", "latitud",
            "fecha_denuncia", "fecha_actualizacion"
        ])

    def action(self, input_data: Optional[Any]) -> Any:
        self.logger.info("⚙️ [action] Transforming update data")
        df = input_data

        df = titlecase_df(df)
        df = list_values_to_null(df, rm_list=NULL_VALUES)

        self.logger.info("🌐 Converting UTM coordinates to WGS84")
        df = utm13n_to_latlon(df, x_col='longitud', y_col='latitud')

        df["hora"] = parse_hour(df["hora"])
        df["fecha_denuncia"] = parse_date(df["fecha_denuncia"])

        self.db.connect()
        with self.db.get_session() as session:
            new_records, mappings = self._get_attributes_records(df, session)
        casos_records = self._get_casos_records(df, mappings)
        self.db.disconnect()

        return {
            **new_records,
            "casos_records": casos_records,
        }

    def finalization(self, input_data: Any) -> Any:
        self.logger.info(f"📤 [finalization] Records transformed: {list(input_data.keys())}")
        self.logger.info(f"📤 [finalization] Casos: {len(input_data['casos_records'])} records")
        return input_data
