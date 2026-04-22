import time
import pandas as pd
from datetime import datetime
from typing import Any, Optional

from selenium.webdriver.common.by import By

from core.db import Database
from core.pipelines.stage import Stage
from core.pipelines.denue.config import settings
from core.pipelines.denue.constants import ENTIDADES_MEXICO, RENAME_HEADER
from core.pipelines.denue.helpers.date_utils import parse_periodo
from core.pipelines.denue.helpers.file_processor import download_denue_csv
from core.pipelines.denue.helpers.web_driver import driver_configuration
from core.pipelines.denue.schemas import Actualizaciones
from core.utils.bulk_ops import get_last_update
from core.utils.logger import get_logger

PIPELINE_NAME = settings.PIPELINE_NAME


class DenueExtract(Stage):
    def __init__(self, mode: str = "bootstrap", start_date: str = None):
        super().__init__(PIPELINE_NAME, "extract")
        self.mode = mode
        self.logger = get_logger(f"{PIPELINE_NAME}.extract")
        raw_date = start_date or settings.BOOTSTRAP_START_DATE
        self.start_date = datetime.strptime(raw_date, "%d/%m/%Y").date()

    def _resolve_start_date(self):
        if self.mode != "update":
            return self.start_date
        db = Database(settings.DB_NAME, settings.database_url)
        db.connect()
        try:
            with db.get_session() as session:
                last_date = get_last_update(session, Actualizaciones, Actualizaciones.fecha_actualizacion.key)
        finally:
            db.disconnect()
        if last_date:
            self.logger.info(f"[source] Update mode: last actualizacion {last_date}")
            return last_date
        return self.start_date

    def source(self, input_data: Optional[Any] = None) -> list[dict]:
        pkl_path = self.work_dir / "denue_extracted.pkl"
        if pkl_path.exists():
            self.logger.info("[source] pkl found, skipping extract")
            return []

        start_date = self._resolve_start_date()
        self.logger.info(f"[source] Fetching URLs for all entidades after {start_date}")
        driver = driver_configuration(settings.DENUE_URL)
        all_urls = []

        try:
            for entidad in ENTIDADES_MEXICO:
                self.logger.info(f"[source] Scraping entidad {entidad}")
                elemento = driver.find_element(By.CSS_SELECTOR, f'a[data-valor="{entidad}"]')
                driver.execute_script("arguments[0].click();", elemento)
                time.sleep(5)

                table = driver.find_element(By.ID, "tblDescargaArchivos_denue")
                rows = table.find_elements(By.TAG_NAME, "tr")
                archivos_unicos = {}

                for row in rows:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) <= 1:
                        continue

                    periodo_date = parse_periodo(cells[1].text.strip())
                    if periodo_date is None:
                        continue

                    periodo = periodo_date.date()
                    if periodo <= start_date:
                        continue

                    for cell in cells:
                        for link in cell.find_elements(By.TAG_NAME, "a"):
                            href = link.get_attribute("href")
                            if href and "csv.zip" in href and href not in archivos_unicos:
                                archivos_unicos[href] = {
                                    "fecha_actualizacion": periodo,
                                    "url": href,
                                    "entidad_id": entidad,
                                }

                entidad_urls = list(archivos_unicos.values())
                self.logger.info(f"[source] Found {len(entidad_urls)} files for entidad {entidad}")
                all_urls.extend(entidad_urls)

        except Exception as e:
            driver.quit()
            raise e

        driver.quit()
        self.logger.info(f"[source] Total files found: {len(all_urls)}")
        return all_urls

    def action(self, input_data: list[dict]) -> pd.DataFrame:
        if not input_data:
            self.logger.info("[action] No URLs to download")
            return pd.DataFrame()

        self.logger.info(f"[action] Downloading {len(input_data)} files")
        columns_to_keep = list(RENAME_HEADER.keys())
        dfs = []

        for item in input_data:
            try:
                self.logger.info(f"[action] Downloading entidad {item['entidad_id']} - {item['fecha_actualizacion']}")
                df = download_denue_csv(item["url"])
                df = df.reindex(columns=columns_to_keep)
                df = df.rename(columns=RENAME_HEADER)
                df["fecha_actualizacion"] = item["fecha_actualizacion"]
                df["entidad_id"] = item["entidad_id"]
                dfs.append(df)
                self.logger.info(f"[action] {len(df)} rows extracted")
            except Exception as e:
                self.logger.warning(f"[action] Failed to download {item['url']}: {e}")
                continue

        if not dfs:
            return pd.DataFrame()

        result = pd.concat(dfs, ignore_index=True)
        self.logger.info(f"[action] {len(result)} total rows extracted")
        return result

    def finalization(self, input_data: pd.DataFrame) -> pd.DataFrame:
        if input_data.empty:
            self.logger.info("[finalization] No data, skipping save")
            return input_data
        pkl_path = self.work_dir / "denue_extracted.pkl"
        input_data.to_pickle(pkl_path)
        self.logger.info(f"[finalization] {len(input_data)} rows saved to {pkl_path}")
        return input_data
