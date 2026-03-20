import requests

from datetime import datetime
from typing import Any, Optional

from core.pipelines.repd.config import settings
from core.pipelines.repd.consts import PIPELINE_NAME
from core.pipelines.stage import Stage


class REPDExtractor(Stage):
    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "extract")
        self.mode = mode

    # Fuente de datos: URL de la API del REPD
    def source(self, input_data: Optional[Any] = None) -> dict:
        url = settings.REPD_DATA_URL
        self.logger.info(f"Fuente de datos: {url}")
        return {"url": url}

    # Descarga el archivo Excel desde la API
    def action(self, input_data: Optional[Any] = None) -> dict:
        url = input_data["url"]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"repd_{timestamp}.xls"
        output_path = self.work_dir / filename

        self.logger.info(f"Descargando datos desde {url}")
        response = requests.get(url, timeout=180)
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "")
        if not response.content:
            raise ValueError("La respuesta esta vacia")
        self.logger.info(f"Content-Type: {content_type}, size: {len(response.content)} bytes")

        output_path.write_bytes(response.content)
        self.logger.info(f"Archivo descargado: {output_path}")

        return {"file_path": str(output_path)}

    # No limpia work_dir porque el archivo sera consumido por Transform
    def finalization(self, input_data: Optional[Any] = None) -> dict:
        self.logger.info(f"Extraccion completa. Archivo: {input_data['file_path']}")
        return input_data
