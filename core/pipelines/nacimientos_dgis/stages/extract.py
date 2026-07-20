import io
import zipfile
from typing import Any, Optional
import pandas as pd

from core.pipelines.nacimientos_dgis.config import settings
from core.pipelines.nacimientos_dgis.constants import DOWNLOAD_TIMEOUT, PIPELINE_NAME, USECOLS
from core.pipelines.stage import Stage
from core.utils.http import http_get
from core.utils.logger import get_logger


class NacimientosDgisExtract(Stage):
    def __init__(self, year: int | None = None):
        super().__init__(PIPELINE_NAME, "extract")
        self.logger = get_logger(f"{PIPELINE_NAME}.extract")
        self.year = year

    def _fetch_year(self, year: int) -> pd.DataFrame | None:
        url = settings.SOURCE_URL.format(year=year)
        self.logger.info(f"[source] Fetching {url}")
        response = http_get(url, timeout=DOWNLOAD_TIMEOUT)

        if response.status_code == 404:
            self.logger.info(f"[source] {year}: not available (404)")
            return None

        response.raise_for_status()

        csv_bytes = self._extract_csv_bytes(response.content, url)
        df = pd.read_csv(io.BytesIO(csv_bytes), usecols=USECOLS, low_memory=False)

        self.logger.info(f"[source] {year}: {len(df):,} rows")
        return df

    def _extract_csv_bytes(self, zip_bytes: bytes, origin: str) -> bytes:
        """Return the CSV payload, descending into nested zips.

        Older editions ship the CSV directly; the 2025 edition wraps it in a
        second zip (sinac_YYYY.zip -> .../sinac_YYYY.zip -> Nacimientos_YYYY.csv).
        """
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
            for name in z.namelist():
                if name.endswith(".csv"):
                    return z.read(name)
            for name in z.namelist():
                if name.endswith(".zip"):
                    return self._extract_csv_bytes(z.read(name), origin)
        raise ValueError(f"No CSV found in archive from {origin}")

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
