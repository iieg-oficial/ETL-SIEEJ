
from typing import Any, Optional
import pandas as pd

from core.utils.logger import get_logger
from core.pipelines.fiscalia.config import settings
from core.pipelines.stage import Stage
from core.pipelines.fiscalia.attributes.data_columns import UpdateCols, RenameUpdateCols
from core.pipelines.fiscalia.helpers.normalize import lowercase_headers
from core.pipelines.fiscalia.helpers.gdrive import download_and_unzip


class FiscaliaExtractUpdate(Stage):
    def __init__(self, pipeline_name: str = 'fiscalia', mode: str = 'update'):
        super().__init__(pipeline_name, 'extract')
        self.mode = mode
        self.logger = get_logger(f"{pipeline_name}.extract")

    def source(self, input_data: Optional[Any] = None) -> Any:
        self.logger.info("[source] Downloading fiscalia xlsx for database update")
        xlsx_path = download_and_unzip(
            folder_url=settings.UPDATE_EXCEL_FOLDER,
            output_folder="data/extract/fiscalia",
            extension=".xlsx"
        )
        return xlsx_path

    def action(self, input_data: str) -> Any:
        self.logger.info("[action] Reading XLSX file")
        df = pd.read_excel(input_data, engine="openpyxl")
        self.logger.info(f"[action] Read {len(df)} rows")
        lowercase_headers(df)
        df.columns = df.columns.str.replace(' ', '_')
        df = df.rename(columns=RenameUpdateCols.rename())
        df = df[UpdateCols.get_values()]
        return df

    def finalization(self, input_data: Optional[Any]) -> Any:
        self.logger.info(f"[finalization] Extracted {len(input_data)} rows from update XLSX")
        self.logger.info(f"[finalization] Records extracted: {list(input_data.keys())}")
        return input_data

