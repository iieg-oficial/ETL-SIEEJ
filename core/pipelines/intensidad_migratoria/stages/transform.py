import pandas as pd
from pathlib import Path
from typing import Any, Optional

from core.pipelines.stage import Stage
from core.utils.logger import get_logger
from core.pipelines.intensidad_migratoria.constants import (
    RENAME_IIM_ESTATAL_2020,
    RENAME_IIM_MUNICIPAL_2020,
)

logger = get_logger("intensidad_migratoria.transform")


class IntensidadMigratoriaTransform(Stage):
    def __init__(self):
        super().__init__("intensidad_migratoria", "transform")

    def source(self, input_data: Optional[Any] = None) -> dict[str, pd.DataFrame]:
        pkl_municipal_2010 = Path("data/extract/intensidad_migratoria/df_municipal_2010.pkl")
        pkl_municipal_2020 = Path("data/extract/intensidad_migratoria/df_municipal_2020.pkl")
        pkl_estatal_2020 = Path("data/extract/intensidad_migratoria/df_estatal_2020.pkl")

        if pkl_municipal_2010.exists() and pkl_municipal_2020.exists() and pkl_estatal_2020.exists():
            logger.info("Loading transform input from extract pkl files")
            return {
                "df_municipal_2010": pd.read_pickle(pkl_municipal_2010),
                "df_municipal_2020": pd.read_pickle(pkl_municipal_2020),
                "df_estatal_2020": pd.read_pickle(pkl_estatal_2020),
            }

        return input_data

    def _process_municipal_2010(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["municipio_id"] = df.apply(
            lambda row: int(f"{int(row['entidad_id']):02}{int(row['municipio_id']):03}"), axis=1
        )
        df["grado_iim"] = df["grado_iim"].astype(str).str.replace(r"^\d+\s*", "", regex=True).str.strip()
        df["lugar_contexto_nacional"] = pd.to_numeric(df["lugar_contexto_nacional"], errors="coerce").astype("Int64")
        df["fecha"] = 2010
        return df[list(RENAME_IIM_MUNICIPAL_2020.values()) + ["fecha"]]

    def _process_municipal_2020(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["municipio_id"] = pd.to_numeric(df["municipio_id"], errors="coerce").astype("Int64")
        df["lugar_contexto_nacional"] = pd.to_numeric(df["lugar_contexto_nacional"], errors="coerce").astype("Int64")
        df["fecha"] = 2020
        return df[list(RENAME_IIM_MUNICIPAL_2020.values()) + ["fecha"]]

    def _process_estatal_2020(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["entidad_id"] = pd.to_numeric(df["entidad_id"], errors="coerce")
        df = df[df["entidad_id"] != 0].copy()
        df["lugar_contexto_nacional"] = pd.to_numeric(df["lugar_contexto_nacional"], errors="coerce").astype("Int64")
        df["fecha"] = 2020
        return df[list(RENAME_IIM_ESTATAL_2020.values()) + ["fecha"]]

    def action(self, input_data: dict[str, pd.DataFrame]) -> dict[str, Any]:
        logger.info("Processing municipal 2010")
        df_municipal_2010 = self._process_municipal_2010(input_data["df_municipal_2010"])
        logger.info(f"Municipal 2010: {len(df_municipal_2010)} rows")

        logger.info("Processing municipal 2020")
        df_municipal_2020 = self._process_municipal_2020(input_data["df_municipal_2020"])
        logger.info(f"Municipal 2020: {len(df_municipal_2020)} rows")

        logger.info("Processing estatal 2020")
        df_estatal_2020 = self._process_estatal_2020(input_data["df_estatal_2020"])
        logger.info(f"Estatal 2020: {len(df_estatal_2020)} rows")

        df_municipal = pd.concat([df_municipal_2010, df_municipal_2020], ignore_index=True)
        logger.info(f"Total municipal rows: {len(df_municipal)}")

        return {"df_municipal": df_municipal, "df_estatal": df_estatal_2020}

    def finalization(self, input_data: dict[str, Any]) -> dict[str, Any]:
        for key, df in input_data.items():
            pkl_path = self.work_dir / f"{key}.pkl"
            df.to_pickle(pkl_path)
            logger.info(f"Saved {key}: {len(df)} rows to {pkl_path}")
        return input_data
