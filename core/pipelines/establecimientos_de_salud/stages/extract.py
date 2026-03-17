import pandas as pd
import requests
from datetime import date
from pathlib import Path
from typing import Any, Optional

from core.db import Database
from core.pipelines.stage import Stage
from core.pipelines.establecimientos_de_salud.helpers import normalize_columns
from core.pipelines.establecimientos_de_salud.attributes.establecimientos import EstablecimientosColMap
from core.pipelines.establecimientos_de_salud.schemas import Establecimientos
from core.pipelines.establecimientos_de_salud.config import settings
from core.utils.logger import get_logger
from core.utils.bulk_ops import get_last_update
from core.utils.periods import next_month_period, generate_monthly_periods


class EstablecimientosExtract(Stage):
    def __init__(
        self,
        pipeline_name: str = "establecimientos_de_salud",
        mode: str = "bootstrap",
        year: int = None,
        month: int = 1,
    ):
        super().__init__(pipeline_name, "extract")
        self.mode = mode
        self.year = year
        self.month = month
        self.logger = get_logger(f"{pipeline_name}.extract")

    def _periods(self) -> list[tuple[int, int]]:
        today = (date.today().year, date.today().month)

        if self.mode == "bootstrap":
            end = (self.year, 12) if self.year and self.year < date.today().year else today
            return generate_monthly_periods((self.year, self.month), end)

        db = Database(settings.DB_NAME, settings.database_url)
        db.connect()
        with db.get_session() as session:
            self.logger.info(f"[periods] Fetching last update from database")
            last = get_last_update(session, Establecimientos, Establecimientos.fecha_actualizacion.key)
        db.disconnect()

        start = next_month_period(last.year, last.month) if last else today
        return generate_monthly_periods(start, today)

    def source(self, input_data: Optional[Any] = None) -> list[tuple[Path, int, int]]:
        self.logger.info(f"[source] Downloading files (mode={self.mode})")
        downloaded = []

        for year, month in self._periods():
            filename = f"ESTABLECIMIENTO_SALUD_{year}{str(month).zfill(2)}.xlsx"
            filepath = self.work_dir / filename

            if filepath.exists():
                self.logger.info(f"[source] Already exists, skipping download: {filename}")
                downloaded.append((filepath, year, month))
                continue

            url = settings.build_url(year, month)
            self.logger.info(f"[source] Downloading {filename}")

            try:
                response = requests.get(url, timeout=60)
                response.raise_for_status()
            except requests.HTTPError:
                self.logger.warning(f"[source] Not found url for year {year}, month {month}")
                continue
            except Exception as e:
                self.logger.warning(f"[source] Failed {url}: {e}")
                continue

            filepath.write_bytes(response.content)
            downloaded.append((filepath, year, month))

        self.logger.info(f"[source] {len(downloaded)} files ready")
        return downloaded

    def action(self, input_data: list[tuple[Path, int, int]]) -> pd.DataFrame:
        self.logger.info(f"[action] Reading {len(input_data)} files")
        expected_cols = EstablecimientosColMap.values()
        dfs = []

        for filepath, year, month in input_data:
            self.logger.info(f"[action] Reading {filepath.name}")
            df = pd.read_excel(filepath, engine="openpyxl")
            df = normalize_columns(df)
            df = df.reindex(columns=expected_cols)
            df[Establecimientos.fecha_actualizacion.key] = date(year, month, 1)
            dfs.append(df)

        return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

    def finalization(self, input_data: pd.DataFrame) -> pd.DataFrame:
        pkl_path = self.work_dir / f"establecimientos_{self.mode}.pkl"
        input_data.to_pickle(pkl_path)
        self.logger.info(f"[finalization] {len(input_data)} rows saved to {pkl_path}")
        return input_data
