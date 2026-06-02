from typing import Any, Optional

import pandas as pd

from core.pipelines.stage import Stage
from core.pipelines.denue.attributes import DenueTables as T
from core.pipelines.denue.config import settings
from core.pipelines.denue.constants import NULL_VALUES, TITLE_COLS, DATE_COLS
from core.pipelines.denue.mappings import RANGO_PERSONAL_MAP, TIPO_ESTABLECIMIENTO_MAP, get_sector_codigo
from core.pipelines.denue.helpers.scian import load_scian_lookups
from core.utils import df_to_records
from core.utils.clean import list_values_to_null
from core.utils.logger import get_logger
from core.utils.normalize import title_col

PIPELINE_NAME = settings.PIPELINE_NAME


class DenueTransform(Stage):
    def __init__(self, mode: str = "bootstrap", entidad: int = None):
        super().__init__(PIPELINE_NAME, "transform")
        self.mode = mode
        self.entidad = entidad
        self.logger = get_logger(f"{PIPELINE_NAME}.transform")
        self.scian_lookups = None

    def source(self, input_data: Optional[Any] = None) -> pd.DataFrame:
        extract_dir = self.work_dir.parents[1] / "extract" / PIPELINE_NAME
        pkl_path = extract_dir / f"denue_extracted_{self.entidad}.pkl"
        self.logger.info(f"[source] Checking for pkl at {pkl_path}")
        if pkl_path.exists():
            self.logger.info("[source] Loading from pkl")
            return pd.read_pickle(pkl_path)
        self.logger.info("[source] pkl not found, using extract output")
        return input_data

    def _build_catalogs(self, df: pd.DataFrame) -> dict:
        self.logger.info(f"[_build_catalogs] Building catalogs from {len(df)} rows")

        actualizaciones = df_to_records(
            df.drop_duplicates(subset=["fecha_actualizacion"]).dropna(subset=["fecha_actualizacion"]),
            ["fecha_actualizacion"],
        )
        self.logger.info(f"[_build_catalogs] {len(actualizaciones)} unique actualizaciones")

        localidades_df = df.drop_duplicates(subset=["localidad_id", "cve_mun", "entidad_id"]).dropna(
            subset=["localidad_id", "cve_mun", "entidad_id"]
        )
        localidades_df = localidades_df.copy()
        localidades_df["cve_geo_id"] = (
            localidades_df["entidad_id"].astype(int) * 10_000_000
            + localidades_df["cve_mun"].astype(int) * 10_000
            + localidades_df["localidad_id"].astype(int)
        )
        localidades = (
            localidades_df[["cve_geo_id", "localidad_id", "entidad_id", "cve_mun", "localidad"]]
            .rename(columns={"cve_mun": "municipio_id"})
            .astype({"cve_geo_id": int, "localidad_id": int, "municipio_id": int, "entidad_id": int})
            .to_dict("records")
        )
        self.logger.info(f"[_build_catalogs] {len(localidades)} unique localidades")

        codigos = df["codigo_actividad"].dropna().astype(int).astype(str).unique()

        sectores_set = {}
        subsectores_set = {}
        ramas_set = {}
        subramas_set = {}
        clases_set = {}

        for codigo in codigos:
            if len(codigo) < 6:
                continue

            sector_cod = get_sector_codigo(codigo)
            subsector_cod = codigo[:3]
            rama_cod = codigo[:4]
            subrama_cod = codigo[:5]

            if sector_cod not in sectores_set and sector_cod in self.scian_lookups["sector"]:
                sectores_set[sector_cod] = {"codigo": sector_cod, "sector": self.scian_lookups["sector"][sector_cod]}

            if subsector_cod not in subsectores_set and subsector_cod in self.scian_lookups["subsector"]:
                subsectores_set[subsector_cod] = {
                    "codigo": subsector_cod,
                    "subsector": self.scian_lookups["subsector"][subsector_cod],
                }

            if rama_cod not in ramas_set and rama_cod in self.scian_lookups["rama"]:
                ramas_set[rama_cod] = {"codigo": rama_cod, "rama": self.scian_lookups["rama"][rama_cod]}

            if subrama_cod not in subramas_set and subrama_cod in self.scian_lookups["subrama"]:
                subramas_set[subrama_cod] = {
                    "codigo": subrama_cod,
                    "subrama": self.scian_lookups["subrama"][subrama_cod],
                }

            if codigo not in clases_set and codigo in self.scian_lookups["clase"]:
                clases_set[codigo] = {"codigo": codigo, "clase": self.scian_lookups["clase"][codigo]}

        self.logger.info(
            f"[_build_catalogs] SCIAN: {len(sectores_set)} sectores, {len(subsectores_set)} subsectores, "
            f"{len(ramas_set)} ramas, {len(subramas_set)} subramas, {len(clases_set)} clases"
        )

        return {
            T.CAT_ACTUALIZACIONES: actualizaciones,
            T.CAT_LOCALIDADES: localidades,
            T.CAT_SECTORES: list(sectores_set.values()),
            T.CAT_SUBSECTORES: list(subsectores_set.values()),
            T.CAT_RAMAS: list(ramas_set.values()),
            T.CAT_SUBRAMAS: list(subramas_set.values()),
            T.CAT_CLASES_ACTIVIDAD: list(clases_set.values()),
        }

    def action(self, input_data: pd.DataFrame) -> Any:
        if input_data.empty:
            self.logger.info("[action] Empty DataFrame, skipping transform")
            return {"df": input_data, "catalogs": {}}

        self.logger.info(f"[action] Starting transformation of {len(input_data)} rows")
        df = input_data

        df["fecha_actualizacion"] = pd.to_datetime(df["fecha_actualizacion"])

        df["codigo_actividad"] = pd.to_numeric(df["codigo_actividad"], errors="coerce")
        df["cve_mun"] = pd.to_numeric(df["cve_mun"], errors="coerce")
        df["localidad_id"] = pd.to_numeric(df["localidad_id"], errors="coerce")
        df["latitud"] = pd.to_numeric(df["latitud"], errors="coerce")
        df["longitud"] = pd.to_numeric(df["longitud"], errors="coerce")

        df = list_values_to_null(df, rm_list=NULL_VALUES)

        for col in DATE_COLS:
            df[col] = pd.to_datetime(df[col], format="mixed", dayfirst=True, errors="coerce").dt.date

        for col in TITLE_COLS:
            if col in df.columns:
                title_col(df, col)

        for col in ["per_ocu", "tipo_uni_eco", "municipio", "localidad", "nombre_asentamiento"]:
            if col in df.columns:
                df[col] = df[col].astype("category")

        per_ocu_str = df["per_ocu"].astype(str)
        df["rango_personal_id"] = None
        for pattern, rango_id in RANGO_PERSONAL_MAP.items():
            mask = per_ocu_str.str.contains(pattern, na=False)
            df.loc[mask, "rango_personal_id"] = rango_id
        df["tipo_establecimiento_id"] = df["tipo_uni_eco"].map(TIPO_ESTABLECIMIENTO_MAP)

        df = df[df["nombre_establecimiento"].notna()]

        extract_dir = self.work_dir.parents[1] / "extract" / PIPELINE_NAME
        self.scian_lookups = load_scian_lookups(extract_dir, settings.SCIAN_CSV_NAME)

        self.logger.info(f"[action] {len(df)} rows after transformation")
        return {"df": df, "catalogs": self._build_catalogs(df)}

    def finalization(self, input_data: Any) -> Any:
        if not input_data["df"].empty:
            df_pkl = self.work_dir / f"denue_df_{self.entidad}.pkl"
            catalogs_pkl = self.work_dir / f"denue_catalogs_{self.entidad}.pkl"
            input_data["df"].to_pickle(df_pkl)
            pd.Series(input_data["catalogs"]).to_pickle(catalogs_pkl)
            self.logger.info(f"[finalization] {len(input_data['df'])} rows saved to {df_pkl}")
        return input_data
