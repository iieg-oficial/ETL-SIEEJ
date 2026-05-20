"""Extract stages para el pipeline asg_imss.

Define dos extractores:
    * `AsgImssCatalogExtractor` — descarga el diccionario XLSX (un sólo archivo).
    * `AsgImssDataExtractor` — descarga un CSV mensual por invocación.

Ambos usan `BROWSER_HEADERS` (IMSS bloquea User-Agents no estándar) y
soportan reintentos configurables. Para CSV se detecta encoding utf-8 con
fallback a latin-1.
"""

import calendar
import time
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Optional

import requests

from core.constants.http import BROWSER_HEADERS
from core.pipelines.asg_imss.config import PIPELINE_NAME, settings
from core.pipelines.stage import Stage


CATALOG_FILENAME = "diccionario_de_datos_1.xlsx"


def _last_day_of_month(year: int, month: int) -> date:
    return date(year, month, calendar.monthrange(year, month)[1])


def _previous_month_end() -> date:
    today = date.today()
    return today.replace(day=1) - timedelta(days=1)


def _generate_month_end_dates(start: date, end: date) -> list[date]:
    dates: list[date] = []
    year, month = start.year, start.month
    while date(year, month, 1) <= date(end.year, end.month, 1):
        dates.append(_last_day_of_month(year, month))
        month += 1
        if month > 12:
            month, year = 1, year + 1
    return dates


def compute_target_dates(mode: str) -> list[date]:
    """Devuelve la lista de fechas (último día de mes) a descargar.

    - bootstrap: rango [ASG_IMSS_DATA_START_DATE, ASG_IMSS_DATA_END_DATE].
      Si END está vacío usa el último mes cerrado (mes anterior al actual).
    - update: sólo el último mes cerrado.
    """
    end_str = settings.ASG_IMSS_DATA_END_DATE.strip()
    end_date = datetime.strptime(end_str, "%Y-%m-%d").date() if end_str else _previous_month_end()

    if mode == "update":
        return [_previous_month_end()]

    start_str = settings.ASG_IMSS_DATA_START_DATE.strip()
    start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
    return _generate_month_end_dates(start_date, end_date)


def _download_with_retries(url: str, dest: Path, logger, *, binary: bool) -> bytes | str:
    """Descarga con reintentos. Devuelve los bytes (binary=True) o texto decodificado."""
    last_exc: Exception | None = None
    for attempt in range(1, settings.MAX_RETRIES + 1):
        try:
            logger.info(f"Descargando intento {attempt}/{settings.MAX_RETRIES}: {url}")
            response = requests.get(url, headers=BROWSER_HEADERS, timeout=settings.TIMEOUT)
            response.raise_for_status()
            if not response.content:
                raise ValueError("Respuesta vacía")

            if binary:
                dest.write_bytes(response.content)
                logger.info(f"Guardado: {dest.name} ({len(response.content):,} bytes)")
                return response.content

            # CSV: intentar utf-8 y luego latin-1
            try:
                text = response.content.decode("utf-8")
            except UnicodeDecodeError:
                text = response.content.decode("latin-1")
            dest.write_text(text, encoding="utf-8")
            logger.info(f"Guardado: {dest.name} ({len(text):,} chars)")
            return text
        except Exception as exc:
            last_exc = exc
            logger.warning(f"Intento {attempt} fallido: {exc}")
            if attempt < settings.MAX_RETRIES:
                time.sleep(3)
    raise RuntimeError(f"Descarga fallida tras {settings.MAX_RETRIES} intentos: {last_exc}")


class AsgImssCatalogExtractor(Stage):
    """Descarga el XLSX del diccionario de datos publicado por IMSS."""

    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "extract")
        self.mode = mode

    def source(self, input_data: Optional[Any] = None) -> dict:
        url = settings.ASG_IMSS_CATALOG_URL
        file_path = self.work_dir / CATALOG_FILENAME
        self.logger.info(f"Catálogo XLSX: {url} → {file_path}")
        return {"url": url, "file_path": file_path}

    def action(self, input_data: Optional[Any] = None) -> dict:
        url = input_data["url"]
        file_path: Path = input_data["file_path"]
        _download_with_retries(url, file_path, self.logger, binary=True)
        return {"file_path": str(file_path)}

    def finalization(self, input_data: Optional[Any] = None) -> dict:
        self.logger.info(f"Extracción catálogo completada: {input_data['file_path']}")
        return input_data


class AsgImssDataExtractor(Stage):
    """Descarga un CSV mensual de asg_imss. Recibe `target_date` por invocación."""

    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "extract")
        self.mode = mode

    def source(self, input_data: Optional[Any] = None) -> dict:
        if not input_data or "target_date" not in input_data:
            raise ValueError("AsgImssDataExtractor requiere 'target_date' en input_data.")
        target_date: date = input_data["target_date"]
        date_str = target_date.strftime("%Y-%m-%d")
        url = settings.ASG_IMSS_DATA_URL.format(date=date_str)
        file_path = self.work_dir / f"asg-{date_str}.csv"
        return {"url": url, "file_path": file_path, "target_date": target_date}

    def action(self, input_data: Optional[Any] = None) -> dict:
        url = input_data["url"]
        file_path: Path = input_data["file_path"]
        target_date: date = input_data["target_date"]
        _download_with_retries(url, file_path, self.logger, binary=False)
        return {"file_path": str(file_path), "target_date": target_date}

    def finalization(self, input_data: Optional[Any] = None) -> dict:
        self.logger.info(f"Extracción {input_data['target_date']} completada: {input_data['file_path']}")
        return input_data
