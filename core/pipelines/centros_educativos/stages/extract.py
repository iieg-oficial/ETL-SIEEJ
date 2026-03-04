
import os
import pandas as pd
import requests
from requests.exceptions import ConnectionError
from retry import retry
import urllib3
from typing import Any, Optional

from core.utils.logger import get_logger
from core.pipelines.stage import Stage
from core.pipelines.centros_educativos.constants import URL_HEADER
from core.pipelines.centros_educativos.config import settings
from core.pipelines.stage import Stage

logger = get_logger("centros_educativos.extract")
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class CentrosExtractor(Stage):
    def __init__(self, mode: str = "bootstrap"):
        super().__init__(settings.PIPELINE_NAME, "extract")
        self.mode = mode

    @retry((ConnectionError, requests.RequestException), tries=6, delay=5, jitter=3, logger=logger)
    def source(self, input_data: Optional[Any] = None) -> list[dict]:
        """..."""
        logger.info("Fetching centros educativos data...")
        response = requests.get(settings.CENTROS_EDUCATIVOS_URL, headers=URL_HEADER, timeout=40, verify=False)
        response.raise_for_status()

        data = response.json()
        return data['Ccts']


    def action(self, input_data: Optional[Any] = None) -> list[dict]:
        """..."""
        df = pd.DataFrame(input_data)
        download_dir = os.path.join(os.getcwd(), "data", "extract", "centros_educativos")
        os.makedirs(download_dir, exist_ok=True)
        output_file = os.path.join(download_dir, "concentrado_escuelas.csv")
        df.to_csv(output_file, index=False, encoding='utf-8')

        return output_file

    def finalization(self, input_data: Optional[Any] = None) -> dict:
        """Escanea directorios extraidos y construye inventario para la etapa Transform."""
        logger.info(f"Finalization: Data saved to {input_data}")

        return input_data

if __name__ == "__main__":
    extractor = CentrosExtractor(mode="bootstrap")
    extractor.execute()
