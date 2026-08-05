import io
import zipfile
from typing import Any, Optional

import pandas as pd

from core.pipelines.ems.config import PIPELINE_NAME, settings
from core.pipelines.ems.constants import CATALOG_RENAME_HEADER, RENAME_HEADER, SOURCE_ENCODING, ZIP_MAGIC
from core.pipelines.ems.helpers import resolve_catalog_member, resolve_dataset_member
from core.pipelines.stage import Stage
from core.utils.http import http_get


class EmsExtract(Stage):
    """Download the EMS monthly ZIP and read its dataset and activity catalog."""

    def __init__(self):
        super().__init__(PIPELINE_NAME, "extract")

    def source(self, input_data: Optional[Any] = None) -> bytes:
        """Download the dataset and return the raw ZIP bytes.

        The published path is stable; what changes with every edition is the ZIP
        content (the dataset CSV is renamed with the new year). What does need
        checking is that the answer really is the dataset: INEGI serves an HTML
        error page with status 200 when a path no longer exists, so the status
        code cannot tell a live path from a dead one and only the file signature
        can.

        Raises:
            FileNotFoundError: if the URL no longer serves a ZIP.
        """
        url = settings.EMS_URL
        self.logger.info(f"Downloading EMS dataset: {url}")
        response = http_get(url, timeout=settings.DOWNLOAD_TIMEOUT)

        if response.status_code != 200 or not response.content.startswith(ZIP_MAGIC):
            raise FileNotFoundError(
                f"{url} did not serve a ZIP (status {response.status_code}). INEGI most likely moved "
                f"the publication: check the program page and update EMS_URL in "
                f"core/pipelines/{settings.PIPELINE_NAME}/.env."
            )

        self.logger.info(f"EMS dataset downloaded ({len(response.content):,} bytes)")
        return response.content

    def action(self, input_data: bytes) -> dict[str, pd.DataFrame]:
        with zipfile.ZipFile(io.BytesIO(input_data)) as zf:
            names = zf.namelist()
            df = self._read_member(zf, resolve_dataset_member(names), RENAME_HEADER)
            actividades = self._read_member(zf, resolve_catalog_member(names), CATALOG_RENAME_HEADER)

        self.logger.info(f"{len(df):,} rows and {len(actividades):,} activities extracted")
        return {"df": df, "actividades": actividades}

    def _read_member(self, zf: zipfile.ZipFile, member: str, rename_header: dict[str, str]) -> pd.DataFrame:
        raw = pd.read_csv(io.BytesIO(zf.read(member)), encoding=SOURCE_ENCODING, dtype=str)

        missing = set(rename_header) - set(raw.columns)
        if missing:
            raise ValueError(f"{member}: expected columns missing from the source: {sorted(missing)}")

        df = raw[list(rename_header)].rename(columns=rename_header)
        self.logger.info(f"{member}: {len(df):,} rows")
        return df

    def finalization(self, input_data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        if input_data["df"].empty:
            self.logger.warning("Source returned no rows, skipping pkl save")
            return input_data

        input_data["df"].to_pickle(self.work_dir / "extract.pkl")
        input_data["actividades"].to_pickle(self.work_dir / "actividades.pkl")
        self.logger.info(f"{len(input_data['df']):,} rows saved to {self.work_dir}")
        return input_data
