import pandas as pd

from pathlib import Path
from typing import Any, Optional

from core.pipelines.etef.consts import (
    CATALOG_COLUMNS,
    COLUMN_RENAME_MAP,
    NATURAL_KEY_COLUMNS,
    NULL_VALUES,
    PIPELINE_NAME,
)
from core.pipelines.etef.config import settings
from core.pipelines.stage import Stage
from core.utils.clean import list_values_to_null
from core.utils.files import clean_directory
from core.utils.normalize import normalize_col


class EtefTransformer(Stage):
    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "transform")
        self.mode = mode

    def source(self, input_data: Optional[Any] = None) -> dict:
        if not input_data or not input_data.get("file_path"):
            raise ValueError("Transform no recibió archivo de Extract")
        self.logger.info(f"Archivo fuente: {input_data['file_path']}")
        return input_data

    def action(self, input_data: Optional[Any] = None) -> dict:
        file_path = input_data["file_path"]

        # Leer CSV
        self.logger.info(f"Leyendo CSV: {file_path}")
        df = pd.read_csv(file_path, dtype=str, encoding="utf-8")
        self.logger.info(f"Registros leídos: {len(df)}, columnas: {len(df.columns)}")

        # Normalizar nombres de columnas a snake_case
        tmp = pd.DataFrame({"c": df.columns.str.strip()})
        df.columns = normalize_col(tmp, "c").values
        df = df.rename(columns=COLUMN_RENAME_MAP)

        # Limpiar valores nulos
        df = list_values_to_null(df, rm_list=NULL_VALUES)

        # Filtrar a Jalisco (CVE_ENT = 14)
        cve_ent_filter = settings.ETEF_FILTER_CVE_ENT
        original_count = len(df)
        df = df[pd.to_numeric(df["cve_ent"], errors="coerce") == cve_ent_filter]
        self.logger.info(f"Filtrado a CVE_ENT={cve_ent_filter}: {original_count} → {len(df)} registros")

        # Convertir tipos de datos
        df["anio"] = pd.to_numeric(df["anio"], errors="coerce").astype("Int64")
        df["val_usd"] = pd.to_numeric(df["val_usd"], errors="coerce")

        # Extraer valores únicos de catálogos
        catalogs: dict[str, list[str]] = {}
        for col in CATALOG_COLUMNS:
            if col in df.columns:
                unique_vals = df[col].dropna().unique().tolist()
                catalogs[col] = sorted(unique_vals)
                self.logger.info(f"Catálogo '{col}': {len(unique_vals)} valores únicos")

        # Sanitizar NaN/NaT residuales a None
        df = df.where(pd.notna(df), other=None)

        # Crear llave natural concatenada
        df["llave_natural"] = df[NATURAL_KEY_COLUMNS].fillna("").astype(str).agg("|".join, axis=1)

        self.logger.info(f"Transformación completa. {len(df)} registros.")

        return {
            "df": df,
            "catalogs": catalogs,
            "row_count": len(df),
        }

    def finalization(self, input_data: Optional[Any] = None) -> dict:
        self.logger.info(f"Transformación completa. {input_data['row_count']} registros procesados.")

        extract_dir = Path(f"data/extract/{PIPELINE_NAME}")
        clean_directory(extract_dir, self.logger)
        clean_directory(self.work_dir, self.logger)

        return input_data
