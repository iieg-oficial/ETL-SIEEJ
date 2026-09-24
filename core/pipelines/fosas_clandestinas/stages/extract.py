from datetime import date, datetime
from typing import Any, Optional
from urllib.parse import unquote, urljoin

import pandas as pd

from core.pipelines.fosas_clandestinas.config import settings
from core.pipelines.fosas_clandestinas.constants import (
    CUTOFF_RE,
    INDEX_DIR_RE,
    INDEX_ROW_RE,
    MONTHS,
    PDF_CONTENT_TYPE,
    PIPELINE_NAME,
    PUBLICACIONES_FILE,
    REGISTER_FILE_RE,
)
from core.pipelines.stage import Stage
from core.utils.http import http_get


def parse_cutoff(filename: str, folder_year: int, folder_month: int) -> date:
    """Cut-off month from the filename; falls back to the month before the upload folder."""
    match = CUTOFF_RE.search(filename.upper())
    if match:
        return date(int(match.group(2)), MONTHS[match.group(1)], 1)
    year, month = (folder_year, folder_month - 1) if folder_month > 1 else (folder_year - 1, 12)
    return date(year, month, 1)


def pick_per_cutoff(candidates: list[dict]) -> list[dict]:
    """One file per cut-off: the most recently uploaded wins, filename breaks ties."""
    ordered = sorted(candidates, key=lambda c: (c["fecha_corte"], c["modificado"], c["archivo"]))
    return list({c["fecha_corte"]: c for c in ordered}.values())


class FosasClandestinasExtract(Stage):
    def __init__(self, since: date | None = None):
        """since: last loaded cut-off; only newer cuts are fetched."""
        super().__init__(PIPELINE_NAME, "extract")
        self.since = since

    def _list(self, url: str) -> str:
        response = http_get(url, timeout=settings.HTTP_TIMEOUT)
        response.raise_for_status()
        return response.text

    def _discover(self) -> list[dict]:
        candidates = []
        years = [int(y) for y in INDEX_DIR_RE.findall(self._list(settings.UPLOADS_URL)) if len(y) == 4]
        for year in (y for y in years if y >= settings.FIRST_YEAR):
            year_url = urljoin(settings.UPLOADS_URL, f"{year}/")
            for month in (int(m) for m in INDEX_DIR_RE.findall(self._list(year_url))):
                month_url = urljoin(year_url, f"{month:02d}/")
                for href, modified in INDEX_ROW_RE.findall(self._list(month_url)):
                    filename = unquote(href)
                    if not REGISTER_FILE_RE.search(filename.upper()):
                        continue
                    candidates.append(
                        {
                            "fecha_corte": parse_cutoff(filename, year, month),
                            "archivo": filename,
                            "url": urljoin(month_url, href),
                            "modificado": datetime.strptime(modified, "%Y-%m-%d %H:%M"),
                        }
                    )
        self.logger.info(f"[source] {len(candidates)} register PDFs found in autoindex")
        return candidates

    def source(self, input_data: Optional[Any] = None) -> list[dict]:
        publicaciones = pick_per_cutoff(self._discover())
        if self.since:
            publicaciones = [p for p in publicaciones if p["fecha_corte"] > self.since]
        self.logger.info(f"[source] {len(publicaciones)} publications after {self.since}")
        return publicaciones

    def action(self, input_data: list[dict]) -> list[dict]:
        for pub in input_data:
            response = http_get(pub["url"], timeout=settings.HTTP_TIMEOUT)
            response.raise_for_status()
            content_type = response.headers.get("Content-Type", "")
            if not content_type.startswith(PDF_CONTENT_TYPE):
                raise ValueError(f"{pub['url']} returned {content_type!r}, expected {PDF_CONTENT_TYPE}")
            path = self.work_dir / f"{pub['fecha_corte']:%Y_%m}.pdf"
            path.write_bytes(response.content)
            pub["ruta"] = str(path)
            self.logger.info(f"[action] {pub['fecha_corte']:%Y-%m} <- {pub['archivo']}")
        return input_data

    def finalization(self, input_data: list[dict]) -> pd.DataFrame:
        df = pd.DataFrame(input_data)
        df.to_pickle(self.work_dir / PUBLICACIONES_FILE)
        self.logger.info(f"[finalization] {len(df)} publications downloaded")
        return df
