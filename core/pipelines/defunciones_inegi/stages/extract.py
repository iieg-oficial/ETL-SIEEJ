import zipfile
from pathlib import Path
from typing import Any, Optional

import pandas as pd

from core.pipelines.defunciones_inegi.attributes import DefuncionesInegiTables as T
from core.pipelines.defunciones_inegi.constants import (
    CATALOG_DIR,
    CATALOG_MEMBER_DIR,
    CODIGO_ADICIONAL_ALIAS,
    EMBEDDED_CATALOG_TABLES,
    MANIFEST_NAME,
    PIPELINE_NAME,
)
from core.pipelines.defunciones_inegi.helpers.source import (
    available_editions,
    catalog_aliases,
    download_edition,
    find_member,
    read_catalog_csv,
)
from core.pipelines.stage import Stage
from core.utils.logger import get_logger


class DefuncionesInegiExtract(Stage):
    """Descarga las ediciones EDR y separa catálogos de hechos.

    El CSV de hechos pesa cientos de MB por edición, así que aquí sólo se deja
    el ZIP en disco: quien lo recorre por lotes es el transform.
    """

    def __init__(self, mode: str = "bootstrap", since_year: int | None = None):
        super().__init__(PIPELINE_NAME, "extract")
        self.mode = mode
        self.since_year = since_year
        self.logger = get_logger(f"{PIPELINE_NAME}.extract")

    def source(self, input_data: Optional[Any] = None) -> dict[int, str]:
        editions = available_editions(since_year=self.since_year)
        if not editions:
            self.logger.warning("[source] No hay ediciones nuevas por descargar")
        return editions

    def action(self, input_data: dict[int, str]) -> dict[str, Any]:
        zip_paths = {year: download_edition(year, url, self.work_dir) for year, url in input_data.items()}
        catalogs = {year: self._extract_catalogs(path) for year, path in zip_paths.items()}
        return {"zip_paths": zip_paths, "catalogs": catalogs}

    def _extract_catalogs(self, zip_path: Path) -> dict[str, pd.DataFrame]:
        """Cada edición publica sólo los catálogos de las variables que trae."""
        found: dict[str, pd.DataFrame] = {}
        with zipfile.ZipFile(zip_path) as archive:
            wanted = {
                str(table): catalog_aliases(table) for table in T.catalogs() if table not in EMBEDDED_CATALOG_TABLES
            }
            wanted[CODIGO_ADICIONAL_ALIAS] = (CODIGO_ADICIONAL_ALIAS,)

            for name, aliases in wanted.items():
                member = find_member(archive, CATALOG_MEMBER_DIR, aliases)
                if member is not None:
                    found[name] = read_catalog_csv(archive, member)

        missing = sorted(str(t) for t in T.catalogs() if str(t) not in found and t not in EMBEDDED_CATALOG_TABLES)
        self.logger.info(f"[action] {zip_path.name}: {len(found)} catálogos; no publicados: {missing or 'ninguno'}")
        return found

    def finalization(self, input_data: dict[str, Any]) -> dict[str, Any]:
        for year, catalogs in input_data["catalogs"].items():
            edition_dir = self.work_dir / CATALOG_DIR / str(year)
            edition_dir.mkdir(parents=True, exist_ok=True)
            for name, df in catalogs.items():
                df.to_pickle(edition_dir / f"{name}.pkl")

        manifest = pd.Series({year: str(path) for year, path in input_data["zip_paths"].items()})
        manifest.to_pickle(self.work_dir / MANIFEST_NAME)
        self.logger.info(f"[finalization] {len(manifest)} ediciones listas en {self.work_dir}")
        return {"editions": sorted(input_data["zip_paths"])}
