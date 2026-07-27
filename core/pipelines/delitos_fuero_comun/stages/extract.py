import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import requests
from dotenv import set_key

from core.config import env_path
from core.pipelines.delitos_fuero_comun.config import PIPELINE_NAME, settings
from core.pipelines.delitos_fuero_comun.helpers.resolve_urls import resolve_urls
from core.pipelines.stage import Stage


class DelitosExtract(Stage):
    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "extract")
        self.mode = mode

    def source(self, input_data: Optional[Any] = None) -> dict:
        url_2026 = settings.URL_2026
        url_historico = settings.URL_HISTORICO

        resolved = resolve_urls()
        if resolved:
            url_2026 = resolved["url_2026"]
            url_historico = resolved["url_historico"]
            self._persist_urls(resolved)
        else:
            self.logger.warning(
                "No se resolvieron los links vigentes de SESNSP; usando los valores del .env como fallback"
            )

        if not url_2026:
            raise ValueError("URL_2026 no configurada")
        if self.mode == "bootstrap" and not url_historico:
            raise ValueError("URL_HISTORICO no configurada")
        self.logger.info(f"Modo: {self.mode}")
        return {
            "url_historico": url_historico if self.mode == "bootstrap" else None,
            "url_2026": url_2026,
        }

    def _persist_urls(self, resolved: dict[str, str]) -> None:
        env_file = env_path(PIPELINE_NAME)
        if resolved["url_2026"] != settings.URL_2026:
            set_key(env_file, "URL_2026", resolved["url_2026"])
            self.logger.info("URL_2026 actualizada en .env con el link vigente")
        if resolved["url_historico"] != settings.URL_HISTORICO:
            set_key(env_file, "URL_HISTORICO", resolved["url_historico"])
            self.logger.info("URL_HISTORICO actualizada en .env con el link vigente")

    def action(self, input_data: Optional[Any] = None) -> dict:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result: dict[str, Any] = {"csv_historico": None, "csv_2026": None, "zip_paths": []}

        if self.mode == "bootstrap":
            zip_hist = self.work_dir / f"historico_{timestamp}.zip"
            self._download(input_data["url_historico"], zip_hist)
            result["csv_historico"] = str(self._extract_csv(zip_hist, settings.CSV_HISTORICO))
            result["zip_paths"].append(str(zip_hist))

        zip_2026 = self.work_dir / f"2026_{timestamp}.zip"
        self._download(input_data["url_2026"], zip_2026)
        result["csv_2026"] = str(self._extract_csv(zip_2026, settings.CSV_2026))
        result["zip_paths"].append(str(zip_2026))

        return result

    def finalization(self, input_data: Optional[Any] = None) -> dict:
        for zip_path_str in input_data.get("zip_paths", []):
            p = Path(zip_path_str)
            if p.exists():
                p.unlink()
                self.logger.info(f"ZIP eliminado: {p}")
        return {k: v for k, v in input_data.items() if k != "zip_paths"}

    def _download(self, url: str, dest: Path) -> None:
        self.logger.info(f"Descargando desde {url}")
        response = requests.get(url, timeout=300)
        response.raise_for_status()
        dest.write_bytes(response.content)
        self.logger.info(f"Descargado: {dest} ({len(response.content):,} bytes)")

    def _extract_csv(self, zip_path: Path, csv_name: str) -> Path:
        with zipfile.ZipFile(zip_path, "r") as zf:
            members = zf.namelist()
            csv_members = [m for m in members if m.endswith(".csv")]
            if not csv_members:
                raise FileNotFoundError(f"No se encontró ningún .csv en el ZIP. Contenido: {members}")
            target = csv_name if csv_name in csv_members else csv_members[0]
            output_path = self.work_dir / Path(target).name
            output_path.write_bytes(zf.read(target))
            self.logger.info(f"CSV extraído: {output_path}")
        return output_path
