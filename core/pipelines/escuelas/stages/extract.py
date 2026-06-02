from pathlib import Path
from typing import Any, Optional

import pandas as pd

from core.pipelines.escuelas.config import settings
from core.pipelines.escuelas.constants import (
    DIRECTORIO_DATASET,
    ESTADISTICA_DATASET,
    PIPELINE_NAME,
)
from core.pipelines.stage import Stage
from core.utils.files import get_file_by_name
from core.utils.gdrive import download_folder
from core.utils.logger import get_logger


class EscuelasExtract(Stage):
    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "extract")
        self.mode = mode
        self.logger = get_logger(f"{PIPELINE_NAME}.extract")

    def _download_sources(self) -> dict[str, Path]:
        output_folder = download_folder(
            settings.GDRIVE_FOLDER_ID,
            str(self.work_dir),
            settings.GDRIVE_CLIENT_EMAIL,
            settings.GDRIVE_PRIVATE_KEY,
        )
        return {
            DIRECTORIO_DATASET: Path(get_file_by_name(output_folder, settings.DIRECTORIO_FILENAME)),
            ESTADISTICA_DATASET: Path(get_file_by_name(output_folder, settings.ESTADISTICA_FILENAME)),
        }

    def source(self, input_data: Optional[Any] = None) -> dict[str, Path]:
        if self.mode != "bootstrap":
            raise ValueError("Escuelas v1 only supports bootstrap mode")

        self.logger.info("[source] Downloading escuelas files from Google Drive")
        return self._download_sources()

    def action(self, input_data: dict[str, Path]) -> dict[str, pd.DataFrame]:
        self.logger.info("[action] Reading escuelas CSV files")
        return {
            DIRECTORIO_DATASET: pd.read_csv(input_data[DIRECTORIO_DATASET], encoding="utf-8-sig"),
            ESTADISTICA_DATASET: pd.read_csv(input_data[ESTADISTICA_DATASET], encoding="utf-8-sig"),
        }

    def finalization(self, input_data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        for dataset, df in input_data.items():
            df.to_pickle(self.work_dir / f"{dataset}.pkl")
            self.logger.info(f"[finalization] {dataset}: {len(df):,} rows saved")

        return input_data
