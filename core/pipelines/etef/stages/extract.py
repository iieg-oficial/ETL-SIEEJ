import requests
import zipfile

from datetime import datetime
from typing import Any, Optional

from core.pipelines.etef.config import settings
from core.pipelines.etef.consts import PIPELINE_NAME
from core.pipelines.stage import Stage


class EtefExtractor(Stage):
    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "extract")
        self.mode = mode

    def source(self, input_data: Optional[Any] = None) -> dict:
        url = settings.ETEF_SOURCE_URL
        self.logger.info(f"Fuente de datos: {url}")
        return {"url": url}

    def action(self, input_data: Optional[Any] = None) -> dict:
        url = input_data["url"]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"etef_{timestamp}.zip"
        zip_path = self.work_dir / zip_filename
        csv_filename = "eef_trimestral_tr_cifra_2007_2025.csv"
        csv_path = self.work_dir / csv_filename

        self.logger.info(f"Descargando ZIP desde {url}")
        response = requests.get(url, timeout=180)
        response.raise_for_status()

        if not response.content:
            raise ValueError("Respuesta vacía del servidor")

        self.logger.info(f"ZIP descargado: {len(response.content)} bytes")
        zip_path.write_bytes(response.content)

        # Extraer CSV del ZIP
        self.logger.info(f"Extrayendo CSV del ZIP")
        with zipfile.ZipFile(zip_path, "r") as zf:
            # Buscar el archivo CSV dentro del ZIP
            csv_files = [f for f in zf.namelist() if f.endswith(csv_filename)]
            if not csv_files:
                raise ValueError(f"No se encontró {csv_filename} en el ZIP")

            csv_content = zf.read(csv_files[0])
            csv_path.write_bytes(csv_content)

        self.logger.info(f"CSV extraído: {csv_path}")
        zip_path.unlink()  # Limpiar ZIP después de extraer

        return {"file_path": str(csv_path)}

    def finalization(self, input_data: Optional[Any] = None) -> dict:
        self.logger.info(f"Extracción completa. CSV: {input_data['file_path']}")
        return input_data
