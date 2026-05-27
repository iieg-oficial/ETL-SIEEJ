import zipfile

from datetime import datetime
from typing import Any, Optional

import requests

from core.pipelines.efipem.config import settings
from core.pipelines.efipem.consts import PIPELINE_NAME, SOURCE_CSV_GLOB
from core.pipelines.stage import Stage


class EfipemExtractor(Stage):
    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "extract")
        self.mode = mode

    # Fuente de datos: URL del ZIP de EFIPEM municipal anual (INEGI)
    def source(self, input_data: Optional[Any] = None) -> dict:
        url = settings.EFIPEM_SOURCE_URL
        self.logger.info(f"Fuente de datos: {url}")
        return {"url": url}

    # Descarga el ZIP y extrae todos los CSVs anuales
    def action(self, input_data: Optional[Any] = None) -> dict:
        url = input_data["url"]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_path = self.work_dir / f"efipem_{timestamp}.zip"

        self.logger.info(f"Descargando ZIP desde {url}")
        response = requests.get(url, timeout=300)
        response.raise_for_status()

        if not response.content:
            raise ValueError("La respuesta esta vacia")

        zip_path.write_bytes(response.content)
        self.logger.info(f"ZIP descargado ({len(response.content)} bytes): {zip_path}")

        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(self.work_dir)
        self.logger.info(f"ZIP extraido en {self.work_dir}")

        # Verificar que existan CSVs anuales
        matches = list(self.work_dir.glob(SOURCE_CSV_GLOB))
        if not matches:
            raise FileNotFoundError(f"No se encontraron CSVs con patron '{SOURCE_CSV_GLOB}' en {self.work_dir}")
        self.logger.info(f"CSVs anuales encontrados: {len(matches)}")

        return {"data_dir": str(self.work_dir), "zip_path": str(zip_path), "csv_count": len(matches)}

    # No limpia work_dir: los CSVs los consume Transform
    def finalization(self, input_data: Optional[Any] = None) -> dict:
        self.logger.info(f"Extraccion completa. {input_data['csv_count']} CSVs en {input_data['data_dir']}")
        return input_data
