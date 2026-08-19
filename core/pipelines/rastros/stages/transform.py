from pathlib import Path
from typing import Any, Optional

import pandas as pd

from core.pipelines.rastros.attributes import RastrosTables as T
from core.pipelines.rastros.config import PIPELINE_NAME, settings
from core.pipelines.rastros.constants import ESTATUS_COLS, INT_COLS, NULL_VALUES
from core.pipelines.rastros.helpers import build_fecha
from core.pipelines.stage import Stage
from core.utils import df_to_records
from core.utils.clean import drop_duplicates_col, list_values_to_null


class RastrosTransform(Stage):
    """Normalize types, build the period date and derive the catalogs."""

    def __init__(self):
        super().__init__(PIPELINE_NAME, "transform")

    def source(self, input_data: Optional[Any] = None) -> pd.DataFrame:
        pkl_path = Path(f"data/extract/{settings.PIPELINE_NAME}/extract.pkl")
        if pkl_path.exists():
            self.logger.info(f"Loading {pkl_path}")
            return pd.read_pickle(pkl_path)
        return input_data

    def action(self, input_data: pd.DataFrame) -> dict[str, Any]:
        if input_data is None or input_data.empty:
            self.logger.warning("Empty input, nothing to transform")
            return {"df": pd.DataFrame(), "catalogs": {}}

        df = input_data.copy()
        self.logger.info(f"Processing {len(df):,} rows")

        for col in INT_COLS:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        fecha = build_fecha(df["anio"], df["mes"])

        df = list_values_to_null(df, rm_list=NULL_VALUES)

        df["fecha"] = fecha.dt.date
        df["entidad_id"] = pd.to_numeric(df["entidad_id"], errors="coerce").astype("Int64")
        for col in INT_COLS:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

        df = df.dropna(subset=["fecha", "entidad_id", "especie_ganadera"])
        self.logger.info(f"{len(df):,} rows with a valid period, entity and species")

        catalogs = self._build_catalogs(df)
        return {"df": df, "catalogs": catalogs}

    def _build_catalogs(self, df: pd.DataFrame) -> dict[str, list[dict]]:
        estatus = pd.DataFrame({"estatus": pd.concat([df[col] for col in ESTATUS_COLS], ignore_index=True)})

        catalogs = {
            T.CAT_ESTATUS: self._unique_records(estatus, "estatus"),
            T.CAT_ESPECIES_GANADERAS: self._unique_records(df, "especie_ganadera"),
            T.CAT_TIPO_CIFRA: self._unique_records(df, "tipo_cifra"),
        }

        for table, records in catalogs.items():
            self.logger.info(f"{table}: {len(records)} entries")
        return catalogs

    @staticmethod
    def _unique_records(df: pd.DataFrame, col: str) -> list[dict]:
        values = df[[col]].dropna(subset=[col])
        return df_to_records(drop_duplicates_col(values, col), [col])

    def finalization(self, input_data: dict[str, Any]) -> dict[str, Any]:
        if input_data["df"].empty:
            self.logger.warning("No transformed data, skipping pkl save")
            return input_data

        input_data["df"].to_pickle(self.work_dir / "transform.pkl")
        pd.to_pickle(input_data["catalogs"], self.work_dir / "catalogs.pkl")
        self.logger.info(f"{len(input_data['df']):,} rows and {len(input_data['catalogs'])} catalogs saved")
        return input_data
