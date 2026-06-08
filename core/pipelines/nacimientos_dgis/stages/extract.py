import io
import zipfile
from typing import Any, Optional
import pandas as pd
import requests

from core.pipelines.nacimientos_dgis.config import settings
from core.pipelines.nacimientos_dgis.constants import PIPELINE_NAME, USECOLS
from core.pipelines.stage import Stage
from core.utils.logger import get_logger


class NacimientosDgisExtract(Stage):
    def __init__(self, year: int | None = None):
        super().__init__(PIPELINE_NAME, "extract")
        self.logger = get_logger(f"{PIPELINE_NAME}.extract")
        self.year = year

    def _fetch_year(self, year: int) -> pd.DataFrame | None:
        url = settings.SOURCE_URL.format(year=year)
        self.logger.info(f"[source] Fetching {url}")
        response = requests.get(url, timeout=300)

        if response.status_code == 404:
            self.logger.info(f"[source] {year}: not available (404)")
            return None

        response.raise_for_status()

        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            csv_name = next(n for n in z.namelist() if n.endswith(".csv"))
            with z.open(csv_name) as f:
                df = pd.read_csv(f, usecols=USECOLS, low_memory=False)

        self.logger.info(f"[source] {year}: {len(df):,} rows")
        return df

    def source(self, input_data: Optional[Any] = None) -> pd.DataFrame | None:
        pkl = self.work_dir / f"sinac_{self.year}.pkl"
        if pkl.exists():
            self.logger.info(f"[source] {self.year}: loaded from cache ({pkl})")
            return pd.read_pickle(pkl)
        return self._fetch_year(self.year)

    def action(self, input_data: pd.DataFrame | None) -> pd.DataFrame | None:
        return input_data

    def finalization(self, input_data: pd.DataFrame | None) -> pd.DataFrame | None:
        if input_data is None or input_data.empty:
            return input_data
        pkl = self.work_dir / f"sinac_{self.year}.pkl"
        input_data.to_pickle(pkl)
        self.logger.info(f"[finalization] {self.year}: {len(input_data):,} rows saved")
        return input_data
