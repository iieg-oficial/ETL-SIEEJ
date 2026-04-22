import zipfile

from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import requests

from core.pipelines.efipem.config import settings
from core.pipelines.efipem.consts import PIPELINE_NAME, SOURCE_CSV_GLOB
from core.pipelines.stage import Stage


class EfipemExtractor(Stage):
    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "extract")
        self.mode = mode

    # Fuente de datos: URL del ZIP de EFIPEM trimestral (INEGI)
    def source(self, input_data: Optional[Any] = None) -> dict:
        url = settings.EFIPEM_SOURCE_URL
        self.logger.info(f"Fuente de datos: {url}")
        return {"url": url}

    # Descarga el ZIP y extrae el CSV de cifras
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

        # Extraer ZIP en work_dir
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(self.work_dir)
        self.logger.info(f"ZIP extraido en {self.work_dir}")

        # Localizar el CSV de cifras
        matches = list(self.work_dir.glob(SOURCE_CSV_GLOB))
        if not matches:
            raise FileNotFoundError(f"No se encontro CSV con patron '{SOURCE_CSV_GLOB}' en {self.work_dir}")
        csv_path: Path = matches[0]
        self.logger.info(f"CSV fuente: {csv_path}")

        return {"file_path": str(csv_path), "zip_path": str(zip_path)}

    # No limpia work_dir: el CSV lo consume Transform
    def finalization(self, input_data: Optional[Any] = None) -> dict:
        self.logger.info(f"Extraccion completa. Archivo: {input_data['file_path']}")
        return input_data
