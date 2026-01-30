
from typing import Any, Optional
import gdown
import os
import pandas as pd

from core.utils.logger import get_logger
from core.pipelines.fiscalia.config import settings
from core.pipelines.stage import Stage
from core.pipelines.fiscalia.attributes import DataColumns

class FiscaliaExtractor(Stage):
    def __init__(self, pipeline_name: str = 'Fiscalia', mode: str = 'bootstrap'):
        super().__init__(pipeline_name, 'extract')
        self.mode = mode
        self.logger = get_logger(f"{pipeline_name}.extract")

    def source(self) -> Any:
        folder_url = settings.G_FOLDER_URL
        temp_folder = "data/extract"
        self.logger.info("[source] Retrieving fiscalia data")
        gdown.download_folder(folder_url, output=temp_folder, quiet=True)
        csv_files = [f for f in os.listdir(temp_folder) if f.endswith('.xlsx')]
        if csv_files:
            target_path = os.path.join(temp_folder,csv_files[0])
            data = pd.read_excel(target_path)
        return data

    def action(self, input_data: pd.DataFrame) -> Any:
        self.logger.info(f"[action] Reading fiscalia data with {len(input_data)} values")
        try:
            input_data.filter(items=DataColumns.values())
        except Exception as e:
            self.logger.error(f"[action] {e}")
        return input_data

    def finalization(self, input_data: Optional[Any]) -> Any:
        self.logger.info(f" [finalization]: {len(input_data)} values extracted")
        self.logger.info(f" [finalization]: {input_data.columns} columns extracted")
        return input_data
if __name__ == "__main__":



    stage_instance = FiscaliaExtractor()
    input_data = stage_instance.source()
    input_data = stage_instance.action(input_data)
    stage_instance.finalization(input_data)

