from pathlib import Path
from typing import Any, Optional

import pandas as pd

from core.pipelines.stage import Stage
from core.pipelines.censos_economicos.constants import CE_YEARS_CONFIG, INEGI_STATE_SLUGS, PIPELINE_NAME
from core.utils.http import fetch_zip
from core.utils.logger import get_logger


def pkl_paths(work_dir: Path, year: int) -> dict:
    return {
        "data": work_dir / f"{year}_data.pkl",
        "cat_actividad": work_dir / f"{year}_cat_actividad.pkl",
        "cat_estrato": work_dir / f"{year}_cat_estrato.pkl",
    }


class CensosEconomicosExtractor(Stage):
    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "extract")
        self.logger = get_logger(f"{PIPELINE_NAME}.extract")

    def source(self, input_data: Optional[Any] = None) -> list[int]:
        years_to_process = []
        for year in CE_YEARS_CONFIG:
            paths = pkl_paths(self.work_dir, year)
            if all(p.exists() for p in paths.values()):
                self.logger.info(f"[source] Year {year}: pkl found, skipping")
            else:
                years_to_process.append(year)
        return years_to_process

    def action(self, input_data: list[int]) -> dict:
        if not input_data:
            self.logger.info("[action] All years cached, skipping download")
            return {}

        slugs = list(INEGI_STATE_SLUGS.values())
        result = {}

        for year in input_data:
            year_config = CE_YEARS_CONFIG[year]
            self.logger.info(f"[action] Processing year {year} with {len(slugs)} slugs")
            dfs = []
            cat_actividad = None
            cat_estrato = None

            for i, slug in enumerate(slugs):
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
                    dfs.append(df)
                    self.logger.info(f"[action] {len(df)} rows from {year}/{slug}")

                    if i == 0:
                        with z.open(year_config["catalog_actividad"]) as f:
                            cat_actividad = pd.read_csv(f, encoding="utf-8-sig", index_col=False)
                        with z.open(year_config["catalog_estrato"]) as f:
                            cat_estrato = pd.read_csv(f, encoding="utf-8-sig", index_col=False)
                        self.logger.info(f"[action] Catalogs loaded from {year}/{slug}")

            if not dfs:
                self.logger.warning(f"[action] No data for year {year}")
                continue

            result[year] = {
                "data": pd.concat(dfs, ignore_index=True),
                "cat_actividad": cat_actividad,
                "cat_estrato": cat_estrato,
            }
            self.logger.info(f"[action] Year {year}: {len(result[year]['data'])} rows total")

        return result

    def finalization(self, input_data: dict) -> dict:
        if not input_data:
            self.logger.info("[finalization] No new data to save")
            return input_data

        for year, year_data in input_data.items():
            paths = pkl_paths(self.work_dir, year)
            year_data["data"].to_pickle(paths["data"])
            year_data["cat_actividad"].to_pickle(paths["cat_actividad"])
            year_data["cat_estrato"].to_pickle(paths["cat_estrato"])
            self.logger.info(f"[finalization] Year {year} saved to {self.work_dir}")

        return input_data
