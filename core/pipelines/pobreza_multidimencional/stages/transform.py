from pathlib import Path
from typing import Any, Optional

import pandas as pd

from core.pipelines.pobreza_multidimencional.consts import (
    FLOAT_COLS,
    INT_COLS,
    NULL_VALUES,
    PIPELINE_NAME,
)
from core.pipelines.pobreza_multidimencional.schemas import PobrezaMultidimencionalDatos
from core.pipelines.stage import Stage
from core.utils.clean import list_values_to_null
from core.utils.files import clean_directory


class PobrezaMultidimencionalTransform(Stage):
    """Normaliza y castea los tipos del CSV de la Base final MMP."""

    def __init__(self, year: int):
        super().__init__(PIPELINE_NAME, "transform")
        self.year = year

    def source(self, input_data: Optional[Any] = None) -> dict:
        if not input_data or not input_data.get("file_path"):
            raise ValueError("Transform no recibió archivo de Extract")
        return input_data

    def action(self, input_data: Optional[Any] = None) -> dict:
        file_path = input_data["file_path"]
        year = input_data["year"]

        df = pd.read_csv(file_path, dtype=str, encoding="utf-8")
        self.logger.info(f"[{year}] Leídos {len(df)} registros, {len(df.columns)} columnas")

        # Limpieza de valores nulos
        df = list_values_to_null(df, rm_list=NULL_VALUES)

        # Casteo de columnas float
        for col in FLOAT_COLS:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # Casteo de columnas enteras
        for col in INT_COLS:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

        # Añadir año de la fuente
        df["anio"] = year

        # Columnas del schema (excluyendo id y municipio_id que se resuelven en load)
        schema_cols = [
            c.key
            for c in PobrezaMultidimencionalDatos.__table__.columns
            if c.key not in ("id", "municipio_id")
        ]

        # Añadir columnas faltantes como None (ej: discap ausente en 2016/2018)
        for col in schema_cols:
            if col not in df.columns:
                self.logger.info(f"Columna '{col}' ausente en {year} — se asigna None")
                df[col] = None

        # Mantener solo columnas del schema
        df = df[[c for c in schema_cols if c in df.columns]]

        # Sanitizar NaN/NaT residuales
        df = df.where(pd.notna(df), other=None)

        self.logger.info(f"[{year}] {len(df)} registros tras transform")
        return {"df": df, "year": year, "row_count": len(df)}

    def finalization(self, input_data: Optional[Any] = None) -> dict:
        clean_directory(Path(f"data/extract/{PIPELINE_NAME}"), self.logger)
        clean_directory(self.work_dir, self.logger)
        return input_data
