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
        zip_path = self.work_dir / f"etef_{timestamp}.zip"
        csv_path = self.work_dir / f"etef_{timestamp}.csv"

        self.logger.info(f"Descargando ZIP desde {url}")
        response = requests.get(url, timeout=180)
        response.raise_for_status()

        if not response.content:
            raise ValueError("Respuesta vacía del servidor")

        self.logger.info(f"ZIP descargado: {len(response.content)} bytes")
        zip_path.write_bytes(response.content)

        # Detect CSV dynamically: prefer conjunto_de_datos/, fall back to any .csv
        self.logger.info("Extrayendo CSV del ZIP")
        with zipfile.ZipFile(zip_path, "r") as zf:
            names = zf.namelist()
            csv_files = [f for f in names if f.startswith("conjunto_de_datos/") and f.endswith(".csv")]
            if not csv_files:
                csv_files = [f for f in names if f.endswith(".csv")]
            if not csv_files:
                raise ValueError(f"No se encontró ningún CSV en el ZIP. Contenido: {names}")

            selected = csv_files[0]
            self.logger.info(f"CSV detectado en ZIP: {selected}")
            csv_path.write_bytes(zf.read(selected))

        zip_path.unlink()
        self.logger.info(f"CSV extraído: {csv_path}")
        return {"file_path": str(csv_path)}

    def finalization(self, input_data: Optional[Any] = None) -> dict:
        self.logger.info(f"Extracción completa. CSV: {input_data['file_path']}")
        return input_data
