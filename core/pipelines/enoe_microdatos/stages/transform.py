import re
from pathlib import Path
from typing import Any, Optional

import pandas as pd

from core.pipelines.stage import Stage
from core.pipelines.enoe_microdatos.attributes import EnoeMicrodatosTables as T
from core.pipelines.enoe_microdatos.config import settings
from core.pipelines.enoe_microdatos.constants import FLOAT_COLS, INT_COLS, NULL_VALUES, RENAME_HEADER, TEXT_COLS
from core.pipelines.enoe_microdatos.mappings import Ocupacion, Sector, SituacionTrabajo
from core.utils.clean import list_values_to_null
from core.utils.logger import get_logger

PIPELINE_NAME = settings.PIPELINE_NAME
_PERIOD_RE = re.compile(r"enoe_microdatos_(\d{4})_(\d)\.pkl$")


class EnoeMicrodatosTransform(Stage):
    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "transform")
        self.mode = mode
        self.logger = get_logger(f"{PIPELINE_NAME}.transform")

    def source(self, input_data: Optional[Any] = None) -> list[Path]:
        extract_dir = Path(f"data/extract/{PIPELINE_NAME}")
        pkls = sorted(extract_dir.glob("enoe_microdatos_*.pkl"))
        if pkls:
            self.logger.info(f"[source] Found {len(pkls)} extract pkls")
            return pkls
        if isinstance(input_data, list):
            return input_data
        return []

    def _parse_period(self, pkl_path: Path) -> tuple[int, int]:
        m = _PERIOD_RE.search(pkl_path.name)
        if not m:
            raise ValueError(f"Cannot parse period from {pkl_path.name}")
        return int(m.group(1)), int(m.group(2))

    def _build_catalogs(self) -> dict:
        return {
            T.CAT_ENOE_SECTOR: Sector.to_records("descripcion"),
            T.CAT_ENOE_OCUPACION: Ocupacion.to_records("descripcion"),
            T.CAT_ENOE_SITUACION_TRABAJO: SituacionTrabajo.to_records("descripcion"),
        }

    def _transform(self, df: pd.DataFrame, anio: int, trimestre: int) -> pd.DataFrame:
        df = df.copy()

        for col in FLOAT_COLS:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        df = list_values_to_null(df, rm_list=NULL_VALUES)

        for col in INT_COLS:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

        df = df.rename(columns=RENAME_HEADER)

        df["anio"] = anio
        df["trimestre"] = trimestre

        # Indicadores derivados — INEGI TIL1
        df["es_pea"] = df["clase1"] == 1
        df["es_ocupado"] = df["clase2"] == 1
        df["es_desocupado"] = df["clase2"] == 2
        df["es_informal"] = (df["clase2"] == 1) & (df["tue_ppal"] == 1)

        return df

    def action(self, input_data: list[Path]) -> list[dict]:
        if not input_data:
            self.logger.info("[action] No extract pkls to transform")
            return []

        catalogs = self._build_catalogs()
        results: list[dict] = []

        for pkl_path in input_data:
            anio, trimestre = self._parse_period(pkl_path)
            df_pkl = self.work_dir / f"enoe_microdatos_{anio}_{trimestre}.pkl"
            cat_pkl = self.work_dir / f"catalogs_{anio}_{trimestre}.pkl"

            if self.mode != "bootstrap" and df_pkl.exists() and cat_pkl.exists():
                self.logger.info(f"[action] Already transformed {anio} T{trimestre}, skipping")
                results.append({"df_path": df_pkl, "catalogs_path": cat_pkl})
                continue

            df = pd.read_pickle(pkl_path)
            if df.empty:
                self.logger.info(f"[action] Empty df for {anio} T{trimestre}, skipping")
                continue

            self.logger.info(f"[action] Transforming {len(df):,} rows for {anio} T{trimestre}")
            df = self._transform(df, anio, trimestre)

            df.to_pickle(df_pkl)
            pd.Series(catalogs).to_pickle(cat_pkl)
            self.logger.info(f"[action] {len(df):,} rows saved to {df_pkl.name}")
            results.append({"df_path": df_pkl, "catalogs_path": cat_pkl})

        return results

    def finalization(self, input_data: list[dict]) -> list[dict]:
        self.logger.info(f"[finalization] {len(input_data)} periods transformed")
        return input_data
