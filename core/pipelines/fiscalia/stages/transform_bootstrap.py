
from core.pipelines.stage import Stage
from typing import Any, Optional, Dict, List
import numpy as np

from core.utils.logger import get_logger
from core.utils.logger import get_logger
from core.pipelines.fiscalia.helpers.normalize import list_values_to_null, titlecase_df, drop_duplicates_col, normalize_col
from core.pipelines.fiscalia.helpers.records import df_to_records_with_id, df_to_records, records_to_map
from core.pipelines.fiscalia.helpers.datetime import parse_hora, parse_fecha
from core.pipelines.fiscalia.attributes.fiscalia import FiscaliaColumns
from core.pipelines.fiscalia.mappings.schemas import (
    BienesAfectados,
    Delitos,
    EsViolencia,
    ZonasGeograficas
)
from core.pipelines.fiscalia.mappings.delitos import map_bienes_to_delitos

class FiscaliaTransformBootstrap(Stage):
    def __init__(self, pipeline_name: str = 'fiscalia', mode: str = 'bootstrap'):
        super().__init__(pipeline_name, 'transform')
        self.mode = mode
        self.logger = get_logger(f"{pipeline_name}.transform")

    def source(self, input_data: Optional[Any]) -> Any:
        self.logger.info(f"📥 [source] fiscalia={len(input_data['fiscalia'])} rows, localidades={len(input_data['localidades'])} rows")
        return input_data

    def _get_attributes_records(self, fiscalia_df, localidades_df) -> Dict:
        bienes_records = BienesAfectados.to_records(FiscaliaColumns.BIEN_AFECTADO)
        bienes_delitos_map = map_bienes_to_delitos()
        delitos_records = [
            {**d, "bien_afectado_id": bienes_delitos_map.get(d[FiscaliaColumns.DELITO])}
            for d in Delitos.to_records(FiscaliaColumns.DELITO)
        ]
        violencia_records = EsViolencia.to_records(FiscaliaColumns.VIOLENCIA)
        zonas_geograficas_records = ZonasGeograficas.to_records(FiscaliaColumns.ZONA_GEOGRAFICA)

        municipio_df = drop_duplicates_col(fiscalia_df, "municipio").dropna(subset=["municipio"])
        colonia_df = drop_duplicates_col(fiscalia_df, "colonia").dropna(subset=["colonia"]).sort_values(by=["colonia"])

        municipios_records = df_to_records_with_id(municipio_df, ["municipio"])
        colonias_records = df_to_records_with_id(colonia_df, ["colonia"])
        localidades_records = localidades_df.to_dict("records")

        return {
            "bienes_records": bienes_records,
            "delitos_records": delitos_records,
            "violencia_records": violencia_records,
            "zonas_geograficas_records": zonas_geograficas_records,
            "municipios_records": municipios_records,
            "colonias_records": colonias_records,
            "localidades_records": localidades_records,
        }

    def _get_casos_records(self, fiscalia_df, attributes: Dict) -> List[Dict]:
        delitos_map = records_to_map(attributes["delitos_records"], FiscaliaColumns.DELITO)
        violencia_map = records_to_map(attributes["violencia_records"], FiscaliaColumns.VIOLENCIA)
        zonas_map = records_to_map(attributes["zonas_geograficas_records"], FiscaliaColumns.ZONA_GEOGRAFICA)
        municipios_map = records_to_map(attributes["municipios_records"], "municipio")
        colonias_map = records_to_map(attributes["colonias_records"], "colonia")

        fiscalia_df["delitos_id"] = normalize_col(fiscalia_df, "delito").map(delitos_map)
        fiscalia_df["violencia_id"] = normalize_col(fiscalia_df, "violencia").map(violencia_map)
        fiscalia_df["zonas_geograficas_id"] = normalize_col(fiscalia_df, "zona_geografica").map(zonas_map)
        fiscalia_df["municipios_id"] = normalize_col(fiscalia_df, "municipio").map(municipios_map)
        fiscalia_df["colonias_id"] = normalize_col(fiscalia_df, "colonia").map(colonias_map)
        fiscalia_df["localidades_id"] = None  # CSV histórico no tiene localidades
        fiscalia_df["calles_id"] = None  # CSV histórico no tiene calles
        fiscalia_df["cruces_id"] = None  # CSV histórico no tiene cruces
        fiscalia_df = fiscalia_df.replace({np.nan: None})


        return df_to_records(fiscalia_df, [
            "delitos_id", "violencia_id", "zonas_geograficas_id", "municipios_id",
            "localidades_id", "colonias_id", "calles_id", "cruces_id",
            "fecha_denuncia", "hora"
        ])

    def action(self, input_data: Optional[Any]) -> Any:
        self.logger.info("⚙️ [action] Transformando datos")

        fiscalia_df = input_data["fiscalia"]
        localidades_df = input_data["localidades"]

        fiscalia_df = titlecase_df(fiscalia_df)
        fiscalia_df = list_values_to_null(fiscalia_df, rm_list=["Nan", "Desconocido", "N.D", "N.D.", "No Disponible", "N.A"])

        localidades_df = titlecase_df(localidades_df)
        localidades_df = list_values_to_null(localidades_df, rm_list=["Nan", "Desconocido", "N.D", "N.D.", "No Disponible", "N.A"])

        fiscalia_df["hora"] = parse_hora(fiscalia_df["hora"])
        fiscalia_df["fecha_denuncia"] = parse_fecha(fiscalia_df["fecha_denuncia"])

        attributes_records = self._get_attributes_records(fiscalia_df, localidades_df)
        casos_records = self._get_casos_records(fiscalia_df, attributes_records)

        return {
            **attributes_records,
            "casos_records": casos_records,
        }

    def finalization(self, input_data: Optional[Any]) -> Any:
        self.logger.info(f"📤 [finalization] Records generados: {list(input_data.keys())}")
        self.logger.info(f"📤 [finalization] Casos: {len(input_data['casos_records'])} records")
        return input_data
