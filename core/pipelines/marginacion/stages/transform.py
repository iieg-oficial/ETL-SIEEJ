from pathlib import Path
from typing import Any, Optional

import pandas as pd

from core.pipelines.marginacion.attributes import MarginacionTables as T
from core.pipelines.marginacion.constants import NULL_VALUES, TITLE_COLS
from core.pipelines.stage import Stage
from core.utils import df_to_records
from core.utils.accents import apply_accents
from core.utils.clean import list_values_to_null
from core.utils.logger import get_logger
from core.utils.normalize import title_col


class MarginacionTransform(Stage):
    def __init__(self, year: int):
        super().__init__("marginacion", "transform")
        self.year = year
        self.logger = get_logger("marginacion.transform")

    def source(self, input_data: Optional[Any] = None) -> dict[str, pd.DataFrame]:
        pkl_municipal = Path(f"data/extract/marginacion/municipal_{self.year}.pkl")
        pkl_localidad = Path(f"data/extract/marginacion/localidad_{self.year}.pkl")

        if pkl_municipal.exists() and pkl_localidad.exists():
            self.logger.info(f"[source] Loading extract pkl files for {self.year}")
            return {
                "df_municipal": pd.read_pickle(pkl_municipal),
                "df_localidad": pd.read_pickle(pkl_localidad),
            }

        return input_data

    def _build_catalogs(self, df_localidad: pd.DataFrame) -> dict:
        localidades = df_localidad.drop_duplicates(subset=["cve_geo_id"]).dropna(
            subset=["cve_geo_id", "clave_localidad", "municipio_id", "entidad_id"]
        )
        localidades_records = df_to_records(
            localidades, ["cve_geo_id", "clave_localidad", "municipio_id", "entidad_id", "localidad"]
        )
        self.logger.info(f"[_build_catalogs] {len(localidades_records)} unique localidades")
        return {T.LOCALIDADES: localidades_records}

    def _process_municipal(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["indice_marginacion"] = pd.to_numeric(df["indice_marginacion"], errors="coerce")
        df["indice_marginacion_normalizado"] = pd.to_numeric(df["indice_marginacion_normalizado"], errors="coerce")
        df["fecha_actualizacion"] = pd.to_datetime(df["fecha_actualizacion"])
        df = list_values_to_null(df, rm_list=NULL_VALUES)
        for col in TITLE_COLS:
            if col in df.columns:
                title_col(df, col)
                df[col] = df[col].apply(apply_accents)
        df["fecha_actualizacion"] = df["fecha_actualizacion"].dt.date
        df["municipio_id"] = pd.to_numeric(df["municipio_id"], errors="coerce").astype("Int64")
        df["entidad_id"] = pd.to_numeric(df["entidad_id"], errors="coerce").astype("Int64")
        return df.round(2)

    def _process_localidad(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["fecha_actualizacion"] = pd.to_datetime(df["fecha_actualizacion"])
        df = list_values_to_null(df, rm_list=NULL_VALUES)
        for col in TITLE_COLS:
            if col in df.columns:
                title_col(df, col)
                df[col] = df[col].apply(apply_accents)
        df["fecha_actualizacion"] = df["fecha_actualizacion"].dt.date
        df["municipio_id"] = (df["entidad_id"] * 1000 + df["municipio_id"]).astype("Int64")
        return df.round(2)

    def action(self, input_data: dict[str, pd.DataFrame]) -> dict[str, Any]:
        df_municipal = input_data["df_municipal"]
        df_localidad = input_data["df_localidad"]

        if df_municipal.empty and df_localidad.empty:
            self.logger.info("[action] Empty input, skipping transform")
            return {"df_municipal": df_municipal, "df_localidad": df_localidad, "catalogs": {}}

        self.logger.info(f"[action] Processing {len(df_municipal)} municipal, {len(df_localidad)} localidad rows")

        df_municipal = self._process_municipal(df_municipal)
        df_localidad = self._process_localidad(df_localidad)

        self.logger.info(f"[action] Done: {len(df_municipal)} municipal, {len(df_localidad)} localidad rows")
        return {
            "df_municipal": df_municipal,
            "df_localidad": df_localidad,
            "catalogs": self._build_catalogs(df_localidad),
        }

    def finalization(self, input_data: dict[str, Any]) -> dict[str, Any]:
        input_data["df_municipal"].to_pickle(self.work_dir / f"municipal_{self.year}.pkl")
        input_data["df_localidad"].to_pickle(self.work_dir / f"localidad_{self.year}.pkl")
        pd.to_pickle(input_data["catalogs"], self.work_dir / f"catalogs_{self.year}.pkl")
        self.logger.info(
            f"[finalization] {self.year}: {len(input_data['df_municipal'])} municipal, "
            f"{len(input_data['df_localidad'])} localidad rows saved"
        )
        return input_data
