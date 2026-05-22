import pandas as pd
from pathlib import Path
from typing import Any, Optional

from core.pipelines.participacion_ciudadana.constants import NULL_VALUES, YEAR_COLUMNS
from core.pipelines.stage import Stage
from core.utils.clean import list_values_to_null
from core.utils.logger import get_logger


class ParticipacionCiudadanaTransform(Stage):
    def __init__(self):
        super().__init__("participacion_ciudadana", "transform")
        self.logger = get_logger("participacion_ciudadana.transform")

    def source(self, input_data: Optional[Any] = None) -> pd.DataFrame:
        pkl_path = Path("data/extract/participacion_ciudadana/participacion.pkl")

        if pkl_path.exists():
            self.logger.info("[source] Loading extract pkl")
            return pd.read_pickle(pkl_path)

        return input_data

    def action(self, input_data: pd.DataFrame) -> pd.DataFrame:
        if input_data.empty:
            self.logger.warning("[action] Empty input, skipping")
            return pd.DataFrame(columns=["entidad_id", "municipio_id", "porc_participacion", "anio"])

        df = input_data.copy()

        for col in YEAR_COLUMNS:
            df[col] = df[col].astype(str).str.replace("%", "", regex=False)
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df = list_values_to_null(df, rm_list=NULL_VALUES)

        df = df.melt(
            id_vars=["entidad_id", "municipio_id"],
            value_vars=YEAR_COLUMNS,
            var_name="anio",
            value_name="porc_participacion",
        )

        df["anio"] = df["anio"].astype(int)
        df["entidad_id"] = pd.to_numeric(df["entidad_id"], errors="coerce").astype("Int64")
        df["municipio_id"] = pd.to_numeric(df["municipio_id"], errors="coerce").astype("Int64")

        df = df.dropna(subset=["porc_participacion"])

        self.logger.info(f"[action] Transformed: {len(df)} rows")
        return df

    def finalization(self, input_data: pd.DataFrame) -> pd.DataFrame:
        input_data.to_pickle(self.work_dir / "participacion.pkl")
        self.logger.info(f"[finalization] {len(input_data)} rows saved")
        return input_data
