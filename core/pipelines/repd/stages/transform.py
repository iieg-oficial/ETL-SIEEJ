import pandas as pd

from pathlib import Path
from typing import Any, Optional

from core.pipelines.repd.consts import (
    CATALOG_COLUMNS,
    COLUMN_RENAME_MAP,
    DATE_COLUMNS,
    NULL_VALUES,
    PIPELINE_NAME,
)
from core.pipelines.stage import Stage
from core.utils.clean import list_values_to_null, parse_boolean
from core.utils.files import clean_directory
from core.utils.normalize import normalize_col, uppercase_col
from core.utils.parse_datetime import parse_month_year


class REPDTransformer(Stage):
    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "transform")
        self.mode = mode

    # Valida la salida de Extract
    def source(self, input_data: Optional[Any] = None) -> dict:
        if not input_data or not input_data.get("file_path"):
            raise ValueError("Transform no recibio archivo de Extract.")
        self.logger.info(f"Archivo fuente: {input_data['file_path']}")
        return input_data

    # Lee el Excel, limpia y transforma los datos
    def action(self, input_data: Optional[Any] = None) -> dict:
        file_path = input_data["file_path"]

        # Leer Excel: hoja "DATOS", header en fila 12 (0-indexed)
        self.logger.info(f"Leyendo archivo: {file_path}")
        df = pd.read_excel(file_path, sheet_name="DATOS", header=12, dtype=str)
        self.logger.info(f"Registros leidos: {len(df)}, columnas: {list(df.columns)}")

        # Normalizar nombres de columnas y quitar acentos
        tmp = pd.DataFrame({"c": df.columns.str.strip()})
        df.columns = normalize_col(tmp, "c").values
        df = df.rename(columns=COLUMN_RENAME_MAP)

        # Limpiar valores nulos
        df = list_values_to_null(df, rm_list=NULL_VALUES)

        # Parsear fechas MM/YYYY a date con dia 1
        for col in DATE_COLUMNS:
            if col in df.columns:
                df[col] = df[col].apply(parse_month_year)

        # Convertir carpeta de investigacion a boolean
        df["tiene_carpeta_investigacion"] = df["tiene_carpeta_investigacion"].apply(parse_boolean)

        # Normalizar estados a UPPER
        for col in ["estado_desaparicion", "estado_localizacion"]:
            if col in df.columns:
                uppercase_col(df, col)

        # Normalizar municipios a UPPER
        for col in ["municipio_desaparicion", "municipio_localizacion"]:
            if col in df.columns:
                uppercase_col(df, col)

        # Extraer valores unicos de catalogos
        catalogs: dict[str, list[str]] = {}
        for col in CATALOG_COLUMNS:
            if col in df.columns:
                unique_vals = df[col].dropna().unique().tolist()
                catalogs[col] = sorted(unique_vals)
                self.logger.info(f"Catalogo '{col}': {len(unique_vals)} valores unicos")

        # Sanitizar: convertir NaN/NaT residuales a None
        df = df.where(pd.notna(df), other=None)

        self.logger.info(f"Transformacion completa. {len(df)} registros.")

        return {
            "df": df,
            "catalogs": catalogs,
            "row_count": len(df),
        }

    # Limpia carpetas de datos (extract ya consumido + la propia)
    def finalization(self, input_data: Optional[Any] = None) -> dict:
        self.logger.info(f"Transformacion completa. {input_data['row_count']} registros procesados.")

        extract_dir = Path(f"data/extract/{PIPELINE_NAME}")
        clean_directory(extract_dir, self.logger)
        clean_directory(self.work_dir, self.logger)

        return input_data
