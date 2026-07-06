from typing import Any, Optional

import pandas as pd

from core.pipelines.defunciones.config import settings
from core.pipelines.defunciones.constants import (
    CAPITULO_GRUPO_DATASET,
    CAPITULO_GRUPO_KEYWORD,
    EDAD_DATASET,
    EDAD_EXCLUDE,
    EDAD_KEYWORD,
    EDICION_DATASET,
    EDITION_COLUMN_ALIASES,
    ENTIDAD_JALISCO,
    FACT_DATASET,
    JALISCO_FILTER_COLUMN,
    PIPELINE_NAME,
)
from core.pipelines.defunciones.helpers.source import (
    discover_catalog_urls,
    discover_registro_urls,
    download_zip,
    edition_year,
    find_catalog_csv,
    find_registro_csv,
    latest_catalog_url,
    latest_registro_url,
    read_capitulo_grupo_csv,
    read_catalog_csv,
    read_registro_csv,
)
from core.pipelines.defunciones.schemas import CATALOG_MODELS, CODED_MODELS, VERSIONED_MODELS
from core.pipelines.stage import Stage
from core.utils.logger import get_logger


class DefuncionesExtract(Stage):
    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "extract")
        self.mode = mode
        self.logger = get_logger(f"{PIPELINE_NAME}.extract")

    def _extract_catalogs(self) -> dict[str, pd.DataFrame]:
        url = settings.CATALOG_URL or latest_catalog_url()
        self.logger.info("[source] Downloading catalog edition: %s", url)
        zip_bytes = download_zip(url)

        out: dict[str, pd.DataFrame] = {}
        member, raw = find_catalog_csv(zip_bytes, keyword=EDAD_KEYWORD, exclude=EDAD_EXCLUDE)
        out[EDAD_DATASET] = read_catalog_csv(raw, member)

        for model in CATALOG_MODELS:
            try:
                member, raw = find_catalog_csv(zip_bytes, keyword=model.keyword, exclude=model.exclude)
                out[model.__tablename__] = read_catalog_csv(raw, member)
            except (FileNotFoundError, ValueError) as error:
                name = model.__tablename__
                self.logger.warning("[source] catalog %s not found; skipping (%s)", name, error)

        for model in CODED_MODELS:
            member, raw = find_catalog_csv(zip_bytes, keyword=model.keyword, exclude=model.exclude)
            out[model.__tablename__] = read_catalog_csv(raw, member)

        member, raw = find_catalog_csv(zip_bytes, keyword=CAPITULO_GRUPO_KEYWORD)
        out[CAPITULO_GRUPO_DATASET] = read_capitulo_grupo_csv(raw, member)

        self.logger.info("[source] Extracted %s catalog datasets", len(out))
        return out

    def _catalog_edition_urls(self) -> list[str]:
        if settings.CATALOG_URL:
            return [settings.CATALOG_URL]
        if self.mode != "bootstrap":
            return [latest_catalog_url()]
        return [u for u in discover_catalog_urls() if edition_year(u) >= settings.BACKFILL_MIN_YEAR]

    def _extract_versioned(self) -> dict[str, pd.DataFrame]:
        urls = self._catalog_edition_urls()
        frames: dict[str, list[pd.DataFrame]] = {m.__tablename__: [] for m in VERSIONED_MODELS}
        years: list[int] = []
        for url in urls:
            year = edition_year(url)
            years.append(year)
            zip_bytes = download_zip(url)
            for model in VERSIONED_MODELS:
                try:
                    member, raw = find_catalog_csv(zip_bytes, keyword=model.keyword)
                    df = read_catalog_csv(raw, member)
                    df["edicion"] = year
                    frames[model.__tablename__].append(df)
                except (FileNotFoundError, ValueError) as error:
                    self.logger.warning("[source] versioned %s not found in %s (%s)", model.__tablename__, year, error)
        out: dict[str, pd.DataFrame] = {
            name: pd.concat(parts, ignore_index=True) for name, parts in frames.items() if parts
        }
        out[EDICION_DATASET] = pd.DataFrame({"anio": sorted(set(years))})
        self.logger.info("[source] Versioned catalogs from editions: %s", sorted(set(years)))
        return out

    def _registro_urls(self) -> list[str]:
        if settings.REGISTRO_URL:
            return [settings.REGISTRO_URL]
        if self.mode != "bootstrap":
            return [latest_registro_url()]
        urls = discover_registro_urls()
        return [u for u in urls if edition_year(u) >= settings.BACKFILL_MIN_YEAR]

    def _read_jalisco(self, url: str) -> pd.DataFrame:
        zip_bytes = download_zip(url)
        member, raw = find_registro_csv(zip_bytes)
        df = read_registro_csv(raw)
        df = df.rename(columns=EDITION_COLUMN_ALIASES)
        total = len(df)
        df = df[df[JALISCO_FILTER_COLUMN] == f"{ENTIDAD_JALISCO:02d}"].reset_index(drop=True)
        self.logger.info("[source] %s: Jalisco %s of %s rows", member, f"{len(df):,}", f"{total:,}")
        return df

    def _extract_registro(self) -> pd.DataFrame:
        cache_path = self.work_dir / f"{FACT_DATASET}.pkl"
        if cache_path.exists():
            self.logger.info("[source] Using cached registro: %s", cache_path)
            return pd.read_pickle(cache_path)

        urls = self._registro_urls()
        self.logger.info("[source] Downloading %s registro edition(s)", len(urls))
        frames = [self._read_jalisco(url) for url in urls]
        return pd.concat(frames, ignore_index=True)

    def source(self, input_data: Optional[Any] = None) -> dict[str, pd.DataFrame]:
        data = self._extract_catalogs()
        data.update(self._extract_versioned())
        data[FACT_DATASET] = self._extract_registro()
        return data

    def action(self, input_data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        if input_data[EDAD_DATASET].empty:
            raise ValueError("[action] edad catalog is empty; aborting extract")
        if input_data[FACT_DATASET].empty:
            raise ValueError("[action] registro is empty after filtering; aborting extract")
        self.logger.info(
            "[action] catalogs=%s registro rows=%s",
            len(input_data) - 1,
            f"{len(input_data[FACT_DATASET]):,}",
        )
        return input_data

    def finalization(self, input_data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        for name, df in input_data.items():
            path = self.work_dir / f"{name}.pkl"
            df.to_pickle(path)
            self.logger.info("[finalization] Saved %s", path)
        return input_data
