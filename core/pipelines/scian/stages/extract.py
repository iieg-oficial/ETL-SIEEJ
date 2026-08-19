import io
from typing import Any, Optional

import pandas as pd
import requests

from core.pipelines.scian.config import settings
from core.pipelines.scian.constants import HEADER_ROWS, REQUEST_TIMEOUT, SHEET_COLUMNS, SHEET_NAME
from core.pipelines.stage import Stage
from core.utils.logger import get_logger

logger = get_logger("scian.extract")


class ScianExtract(Stage):
    def __init__(self):
        super().__init__("scian", "extract")

    def _fetch_estructura(self) -> pd.DataFrame:
        logger.info("Fetching SCIAN structure")
        response = requests.get(settings.SCIAN_ESTRUCTURA_URL, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        df = pd.read_excel(
            io.BytesIO(response.content),
            sheet_name=SHEET_NAME,
            header=None,
            names=SHEET_COLUMNS,
            dtype=str,
        )
        df = df.iloc[HEADER_ROWS:].dropna(how="all")
        logger.info(f"Structure: {len(df)} rows fetched")
        return df

    def source(self, input_data: Optional[Any] = None) -> pd.DataFrame:
        pkl_estructura = self.work_dir / "df_estructura.pkl"

        if pkl_estructura.exists():
            logger.info("Loading extract data from cached pkl file")
            return pd.read_pickle(pkl_estructura)

        return self._fetch_estructura()

    def action(self, input_data: pd.DataFrame) -> pd.DataFrame:
        return input_data

    def finalization(self, input_data: pd.DataFrame) -> pd.DataFrame:
        pkl_path = self.work_dir / "df_estructura.pkl"
        input_data.to_pickle(pkl_path)
        logger.info(f"Saved df_estructura: {len(input_data)} rows to {pkl_path}")
        return input_data
