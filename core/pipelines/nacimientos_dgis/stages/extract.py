import io
import zipfile
from datetime import date
from typing import Any, Optional

import pandas as pd
import requests

from core.pipelines.nacimientos_dgis.config import settings
from core.pipelines.nacimientos_dgis.constants import PIPELINE_NAME, USECOLS
from core.pipelines.stage import Stage
from core.utils.logger import get_logger


class NacimientosDgisExtract(Stage):
    def __init__(self):
        super().__init__(PIPELINE_NAME, "extract")
        self.logger = get_logger(f"{PIPELINE_NAME}.extract")

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

    def source(self, input_data: Optional[Any] = None) -> dict[int, pd.DataFrame]:
        current_year = date.today().year
        cached = {}
        missing_years = []

        for year in range(settings.START_YEAR, current_year + 1):
            pkl = self.work_dir / f"sinac_{year}.pkl"
            if pkl.exists():
                cached[year] = pd.read_pickle(pkl)
                self.logger.info(f"[source] {year}: loaded from cache ({len(cached[year]):,} rows)")
            else:
                missing_years.append(year)

        for year in missing_years:
            df = self._fetch_year(year)
            if df is not None:
                cached[year] = df

        return cached

    def action(self, input_data: dict[int, pd.DataFrame]) -> dict[int, pd.DataFrame]:
        return input_data

    def finalization(self, input_data: dict[int, pd.DataFrame]) -> dict[int, pd.DataFrame]:
        for year, df in input_data.items():
            df.to_pickle(self.work_dir / f"sinac_{year}.pkl")

        total = sum(len(df) for df in input_data.values())
        self.logger.info(f"[finalization] {total:,} rows saved across {len(input_data)} years")
        return input_data
