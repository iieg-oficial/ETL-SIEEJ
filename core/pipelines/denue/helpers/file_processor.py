import pandas as pd
import requests

from io import BytesIO
from zipfile import ZipFile
from requests.exceptions import ChunkedEncodingError, ConnectionError, HTTPError, Timeout
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from core.pipelines.denue.constants import COLUMN_ALIASES, DTYPE_OVERRIDES
from core.utils.logger import get_console_logger

logger = get_console_logger(__name__)


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


def _read_csv(buffer: bytes) -> pd.DataFrame:
    header = pd.read_csv(BytesIO(buffer), nrows=0).columns
    dtype = {col: DTYPE_OVERRIDES[col.lower()] for col in header if col.lower() in DTYPE_OVERRIDES}
    df = pd.read_csv(BytesIO(buffer), dtype=dtype, low_memory=False)
    df.columns = df.columns.str.lower()
    return df.rename(columns=COLUMN_ALIASES)


def _csv_to_dataframe(csv_content: bytes) -> pd.DataFrame:
    try:
        return _read_csv(csv_content)
    except UnicodeDecodeError:
        return _read_csv(csv_content.decode("latin-1").encode("utf-8"))


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=2, min=2, max=30),
    retry=retry_if_exception_type((ConnectionError, Timeout, HTTPError, ChunkedEncodingError)),
    before_sleep=lambda state: logger.warning(f"Retry attempt {state.attempt_number} for download"),
)
def download_denue_csv(url: str) -> pd.DataFrame:
    zip_content = _download_zip(url)
    csv_content = _extract_csv_from_zip(zip_content)
    return _csv_to_dataframe(csv_content)
