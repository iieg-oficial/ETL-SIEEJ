from pathlib import Path
from typing import Any, Optional

import pandas as pd

from core.pipelines.stage import Stage
from core.pipelines.censos_economicos.config import settings
from core.pipelines.censos_economicos.constants import (
    CE_YEARS_CONFIG,
    CLASIFICADOR_TEXT_TO_ID,
    GEO_LEVEL_ESTATAL,
    GEO_LEVEL_MUNICIPAL,
    GEO_LEVEL_NACIONAL,
    GEO_RENAME_2019,
    GEO_RENAME_2024,
    NULL_VALUES,
    RENAME_COLS_BY_YEAR,
)
from core.utils import list_values_to_null
from core.utils.logger import get_logger

PIPELINE_NAME = settings.PIPELINE_NAME


def classify_geo(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    ent = df["entidad"].fillna("").astype(str).str.strip()
    mun = df["municipio"].fillna("").astype(str).str.strip()

    mask_mun = mun != ""
    mask_ent = (ent != "") & ~mask_mun
    mask_nac = ~mask_mun & ~mask_ent

    return df[mask_nac].copy(), df[mask_ent].copy(), df[mask_mun].copy()


def add_geo_ids(df_est: pd.DataFrame, df_mun: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    df_est = df_est.copy()
    df_est["cve_ent"] = pd.to_numeric(df_est["entidad"], errors="coerce").astype("Int64")
    df_est = df_est.drop(columns=["entidad", "municipio"])

    df_mun = df_mun.copy()
    df_mun["cve_ent"] = pd.to_numeric(df_mun["entidad"], errors="coerce").astype("Int64")
    df_mun["cve_mun"] = pd.to_numeric(df_mun["municipio"], errors="coerce").astype("Int64")
    df_mun = df_mun.drop(columns=["entidad", "municipio"])

    return df_est, df_mun


class CensosEconomicosTransformer(Stage):
    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "transform")
        self.logger = get_logger(f"{PIPELINE_NAME}.transform")

    def source(self, input_data: Optional[Any] = None) -> dict:
        extract_dir = Path(f"data/extract/{PIPELINE_NAME}")
        years_needed = list(CE_YEARS_CONFIG.keys())
        result = {}

        for year in years_needed:
            data_pkl = extract_dir / f"{year}_data.pkl"
            act_pkl = extract_dir / f"{year}_cat_actividad.pkl"

            if data_pkl.exists() and act_pkl.exists():
                self.logger.info(f"[source] Year {year}: loading from pkl")
                result[year] = {
                    "data": pd.read_pickle(data_pkl),
                    "cat_actividad": pd.read_pickle(act_pkl),
                }
            elif input_data and year in input_data:
                self.logger.info(f"[source] Year {year}: using extract output")
                result[year] = input_data[year]
            else:
                self.logger.warning(f"[source] Year {year}: no data found")

        return result

    def _cast_data_cols(self, df: pd.DataFrame, data_cols: list[str]) -> pd.DataFrame:
        for col in data_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        return df

    def _process_catalog_actividad(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df.columns = df.columns.str.lower()
        if "unnamed: 3" in df.columns:
            df = df.drop(columns=["unnamed: 3"])
        df = df.rename(columns={"desc_codigo": "descripcion"})
        df = df.dropna(subset=["descripcion"])
        df["clasificador_codigo"] = df["clasificador_codigo"].str.strip().str.lower().map(CLASIFICADOR_TEXT_TO_ID)
        df = df.dropna(subset=["clasificador_codigo"])
        df["clasificador_codigo"] = df["clasificador_codigo"].astype("Int64")
        return df

    def _process_year(self, year: int, raw: dict) -> dict:
        self.logger.info(f"[_process_year] Processing {year}")
        df = raw["data"].copy()

        df.columns = df.columns.str.lower()

        geo_rename = GEO_RENAME_2024 if year == 2024 else GEO_RENAME_2019
        if geo_rename:
            df = df.rename(columns=geo_rename)

        # Classify before list_values_to_null: mixed-type columns (int/str) are
        # corrupted by str.strip() inside list_values_to_null, turning ints to NaN.
        df_nac, df_est, df_mun = classify_geo(df)
        self.logger.info(f"[_process_year] {year}: nac={len(df_nac)}, est={len(df_est)}, mun={len(df_mun)}")

        df_nac = df_nac.drop(columns=["entidad", "municipio"])
        df_est, df_mun = add_geo_ids(df_est, df_mun)

        rename_cols = RENAME_COLS_BY_YEAR[year]
        data_cols = list(rename_cols.values())

        frames = {}
        for key, frame in [
            (GEO_LEVEL_NACIONAL, df_nac),
            (GEO_LEVEL_ESTATAL, df_est),
            (GEO_LEVEL_MUNICIPAL, df_mun),
        ]:
            frame = list_values_to_null(frame, rm_list=NULL_VALUES)
            frame = frame.rename(columns=rename_cols)
            self._cast_data_cols(frame, data_cols)
            frames[key] = frame

        cat_actividad = self._process_catalog_actividad(raw["cat_actividad"])

        return {
            GEO_LEVEL_NACIONAL: frames[GEO_LEVEL_NACIONAL],
            GEO_LEVEL_ESTATAL: frames[GEO_LEVEL_ESTATAL],
            GEO_LEVEL_MUNICIPAL: frames[GEO_LEVEL_MUNICIPAL],
            "cat_actividad": cat_actividad,
        }

    def action(self, input_data: dict) -> dict:
        if not input_data:
            self.logger.info("[action] No data to transform")
            return {}

        result = {}
        for year, raw in input_data.items():
            result[year] = self._process_year(year, raw)

        return result

    def finalization(self, input_data: dict) -> dict:
        if not input_data:
            self.logger.info("[finalization] Nothing to save")
            return input_data

        for year, year_data in input_data.items():
            for key, df in year_data.items():
                pkl_path = self.work_dir / f"{year}_{key}.pkl"
                df.to_pickle(pkl_path)
            self.logger.info(f"[finalization] Year {year} saved to {self.work_dir}")

        return input_data
