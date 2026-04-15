import io
import zipfile
from datetime import date
from typing import Any, Optional

import pandas as pd
import requests
import urllib3

from core.pipelines.marginacion.config import settings
from core.pipelines.marginacion.constants import rename_localidad, rename_municipal
from core.pipelines.stage import Stage
from core.utils.logger import get_logger

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ENTIDAD_JALISCO = "14"
MUNICIPAL_HEADER_ROW = 5


class MarginacionExtract(Stage):
    def __init__(self, year: int):
        super().__init__("marginacion", "extract")
        self.year = year
        self.logger = get_logger("marginacion.extract")

    def _fetch_municipal(self) -> pd.DataFrame:
        url = settings.URL_MUNICIPAL.format(self.year)
        self.logger.info(f"[source] Fetching municipal {self.year}")
        response = requests.get(url, verify=False, timeout=60)
        response.raise_for_status()

        rename = rename_municipal(self.year)
        df = pd.read_excel(io.BytesIO(response.content), header=MUNICIPAL_HEADER_ROW)
        df = df.loc[:, ~df.columns.str.startswith("Unnamed")]
        df = df[list(rename.keys())].rename(columns=rename)
        df = df[df["entidad_id"].astype(str).str.strip() == ENTIDAD_JALISCO].copy()
        df["fecha_actualizacion"] = date(self.year, 1, 1)

        self.logger.info(f"[source] Municipal {self.year}: {len(df)} rows")
        return df

    def _fetch_localidad(self) -> pd.DataFrame:
        url = settings.URL_LOCALIDAD.format(self.year)
        self.logger.info(f"[source] Fetching localidad {self.year}")
        response = requests.get(url, verify=False, timeout=120)
        response.raise_for_status()

        rename = rename_localidad(self.year)
        dfs = []

        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            xls_name = next(n for n in z.namelist() if n.endswith(".xls"))
            xl = pd.ExcelFile(io.BytesIO(z.read(xls_name)))
            data_sheets = [s for s in xl.sheet_names if s != "Diccionario"]

            for sheet in data_sheets:
                df_sheet = pd.read_excel(xl, sheet_name=sheet, header=0)
                jalisco = df_sheet[df_sheet["ENT"].astype(str).str.strip() == ENTIDAD_JALISCO]
                jalisco = jalisco[jalisco["LOC"] != 9999].copy()
                if not jalisco.empty:
                    dfs.append(jalisco)

        if not dfs:
            self.logger.warning(f"[source] No Jalisco localidad rows found for {self.year}")
            return pd.DataFrame()

        df = pd.concat(dfs, ignore_index=True)
        df = df[list(rename.keys())].rename(columns=rename)
        df["fecha_actualizacion"] = date(self.year, 1, 1)

        self.logger.info(f"[source] Localidad {self.year}: {len(df)} rows")
        return df

    def source(self, input_data: Optional[Any] = None) -> dict[str, pd.DataFrame]:
        pkl_municipal = self.work_dir / f"municipal_{self.year}.pkl"
        pkl_localidad = self.work_dir / f"localidad_{self.year}.pkl"

        if pkl_municipal.exists() and pkl_localidad.exists():
            self.logger.info(f"[source] Loading cached files for {self.year}")
            return {
                "df_municipal": pd.read_pickle(pkl_municipal),
                "df_localidad": pd.read_pickle(pkl_localidad),
            }

        return {
            "df_municipal": self._fetch_municipal(),
            "df_localidad": self._fetch_localidad(),
        }

    def action(self, input_data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        return input_data

    def finalization(self, input_data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        input_data["df_municipal"].to_pickle(self.work_dir / f"municipal_{self.year}.pkl")
        input_data["df_localidad"].to_pickle(self.work_dir / f"localidad_{self.year}.pkl")
        self.logger.info(
            f"[finalization] {self.year}: {len(input_data['df_municipal'])} municipal, "
            f"{len(input_data['df_localidad'])} localidad rows saved"
        )
        return input_data
