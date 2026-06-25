from pathlib import Path
from typing import Any, Optional

from sqlalchemy import select

from core.db import Database
from core.pipelines.stage import Stage
from core.pipelines.enoe.config import settings
from core.pipelines.enoe.helpers.downloader import download_sdem, trimestres_range
from core.pipelines.enoe.schemas import StgEnoe
from core.utils.logger import get_logger

PIPELINE_NAME = settings.PIPELINE_NAME


class EnoeExtract(Stage):
    def __init__(self, mode: str = "bootstrap", start_year: int = None, start_trimestre: int = 1):
        super().__init__(PIPELINE_NAME, "extract")
        self.mode = mode
        self.start_year = start_year or settings.BOOTSTRAP_START_YEAR
        self.start_trimestre = start_trimestre
        self.logger = get_logger(f"{PIPELINE_NAME}.extract")

    def _last_period(self) -> tuple[int, int] | None:
        db = Database(settings.DB_NAME, settings.database_url)
        db.connect()
        try:
            with db.get_session() as session:
                result = session.execute(
                    select(StgEnoe.anio, StgEnoe.trimestre)
                    .order_by(StgEnoe.anio.desc(), StgEnoe.trimestre.desc())
                    .limit(1)
                ).first()
        finally:
            db.disconnect()
        return (result.anio, result.trimestre) if result else None

    def _periods(self) -> list[tuple[int, int]]:
        if self.mode == "bootstrap":
            return trimestres_range(self.start_year, self.start_trimestre)

        last = self._last_period()
        if last is None:
            return trimestres_range(self.start_year, self.start_trimestre)

        last_anio, last_t = last
        next_t = last_t + 1 if last_t < 4 else 1
        next_anio = last_anio if last_t < 4 else last_anio + 1
        return trimestres_range(next_anio, next_t)

    def source(self, input_data: Optional[Any] = None) -> list[tuple[int, int]]:
        periods = self._periods()
        self.logger.info(f"[source] {len(periods)} trimestres to process (mode={self.mode})")
        return periods

    def action(self, input_data: list[tuple[int, int]]) -> list[Path]:
        saved: list[Path] = []

        for anio, trimestre in input_data:
            pkl_path = self.work_dir / f"enoe_{anio}_{trimestre}.pkl"

            if pkl_path.exists():
                self.logger.info(f"[action] Already exists: {pkl_path.name}, skipping")
                saved.append(pkl_path)
                continue

            url = settings.build_url(anio, trimestre)
            url_alt = settings.build_url_alt(anio, trimestre)
            self.logger.info(f"[action] Downloading {anio} T{trimestre}")

            try:
                df = download_sdem(url, anio, trimestre, url_alt=url_alt)
            except Exception as e:
                self.logger.warning(f"[action] Failed {anio} T{trimestre}: {e}")
                continue

            if df.empty:
                self.logger.warning(f"[action] No Jalisco rows for {anio} T{trimestre}, skipping")
                continue

            df.to_pickle(pkl_path)
            self.logger.info(f"[action] {len(df):,} Jalisco rows saved to {pkl_path.name}")
            saved.append(pkl_path)

        return saved

    def finalization(self, input_data: list[Path]) -> list[Path]:
        self.logger.info(f"[finalization] {len(input_data)} pkl files ready")
        return input_data
