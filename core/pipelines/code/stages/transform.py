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
    REQUIRED_COLUMNS,
    SHEET_ACTIVIDADES,
    SHEET_PUNTOS,
    UNIQUE_KEY,
)
from core.pipelines.code.datasets import ACADEMIAS, MAIN_FRAMES, POLIDEPORTIVOS, RETO
from core.pipelines.code.helpers.academias import transform_academias
from core.pipelines.code.helpers.polideportivos import transform_polideportivos
from core.pipelines.code.helpers.values import title_es
from core.pipelines.stage import Stage
from core.utils.clean import list_values_to_null
from core.utils.files import clean_directory, read_json
from core.utils.logger import get_logger
from core.utils.normalize import normalize_text


class CodeTransform(Stage):
    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "transform")
        self.mode = mode
        self.logger = get_logger(f"{PIPELINE_NAME}.transform")

    def source(self, input_data: Optional[Any] = None) -> dict[str, dict[str, Any]]:
        extract_dir = Path("data/extract") / PIPELINE_NAME
        manifest = read_json(extract_dir / MANIFEST_FILENAME) or {}

        loaded = {}
        for key, entry in manifest.items():
            frames = {path.stem: pd.read_pickle(path) for path in sorted((extract_dir / key).glob("*.pkl"))}
            if frames:
                loaded[key] = {"frames": frames, "manifest": entry}

        if loaded:
            self.logger.info(f"[source] Loaded {sorted(loaded)} from extract")
            return loaded

        if input_data:
            return input_data

        self.logger.info("[source] No data to transform")
        return {}

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
        df = list_values_to_null(df, rm_list=NULL_VALUES)
        df["region"] = df["region"].map(title_es)

        for column in INTEGER_COLUMNS:
            df[column] = pd.to_numeric(df[column], errors="coerce").astype("Int64")

        for column in FLOAT_COLUMNS:
            df[column] = pd.to_numeric(df[column], errors="coerce")

        df["entidad_id"] = JALISCO_CVE_ENTIDAD
        df = self._add_dates(df, manifest)
        self._validate_puntos(df)
        return df

    def _validate_puntos(self, df: pd.DataFrame) -> None:
        """Fail here with the offending values, not later as a database error."""
        for column in REQUIRED_COLUMNS:
            if df[column].isna().any():
                raise ValueError(f"Column '{column}' has {int(df[column].isna().sum())} row(s) without a value")

        duplicated = df.loc[df.duplicated(UNIQUE_KEY, keep=False), UNIQUE_KEY].drop_duplicates()
        if not duplicated.empty:
            raise ValueError(f"Found duplicated {UNIQUE_KEY} keys:\n{duplicated.to_string(index=False)}")

    def _build_catalogs(self, puntos: pd.DataFrame, actividades: pd.DataFrame) -> dict[str, list[dict[str, Any]]]:
        actividades = list_values_to_null(actividades[ACTIVIDADES_COLUMNS], rm_list=NULL_VALUES).dropna()
        actividades["id"] = actividades["id"].astype(int)

        unknown = sorted(set(puntos["actividad_id"].dropna()) - set(actividades["id"]))
        if unknown:
            raise ValueError(f"actividad_id values missing from the activities catalog: {unknown}")

        return {
            "actividades": actividades.sort_values("id").to_dict("records"),
            "regiones": [{"region": value} for value in sorted(puntos["region"].dropna().unique())],
        }

    def _transform_reto(self, frames: dict[str, pd.DataFrame], manifest: dict[str, Any]) -> tuple[dict, dict]:
        puntos = self._prepare_puntos(frames[SHEET_PUNTOS], manifest)
        catalogs = self._build_catalogs(puntos, frames[SHEET_ACTIVIDADES])
        return {PUNTOS_FRAME: puntos}, catalogs

    def action(self, input_data: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
        if not input_data:
            self.logger.info("[action] Nothing to transform")
            return {}

        handlers = {
            RETO: self._transform_reto,
            ACADEMIAS: transform_academias,
            POLIDEPORTIVOS: transform_polideportivos,
        }

        transformed = {}
        for key, entry in input_data.items():
            frames, catalogs = handlers[key](entry["frames"], entry["manifest"])
            if frames[MAIN_FRAMES[key]].empty:
                raise ValueError(f"{key}: the source has no rows")
            for name, df in frames.items():
                self.logger.info(f"[action] {key}/{name}: {len(df):,} rows prepared")
            transformed[key] = {"frames": frames, "manifest": entry["manifest"], "catalogs": catalogs}

        return transformed

    def finalization(self, input_data: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
        for key, entry in input_data.items():
            folder = self.work_dir / key
            folder.mkdir(parents=True, exist_ok=True)
            clean_directory(folder, self.logger)
            for name, df in entry["frames"].items():
                df.to_pickle(folder / f"{name}.pkl")
                self.logger.info(f"[finalization] {key}/{name}: {len(df):,} rows saved")

            pd.to_pickle(entry["catalogs"], folder / CATALOGS_FILENAME)
            self.logger.info(f"[finalization] {key}: {len(entry['catalogs'])} catalog(s) saved")

        return input_data
