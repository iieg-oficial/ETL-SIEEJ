from datetime import date
from pathlib import Path
from typing import Any, Optional

import pandas as pd

from core.pipelines.escuelas.config import settings
from core.pipelines.escuelas.constants import (
    CATALOG_VALUE_COLUMNS,
    DIRECTORIO_COLUMN_RENAMES,
    DIRECTORIO_COLUMNS,
    DIRECTORIO_DATASET,
    DIRECTORIO_FLOAT_COLUMNS,
    DIRECTORIO_NUMERIC_COLUMNS,
    ENTIDAD_ID_JALISCO,
    ESTADISTICA_COLUMNS,
    ESTADISTICA_DATASET,
    ESTADISTICA_NUMERIC_COLUMNS,
    NULL_VALUES,
    OPTIONAL_ZERO_TO_NULL_COLUMNS,
    PIPELINE_NAME,
)
from core.pipelines.escuelas.helpers.values import clean_catalog_value, clean_optional_text
from core.pipelines.stage import Stage
from core.utils.clean import list_values_to_null
from core.utils.logger import get_logger
from core.utils.normalize import normalize_text


class EscuelasTransform(Stage):
    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "transform")
        self.mode = mode
        self.logger = get_logger(f"{PIPELINE_NAME}.transform")

    def source(self, input_data: Optional[Any] = None) -> dict[str, pd.DataFrame]:
        extract_dir = Path("data/extract") / PIPELINE_NAME
        directorio_path = extract_dir / f"{DIRECTORIO_DATASET}.pkl"
        estadistica_path = extract_dir / f"{ESTADISTICA_DATASET}.pkl"

        if directorio_path.exists() and estadistica_path.exists():
            self.logger.info("[source] Loading extract pickle files")
            return {
                DIRECTORIO_DATASET: pd.read_pickle(directorio_path),
                ESTADISTICA_DATASET: pd.read_pickle(estadistica_path),
            }

        return input_data

    def _standardize_columns(
        self,
        df: pd.DataFrame,
        columns: list[str],
        renames: dict[str, str] | None = None,
    ) -> pd.DataFrame:
        df = df.copy()
        df.columns = [normalize_text(column) for column in df.columns]
        df = df.rename(columns=renames or {})
        return df[columns]

    def _prepare_directorio(self, df: pd.DataFrame) -> pd.DataFrame:
        df = self._standardize_columns(df, DIRECTORIO_COLUMNS, DIRECTORIO_COLUMN_RENAMES)
        df = list_values_to_null(df, rm_list=NULL_VALUES)

        for column in CATALOG_VALUE_COLUMNS:
            if column in df.columns:
                df[column] = df[column].map(clean_catalog_value)

        for column in ["telefono", "codigo_postal", "nombre_colonia"]:
            df[column] = df[column].map(clean_optional_text)

        for column in DIRECTORIO_NUMERIC_COLUMNS:
            df[column] = pd.to_numeric(df[column], errors="coerce").astype("Int64")

        for column in DIRECTORIO_FLOAT_COLUMNS:
            df[column] = pd.to_numeric(df[column], errors="coerce")

        for column in OPTIONAL_ZERO_TO_NULL_COLUMNS:
            if column in df.columns:
                df.loc[df[column].astype(str).isin(["0", "0.0"]), column] = pd.NA

        df["anio"] = settings.SOURCE_YEAR
        df["entidad_id"] = ENTIDAD_ID_JALISCO
        df["fecha_actualizacion"] = date.today()

        return df

    def _prepare_estadistica(self, df: pd.DataFrame) -> pd.DataFrame:
        df = self._standardize_columns(df, ESTADISTICA_COLUMNS)
        df = list_values_to_null(df, rm_list=NULL_VALUES)

        df["nivel_programa"] = df["nivel_programa"].map(clean_catalog_value)
        df["sostenimiento"] = df["sostenimiento"].map(clean_catalog_value)

        for column in ESTADISTICA_NUMERIC_COLUMNS:
            df[column] = pd.to_numeric(df[column], errors="coerce").astype("Int64")

        df["anio"] = settings.SOURCE_YEAR
        df["fecha_actualizacion"] = date.today()

        return df

    def _build_catalogs(self, directorio: pd.DataFrame, estadistica: pd.DataFrame) -> dict[str, list[dict[str, Any]]]:
        sostenimientos = (
            pd.concat([directorio["sostenimiento"], estadistica["sostenimiento"]]).dropna().drop_duplicates()
        )

        return {
            "turnos": directorio[["turno_id", "nombre_turno"]]
            .dropna()
            .drop_duplicates()
            .rename(columns={"turno_id": "id"})
            .sort_values("id")
            .to_dict("records"),
            "sostenimientos": pd.DataFrame({"sostenimiento": sorted(sostenimientos)}).to_dict("records"),
            "codigos_sostenimiento": directorio[["codigo_sostenimiento_id", "sostenimiento"]]
            .dropna()
            .drop_duplicates()
            .rename(columns={"codigo_sostenimiento_id": "id"})
            .sort_values("id")
            .to_dict("records"),
            "niveles": pd.DataFrame({"nivel": sorted(directorio["nivel"].dropna().unique())}).to_dict("records"),
            "programas": pd.DataFrame({"programa": sorted(directorio["programa"].dropna().unique())}).to_dict(
                "records"
            ),
            "regiones": directorio[["region_id", "nombre_region"]]
            .dropna()
            .drop_duplicates()
            .rename(columns={"region_id": "id"})
            .sort_values("id")
            .to_dict("records"),
            "medios": pd.DataFrame({"medio": sorted(directorio["medio"].dropna().unique())}).to_dict("records"),
            "niveles_programa": pd.DataFrame(
                {"nivel_programa": sorted(estadistica["nivel_programa"].dropna().unique())}
            ).to_dict("records"),
        }

    def action(self, input_data: dict[str, pd.DataFrame]) -> dict[str, Any]:
        if self.mode != "bootstrap":
            raise ValueError("Escuelas v1 only supports bootstrap mode")

        directorio = self._prepare_directorio(input_data[DIRECTORIO_DATASET])
        estadistica = self._prepare_estadistica(input_data[ESTADISTICA_DATASET])

        return {
            DIRECTORIO_DATASET: directorio,
            ESTADISTICA_DATASET: estadistica,
            "catalogs": self._build_catalogs(directorio, estadistica),
        }

    def finalization(self, input_data: dict[str, Any]) -> dict[str, Any]:
        for dataset in [DIRECTORIO_DATASET, ESTADISTICA_DATASET]:
            input_data[dataset].to_pickle(self.work_dir / f"{dataset}.pkl")

        self.logger.info(
            "[finalization] directorio=%s rows estadistica=%s rows",
            f"{len(input_data[DIRECTORIO_DATASET]):,}",
            f"{len(input_data[ESTADISTICA_DATASET]):,}",
        )
        return input_data
