import io
import pandas as pd
import requests
from typing import Any, Optional

from core.pipelines.stage import Stage
from core.pipelines.censo_poblacion.config import settings
from core.pipelines.censo_poblacion.constants import (
    RENAME_INEGI_2010_COL,
    RENAME_INEGI_2015_COL,
    RENAME_INEGI_2020_COL,
)
from core.utils.files import read_csv_from_zip_url
from core.utils.logger import get_logger

logger = get_logger("censo_poblacion.extract")


class CensoPoblacionExtract(Stage):
    def __init__(self):
        super().__init__("censo_poblacion", "extract")

    def _fetch_2010(self) -> pd.DataFrame:
        logger.info("Fetching 2010 census data")
        df = read_csv_from_zip_url(
            settings.CENSO_URL_2010,
            "iter_14_cpv2010/conjunto_de_datos/iter_14_cpv2010.csv",
            low_memory=False,
        )
        df = df[list(RENAME_INEGI_2010_COL.keys())].rename(columns=RENAME_INEGI_2010_COL).copy()
        logger.info(f"2010: {len(df)} rows fetched")
        return df

    def _fetch_2015(self) -> pd.DataFrame:
        logger.info("Fetching 2015 intercensal data")
        response = requests.get(settings.CENSO_URL_2015)
        response.raise_for_status()
        df = pd.read_excel(io.BytesIO(response.content), engine="xlrd", sheet_name=3, header=6)
        df = df[df["Estimador"] == "Valor"]
        df = df[list(RENAME_INEGI_2015_COL.keys())].rename(columns=RENAME_INEGI_2015_COL).copy()
        logger.info(f"2015: {len(df)} rows fetched")
        return df

    def _fetch_2020(self) -> pd.DataFrame:
        logger.info("Fetching 2020 census data")
        df = read_csv_from_zip_url(
            settings.CENSO_URL_2020,
            "ITER_14CSV20.csv",
            encoding="utf-8-sig",
            low_memory=False,
        )
        df = df[list(RENAME_INEGI_2020_COL.keys())].rename(columns=RENAME_INEGI_2020_COL).copy()
        logger.info(f"2020: {len(df)} rows fetched")
        return df

    def source(self, input_data: Optional[Any] = None) -> dict[str, pd.DataFrame]:
        pkl_2010 = self.work_dir / "df_2010.pkl"
        pkl_2015 = self.work_dir / "df_2015.pkl"
        pkl_2020 = self.work_dir / "df_2020.pkl"

        if pkl_2010.exists() and pkl_2015.exists() and pkl_2020.exists():
            logger.info("Loading extract data from cached pkl files")
            return {
                "df_2010": pd.read_pickle(pkl_2010),
                "df_2015": pd.read_pickle(pkl_2015),
                "df_2020": pd.read_pickle(pkl_2020),
            }

        return {
            "df_2010": self._fetch_2010(),
            "df_2015": self._fetch_2015(),
            "df_2020": self._fetch_2020(),
        }

    def action(self, input_data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        return input_data

    def finalization(self, input_data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        for key, df in input_data.items():
            pkl_path = self.work_dir / f"{key}.pkl"
            df.to_pickle(pkl_path)
            logger.info(f"Saved {key}: {len(df)} rows to {pkl_path}")
        return input_data
