from pathlib import Path
from typing import Any, Optional

import pandas as pd

from core.pipelines.stage import Stage
from core.pipelines.denue.attributes import DenueTables as T
from core.pipelines.denue.config import settings
from core.pipelines.denue.constants import ENTIDAD_JALISCO, NULL_VALUES, TITLE_COLS, DATE_COLS
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
        self.is_jalisco = entidad == ENTIDAD_JALISCO
        self.logger = get_logger(f"{PIPELINE_NAME}.transform")
        self.scian_lookups = None

    def source(self, input_data: Optional[Any] = None) -> list[Path]:
        extract_dir = self.work_dir.parents[1] / "extract" / PIPELINE_NAME

        per_period = sorted(extract_dir.glob(f"denue_{self.entidad}_*.pkl"))
        if per_period:
            self.logger.info(f"[source] Found {len(per_period)} per-period pkls for entidad {self.entidad}")
            return per_period

        old_pkl = extract_dir / f"denue_extracted_{self.entidad}.pkl"
        if old_pkl.exists():
            self.logger.info(f"[source] Found legacy pkl for entidad {self.entidad}")
            return [old_pkl]

        self.logger.info(f"[source] No extract pkls found for entidad {self.entidad}")
        return []

    def _transform_jalisco(self, df: pd.DataFrame) -> pd.DataFrame:
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

        df = df[df["clee"].notna()]
        return df

    def _aggregate_resumen(self, df: pd.DataFrame) -> pd.DataFrame:
        df["codigo_actividad"] = pd.to_numeric(df["codigo_actividad"], errors="coerce")
        df = df[df["clee"].notna()]

        return (
            df.groupby(["entidad_id", "fecha_actualizacion", "codigo_actividad"], dropna=False)
            .size()
            .reset_index(name="num_establecimientos")
        )

    def _build_catalogs(self, df: pd.DataFrame) -> dict:
        self.logger.info(f"[_build_catalogs] Building catalogs from {len(df)} rows")

        actualizaciones = df_to_records(
            df.drop_duplicates(subset=["fecha_actualizacion"]).dropna(subset=["fecha_actualizacion"]),
            ["fecha_actualizacion"],
        )

        catalogs = {T.CAT_ACTUALIZACIONES: actualizaciones}
        catalogs.update(self._build_scian_catalogs(df["codigo_actividad"]))

        if self.is_jalisco:
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
            catalogs[T.CAT_LOCALIDADES] = localidades

        return catalogs

    def _build_scian_catalogs(self, codigos_col: pd.Series) -> dict:
        codigos = codigos_col.dropna().astype(int).astype(str).unique()

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
            f"[_build_scian_catalogs] {len(sectores_set)} sectores, {len(subsectores_set)} subsectores, "
            f"{len(ramas_set)} ramas, {len(subramas_set)} subramas, {len(clases_set)} clases"
        )

        return {
            T.CAT_SECTORES: list(sectores_set.values()),
            T.CAT_SUBSECTORES: list(subsectores_set.values()),
            T.CAT_RAMAS: list(ramas_set.values()),
            T.CAT_SUBRAMAS: list(subramas_set.values()),
            T.CAT_CLASES_ACTIVIDAD: list(clases_set.values()),
        }

    def action(self, input_data: list[Path]) -> list[dict]:
        if not input_data:
            self.logger.info("[action] No extract pkls to process")
            return []

        extract_dir = self.work_dir.parents[1] / "extract" / PIPELINE_NAME
        self.scian_lookups = load_scian_lookups(extract_dir, settings.SCIAN_CSV_NAME)
        prefix = "denue_df" if self.is_jalisco else "denue_resumen"

        periods = []
        for pkl_path in input_data:
            df = pd.read_pickle(pkl_path)
            if df.empty:
                continue

            for fecha, chunk in df.groupby("fecha_actualizacion"):
                date_str = pd.Timestamp(fecha).strftime("%Y%m%d")
                df_pkl = self.work_dir / f"{prefix}_{self.entidad}_{date_str}.pkl"
                cat_pkl = self.work_dir / f"denue_catalogs_{self.entidad}_{date_str}.pkl"

                if self.mode != "bootstrap" and df_pkl.exists() and cat_pkl.exists():
                    self.logger.info(f"[action] Already transformed periodo {date_str}, skipping")
                    periods.append({"df_path": df_pkl, "catalogs_path": cat_pkl})
                    continue

                self.logger.info(f"[action] Transforming {len(chunk):,} rows for periodo {date_str}")
                chunk = chunk.copy()

                if self.is_jalisco:
                    transformed = self._transform_jalisco(chunk)
                    catalogs = self._build_catalogs(transformed)
                else:
                    catalogs = self._build_catalogs(chunk)
                    transformed = self._aggregate_resumen(chunk)

                transformed.to_pickle(df_pkl)
                pd.Series(catalogs).to_pickle(cat_pkl)
                self.logger.info(f"[action] {len(transformed):,} rows saved to {df_pkl.name}")
                periods.append({"df_path": df_pkl, "catalogs_path": cat_pkl})

        return periods

    def finalization(self, input_data: list[dict]) -> list[dict]:
        self.logger.info(f"[finalization] {len(input_data)} periodos transformed for entidad {self.entidad}")
        return input_data
