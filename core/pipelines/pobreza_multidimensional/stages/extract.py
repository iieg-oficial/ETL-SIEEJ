import zipfile
from typing import Any, Optional

import requests

from core.pipelines.pobreza_multidimensional.config import settings
from core.pipelines.pobreza_multidimensional.consts import (
    DATA_YEARS,
    PIPELINE_NAME,
)
from core.pipelines.stage import Stage


class PobrezaMultidimensionalExtract(Stage):
    """Descarga el ZIP de CONEVAL y extrae el CSV de la Base final."""

    def __init__(self, year: int):
        super().__init__(PIPELINE_NAME, "extract")
        if year not in DATA_YEARS:
            raise ValueError(f"Año {year} no válido. Válidos: {DATA_YEARS}")
        self.year = year

    def source(self, input_data: Optional[Any] = None) -> dict:
        url = settings.SOURCE_URL_TEMPLATE.format(year=self.year)
        self.logger.info(f"Fuente ZIP: {url}")
        return {"url": url, "year": self.year}

    def action(self, input_data: Optional[Any] = None) -> dict:
        url = input_data["url"]
        year = input_data["year"]

        zip_path = self.work_dir / f"Python_MMP_{year}.zip"

        # Descarga del ZIP
        self.logger.info(f"Descargando ZIP para año {year}...")
        response = requests.get(url, timeout=300)
        response.raise_for_status()
        if not response.content:
            raise ValueError(f"Respuesta vacía al descargar {url}")

        zip_path.write_bytes(response.content)
        self.logger.info(f"ZIP descargado: {zip_path} ({zip_path.stat().st_size:,} bytes)")

        # Búsqueda y extracción del CSV dentro del ZIP
        # Estructura real del ZIP: "Base final/pobreza{YY}.csv"
        csv_output = self.work_dir / f"pobreza_multidimensional_{year}.csv"

        with zipfile.ZipFile(zip_path) as zf:
            csv_entries = [n for n in zf.namelist() if n.lower().endswith(".csv") and "base final" in n.lower()]
            if not csv_entries:
                raise FileNotFoundError(
                    f"No se encontró CSV en 'Base final/' dentro del ZIP. Entradas disponibles: {zf.namelist()[:20]}"
                )
            csv_entry = csv_entries[0]
            self.logger.info(f"CSV encontrado en ZIP: {csv_entry}")
            with zf.open(csv_entry) as src:
                csv_output.write_bytes(src.read())

        # Borrar el ZIP tras extraer
        zip_path.unlink()
        self.logger.info(f"ZIP eliminado: {zip_path}")

        return {"file_path": str(csv_output), "year": year}

    def finalization(self, input_data: Optional[Any] = None) -> dict:
        self.logger.info(f"Extracción completada: {input_data['file_path']}")
        return input_data
