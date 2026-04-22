import pandas as pd

from pathlib import Path
from typing import Any, Optional

from core.pipelines.efipem.config import settings
from core.pipelines.efipem.consts import (
    CATALOG_COLUMNS,
    CLASIFICADOR_NORMALIZATION,
    COLUMN_RENAME_MAP,
    NULL_VALUES,
    PIPELINE_NAME,
)
from core.pipelines.stage import Stage
from core.utils.clean import list_values_to_null
from core.utils.files import clean_directory


class EfipemTransformer(Stage):
    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "transform")
        self.mode = mode

    # Valida la salida de Extract
    def source(self, input_data: Optional[Any] = None) -> dict:
        if not input_data or not input_data.get("file_path"):
            raise ValueError("Transform no recibio archivo de Extract.")
        self.logger.info(f"Archivo fuente: {input_data['file_path']}")
        return input_data

    # Lee el CSV, filtra Jalisco, normaliza y extrae catalogos
    def action(self, input_data: Optional[Any] = None) -> dict:
        file_path = input_data["file_path"]
        cve_ent_filter = settings.EFIPEM_CVE_ENT_FILTER

        self.logger.info(f"Leyendo CSV: {file_path}")
        df = pd.read_csv(file_path, dtype=str, encoding="utf-8")
        self.logger.info(f"Registros leidos: {len(df)}, columnas: {list(df.columns)}")

        # Normalizar headers a minusculas y renombrar
        df.columns = [c.strip().lower() for c in df.columns]
        df = df.rename(columns=COLUMN_RENAME_MAP)

        # Limpiar valores nulos
        df = list_values_to_null(df, rm_list=NULL_VALUES)

        # Zero-pad CVEGEO y CVE_ENT a 2 digitos (vienen como "1", "2", ... en el CSV)
        for col in ["cvegeo", "cve_ent"]:
            if col in df.columns:
                df[col] = df[col].str.strip().str.zfill(2)

        # Filtrar solo la entidad solicitada (Jalisco)
        before = len(df)
        df = df[df["cve_ent"] == cve_ent_filter].copy()
        self.logger.info(f"Filtro cve_ent='{cve_ent_filter}': {before} -> {len(df)} registros")

        if df.empty:
            raise ValueError(f"No hay registros tras filtrar cve_ent='{cve_ent_filter}'")

        # Normalizar clasificador (unificar guiones em-dash / hyphen)
        df["clasificador"] = df["clasificador"].str.strip()
        df["clasificador"] = df["clasificador"].map(CLASIFICADOR_NORMALIZATION).fillna(df["clasificador"])

        # Tipar numericos
        df["anio"] = df["anio"].astype(int)
        df["valor"] = df["valor"].astype("int64")

        # Extraer catalogos simples (name-only)
        catalogs: dict[str, list[str]] = {}
        for col in CATALOG_COLUMNS:
            if col in df.columns:
                unique_vals = sorted(df[col].dropna().unique().tolist())
                catalogs[col] = unique_vals
                self.logger.info(f"Catalogo '{col}': {len(unique_vals)} valores unicos")

        # Catalogo compuesto concepto: (clasificador, concepto)
        concepto_pairs = df[["clasificador", "concepto"]].dropna().drop_duplicates().to_records(index=False).tolist()
        concepto_pairs = [(str(c), str(n)) for c, n in concepto_pairs]
        self.logger.info(f"Catalogo 'concepto': {len(concepto_pairs)} pares (clasificador, concepto)")

        # Sanitizar NaN residuales
        df = df.where(pd.notna(df), other=None)

        return {
            "df": df,
            "catalogs": catalogs,
            "concepto_pairs": concepto_pairs,
            "row_count": len(df),
        }

    # Limpia extract y la propia carpeta de trabajo
    def finalization(self, input_data: Optional[Any] = None) -> dict:
        self.logger.info(f"Transformacion completa. {input_data['row_count']} registros procesados.")

        extract_dir = Path(f"data/extract/{PIPELINE_NAME}")
        clean_directory(extract_dir, self.logger)
        clean_directory(self.work_dir, self.logger)

        return input_data
