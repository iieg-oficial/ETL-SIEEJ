from typing import Any, Optional
import pandas as pd

from core.utils import lowercase_headers
from core.utils.logger import get_logger
from core.pipelines.fiscalia.config import settings
from core.pipelines.stage import Stage
from core.pipelines.fiscalia.attributes.data_columns import (
    HistoricalCols, RenameHistoricalCols,
    UpdateCols, RenameUpdateCols,
)
from core.utils.gdrive import gdown_folder
from core.utils.files import (
    get_file_by_name, get_latest_file, get_latest_files_per_year,
    parse_date_from_filename,
)


class FiscaliaExtract(Stage):
    def __init__(self, pipeline_name: str = 'fiscalia', mode: str = 'bootstrap'):
        super().__init__(pipeline_name, 'extract')
        self.mode = mode
        self.logger = get_logger(f"{pipeline_name}.extract")

    def source(self, input_data: Optional[Any] = None) -> Any:
        self.logger.info(f"[source] Downloading fiscalia files (mode={self.mode})")
        output_folder = gdown_folder(settings.GDRIVE_FOLDER, "data/extract/fiscalia")

        if self.mode == 'bootstrap':
            historical = get_file_by_name(output_folder, settings.HISTORICAL_FILENAME)
            updates = get_latest_files_per_year(output_folder)
            return [historical] + updates
        else:
            return [get_latest_file(output_folder)]

    def action(self, input_data: list[str]) -> Any:
        self.logger.info(f"[action] Processing {len(input_data)} files")
        dfs = []

        for filepath in input_data:
            df = pd.read_excel(filepath, engine="openpyxl")
            lowercase_headers(df)
            df.columns = df.columns.str.replace(' ', '_')

            if parse_date_from_filename(filepath, ".xlsx") is None:
                df = df.rename(columns=RenameHistoricalCols.rename())
                df = df[HistoricalCols.get_values()]
                df["violencia"] = None # Datos Históricos no tienen violencia
                df["calle"] = None # Datos Históricos no tienen columna calle
                df["cruce"] = None # Datos Históricos no tienen columna cruce
                df["_is_update"] = False
            else:
                df = df.rename(columns=RenameUpdateCols.rename())
                df = df[UpdateCols.get_values()]
                df["_is_update"] = True

            dfs.append(df)
        return pd.concat(dfs, ignore_index=True)

    def finalization(self, input_data: Optional[Any]) -> Any:
        self.logger.info(f"[finalization] Extracted {len(input_data)} total rows")
        return input_data
