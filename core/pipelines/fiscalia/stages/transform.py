from typing import Any, Optional

from core.pipelines.stage import Stage
from core.utils.logger import get_logger
from core.utils import list_values_to_null, titlecase_df, drop_duplicates_col, df_to_records
from core.utils.parse_datetime import parse_hour, parse_date
from core.pipelines.fiscalia.constants import NULL_VALUES


class FiscaliaTransform(Stage):
    def __init__(self, pipeline_name: str = 'fiscalia', mode: str = 'bootstrap'):
        super().__init__(pipeline_name, 'transform')
        self.mode = mode
        self.logger = get_logger(f"{pipeline_name}.transform")

    def source(self, input_data: Optional[Any]) -> Any:
        self.logger.info(f"[source] fiscalia={len(input_data)} rows")
        return input_data

    def action(self, input_data: Optional[Any]) -> Any:
        self.logger.info("[action] Transforming data")
        df = input_data

        df = titlecase_df(df)
        df = list_values_to_null(df, rm_list=NULL_VALUES)
        df = df.drop(columns=["_is_update"])

        df["hora"] = parse_hour(df["hora"])
        df["fecha_denuncia"] = parse_date(df["fecha_denuncia"])

        natural_key = ["delito", "fecha_denuncia", "longitud", "latitud"]
        before_dedup = len(df)
        df = df.drop_duplicates(subset=natural_key, keep="last")
        dupes = before_dedup - len(df)
        if dupes:
            self.logger.info(f"[action] Dropped {dupes} duplicate rows on {natural_key}")

        colonias_df = drop_duplicates_col(df, "colonia").dropna(subset=["colonia"])
        calles_df = drop_duplicates_col(df, "calle").dropna(subset=["calle"])
        cruces_df = drop_duplicates_col(df, "cruce").dropna(subset=["cruce"])

        return {
            "df": df,
            "colonias_records": df_to_records(colonias_df, ["colonia"]),
            "calles_records": df_to_records(calles_df, ["calle"]),
            "cruces_records": df_to_records(cruces_df, ["cruce"]),
        }

    def finalization(self, input_data: Any) -> Any:
        self.logger.info(f"[finalization] DataFrame transformed: {len(input_data['df'])} rows")
        return input_data
