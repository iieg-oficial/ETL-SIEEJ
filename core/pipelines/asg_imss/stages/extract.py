import calendar
import time
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Optional

import requests

from core.pipelines.asg_imss.config import settings
from core.constants.http import BROWSER_HEADERS
from core.pipelines.asg_imss.consts import CATALOG_DICT_FILENAME, CATALOG_DICT_URL, PIPELINE_NAME, SOURCE_URL_TEMPLATE
from core.pipelines.stage import Stage


def _last_day_of_month(year: int, month: int) -> date:
    last = calendar.monthrange(year, month)[1]
    return date(year, month, last)


def _previous_month_end() -> date:
    today = date.today()
    return today.replace(day=1) - timedelta(days=1)


def _generate_month_end_dates(start: date, end: date) -> list[date]:
    dates = []
    year, month = start.year, start.month
    while date(year, month, 1) <= date(end.year, end.month, 1):
        dates.append(_last_day_of_month(year, month))
        month += 1
        if month > 12:
            month = 1
            year += 1
    return dates


class AsgImssExtractor(Stage):
    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "extract")
        self.mode = mode

    def source(self, input_data: Optional[Any] = None) -> dict:
        end_date = _previous_month_end()

        if self.mode == "bootstrap":
            start_date = datetime.strptime(settings.ASG_START_DATE, "%Y-%m-%d").date()
            target_dates = _generate_month_end_dates(start_date, end_date)
        else:
            target_dates = [end_date]

        pending = []
        skipped = 0
        for d in target_dates:
            date_str = d.strftime("%Y-%m-%d")
            file_path = self.work_dir / f"asg-{date_str}.csv"
            url = SOURCE_URL_TEMPLATE.format(date=date_str)
            if file_path.exists():
                self.logger.info(f"Archivo ya existe, omitiendo: {file_path.name}")
                skipped += 1
            else:
                pending.append({"date": date_str, "url": url, "file_path": str(file_path)})

        self.logger.info(f"Fechas a descargar: {len(pending)} | Ya existentes: {skipped}")

        catalog_pending = None
        if self.mode == "bootstrap":
            catalog_path = self.work_dir / CATALOG_DICT_FILENAME
            if catalog_path.exists():
                self.logger.info(f"Diccionario de datos ya existe: {catalog_path.name}")
            else:
                catalog_pending = {"url": CATALOG_DICT_URL, "file_path": str(catalog_path)}
                self.logger.info(f"Diccionario de datos a descargar: {catalog_path.name}")

        return {"pending": pending, "skipped": skipped, "catalog_pending": catalog_pending}

    def action(self, input_data: Optional[Any] = None) -> dict:
        pending: list[dict] = input_data["pending"]
        catalog_pending: Optional[dict] = input_data.get("catalog_pending")
        downloaded = []
        failed = []

        # Download catalog dictionary Excel first (bootstrap only)
        catalog_file_path: Optional[str] = None
        if catalog_pending:
            url = catalog_pending["url"]
            file_path = Path(catalog_pending["file_path"])
            catalog_downloaded = False
            for attempt in range(1, settings.ASG_DOWNLOAD_MAX_RETRIES + 1):
                try:
                    self.logger.info(f"Descargando diccionario de datos (intento {attempt}): {url}")
                    response = requests.get(url, headers=BROWSER_HEADERS, timeout=settings.ASG_DOWNLOAD_TIMEOUT)
                    response.raise_for_status()
                    if not response.content:
                        raise ValueError("Respuesta vacía")
                    file_path.write_bytes(response.content)
                    self.logger.info(f"Diccionario guardado: {file_path.name} ({len(response.content):,} bytes)")
                    catalog_file_path = str(file_path)
                    catalog_downloaded = True
                    break
                except Exception as exc:
                    self.logger.warning(f"Intento {attempt} fallido para diccionario: {exc}")
                    if attempt < settings.ASG_DOWNLOAD_MAX_RETRIES:
                        time.sleep(3)
            if not catalog_downloaded:
                self.logger.error(
                    f"No se pudo descargar el diccionario de datos tras {settings.ASG_DOWNLOAD_MAX_RETRIES} intentos."
                )
        elif self.mode == "bootstrap":
            existing = self.work_dir / CATALOG_DICT_FILENAME
            if existing.exists():
                catalog_file_path = str(existing)
        for i, item in enumerate(pending):
            date_str = item["date"]
            url = item["url"]
            file_path = Path(item["file_path"])

            success = False
            for attempt in range(1, settings.ASG_DOWNLOAD_MAX_RETRIES + 1):
                try:
                    self.logger.info(
                        f"Descargando {date_str} (intento {attempt}/{settings.ASG_DOWNLOAD_MAX_RETRIES}): {url}"
                    )
                    response = requests.get(url, headers=BROWSER_HEADERS, timeout=settings.ASG_DOWNLOAD_TIMEOUT)
                    response.raise_for_status()

                    if not response.content:
                        raise ValueError("Respuesta vacía")

                    # Detectar encoding
                    try:
                        content = response.content.decode("utf-8")
                    except UnicodeDecodeError:
                        try:
                            content = response.content.decode("latin-1")
                        except UnicodeDecodeError:
                            content = response.content.decode("utf-8", errors="replace")

                    file_path.write_text(content, encoding="utf-8")
                    self.logger.info(f"Guardado: {file_path.name} ({len(content):,} chars)")
                    downloaded.append({"date": date_str, "file_path": str(file_path)})
                    success = True
                    break

                except Exception as exc:
                    self.logger.warning(f"Intento {attempt} fallido para {date_str}: {exc}")
                    if attempt < settings.ASG_DOWNLOAD_MAX_RETRIES:
                        time.sleep(3)

            if not success:
                self.logger.error(f"No se pudo descargar {date_str} tras {settings.ASG_DOWNLOAD_MAX_RETRIES} intentos.")
                failed.append(date_str)

            # Sleep entre descargas para no ser detectado como bot
            if i < len(pending) - 1:
                time.sleep(3)

        self.logger.info(f"Descargados: {len(downloaded)} | Fallidos: {len(failed)}")
        return {"downloaded": downloaded, "failed": failed, "catalog_file_path": catalog_file_path}

    def finalization(self, input_data: Optional[Any] = None) -> dict:
        downloaded = input_data.get("downloaded", [])
        failed = input_data.get("failed", [])
        self.logger.info(f"Extracción finalizada. Archivos descargados: {len(downloaded)} | Fallidos: {len(failed)}")
        return input_data
