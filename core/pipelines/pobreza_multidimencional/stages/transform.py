from pathlib import Path
from typing import Any, Optional

import pandas as pd

from core.pipelines.pobreza_multidimencional.consts import (
    DATA_YEARS,
    EXCEL_COL_NAMES,
    EXCEL_SHEET,
    EXCEL_SKIP_ROWS,
    EXCEL_USE_COLS,
    INDICATOR_PREFIXES,
    NULL_VALUES,
    PIPELINE_NAME,
)
from core.pipelines.stage import Stage
from core.utils.clean import list_values_to_null
from core.utils.files import clean_directory


class PobrezaMultidimencionalTransform(Stage):
    """Transforma el XLSX wide → tidy (municipio × año) y extrae el catálogo de entidades."""

    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "transform")
        self.mode = mode

    def source(self, input_data: Optional[Any] = None) -> dict:
        if not input_data or not input_data.get("file_path"):
            raise ValueError("Transform no recibió archivo de Extract")
        return input_data

    def action(self, input_data: Optional[Any] = None) -> dict:
        file_path = input_data["file_path"]
        self.logger.info(f"Leyendo: {file_path}")

        df_wide = self._read_excel(file_path)
        self.logger.info(f"Leídos {len(df_wide)} municipios, {len(df_wide.columns)} columnas")

        df_tidy = self._wide_to_tidy(df_wide)
        self.logger.info(f"Filas tidy (municipio × año): {len(df_tidy)}")

        catalogs = self._extract_catalogs(df_wide)

        # Sanitizar NaN/NaT residuales → None para SQLAlchemy
        df_tidy = df_tidy.where(pd.notna(df_tidy), other=None)

        return {"df": df_tidy, "catalogs": catalogs, "row_count": len(df_tidy)}

    def finalization(self, input_data: Optional[Any] = None) -> dict:
        clean_directory(Path(f"data/extract/{PIPELINE_NAME}"), self.logger)
        clean_directory(self.work_dir, self.logger)
        return input_data

    # ------------------------------------------------------------------
    # Métodos privados
    # ------------------------------------------------------------------

    def _read_excel(self, file_path: str) -> pd.DataFrame:
        """Lee el XLSX saltando los encabezados multi-nivel y asigna nombres de columna."""
        df = pd.read_excel(
            file_path,
            sheet_name=EXCEL_SHEET,
            header=None,
            skiprows=EXCEL_SKIP_ROWS,
            usecols=EXCEL_USE_COLS,
            dtype=str,
        )
        df.columns = EXCEL_COL_NAMES

        # Filtrar filas inválidas: cve_mun debe ser un código de 5 dígitos
        df = df[df["cve_mun"].str.match(r"^\d{5}$", na=False)].copy()

        # Aplicar nulos
        df = list_values_to_null(df, rm_list=NULL_VALUES)

        # Convertir columnas numéricas al tipo correcto
        df = self._cast_numeric(df)

        return df.reset_index(drop=True)

    def _cast_numeric(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convierte las columnas de métricas a float o int según el sufijo."""
        for col in df.columns:
            if col in ("cve_ent", "nombre_ent", "cve_mun", "nombre_municipio"):
                continue
            if col.startswith("poblacion_"):
                df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
            elif "_personas_" in col:
                df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
            else:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        return df

    def _wide_to_tidy(self, df_wide: pd.DataFrame) -> pd.DataFrame:
        """Convierte formato wide (un municipio por fila) a tidy (municipio × año)."""
        id_cols = ["cve_ent", "nombre_ent", "cve_mun", "nombre_municipio"]
        frames: list[pd.DataFrame] = []

        for year in DATA_YEARS:
            row = df_wide[id_cols].copy()
            row["anio"] = year
            row["poblacion"] = df_wide[f"poblacion_{year}"]

            for prefix, has_car_prom in INDICATOR_PREFIXES:
                row[f"{prefix}_porcentaje"] = df_wide[f"{prefix}_porcentaje_{year}"]
                row[f"{prefix}_personas"] = df_wide[f"{prefix}_personas_{year}"]
                if has_car_prom:
                    row[f"{prefix}_carencias_promedio"] = df_wide[f"{prefix}_carencias_promedio_{year}"]

            frames.append(row)

        return pd.concat(frames, ignore_index=True)

    def _extract_catalogs(self, df_wide: pd.DataFrame) -> dict:
        """Extrae el catálogo de entidades federativas."""
        cat_entidad = (
            df_wide[["cve_ent", "nombre_ent"]]
            .dropna(subset=["cve_ent"])
            .drop_duplicates(subset=["cve_ent"])
            .sort_values("cve_ent")
            .rename(columns={"cve_ent": "cve_ent", "nombre_ent": "nombre_entidad"})
            .to_dict("records")
        )
        return {"entidad": cat_entidad}
