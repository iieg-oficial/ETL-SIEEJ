import io
import zipfile
from datetime import date
from typing import Any, Optional

import pandas as pd
import requests
import urllib3

from core.pipelines.conapo.config import settings
from core.pipelines.conapo.constants import (
    RENAME_HEADER_GGE,
    RENAME_HEADER_IDD,
    RENAME_HEADER_PMA,
)
from core.pipelines.stage import Stage
from core.utils.logger import get_logger

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ConapoExtract(Stage):
    def __init__(self):
        super().__init__("conapo", "extract")
        self.logger = get_logger("conapo.extract")

    def _fetch_zip(self) -> zipfile.ZipFile:
        """Download and open the CONAPO ZIP file."""
        self.logger.info(f"[source] Fetching {settings.CONAPO_URL}")
        response = requests.get(settings.CONAPO_URL, verify=False, timeout=120)
        response.raise_for_status()
        return zipfile.ZipFile(io.BytesIO(response.content))

    def _read_excel_from_zip(self, z: zipfile.ZipFile, filename: str) -> pd.DataFrame:
        """Read an Excel file from the ZIP archive."""
        with z.open(filename) as f:
            return pd.read_excel(f)

    def _fetch_pma(self, z: zipfile.ZipFile) -> pd.DataFrame:
        """Fetch poblacion mitad de ano data."""
        self.logger.info("[source] Fetching poblacion mitad de ano")
        df = self._read_excel_from_zip(z, "14_Jalisco/1_Grupo_Quinq_14_JL.xlsx")
        df = df[list(RENAME_HEADER_PMA.keys())].rename(columns=RENAME_HEADER_PMA)
        df["fecha_actualizacion"] = date.today()
        self.logger.info(f"[source] PMA: {len(df)} rows")
        return df

    def _fetch_gge(self, z: zipfile.ZipFile) -> pd.DataFrame:
        """Fetch grandes grupos de edad data."""
        self.logger.info("[source] Fetching grandes grupos de edad")
        df = self._read_excel_from_zip(z, "14_Jalisco/2_Gran_Gedad_14_JL.xlsx")
        df = df[list(RENAME_HEADER_GGE.keys())].rename(columns=RENAME_HEADER_GGE)
        df["fecha_actualizacion"] = date.today()
        self.logger.info(f"[source] GGE: {len(df)} rows")
        return df

    def _fetch_idd(self, z: zipfile.ZipFile) -> pd.DataFrame:
        """Fetch indicadores demograficos diversos data."""
        self.logger.info("[source] Fetching indicadores demograficos diversos")
        df = self._read_excel_from_zip(z, "14_Jalisco/3_Indicadores_Dem_14_JL.xlsx")
        df = df[list(RENAME_HEADER_IDD.keys())].rename(columns=RENAME_HEADER_IDD)
        df["fecha_actualizacion"] = date.today()
        self.logger.info(f"[source] IDD: {len(df)} rows")
        return df

    def source(self, input_data: Optional[Any] = None) -> dict[str, pd.DataFrame]:
        pkl_pma = self.work_dir / "pma.pkl"
        pkl_gge = self.work_dir / "gge.pkl"
        pkl_idd = self.work_dir / "idd.pkl"

        if pkl_pma.exists() and pkl_gge.exists() and pkl_idd.exists():
            self.logger.info("[source] Loading cached files")
            return {
                "df_pma": pd.read_pickle(pkl_pma),
                "df_gge": pd.read_pickle(pkl_gge),
                "df_idd": pd.read_pickle(pkl_idd),
            }

        z = self._fetch_zip()
        return {
            "df_pma": self._fetch_pma(z),
            "df_gge": self._fetch_gge(z),
            "df_idd": self._fetch_idd(z),
        }

    def action(self, input_data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        return input_data

    def finalization(self, input_data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        input_data["df_pma"].to_pickle(self.work_dir / "pma.pkl")
        input_data["df_gge"].to_pickle(self.work_dir / "gge.pkl")
        input_data["df_idd"].to_pickle(self.work_dir / "idd.pkl")
        self.logger.info(
            f"[finalization] {len(input_data['df_pma'])} PMA, "
            f"{len(input_data['df_gge'])} GGE, "
            f"{len(input_data['df_idd'])} IDD rows saved"
        )
        return input_data
