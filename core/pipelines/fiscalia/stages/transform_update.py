
from typing import Any, Optional

from core.pipelines.stage import Stage
from core.utils.logger import get_logger
from core.utils import list_values_to_null, titlecase_df, drop_duplicates_col, df_to_records
from core.pipelines.fiscalia.helpers import parse_hour, parse_date, utm13n_to_latlon
from core.pipelines.fiscalia.constants import NULL_VALUES


class FiscaliaTransformUpdate(Stage):
    def __init__(self, pipeline_name: str = 'fiscalia', mode: str = 'update'):
        super().__init__(pipeline_name, 'transform')
        self.mode = mode
        self.logger = get_logger(f"{pipeline_name}.transform")

    def source(self, input_data: Optional[Any]) -> Any:
        self.logger.info(f"📥 [source] fiscalia={len(input_data)} rows")
        return input_data

    def action(self, input_data: Optional[Any]) -> Any:
        self.logger.info("⚙️ [action] Transforming update data")
        df = input_data

        df = titlecase_df(df)
        df = list_values_to_null(df, rm_list=NULL_VALUES)

        self.logger.info("🌐 Converting UTM coordinates to WGS84")
        df = utm13n_to_latlon(df, x_col='longitud', y_col='latitud')

        df["hora"] = parse_hour(df["hora"])
        df["fecha_denuncia"] = parse_date(df["fecha_denuncia"])

        calles_df = drop_duplicates_col(df, "calle").dropna(subset=["calle"])
        cruces_df = drop_duplicates_col(df, "cruce").dropna(subset=["cruce"])
        colonias_df = drop_duplicates_col(df, "colonia").dropna(subset=["colonia"])

        return {
            "df": df,
            "calles_records": df_to_records(calles_df, ["calle"]),
            "cruces_records": df_to_records(cruces_df, ["cruce"]),
            "colonias_records": df_to_records(colonias_df, ["colonia"]),
        }

    def finalization(self, input_data: Any) -> Any:
        self.logger.info(f"📤 [finalization] DataFrame transformed: {len(input_data['df'])} rows")
        return input_data
