import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import requests

from core.pipelines.pobreza_multidimencional.config import settings
from core.pipelines.pobreza_multidimencional.consts import PIPELINE_NAME
from core.pipelines.stage import Stage

XLSX_FILENAME = "Concentrado_indicadores_de_pobreza_2020.xlsx"


class PobrezaMultidimencionalExtract(Stage):
    """Descarga el ZIP de CONEVAL y extrae el XLSX de indicadores municipales."""

    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "extract")
        self.mode = mode

    def source(self, input_data: Optional[Any] = None) -> dict:
        url = settings.POBREZA_MULTIDIMENCIONAL_SOURCE_URL
        if not url:
            raise ValueError("POBREZA_MULTIDIMENCIONAL_SOURCE_URL no configurada")
        self.logger.info(f"Fuente: {url}")
        return {"url": url}

    def action(self, input_data: Optional[Any] = None) -> dict:
        url = input_data["url"]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_path = self.work_dir / f"{PIPELINE_NAME}_{timestamp}.zip"

        self.logger.info(f"Descargando ZIP desde {url}")
        response = requests.get(url, timeout=180)
        response.raise_for_status()
        if not response.content:
            raise ValueError("Respuesta vacía al descargar el ZIP")

        zip_path.write_bytes(response.content)
        self.logger.info(f"ZIP descargado: {zip_path} ({len(response.content):,} bytes)")

        xlsx_path = self._extract_xlsx(zip_path)
        return {"file_path": str(xlsx_path), "zip_path": str(zip_path)}

    def finalization(self, input_data: Optional[Any] = None) -> dict:
        # Eliminar el ZIP para liberar espacio; el XLSX lo borra transform
        zip_path = Path(input_data.get("zip_path", ""))
        if zip_path.exists():
            zip_path.unlink()
            self.logger.info(f"ZIP eliminado: {zip_path}")
        self.logger.info(f"Extracción completa: {input_data['file_path']}")
        return input_data

    def _extract_xlsx(self, zip_path: Path) -> Path:
        """Extrae el XLSX del ZIP y lo guarda en work_dir."""
        with zipfile.ZipFile(zip_path, "r") as zf:
            members = zf.namelist()
            xlsx_members = [m for m in members if m.endswith(".xlsx")]
            if not xlsx_members:
                raise FileNotFoundError(
                    f"No se encontró ningún .xlsx en el ZIP. Contenido: {members}"
                )
            # Preferir el archivo esperado; si no, tomar el primero
            target = XLSX_FILENAME if XLSX_FILENAME in xlsx_members else xlsx_members[0]
            output_path = self.work_dir / target
            output_path.write_bytes(zf.read(target))
            self.logger.info(f"XLSX extraído: {output_path}")
        return output_path
