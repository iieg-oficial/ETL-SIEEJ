import io
import pandas as pd
import requests
import urllib3
from typing import Any, Optional

from core.pipelines.produccion_ganadera.config import settings
from core.pipelines.produccion_ganadera.constants import RENAME_HEADER_BASE, RENAME_HEADER_NO_GEO
from core.pipelines.stage import Stage
from core.utils.logger import get_logger

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class GanaderaExtract(Stage):
    def __init__(self, year: int):
        super().__init__(settings.PIPELINE_NAME, "extract")
        self.year = year
        self.logger = get_logger(f"{settings.PIPELINE_NAME}.extract")

    def source(self, input_data: Optional[Any] = None) -> pd.DataFrame:
        pkl_path = self.work_dir / f"extract_{self.year}.pkl"
        if pkl_path.exists():
            self.logger.info(f"Cache found for {self.year}, loading pkl")
            return pd.read_pickle(pkl_path)

        url = settings.SIAP_URL.format(anio=self.year)
        self.logger.info(f"Fetching {self.year}: {url}")
        response = requests.get(url, verify=False, timeout=60)
        response.raise_for_status()

        df = pd.read_csv(io.BytesIO(response.content), encoding="latin-1")

        if df.empty:
            self.logger.warning(f"Empty response for {self.year}, skipping")
            return pd.DataFrame()

        self.logger.info(f"{self.year}: {len(df)} rows fetched")
        return df

    def action(self, input_data: pd.DataFrame) -> pd.DataFrame:
        if input_data.empty:
            self.logger.info("Empty input, skipping rename")
            return input_data

        has_geo = "Cveddr" in input_data.columns
        rename = RENAME_HEADER_BASE if has_geo else RENAME_HEADER_NO_GEO

        if set(rename.values()).issubset(set(input_data.columns)):
            self.logger.info(f"{self.year}: columns already renamed, skipping")
            return input_data

        df = input_data[list(rename.keys())].rename(columns=rename)

        if not has_geo:
            df["distrito_des_rural_id"] = None
            df["dis_des_rural"] = None
            df["municipio_id"] = None
            df["municipio"] = None
            self.logger.info(f"{self.year}: no geo columns, filled with None")

        self.logger.info(f"{self.year}: {len(df)} rows renamed")
        return df

    def finalization(self, input_data: pd.DataFrame) -> pd.DataFrame:
        if input_data.empty:
            self.logger.info("No data, skipping save")
            return input_data
        pkl_path = self.work_dir / f"extract_{self.year}.pkl"
        input_data.to_pickle(pkl_path)
        self.logger.info(f"{self.year}: {len(input_data)} rows saved to {pkl_path}")
        return input_data
