from pathlib import Path
from typing import Any, Optional

import pandas as pd

from core.pipelines.stage import Stage
from core.pipelines.censos_economicos.constants import CE_YEARS_CONFIG, INEGI_STATE_SLUGS, PIPELINE_NAME
from core.utils.files import fetch_zip
from core.utils.logger import get_logger


def catalog_pkl_paths(work_dir: Path, year: int) -> dict:
    return {
        "cat_actividad": work_dir / f"{year}_cat_actividad.pkl",
        "cat_estrato": work_dir / f"{year}_cat_estrato.pkl",
    }


def entity_pkl_path(work_dir: Path, year: int, slug: str) -> Path:
    return work_dir / f"{year}_{slug}_data.pkl"


class CensosEconomicosExtractor(Stage):
    def __init__(self, mode: str = "bootstrap", slugs: Optional[list[str]] = None):
        super().__init__(PIPELINE_NAME, "extract")
        self.logger = get_logger(f"{PIPELINE_NAME}.extract")
        self._slugs = slugs

    def _target_slugs(self) -> list[str]:
        return self._slugs if self._slugs is not None else list(INEGI_STATE_SLUGS.values())

    def source(self, input_data: Optional[Any] = None) -> dict:
        target = self._target_slugs()
        result = {}

        for year in CE_YEARS_CONFIG:
            catalogs = catalog_pkl_paths(self.work_dir, year)
            catalogs_ok = all(p.exists() for p in catalogs.values())

            to_download = []
            cached = []
            for slug in target:
                ep = entity_pkl_path(self.work_dir, year, slug)
                if ep.exists() and catalogs_ok:
                    self.logger.info(f"[source] {year}/{slug}: cached")
                    cached.append(slug)
                else:
                    to_download.append(slug)

            result[year] = {"to_download": to_download, "cached": cached}

        return result

    def action(self, input_data: dict) -> dict:
        result = {}

        for year, info in input_data.items():
            to_download = info["to_download"]
            cached = info["cached"]
            year_config = CE_YEARS_CONFIG[year]
            catalogs = catalog_pkl_paths(self.work_dir, year)

            entity_data: dict[str, pd.DataFrame] = {}
            cat_actividad = None
            cat_estrato = None

            for slug in cached:
                entity_data[slug] = pd.read_pickle(entity_pkl_path(self.work_dir, year, slug))

            if all(p.exists() for p in catalogs.values()):
                cat_actividad = pd.read_pickle(catalogs["cat_actividad"])
                cat_estrato = pd.read_pickle(catalogs["cat_estrato"])

            for slug in to_download:
                url = year_config["url_template"].format(slug=slug)
                self.logger.info(f"[action] Downloading {year}/{slug}")

                try:
                    z = fetch_zip(url)
                except Exception as e:
                    self.logger.warning(f"[action] Failed {year}/{slug}: {e}")
                    continue

                with z:
                    data_csv = year_config["data_csv_pattern"].format(slug=slug)
                    with z.open(data_csv) as f:
                        df = pd.read_csv(f, encoding="utf-8-sig", index_col=False)
                    entity_data[slug] = df
                    self.logger.info(f"[action] {len(df)} rows from {year}/{slug}")

                    if cat_actividad is None:
                        with z.open(year_config["catalog_actividad"]) as f:
                            cat_actividad = pd.read_csv(f, encoding="utf-8-sig", index_col=False)
                        with z.open(year_config["catalog_estrato"]) as f:
                            cat_estrato = pd.read_csv(f, encoding="utf-8-sig", index_col=False)
                        self.logger.info(f"[action] Catalogs loaded from {year}/{slug}")

            if not entity_data:
                self.logger.warning(f"[action] No data for year {year}")
                continue

            result[year] = {
                "entity_data": entity_data,
                "to_save": to_download,
                "cat_actividad": cat_actividad,
                "cat_estrato": cat_estrato,
            }

        return result

    def finalization(self, input_data: dict) -> dict:
        output = {}

        for year, year_data in input_data.items():
            catalogs = catalog_pkl_paths(self.work_dir, year)

            if not all(p.exists() for p in catalogs.values()) and year_data["cat_actividad"] is not None:
                year_data["cat_actividad"].to_pickle(catalogs["cat_actividad"])
                year_data["cat_estrato"].to_pickle(catalogs["cat_estrato"])

            for slug in year_data.get("to_save", []):
                if slug in year_data["entity_data"]:
                    ep = entity_pkl_path(self.work_dir, year, slug)
                    year_data["entity_data"][slug].to_pickle(ep)

            dfs = list(year_data["entity_data"].values())
            if not dfs:
                continue

            output[year] = {
                "data": pd.concat(dfs, ignore_index=True),
                "cat_actividad": year_data["cat_actividad"],
            }
            self.logger.info(f"[finalization] Year {year}: {len(dfs)} entities ready")

        return output
