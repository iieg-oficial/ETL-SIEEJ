import pandas as pd
from typing import Any, Optional

from core.pipelines.participacion_ciudadana.config import settings
from core.pipelines.participacion_ciudadana.constants import RENAME_HEADER
from core.pipelines.stage import Stage
from core.utils.gdrive import download_public_file
from core.utils.logger import get_logger


class ParticipacionCiudadanaExtract(Stage):
    def __init__(self):
        super().__init__("participacion_ciudadana", "extract")
        self.logger = get_logger("participacion_ciudadana.extract")

    def source(self, input_data: Optional[Any] = None) -> pd.DataFrame:
        pkl_path = self.work_dir / "participacion.pkl"

        if pkl_path.exists():
            self.logger.info("[source] Loading cached file")
            return pd.read_pickle(pkl_path)

        csv_path = self.work_dir / "participacion.csv"
        self.logger.info("[source] Downloading participacion ciudadana CSV")
        download_public_file(settings.GDRIVE_FILE_ID, csv_path)

        df = pd.read_csv(csv_path, encoding="utf-8")
        self.logger.info(f"[source] Fetched {len(df)} rows")
        return df

    def action(self, input_data: pd.DataFrame) -> pd.DataFrame:
        if input_data.empty:
            self.logger.warning("[action] Empty input, skipping")
            return input_data

        df = input_data.rename(columns=RENAME_HEADER)
        df = df[list(RENAME_HEADER.values())]
        self.logger.info(f"[action] Renamed columns: {len(df)} rows")
        return df

    def finalization(self, input_data: pd.DataFrame) -> pd.DataFrame:
        input_data.to_pickle(self.work_dir / "participacion.pkl")
        self.logger.info(f"[finalization] {len(input_data)} rows saved")
        return input_data
