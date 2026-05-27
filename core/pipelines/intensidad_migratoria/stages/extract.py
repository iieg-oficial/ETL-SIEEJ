import io
from typing import Any, Optional

import pandas as pd
import requests

from core.pipelines.intensidad_migratoria.config import settings
from core.pipelines.intensidad_migratoria.constants import (
    RENAME_IIM_ESTATAL_2020,
    RENAME_IIM_MUNICIPAL_2010,
    RENAME_IIM_MUNICIPAL_2020,
)
from core.pipelines.stage import Stage
from core.utils.logger import get_logger

logger = get_logger("intensidad_migratoria.extract")


class IntensidadMigratoriaExtract(Stage):
    def __init__(self):
        super().__init__("intensidad_migratoria", "extract")

    def _fetch_municipal_2010(self) -> pd.DataFrame:
        logger.info("Fetching IIM municipal 2010")
        response = requests.get(settings.IIM_URL_MUNICIPAL_2010)
        response.raise_for_status()
        df = pd.read_csv(io.BytesIO(response.content))
        df = df[list(RENAME_IIM_MUNICIPAL_2010.keys())].rename(columns=RENAME_IIM_MUNICIPAL_2010).copy()
        logger.info(f"Municipal 2010: {len(df)} rows fetched")
        return df

    def _fetch_municipal_2020(self) -> pd.DataFrame:
        logger.info("Fetching IIM municipal 2020")
        response = requests.get(settings.IIM_URL_MUNICIPAL_2020)
        response.raise_for_status()
        df = pd.read_csv(io.BytesIO(response.content))
        df = df[list(RENAME_IIM_MUNICIPAL_2020.keys())].rename(columns=RENAME_IIM_MUNICIPAL_2020).copy()
        logger.info(f"Municipal 2020: {len(df)} rows fetched")
        return df

    def _fetch_estatal_2020(self) -> pd.DataFrame:
        logger.info("Fetching IIM estatal 2020")
        response = requests.get(settings.IIM_URL_ESTATAL_2020)
        response.raise_for_status()
        df = pd.read_csv(io.BytesIO(response.content))
        df = df[list(RENAME_IIM_ESTATAL_2020.keys())].rename(columns=RENAME_IIM_ESTATAL_2020).copy()
        logger.info(f"Estatal 2020: {len(df)} rows fetched")
        return df

    def source(self, input_data: Optional[Any] = None) -> dict[str, pd.DataFrame]:
        pkl_municipal_2010 = self.work_dir / "df_municipal_2010.pkl"
        pkl_municipal_2020 = self.work_dir / "df_municipal_2020.pkl"
        pkl_estatal_2020 = self.work_dir / "df_estatal_2020.pkl"

        if pkl_municipal_2010.exists() and pkl_municipal_2020.exists() and pkl_estatal_2020.exists():
            logger.info("Loading extract data from cached pkl files")
            return {
                "df_municipal_2010": pd.read_pickle(pkl_municipal_2010),
                "df_municipal_2020": pd.read_pickle(pkl_municipal_2020),
                "df_estatal_2020": pd.read_pickle(pkl_estatal_2020),
            }

        return {
            "df_municipal_2010": self._fetch_municipal_2010(),
            "df_municipal_2020": self._fetch_municipal_2020(),
            "df_estatal_2020": self._fetch_estatal_2020(),
        }

    def action(self, input_data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        return input_data

    def finalization(self, input_data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        for key, df in input_data.items():
            pkl_path = self.work_dir / f"{key}.pkl"
            df.to_pickle(pkl_path)
            logger.info(f"Saved {key}: {len(df)} rows to {pkl_path}")
        return input_data
