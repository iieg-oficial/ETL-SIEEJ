import time
from pathlib import Path
from typing import Any, Optional

from sqlalchemy import select

from core.db import Database
from core.pipelines.stage import Stage
from core.pipelines.enoe_microdatos.config import settings
from core.pipelines.enoe_microdatos.helpers.downloader import download_sdem_coe, trimestres_range
from core.pipelines.enoe_microdatos.schemas import StgEnoeMicrodatos
from core.utils.logger import get_logger

PIPELINE_NAME = settings.PIPELINE_NAME


class EnoeMicrodatosExtract(Stage):
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
                    select(StgEnoeMicrodatos.anio, StgEnoeMicrodatos.trimestre)
                    .order_by(StgEnoeMicrodatos.anio.desc(), StgEnoeMicrodatos.trimestre.desc())
                    .limit(1)
                ).first()
        finally:
            db.disconnect()
        return (result.anio, result.trimestre) if result else None

    def _loaded_periods(self) -> set[tuple[int, int]]:
        db = Database(settings.DB_NAME, settings.database_url)
        db.connect()
        try:
            with db.get_session() as session:
                rows = session.execute(
                    select(StgEnoeMicrodatos.anio, StgEnoeMicrodatos.trimestre)
                    .group_by(StgEnoeMicrodatos.anio, StgEnoeMicrodatos.trimestre)
                ).all()
        finally:
            db.disconnect()
        return {(r.anio, r.trimestre) for r in rows}

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
        loaded = self._loaded_periods()

        for anio, trimestre in input_data:
            pkl_path = self.work_dir / f"enoe_microdatos_{anio}_{trimestre}.pkl"

            if pkl_path.exists():
                self.logger.info(f"[action] Already exists: {pkl_path.name}, skipping")
                saved.append(pkl_path)
                continue

            if (anio, trimestre) in loaded:
                self.logger.info(f"[action] {anio} T{trimestre} already in DB, skipping")
                continue

            url = settings.build_url(anio, trimestre)
            self.logger.info(f"[action] Downloading {anio} T{trimestre}")

            try:
                df = download_sdem_coe(url, anio, trimestre)
            except Exception as e:
                self.logger.warning(f"[action] Failed {anio} T{trimestre}: {e}")
                time.sleep(2)
                continue

            if df.empty:
                self.logger.warning(f"[action] No Jalisco rows for {anio} T{trimestre}, skipping")
                continue

            df.to_pickle(pkl_path)
            self.logger.info(f"[action] {len(df):,} Jalisco rows saved to {pkl_path.name}")
            saved.append(pkl_path)
            time.sleep(1)

        return saved

    def finalization(self, input_data: list[Path]) -> list[Path]:
        self.logger.info(f"[finalization] {len(input_data)} pkl files ready")
        return input_data
