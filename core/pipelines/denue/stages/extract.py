import time
from datetime import datetime
from typing import Any, Optional

from selenium.webdriver.common.by import By

from core.pipelines.stage import Stage
from core.pipelines.denue.config import settings
from core.pipelines.denue.constants import RENAME_HEADER
from core.pipelines.denue.helpers.date_utils import parse_periodo, resolve_start_date
from core.pipelines.denue.helpers.file_processor import download_denue_csv
from core.pipelines.denue.helpers.scian import download_scian
from core.pipelines.denue.helpers.web_driver import driver_configuration
from core.utils.logger import get_logger

PIPELINE_NAME = settings.PIPELINE_NAME


class DenueExtract(Stage):
    def __init__(self, mode: str = "bootstrap", entidad: int = None, start_date: str = None):
        super().__init__(PIPELINE_NAME, "extract")
        self.mode = mode
        self.entidad = entidad
        self.logger = get_logger(f"{PIPELINE_NAME}.extract")
        raw_date = start_date or settings.BOOTSTRAP_START_DATE
        self.start_date = datetime.strptime(raw_date, "%d/%m/%Y").date()

    def source(self, input_data: Optional[Any] = None) -> list[dict]:
        download_scian(self.work_dir, settings.SCIAN_FILE_ID, settings.SCIAN_CSV_NAME)

        start_date = resolve_start_date(self.mode, self.start_date, settings.DB_NAME, settings.database_url)
        self.logger.info(f"[source] Scraping URLs for entidad {self.entidad} after {start_date}")
        driver = driver_configuration(settings.DENUE_URL)

        try:
            elemento = driver.find_element(By.CSS_SELECTOR, f'a[data-valor="{self.entidad}"]')
            driver.execute_script("arguments[0].click();", elemento)
            time.sleep(5)

            archivos_unicos = {}

            while True:
                table = driver.find_element(By.ID, "tblDescargaArchivos_denue")
                rows = table.find_elements(By.TAG_NAME, "tr")

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
                            if href and "csv.zip" in href:
                                if (
                                    href not in archivos_unicos
                                    or periodo > archivos_unicos[href]["fecha_actualizacion"]
                                ):
                                    archivos_unicos[href] = {
                                        "fecha_actualizacion": periodo,
                                        "url": href,
                                        "entidad_id": self.entidad,
                                    }

                next_btn = driver.find_elements(By.CSS_SELECTOR, "#tblDescargaArchivos_denue_next:not(.disabled)")
                if not next_btn:
                    break
                driver.execute_script("arguments[0].click();", next_btn[0])
                time.sleep(1)

            urls = list(archivos_unicos.values())
            self.logger.info(f"[source] Found {len(urls)} files for entidad {self.entidad}")
        except Exception as e:
            driver.quit()
            raise e

        driver.quit()
        return urls

    def action(self, input_data: list[dict]) -> list[str]:
        if not input_data:
            self.logger.info("[action] No URLs to download")
            return []

        self.logger.info(f"[action] Downloading {len(input_data)} files for entidad {self.entidad}")
        columns_to_keep = list(RENAME_HEADER.keys())
        saved = []

        for item in input_data:
            periodo_str = item["fecha_actualizacion"].strftime("%Y%m%d")
            pkl_path = self.work_dir / f"denue_{self.entidad}_{periodo_str}.pkl"

            if self.mode != "bootstrap" and pkl_path.exists():
                self.logger.info(f"[action] pkl exists for periodo {periodo_str}, skipping")
                saved.append(str(pkl_path))
                continue

            self.logger.info(
                f"[action] Downloading entidad {item['entidad_id']}, periodo: {item['fecha_actualizacion']}"
            )
            df = download_denue_csv(item["url"])
            df = df.reindex(columns=columns_to_keep)
            df = df.rename(columns=RENAME_HEADER)
            df["fecha_actualizacion"] = item["fecha_actualizacion"]
            df["entidad_id"] = item["entidad_id"]
            df.to_pickle(pkl_path)
            self.logger.info(f"[action] {len(df)} rows saved to {pkl_path.name}")
            saved.append(str(pkl_path))

        return saved

    def finalization(self, input_data: list[str]) -> list[str]:
        self.logger.info(f"[finalization] {len(input_data)} periodo files for entidad {self.entidad}")
        return input_data
