
from typing import Any, Optional
import pandas as pd

from core.utils.logger import get_logger
from core.pipelines.fiscalia.config import settings
from core.pipelines.stage import Stage
from core.pipelines.fiscalia.attributes.data_columns import HistoricalCols, RenameHistoricalCols
from core.pipelines.fiscalia.helpers.gdrive import download_files_from_folder


class FiscaliaExtractBootstrap(Stage):
    def __init__(self, pipeline_name: str = 'Fiscalia', mode: str = 'bootstrap'):
        super().__init__(pipeline_name, 'extract')
        self.mode = mode
        self.logger = get_logger(f"{pipeline_name}.extract")

    def source(self, input_data: Optional[Any] = None) -> Any:
        self.logger.info("[source] Retrieving fiscalia data")
        file_paths = download_files_from_folder(
            folder_url=settings.BOOTSTRAP_CSV_FOLDER,
            output_folder="data/extract/Fiscalia",
            filenames=["fiscalia_data.csv"]
        )
        return pd.read_csv(file_paths["fiscalia_data.csv"], encoding="utf-8")


    def action(self, input_data: dict) -> Any:
        self.logger.info(f"[action] Reading fiscalia data with {len(input_data)} values")
        try:
            input_data = input_data.rename(columns=RenameHistoricalCols.rename())
            input_data = input_data[HistoricalCols.get_values()]
        except Exception as e:
            self.logger.error(f"[action] {e}")
        return input_data

    def finalization(self, input_data: Optional[Any]) -> Any:
        self.logger.info(f"[finalization] Records extracted: {list(input_data.keys())}")
        self.logger.info(f"[finalization]: where fiscalia csv has={len(input_data)} rows")
        return input_data

