
from core.pipelines.stage import Stage
from typing import Any, Optional

from core.utils.logger import get_logger
from core.pipelines.fiscalia.helpers.normalize import list_values_to_null, titlecase_df, drop_duplicates_col
from core.pipelines.fiscalia.helpers.records import df_to_records_with_id, df_to_records
from core.pipelines.fiscalia.attributes.fiscalia import FiscaliaColumns
from core.pipelines.fiscalia.mappings.schemas import (
    BienesAfectados,
    Delitos,
    EsViolencia,
    ZonasGeograficas
)


class FiscaliaTransformBootstrap(Stage):
    def __init__(self, pipeline_name: str = 'fiscalia', mode: str = 'bootstrap'):
        super().__init__(pipeline_name, 'transform')
        self.mode = mode
        self.logger = get_logger(f"{pipeline_name}.transform")

    def source(self, input_data: Optional[Any]) -> Any:
        self.logger.info(f"📥 [source] fiscalia={len(input_data['fiscalia'])} rows, localidades={len(input_data['localidades'])} rows")
        return input_data

    def action(self, input_data: Optional[Any]) -> Any:
        self.logger.info("⚙️ [action] Transformando datos")

        fiscalia_df = input_data["fiscalia"]
        localidades_df = input_data["localidades"]

        fiscalia_df = titlecase_df(fiscalia_df)
        fiscalia_df = list_values_to_null(fiscalia_df, rm_list=["Nan", "Desconocido", "N.D", "N.D.", "No Disponible", "N.A"])

        localidades_df = titlecase_df(localidades_df)
        localidades_df = list_values_to_null(localidades_df, rm_list=["Nan", "Desconocido", "N.D", "N.D.", "No Disponible", "N.A"])

        bienes_records = BienesAfectados.to_records(FiscaliaColumns.BIEN_AFECTADO)
        delitos_records = Delitos.to_records(FiscaliaColumns.DELITO)
        violencia_records = EsViolencia.to_records(FiscaliaColumns.VIOLENCIA)
        zonas_geograficas_records = ZonasGeograficas.to_records(FiscaliaColumns.ZONA_GEOGRAFICA)

        municipio_df = drop_duplicates_col(fiscalia_df, "municipio").dropna(subset=["municipio"])
        colonia_df = drop_duplicates_col(fiscalia_df, "colonia").dropna(subset=["colonia"]).sort_values(by=["colonia"])

        municipios_records = df_to_records_with_id(municipio_df, ["municipio"])
        colonias_records = df_to_records(colonia_df, ["colonia"])
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

    def finalization(self, input_data: Optional[Any]) -> Any:
        self.logger.info(f"📤 [finalization] Records generados: {list(input_data.keys())}")
        return input_data
