import io
import pandas as pd
import requests
import urllib3
from typing import Any, Optional

from core.pipelines.agropecuario_siap.config import settings
from core.pipelines.agropecuario_siap.helpers import rename_header
from core.pipelines.stage import Stage
from core.utils.logger import get_logger

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class AgropecuarioExtract(Stage):
    def __init__(self, year: int):
        super().__init__(settings.PIPELINE_NAME, "extract")
        self.year = year
        self.logger = get_logger(f"{settings.PIPELINE_NAME}.extract")

    def source(self, input_data: Optional[Any] = None) -> pd.DataFrame:
        pkl_path = self.work_dir / f"extract_{self.year}.pkl"
        if pkl_path.exists():
            self.logger.info(f"[source] Cache found for {self.year}, loading pkl")
            return pd.read_pickle(pkl_path)

        url = settings.SIAP_URL.format(anio=self.year)
        self.logger.info(f"[source] Fetching {self.year}: {url}")
        response = requests.get(url, verify=False, timeout=60)
        response.raise_for_status()

        df = pd.read_csv(io.BytesIO(response.content), encoding="latin-1")

        if df.empty:
            self.logger.warning(f"[source] Empty response for {self.year}, skipping")
            return pd.DataFrame()

        self.logger.info(f"[source] {self.year}: {len(df)} rows fetched")
        return df

    def action(self, input_data: pd.DataFrame) -> pd.DataFrame:
        if input_data.empty:
            self.logger.info("[action] Empty input, skipping rename")
            return input_data

        rename = rename_header(self.year)
        if set(rename.values()).issubset(set(input_data.columns)):
            self.logger.info(f"[action] {self.year}: columns already renamed, skipping")
            return input_data

        df = input_data[list(rename.keys())].rename(columns=rename)
        self.logger.info(f"[action] {self.year}: {len(df)} rows renamed")
        return df

    def finalization(self, input_data: pd.DataFrame) -> pd.DataFrame:
        if input_data.empty:
            self.logger.info("[finalization] No data, skipping save")
            return input_data
        pkl_path = self.work_dir / f"extract_{self.year}.pkl"
        input_data.to_pickle(pkl_path)
        self.logger.info(f"[finalization] {self.year}: {len(input_data)} rows saved to {pkl_path}")
        return input_data
