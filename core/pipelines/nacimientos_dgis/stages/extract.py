import io
import shutil
import zipfile
from pathlib import Path
from typing import Any, Optional

import pandas as pd

from core.pipelines.nacimientos_dgis.config import settings
from core.pipelines.nacimientos_dgis.constants import (
    CATALOG_DIR,
    CATALOG_EDITIONS,
    CATALOG_MEMBERS,
    CSV_SUFFIX,
    DOWNLOAD_TIMEOUT,
    MANIFEST_NAME,
    PIPELINE_NAME,
    USECOLS,
    XLSX_SUFFIX,
    ZIP_SUFFIX,
)
from core.pipelines.nacimientos_dgis.helpers.catalogs import read_catalog
from core.pipelines.stage import Stage
from core.utils.http import http_get
from core.utils.logger import get_logger

PARTIAL_SUFFIX = ".partial"


class NacimientosDgisExtract(Stage):
    """Baja el microdato del año y, por separado, el paquete de catálogos que le toca.

    DGIS publica los catálogos en su propio ZIP por rango de ediciones: no vienen
    dentro de `sinac_{year}.zip`, que sólo trae el CSV.
    """

    def __init__(self, year: int | None = None):
        super().__init__(PIPELINE_NAME, "extract")
        self.logger = get_logger(f"{PIPELINE_NAME}.extract")
        self.year = year

    # ------------------------------------------------------------------
    # Microdato
    # ------------------------------------------------------------------
    def _fetch_year(self, year: int) -> pd.DataFrame | None:
        url = settings.SOURCE_URL.format(year=year)
        self.logger.info(f"[source] Fetching {url}")
        response = http_get(url, timeout=DOWNLOAD_TIMEOUT)

        if response.status_code == 404:
            self.logger.info(f"[source] {year}: not available (404)")
            return None

        response.raise_for_status()

        csv_bytes = self._member_bytes(response.content, CSV_SUFFIX, url)
        # Las ediciones viejas no traen las 35 columnas; se pide lo que exista.
        available = self._available_columns(csv_bytes)
        df = pd.read_csv(io.BytesIO(csv_bytes), usecols=available, low_memory=False)

        missing = sorted(set(USECOLS) - set(available))
        if missing:
            self.logger.warning(f"[source] {year}: columnas ausentes en la fuente: {missing}")

        self.logger.info(f"[source] {year}: {len(df):,} rows, {len(df.columns)} columns")
        return df

    @staticmethod
    def _available_columns(csv_bytes: bytes) -> list[str]:
        header = pd.read_csv(io.BytesIO(csv_bytes), nrows=0)
        published = {str(column).strip().upper() for column in header.columns}
        return [column for column in USECOLS if column in published]

    def _member_bytes(self, zip_bytes: bytes, suffix: str, origin: str) -> bytes:
        """Contenido del primer miembro con ese sufijo, bajando por ZIPs anidados.

        Las ediciones viejas entregan el archivo directo; 2025 lo envuelve en un
        segundo ZIP dentro de una carpeta.
        """
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
            for name in archive.namelist():
                if name.lower().endswith(suffix):
                    return archive.read(name)
            for name in archive.namelist():
                if name.lower().endswith(ZIP_SUFFIX):
                    return self._member_bytes(archive.read(name), suffix, origin)
        raise ValueError(f"No se encontró ningún {suffix} en el archivo de {origin}")

    # ------------------------------------------------------------------
    # Catálogos
    # ------------------------------------------------------------------
    @staticmethod
    def catalog_package(year: int) -> str:
        """Paquete de catálogos que cubre a esa edición."""
        for start, end, package in CATALOG_EDITIONS:
            if start <= year <= end:
                return package
        # Un año más nuevo que los rangos conocidos usa el paquete más reciente.
        return CATALOG_EDITIONS[-1][2]

    def _catalog_archive(self, package: str) -> zipfile.ZipFile:
        url = settings.CATALOG_URL.format(package=package)
        self.logger.info(f"[source] Fetching {url}")
        response = http_get(url, timeout=DOWNLOAD_TIMEOUT)
        response.raise_for_status()

        payload = response.content
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            nested = [name for name in archive.namelist() if name.lower().endswith(ZIP_SUFFIX)]
            has_sheets = any(name.lower().endswith(XLSX_SUFFIX) for name in archive.namelist())
            if nested and not has_sheets:
                payload = archive.read(nested[0])

        return zipfile.ZipFile(io.BytesIO(payload))

    @staticmethod
    def _find_member(archive: zipfile.ZipFile, prefixes: tuple[str, ...]) -> str | None:
        """Los nombres se mueven entre ediciones, así que se busca por prefijo."""
        sheets = [name for name in archive.namelist() if name.lower().endswith(XLSX_SUFFIX)]
        for prefix in prefixes:
            for name in sheets:
                if Path(name).name.upper().startswith(prefix):
                    return name
        return None

    def _fetch_catalogs(self, package: str) -> None:
        """Baja y normaliza el paquete de catálogos, o lo toma del caché.

        Se escribe en un directorio aparte y se renombra al final: si la corrida
        muere a media descarga, el caché no queda a medias y la siguiente vuelve
        a intentarlo en vez de dar por buenos los catálogos que alcanzaron.
        """
        target = self.work_dir / CATALOG_DIR / package.removesuffix(ZIP_SUFFIX)
        if target.exists():
            self.logger.info(f"[source] {package}: ya en caché")
            return

        staging = target.with_name(f"{target.name}{PARTIAL_SUFFIX}")
        shutil.rmtree(staging, ignore_errors=True)
        staging.mkdir(parents=True)

        archive = self._catalog_archive(package)
        try:
            for table, prefixes in CATALOG_MEMBERS.items():
                member = self._find_member(archive, prefixes)
                if member is None:
                    self.logger.warning(f"[source] {package}: sin catálogo para {table}")
                    continue
                with archive.open(member) as handle:
                    read_catalog(handle).to_pickle(staging / f"{table}.pkl")
                self.logger.info(f"[source] {package}: {table} desde {Path(member).name}")
        finally:
            archive.close()

        staging.rename(target)

    # ------------------------------------------------------------------
    # Stage
    # ------------------------------------------------------------------
    def source(self, input_data: Optional[Any] = None) -> pd.DataFrame | None:
        self._fetch_catalogs(self.catalog_package(self.year))

        pkl = self.work_dir / f"sinac_{self.year}.pkl"
        if pkl.exists():
            self.logger.info(f"[source] {self.year}: loaded from cache ({pkl})")
            return pd.read_pickle(pkl)
        return self._fetch_year(self.year)

    def action(self, input_data: pd.DataFrame | None) -> pd.DataFrame | None:
        return input_data

    def finalization(self, input_data: pd.DataFrame | None) -> pd.DataFrame | None:
        if input_data is None or input_data.empty:
            return input_data

        pkl = self.work_dir / f"sinac_{self.year}.pkl"
        input_data.to_pickle(pkl)

        # El transform necesita saber qué paquete de catálogos le toca a cada año.
        manifest_path = self.work_dir / MANIFEST_NAME
        manifest = pd.read_pickle(manifest_path) if manifest_path.exists() else {}
        manifest[int(self.year)] = self.catalog_package(self.year).removesuffix(ZIP_SUFFIX)
        pd.to_pickle(manifest, manifest_path)

        self.logger.info(f"[finalization] {self.year}: {len(input_data):,} rows saved")
        return input_data
