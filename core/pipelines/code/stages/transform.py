from datetime import date
from pathlib import Path
from typing import Any, Optional

import pandas as pd

from core.constants.geo import JALISCO_CVE_ENTIDAD
from core.pipelines.code.constants import (
    ACTIVIDADES_COLUMNS,
    CATALOGS_FILENAME,
    FLOAT_COLUMNS,
    INTEGER_COLUMNS,
    MANIFEST_FILENAME,
    NULL_VALUES,
    PIPELINE_NAME,
    PUNTOS_COLUMNS,
    PUNTOS_FRAME,
    PUNTOS_RENAMES,
    SHEET_ACTIVIDADES,
    SHEET_PUNTOS,
)
from core.pipelines.code.helpers.values import title_es
from core.pipelines.stage import Stage
from core.utils.clean import list_values_to_null
from core.utils.files import read_json
from core.utils.logger import get_logger
from core.utils.normalize import normalize_text


class CodeTransform(Stage):
    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "transform")
        self.mode = mode
        self.logger = get_logger(f"{PIPELINE_NAME}.transform")

    def source(self, input_data: Optional[Any] = None) -> dict[str, Any]:
        extract_dir = Path("data/extract") / PIPELINE_NAME
        manifest = read_json(extract_dir / MANIFEST_FILENAME) or {}

        frames = {}
        for sheet in (SHEET_PUNTOS, SHEET_ACTIVIDADES):
            pickle_path = extract_dir / f"{sheet}.pkl"
            if manifest and pickle_path.exists():
                frames[sheet] = pd.read_pickle(pickle_path)

        if frames:
            self.logger.info(f"[source] Loaded {len(frames)} sheet(s) from extract")
            return {"frames": frames, "manifest": manifest}

        if input_data:
            return input_data

        self.logger.info("[source] No data to transform")
        return {"frames": {}, "manifest": manifest}

    def _standardize(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize headers, rename to the schema names and keep the modeled columns."""
        df = df.dropna(how="all")
        df.columns = [normalize_text(column) for column in df.columns]
        df = df.rename(columns=PUNTOS_RENAMES)

        missing = [column for column in PUNTOS_COLUMNS if column not in df.columns]
        if missing:
            raise KeyError(f"Source is missing modeled columns: {missing}")

        return df[PUNTOS_COLUMNS].copy()

    def _add_dates(self, df: pd.DataFrame, manifest: dict[str, Any]) -> pd.DataFrame:
        if df["fecha_corte"].isna().any():
            raise ValueError("The source has rows without a valid fecha")

        df["fecha_corte"] = pd.to_datetime(df["fecha_corte"]).dt.date
        df["fecha_actualizacion_fuente"] = (
            pd.to_datetime(manifest["actualizado_en"]).date() if manifest.get("actualizado_en") else None
        )
        df["fecha_actualizacion"] = date.today()
        return df

    def _prepare_puntos(self, df: pd.DataFrame, manifest: dict[str, Any]) -> pd.DataFrame:
        df = self._standardize(df)
        df["region"] = df["region"].map(title_es)
        df = list_values_to_null(df, rm_list=NULL_VALUES)

        for column in INTEGER_COLUMNS:
            df[column] = pd.to_numeric(df[column], errors="coerce").astype("Int64")

        for column in FLOAT_COLUMNS:
            df[column] = pd.to_numeric(df[column], errors="coerce")

        df["entidad_id"] = JALISCO_CVE_ENTIDAD
        return self._add_dates(df, manifest)

    def _build_catalogs(self, puntos: pd.DataFrame, actividades: pd.DataFrame) -> dict[str, list[dict[str, Any]]]:
        actividades = list_values_to_null(actividades[ACTIVIDADES_COLUMNS], rm_list=NULL_VALUES).dropna()
        actividades["id"] = actividades["id"].astype(int)

        return {
            "actividades": actividades.sort_values("id").to_dict("records"),
            "regiones": [{"region": value} for value in sorted(puntos["region"].dropna().unique())],
        }

    def action(self, input_data: dict[str, Any]) -> dict[str, Any]:
        frames = input_data["frames"]
        manifest = input_data["manifest"]

        if not frames:
            self.logger.info("[action] Nothing to transform")
            return {"frames": {}, "manifest": manifest, "catalogs": {}}

        puntos = self._prepare_puntos(frames[SHEET_PUNTOS], manifest)
        self.logger.info(f"[action] {PUNTOS_FRAME}: {len(puntos):,} rows prepared")

        catalogs = self._build_catalogs(puntos, frames[SHEET_ACTIVIDADES])
        return {"frames": {PUNTOS_FRAME: puntos}, "manifest": manifest, "catalogs": catalogs}

    def finalization(self, input_data: dict[str, Any]) -> dict[str, Any]:
        for name, df in input_data["frames"].items():
            df.to_pickle(self.work_dir / f"{name}.pkl")
            self.logger.info(f"[finalization] {name}: {len(df):,} rows saved")

        pd.to_pickle(input_data["catalogs"], self.work_dir / CATALOGS_FILENAME)
        self.logger.info(f"[finalization] {len(input_data['catalogs'])} catalog(s) saved")

        return input_data
