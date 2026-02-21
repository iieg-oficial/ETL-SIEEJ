import os
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Optional

import requests

from core.pipelines.censos_economicos.config import settings
from core.pipelines.censos_economicos.consts import CE_YEARS_CONFIG, PIPELINE_NAME, RETRYABLE_STATUS_CODES
from core.pipelines.stage import Stage


class CEExtractor(Stage):
    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "extract")
        self.mode = mode

    def source(self, input_data: Optional[Any] = None) -> list[dict]:
        """Identifica ZIPs pendientes de descarga. Omite slugs ya extraidos."""
        downloads = []
        seen_masiva: set[tuple[str, str]] = set()  # (masiva_group, slug)

        for year in settings.years_list:
            year_config = CE_YEARS_CONFIG.get(year)
            if year_config is None:
                self.logger.warning(f"Sin configuracion para el anio censal {year}, omitiendo.")
                continue

            url_template = year_config["url_template"]
            data_csv_pattern = year_config["data_csv_pattern"]
            masiva_group = year_config.get("masiva_group")

            for key, slug in year_config["slugs"].items():
                if masiva_group:
                    slug_dir = self.work_dir / masiva_group / slug
                else:
                    slug_dir = self.work_dir / str(year) / slug

                expected_csv = slug_dir / data_csv_pattern.format(slug=slug)

                if expected_csv.exists():
                    self.logger.info(f"Omitiendo {year}/{slug} - ya extraido.")
                    continue

                # Evitar descargas duplicadas para anios masiva que comparten archivos
                if masiva_group:
                    if (masiva_group, slug) in seen_masiva:
                        continue
                    seen_masiva.add((masiva_group, slug))

                downloads.append(
                    {
                        "year": year,
                        "key": key,
                        "slug": slug,
                        "url": url_template.format(slug=slug),
                        "slug_dir": str(slug_dir),
                    }
                )

        self.logger.info(f"Se encontraron {len(downloads)} archivos ZIP por descargar.")
        return downloads

    def action(self, input_data: Optional[Any] = None) -> list[dict]:
        """Descarga y extrae ZIPs concurrentemente con reintentos."""
        downloads = input_data or []
        if not downloads:
            self.logger.info("Nada que descargar.")
            return downloads

        max_workers = settings.CE_DOWNLOAD_MAX_WORKERS
        self.logger.info(f"Descargando {len(downloads)} archivos ZIP con {max_workers} workers.")
        failures: list[dict] = []

        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            future_to_item = {pool.submit(self._download_one, item): item for item in downloads}

            for future in as_completed(future_to_item):
                item = future_to_item[future]
                try:
                    future.result()
                except Exception as e:
                    self.logger.error(f"Fallo despues de reintentos: {item['slug']} - {e}")
                    failures.append({"slug": item["slug"], "error": str(e)})

        if failures:
            slugs = ", ".join(f["slug"] for f in failures)
            raise RuntimeError(f"{len(failures)} descargas fallaron: {slugs}")

        self.logger.info(f"Los {len(downloads)} archivos se descargaron y extrajeron correctamente.")
        return downloads

    def finalization(self, input_data: Optional[Any] = None) -> dict:
        """Escanea directorios extraidos y construye inventario para la etapa Transform."""
        inventory: dict[str, dict] = {"years": {}}

        for year in settings.years_list:
            year_config = CE_YEARS_CONFIG.get(year)
            if year_config is None:
                continue

            year_entries = []
            data_csv_pattern = year_config["data_csv_pattern"]
            masiva_group = year_config.get("masiva_group")

            for key, slug in year_config["slugs"].items():
                if masiva_group:
                    slug_dir = self.work_dir / masiva_group / slug
                else:
                    slug_dir = self.work_dir / str(year) / slug

                data_csv = slug_dir / data_csv_pattern.format(slug=slug)

                if not data_csv.exists():
                    self.logger.warning(f"CSV de datos no encontrado para {year}/{slug}: {data_csv}")
                    continue

                catalog_paths = {}
                for catalog_key in ["catalog_actividad", "catalog_entidad_municipio", "catalog_estrato", "diccionario"]:
                    cat_rel_path = year_config.get(catalog_key)
                    if not cat_rel_path:
                        continue
                    cat_path = slug_dir / cat_rel_path.format(slug=slug)
                    if cat_path.exists():
                        catalog_paths[catalog_key] = str(cat_path)

                year_entries.append(
                    {
                        "year": year,
                        "key": key,
                        "slug": slug,
                        "slug_dir": str(slug_dir),
                        "data_csv": str(data_csv),
                        "catalogs": catalog_paths,
                        "url": year_config["url_template"].format(slug=slug),
                    }
                )

            inventory["years"][year] = year_entries
            self.logger.info(f"Anio {year}: {len(year_entries)} entradas de slug en el inventario.")

        return inventory

    def _download_one(self, item: dict) -> None:
        year = item["year"]
        slug = item["slug"]
        url = item["url"]
        slug_dir = item["slug_dir"]

        os.makedirs(slug_dir, exist_ok=True)
        zip_path = os.path.join(slug_dir, f"ce_{slug}_{year}.zip")

        max_retries = settings.CE_DOWNLOAD_MAX_RETRIES
        backoff = settings.CE_DOWNLOAD_RETRY_BACKOFF
        timeout = settings.CE_DOWNLOAD_TIMEOUT

        last_error: Exception | None = None
        for attempt in range(1, max_retries + 1):
            try:
                self.logger.info(f"[{slug}] Descargando (intento {attempt}/{max_retries})")
                response = requests.get(url, timeout=timeout, stream=True)

                if response.status_code in RETRYABLE_STATUS_CODES:
                    raise requests.RequestException(f"HTTP {response.status_code}")

                response.raise_for_status()

                with open(zip_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

                self.logger.info(f"[{slug}] Extrayendo")
                with zipfile.ZipFile(zip_path, "r") as zf:
                    zf.extractall(slug_dir)

                os.remove(zip_path)
                self.logger.info(f"[{slug}] Listo")
                return

            except (requests.RequestException, requests.ConnectionError, requests.Timeout) as e:
                last_error = e
                if attempt < max_retries:
                    wait = backoff * (2 ** (attempt - 1))
                    self.logger.warning(f"[{slug}] Intento {attempt} fallo: {e}. Reintentando en {wait}s.")
                    time.sleep(wait)
                    if os.path.exists(zip_path):
                        os.remove(zip_path)

            except zipfile.BadZipFile as e:
                last_error = e
                if os.path.exists(zip_path):
                    os.remove(zip_path)
                if attempt < max_retries:
                    wait = backoff * (2 ** (attempt - 1))
                    self.logger.warning(f"[{slug}] ZIP corrupto en intento {attempt}: {e}. Reintentando en {wait}s.")
                    time.sleep(wait)

        raise RuntimeError(f"[{slug}] Los {max_retries} intentos fallaron: {last_error}")
