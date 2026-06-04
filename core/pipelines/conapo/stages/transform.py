from pathlib import Path
from typing import Any, Optional

import pandas as pd

from core.pipelines.conapo.attributes import ConapoTables as T
from core.pipelines.conapo.constants import (
    FLOAT_COLS_IDD,
    INT_COLS_GGE,
    INT_COLS_IDD,
    INT_COLS_PMA,
    NULL_VALUES,
    RENAME_COLS,
    SEXO_MAP,
)
from core.pipelines.stage import Stage
from core.utils.clean import list_values_to_null
from core.utils.logger import get_logger


class ConapoTransform(Stage):
    def __init__(self):
        super().__init__("conapo", "transform")
        self.logger = get_logger("conapo.transform")

    def source(self, input_data: Optional[Any] = None) -> dict[str, pd.DataFrame]:
        pkl_pma = Path("data/extract/conapo/pma.pkl")
        pkl_gge = Path("data/extract/conapo/gge.pkl")
        pkl_idd = Path("data/extract/conapo/idd.pkl")

        if pkl_pma.exists() and pkl_gge.exists() and pkl_idd.exists():
            self.logger.info("[source] Loading extract pkl files")
            return {
                "df_pma": pd.read_pickle(pkl_pma),
                "df_gge": pd.read_pickle(pkl_gge),
                "df_idd": pd.read_pickle(pkl_idd),
            }

        return input_data

    def _build_catalogs(self) -> dict:
        """Build catalog records for sexo."""
        sexo_records = [{"id": v, "sexo": k} for k, v in SEXO_MAP.items()]
        self.logger.info(f"[_build_catalogs] {len(sexo_records)} sexo records")
        return {T.CAT_SEXO: sexo_records}

    def _process_pma(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process poblacion mitad de ano data."""
        df = df.copy()

        # Convert numeric columns
        for col in INT_COLS_PMA:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

        # Convert fecha_actualizacion
        df["fecha_actualizacion"] = pd.to_datetime(df["fecha_actualizacion"])
        df = list_values_to_null(df, rm_list=NULL_VALUES)
        df["fecha_actualizacion"] = df["fecha_actualizacion"].dt.date

        # Map sexo to FK
        df["sexo_id"] = df["sexo"].map(SEXO_MAP)

        # Rename cve_mun to municipio_id
        df = df.rename(columns=RENAME_COLS)

        return df

    def _process_gge(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process grandes grupos de edad data."""
        df = df.copy()

        # Convert numeric columns
        for col in INT_COLS_GGE:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

        # Convert fecha_actualizacion
        df["fecha_actualizacion"] = pd.to_datetime(df["fecha_actualizacion"])
        df = list_values_to_null(df, rm_list=NULL_VALUES)
        df["fecha_actualizacion"] = df["fecha_actualizacion"].dt.date

        # Map sexo to FK
        df["sexo_id"] = df["sexo"].map(SEXO_MAP)

        # Rename cve_mun to municipio_id
        df = df.rename(columns=RENAME_COLS)

        return df

    def _process_idd(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process indicadores demograficos diversos data."""
        df = df.copy()

        # Convert int columns
        for col in INT_COLS_IDD:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

        # Convert float columns
        for col in FLOAT_COLS_IDD:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # Convert fecha_actualizacion
        df["fecha_actualizacion"] = pd.to_datetime(df["fecha_actualizacion"])
        df = list_values_to_null(df, rm_list=NULL_VALUES)
        df["fecha_actualizacion"] = df["fecha_actualizacion"].dt.date

        # Rename cve_mun to municipio_id
        df = df.rename(columns=RENAME_COLS)

        return df

    def action(self, input_data: dict[str, pd.DataFrame]) -> dict[str, Any]:
        df_pma = input_data["df_pma"]
        df_gge = input_data["df_gge"]
        df_idd = input_data["df_idd"]

        if df_pma.empty and df_gge.empty and df_idd.empty:
            self.logger.info("[action] Empty input, skipping transform")
            return {
                "df_pma": df_pma,
                "df_gge": df_gge,
                "df_idd": df_idd,
                "catalogs": {},
            }

        self.logger.info(f"[action] Processing {len(df_pma)} PMA, {len(df_gge)} GGE, {len(df_idd)} IDD rows")

        df_pma = self._process_pma(df_pma)
        df_gge = self._process_gge(df_gge)
        df_idd = self._process_idd(df_idd)
        catalogs = self._build_catalogs()

        self.logger.info(f"[action] Done: {len(df_pma)} PMA, {len(df_gge)} GGE, {len(df_idd)} IDD rows")
        return {
            "df_pma": df_pma,
            "df_gge": df_gge,
            "df_idd": df_idd,
            "catalogs": catalogs,
        }

    def finalization(self, input_data: dict[str, Any]) -> dict[str, Any]:
        input_data["df_pma"].to_pickle(self.work_dir / "pma.pkl")
        input_data["df_gge"].to_pickle(self.work_dir / "gge.pkl")
        input_data["df_idd"].to_pickle(self.work_dir / "idd.pkl")
        pd.to_pickle(input_data["catalogs"], self.work_dir / "catalogs.pkl")
        self.logger.info(
            f"[finalization] {len(input_data['df_pma'])} PMA, "
            f"{len(input_data['df_gge'])} GGE, "
            f"{len(input_data['df_idd'])} IDD rows saved"
        )
        return input_data
