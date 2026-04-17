import io
import zipfile
from datetime import date
from typing import Any, Optional

ENTIDAD_JALISCO_ID = 14

import pandas as pd
import requests
import urllib3

from core.pipelines.marginacion.config import settings
from core.pipelines.marginacion.constants import rename_estatal, rename_localidad, rename_municipal
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

    def _fetch_municipal(self, refri_map: dict[int, float]) -> pd.DataFrame:
        url_template = settings.URL_MUNICIPAL_DP2 if self.year <= 2015 else settings.URL_MUNICIPAL
        url = url_template.format(self.year)
        self.logger.info(f"[source] Fetching municipal {self.year}")
        response = requests.get(url, verify=False, timeout=60)
        response.raise_for_status()

        rename = rename_municipal(self.year)
        df = pd.read_excel(io.BytesIO(response.content), header=MUNICIPAL_HEADER_ROW)
        lugar_nacional = df.iloc[:, 18]
        df = df.loc[:, ~df.columns.str.startswith("Unnamed")]
        df = df[list(rename.keys())].rename(columns=rename)
        df = df[df["entidad_id"].astype(str).str.strip() == ENTIDAD_JALISCO].copy()
        df["lugar_contexto_nacional"] = lugar_nacional[df.index]
        df["porc_viv_sin_refrigerador"] = (
            pd.to_numeric(df["municipio_id"], errors="coerce").map(refri_map) if refri_map else None
        )
        df["fecha_actualizacion"] = date(self.year, 1, 1)

        self.logger.info(f"[source] Municipal {self.year}: {len(df)} rows")
        return df

    def _fetch_localidad(self) -> pd.DataFrame:
        url = settings.URL_LOCALIDAD.format(self.year)
        self.logger.info(f"[source] Fetching localidad {self.year}")
        response = requests.get(url, verify=False, timeout=120)
        if response.status_code == 404:
            self.logger.warning(f"[source] Localidad {self.year} not available (404), skipping")
            return pd.DataFrame()
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

    def _fetch_estatal(self, refri_map: dict[int, float]) -> pd.DataFrame:
        if self.year == 2015:
            url = "https://conapo.segob.gob.mx/work/models/CONAPO/Datos_Abiertos/Entidad_Federativa/Base_Indice_de_marginacion_estatal_90-15.csv"
            self.logger.info(f"[source] Fetching estatal {self.year} (CSV historico)")
            response = requests.get(url, verify=False, timeout=60)
            response.raise_for_status()
            df = pd.read_csv(io.BytesIO(response.content), encoding="latin1")
            df = df[df["AÑO"] == self.year].copy()
        else:
            url_template = (
                "https://conapo.segob.gob.mx/work/models/CONAPO/Datos_Abiertos/Entidad_Federativa/IME_DP2_{}.xlsx"
                if self.year <= 2010
                else "https://conapo.segob.gob.mx/work/models/CONAPO/Datos_Abiertos/Entidad_Federativa/IME_{}.xls"
            )
            url = url_template.format(self.year)
            self.logger.info(f"[source] Fetching estatal {self.year}")
            response = requests.get(url, verify=False, timeout=60)
            response.raise_for_status()
            df = pd.read_excel(io.BytesIO(response.content), header=2)

        rename = rename_estatal(self.year)
        df = df[list(rename.keys())].rename(columns=rename)
        df = df[pd.to_numeric(df["entidad_id"], errors="coerce").notna()].copy()
        df["porc_viv_sin_refrigerador"] = (
            pd.to_numeric(df["entidad_id"], errors="coerce").astype("Int64").map(refri_map) if refri_map else None
        )
        df["fecha_actualizacion"] = date(self.year, 1, 1)
        self.logger.info(f"[source] Estatal {self.year}: {len(df)} rows")
        return df

    def _fetch_iter_refri(self) -> tuple[dict[int, float], dict[int, float]]:
        estatal_map: dict[int, float] = {}
        municipal_map: dict[int, float] = {}
        for state_id in range(1, 33):
            url = f"https://www.inegi.org.mx/contenidos/programas/ccpv/2020/microdatos/iter/iter_{state_id:02d}_2020_csv.zip"
            self.logger.info(f"[source] Fetching ITER state {state_id:02d}")
            try:
                response = requests.get(url, verify=False, timeout=120)
                response.raise_for_status()
                with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                    csv_name = next(n for n in z.namelist() if n.lower().endswith(".csv"))
                    df = pd.read_csv(io.BytesIO(z.read(csv_name)), encoding="latin1", low_memory=False)
                    df.columns = [c.replace("ï»¿", "").strip() for c in df.columns]
                    df["TVIVPARHAB"] = pd.to_numeric(df["TVIVPARHAB"], errors="coerce")
                    df["VPH_REFRI"] = pd.to_numeric(df["VPH_REFRI"], errors="coerce")

                    row = df[(df["MUN"] == 0) & (df["LOC"] == 0)]
                    if not row.empty:
                        tviv = row["TVIVPARHAB"].values[0]
                        refri = row["VPH_REFRI"].values[0]
                        estatal_map[state_id] = round((tviv - refri) / tviv * 100, 2) if tviv else None

                    municipios = df[(df["MUN"] != 0) & (df["LOC"] == 0)].copy()
                    municipios["municipio_id"] = state_id * 1000 + municipios["MUN"]
                    for _, mrow in municipios.iterrows():
                        tviv = mrow["TVIVPARHAB"]
                        refri = mrow["VPH_REFRI"]
                        mun_id = int(mrow["municipio_id"])
                        municipal_map[mun_id] = round((tviv - refri) / tviv * 100, 2) if tviv else None
            except Exception as e:
                self.logger.warning(f"[source] ITER state {state_id:02d} failed: {e}")
        return estatal_map, municipal_map

    def source(self, input_data: Optional[Any] = None) -> dict[str, pd.DataFrame]:
        pkl_municipal = self.work_dir / f"municipal_{self.year}.pkl"
        pkl_localidad = self.work_dir / f"localidad_{self.year}.pkl"

        pkl_estatal = self.work_dir / f"estatal_{self.year}.pkl"

        if pkl_municipal.exists() and pkl_localidad.exists() and pkl_estatal.exists():
            self.logger.info(f"[source] Loading cached files for {self.year}")
            return {
                "df_municipal": pd.read_pickle(pkl_municipal),
                "df_localidad": pd.read_pickle(pkl_localidad),
                "df_estatal": pd.read_pickle(pkl_estatal),
            }

        estatal_refri, municipal_refri = self._fetch_iter_refri() if self.year == 2020 else ({}, {})
        return {
            "df_municipal": self._fetch_municipal(municipal_refri),
            "df_localidad": self._fetch_localidad(),
            "df_estatal": self._fetch_estatal(estatal_refri),
        }

    def action(self, input_data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        return input_data

    def finalization(self, input_data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        input_data["df_municipal"].to_pickle(self.work_dir / f"municipal_{self.year}.pkl")
        input_data["df_localidad"].to_pickle(self.work_dir / f"localidad_{self.year}.pkl")
        input_data["df_estatal"].to_pickle(self.work_dir / f"estatal_{self.year}.pkl")
        self.logger.info(
            f"[finalization] {self.year}: {len(input_data['df_municipal'])} municipal, "
            f"{len(input_data['df_localidad'])} localidad, "
            f"{len(input_data['df_estatal'])} estatal rows saved"
        )
        return input_data
