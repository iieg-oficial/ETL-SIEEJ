import io
import pandas as pd
import zipfile
from typing import Any, Optional

from core.pipelines.enec.config import PIPELINE_NAME, settings
from core.pipelines.enec.constants import (
    ENTIDAD_DESCRIPTION,
    ENTIDAD_MEMBER_PATTERN,
    ENTIDAD_RENAME,
    NACIONAL_DESCRIPTION,
    NACIONAL_MEMBER_PATTERN,
    NACIONAL_RENAME,
    SOURCE_ENCODING,
    ZIP_MAGIC,
)
from core.pipelines.stage import Stage
from core.utils.http import http_get
from core.utils.zip_members import resolve_year_member


class EnecExtract(Stage):
    """Download the ENEC monthly ZIP and read its national and state datasets."""

    def __init__(self):
        super().__init__(PIPELINE_NAME, "extract")

    def source(self, input_data: Optional[Any] = None) -> bytes:
        """Download the dataset and return the raw ZIP bytes.

        The published path is stable; what changes with every edition is the ZIP
        content (the CSVs are renamed with the new year). What does need checking
        is that the answer really is the dataset: INEGI serves an HTML error page
        with status 200 when a path no longer exists, so the status code cannot
        tell a live path from a dead one and only the file signature can.

        Raises:
            FileNotFoundError: if the URL no longer serves a ZIP.
        """
        url = settings.ENEC_URL
        self.logger.info(f"Downloading ENEC dataset: {url}")
        response = http_get(url, timeout=settings.DOWNLOAD_TIMEOUT)

        if response.status_code != 200 or not response.content.startswith(ZIP_MAGIC):
            raise FileNotFoundError(
                f"{url} did not serve a ZIP (status {response.status_code}). INEGI most likely moved "
                f"the publication: check the program page and update ENEC_URL in "
                f"core/pipelines/{settings.PIPELINE_NAME}/.env."
            )

        self.logger.info(f"ENEC dataset downloaded ({len(response.content):,} bytes)")
        return response.content

    def action(self, input_data: bytes) -> dict[str, pd.DataFrame]:
        with zipfile.ZipFile(io.BytesIO(input_data)) as zf:
            names = zf.namelist()
            nacional = resolve_year_member(
                names,
                template=settings.ENEC_NACIONAL_CSV,
                pattern=NACIONAL_MEMBER_PATTERN,
                description=NACIONAL_DESCRIPTION,
            )
            entidad = resolve_year_member(
                names,
                template=settings.ENEC_ENTIDAD_CSV,
                pattern=ENTIDAD_MEMBER_PATTERN,
                description=ENTIDAD_DESCRIPTION,
            )

            df_nacional = self._read_member(zf, nacional, NACIONAL_RENAME)
            df_entidad = self._read_member(zf, entidad, ENTIDAD_RENAME)

        self.logger.info(f"{len(df_nacional):,} national rows and {len(df_entidad):,} state rows extracted")
        return {"nacional": df_nacional, "entidad": df_entidad}

    def _read_member(self, zf: zipfile.ZipFile, member: str, rename_header: dict[str, str]) -> pd.DataFrame:
        raw = pd.read_csv(io.BytesIO(zf.read(member)), encoding=SOURCE_ENCODING, dtype=str)

        # "J000A " ships with a trailing space in the header. Without this the
        # rename misses it and the column is silently dropped.
        raw.columns = [column.strip() for column in raw.columns]

        missing = set(rename_header) - set(raw.columns)
        if missing:
            raise ValueError(f"{member}: expected columns missing from the source: {sorted(missing)}")

        df = raw[list(rename_header)].rename(columns=rename_header)
        self.logger.info(f"{member}: {len(df):,} rows")
        return df

    def finalization(self, input_data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        if input_data["nacional"].empty and input_data["entidad"].empty:
            self.logger.warning("Source returned no rows, skipping pkl save")
            return input_data

        input_data["nacional"].to_pickle(self.work_dir / "nacional.pkl")
        input_data["entidad"].to_pickle(self.work_dir / "entidad.pkl")
        self.logger.info(f"Datasets saved to {self.work_dir}")
        return input_data
