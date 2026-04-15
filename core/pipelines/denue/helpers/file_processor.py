import pandas as pd
import requests
from io import BytesIO
from zipfile import ZipFile
from requests.exceptions import ConnectionError, HTTPError, Timeout
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from core.utils.logger import get_console_logger

logger = get_console_logger(__name__)

DTYPE_OVERRIDES = {
    "numero_int": str,
    "codigo_postal": str,
    "telefono": str,
}


def _download_zip(url: str) -> BytesIO:
    response = requests.get(url, stream=True, timeout=60)
    response.raise_for_status()
    return BytesIO(response.content)


def _extract_csv_from_zip(zip_content: BytesIO) -> bytes:
    with ZipFile(zip_content) as zf:
        csv_files = [f for f in zf.namelist() if f.endswith(".csv") and "inegi" in f.lower()]
        if not csv_files:
            raise ValueError("No CSV file with 'inegi' found in zip")
        if len(csv_files) > 1:
            raise ValueError(f"Multiple inegi CSV files found: {csv_files}")
        return zf.read(csv_files[0])


def _csv_to_dataframe(csv_content: bytes) -> pd.DataFrame:
    try:
        return pd.read_csv(BytesIO(csv_content), dtype=DTYPE_OVERRIDES, low_memory=False)
    except Exception:
        csv_utf8 = csv_content.decode("latin-1").encode("utf-8")
        return pd.read_csv(BytesIO(csv_utf8), dtype=DTYPE_OVERRIDES, low_memory=False)


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=2, min=2, max=30),
    retry=retry_if_exception_type((ConnectionError, Timeout, HTTPError)),
    before_sleep=lambda state: logger.warning(f"Retry attempt {state.attempt_number} for download"),
)
def download_denue_csv(url: str) -> pd.DataFrame:
    zip_content = _download_zip(url)
    csv_content = _extract_csv_from_zip(zip_content)
    return _csv_to_dataframe(csv_content)
