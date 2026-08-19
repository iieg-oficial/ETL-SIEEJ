import io
import pandas as pd
from typing import Any, Optional

from core.pipelines.indice_shf_vivienda.config import PIPELINE_NAME, settings
from core.pipelines.indice_shf_vivienda.constants import RENAME_HEADER, SHEET_NAME, XLSX_MAGIC
from core.pipelines.stage import Stage
from core.utils.http import http_get


class IndiceShfViviendaExtract(Stage):
    """Download the SHF housing price index workbook and read its single sheet."""

    def __init__(self):
        super().__init__(PIPELINE_NAME, "extract")

    def source(self, input_data: Optional[Any] = None) -> bytes:
        """Download the workbook and return its raw bytes.

        gob.mx sits behind a WAF that answers 200 with a 1.8 KB "Challenge
        Validation" page when it decides to block a client, so the status code
        cannot tell a real download from a rejection and only the file signature
        can. Plain requests passes the challenge today; a curl-like client does
        not, which is exactly the failure this guard has to catch.

        Raises:
            FileNotFoundError: if the URL no longer serves a workbook.
        """
        url = settings.SHF_URL
        self.logger.info(f"Downloading SHF housing price index: {url}")
        response = http_get(url, timeout=settings.DOWNLOAD_TIMEOUT)

        if response.status_code != 200 or not response.content.startswith(XLSX_MAGIC):
            raise FileNotFoundError(
                f"{url} did not serve an XLSX (status {response.status_code}, "
                f"{len(response.content):,} bytes). SHF publishes a new file id and a new quarter "
                f"in the name every edition: check https://www.gob.mx/shf/archivo/documentos and "
                f"update SHF_URL in core/pipelines/{settings.PIPELINE_NAME}/.env."
            )

        self.logger.info(f"Workbook downloaded ({len(response.content):,} bytes)")
        return response.content

    def action(self, input_data: bytes) -> pd.DataFrame:
        raw = pd.read_excel(io.BytesIO(input_data), sheet_name=SHEET_NAME, dtype=str)
        raw.columns = [str(column).strip() for column in raw.columns]

        missing = set(RENAME_HEADER) - set(raw.columns)
        if missing:
            raise ValueError(f"{SHEET_NAME}: expected columns missing from the source: {sorted(missing)}")

        df = raw[list(RENAME_HEADER)].rename(columns=RENAME_HEADER)
        self.logger.info(f"{len(df):,} rows extracted")
        return df

    def finalization(self, input_data: pd.DataFrame) -> pd.DataFrame:
        if input_data.empty:
            self.logger.warning("Source returned no rows, skipping pkl save")
            return input_data

        input_data.to_pickle(self.work_dir / "extract.pkl")
        self.logger.info(f"Dataset saved to {self.work_dir}")
        return input_data
