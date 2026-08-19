import io
import zipfile
from typing import Any, Optional

import pandas as pd

from core.pipelines.rastros.config import PIPELINE_NAME
from core.pipelines.rastros.constants import DATASET_MEMBER_PATTERN, RENAME_HEADER, SOURCE_ENCODING
from core.pipelines.rastros.helpers import fetch_dataset
from core.pipelines.stage import Stage


class RastrosExtract(Stage):
    """Download the ESGRM monthly ZIP and concatenate its yearly CSV files."""

    def __init__(self):
        super().__init__(PIPELINE_NAME, "extract")

    def source(self, input_data: Optional[Any] = None) -> bytes:
        return fetch_dataset()

    def action(self, input_data: bytes) -> pd.DataFrame:
        with zipfile.ZipFile(io.BytesIO(input_data)) as zf:
            members = sorted(m for m in zf.namelist() if DATASET_MEMBER_PATTERN.search(m))
            if not members:
                raise FileNotFoundError(f"The ZIP has no esgrm_mensual_tr_cifra yearly CSV. Contents: {zf.namelist()}")
            self.logger.info(f"{len(members)} yearly files found in the ZIP")
            frames = [self._read_member(zf, member) for member in members]

        df = pd.concat(frames, ignore_index=True)
        self.logger.info(f"{len(df):,} rows extracted in total")
        return df

    def _read_member(self, zf: zipfile.ZipFile, member: str) -> pd.DataFrame:
        raw = pd.read_csv(io.BytesIO(zf.read(member)), encoding=SOURCE_ENCODING, dtype=str)

        missing = set(RENAME_HEADER) - set(raw.columns)
        if missing:
            raise ValueError(f"{member}: expected columns missing from the source: {sorted(missing)}")

        df = raw[list(RENAME_HEADER)].rename(columns=RENAME_HEADER)
        self.logger.info(f"{member}: {len(df):,} rows")
        return df

    def finalization(self, input_data: pd.DataFrame) -> pd.DataFrame:
        if input_data.empty:
            self.logger.warning("Source returned no rows, skipping pkl save")
            return input_data

        pkl_path = self.work_dir / "extract.pkl"
        input_data.to_pickle(pkl_path)
        self.logger.info(f"{len(input_data):,} rows saved to {pkl_path}")
        return input_data
