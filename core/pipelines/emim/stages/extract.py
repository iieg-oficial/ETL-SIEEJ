import io
import pandas as pd
import zipfile
from typing import Any, Optional

from core.pipelines.emim.config import PIPELINE_NAME, settings
from core.pipelines.emim.constants import (
    CATALOG_DESCRIPTION,
    CATALOG_MEMBER_PATTERN,
    CATALOG_RENAME_HEADER,
    DATASET_DESCRIPTION,
    DATASET_MEMBER_PATTERN,
    RENAME_HEADER,
    SOURCE_ENCODING,
    ZIP_MAGIC,
)
from core.pipelines.stage import Stage
from core.utils.http import http_get
from core.utils.zip_members import resolve_member, resolve_year_member


class EmimExtract(Stage):
    """Download the EMIM monthly ZIP and read its dataset and activity catalog."""

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
        url = settings.EMIM_URL
        self.logger.info(f"Downloading EMIM dataset: {url}")
        response = http_get(url, timeout=settings.DOWNLOAD_TIMEOUT)

        if response.status_code != 200 or not response.content.startswith(ZIP_MAGIC):
            raise FileNotFoundError(
                f"{url} did not serve a ZIP (status {response.status_code}). INEGI most likely moved "
                f"the publication: check the program page and update EMIM_URL in "
                f"core/pipelines/{settings.PIPELINE_NAME}/.env."
            )

        self.logger.info(f"EMIM dataset downloaded ({len(response.content):,} bytes)")
        return response.content

    def action(self, input_data: bytes) -> dict[str, pd.DataFrame]:
        with zipfile.ZipFile(io.BytesIO(input_data)) as zf:
            names = zf.namelist()
            dataset = resolve_year_member(
                names,
                template=settings.EMIM_CSV,
                pattern=DATASET_MEMBER_PATTERN,
                description=DATASET_DESCRIPTION,
            )
            catalog = resolve_member(
                names,
                expected=settings.EMIM_CATALOG_CSV,
                pattern=CATALOG_MEMBER_PATTERN,
                description=CATALOG_DESCRIPTION,
            )

            df = self._read_member(zf, dataset, RENAME_HEADER)
            actividades = self._read_member(zf, catalog, CATALOG_RENAME_HEADER)

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
