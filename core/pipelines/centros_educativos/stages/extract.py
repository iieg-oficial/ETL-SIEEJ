import pandas as pd
import requests
import urllib3

from pathlib import Path
from requests.exceptions import ConnectionError
from retry import retry
from typing import Any, Optional
from datetime import date

from core.utils.logger import get_logger
from core.pipelines.stage import Stage
from core.pipelines.centros_educativos.constants import URL_HEADER, RENAME_HEADER
from core.pipelines.centros_educativos.config import settings
from core.pipelines.stage import Stage

logger = get_logger("centros_educativos.extract")
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class CentrosExtractor(Stage):
    def __init__(self, mode: str = "bootstrap", entidad: int = None):
        super().__init__(settings.PIPELINE_NAME, "extract")
        self.mode = mode
        self.entidad = entidad

    @retry((ConnectionError, requests.RequestException), tries=6, delay=5, jitter=3, logger=logger)
    def source(self, input_data: Optional[Any] = None) -> list[dict]:
        """Descarga los datos de centros educativos desde la URL especificada en settings para la entidad especifica."""
        if not self.entidad:
            raise ValueError("Entidad parameter is required")

        url = settings.CENTROS_EDUCATIVOS_URL.format(self.entidad)
        logger.info(f"Fetching centros educativos data for entidad_id {self.entidad}")

        response = requests.get(url, headers=URL_HEADER, timeout=40, verify=False)
        response.raise_for_status()

        data = response.json()
        ccts = data.get('Ccts', [])
        logger.info(f"Entidad {self.entidad}: {len(ccts)} centros found")
        return ccts


    def action(self, input_data: Optional[Any] = None) -> pd.DataFrame:
        """Convierte los datos de centros educativos en un DataFrame de pandas."""
        df = pd.DataFrame(input_data)
        df['fecha_actualizacion'] = date.today()
        columns_to_keep = list(RENAME_HEADER.keys())
        df_clean = df[columns_to_keep]
        df_clean = df_clean.rename(columns=RENAME_HEADER).copy()
        download_dir = Path("data/extract/centros_educativos")
        download_dir.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"Action df columns: {list(df_clean.columns)}")
        return df_clean

    def finalization(self, input_data: pd.DataFrame) -> pd.DataFrame:
        """Guarda el DataFrame en formato pickle."""
        pkl_path = self.work_dir / f"centros_educativos_{self.entidad}.pkl"
        input_data.to_pickle(pkl_path)
        logger.info(f"Finalization: {len(input_data)} rows saved to {pkl_path}")

        return input_data

