import pandas as pd

from pathlib import Path
from typing import Any, Optional

from core.pipelines.efipem.consts import (
    CATALOG_COLUMNS,
    COLUMN_RENAME_MAP,
    JALISCO_CVE_ENT,
    NULL_VALUES,
    PIPELINE_NAME,
    SOURCE_CSV_GLOB,
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
        if not input_data or not input_data.get("data_dir"):
            raise ValueError("Transform no recibio directorio de Extract.")
        self.logger.info(f"Directorio fuente: {input_data['data_dir']}")
        return input_data

    # Lee todos los CSVs anuales, concatena, filtra a Jalisco y normaliza
    def action(self, input_data: Optional[Any] = None) -> dict:
        data_dir = Path(input_data["data_dir"])
        csv_paths = sorted(data_dir.glob(SOURCE_CSV_GLOB))
        if not csv_paths:
            raise FileNotFoundError(f"No se encontraron CSVs con patron '{SOURCE_CSV_GLOB}' en {data_dir}")

        self.logger.info(f"Leyendo {len(csv_paths)} CSVs anuales...")
        frames = []
        for csv_path in csv_paths:
            df_year = pd.read_csv(csv_path, dtype=str, encoding="utf-8")
            frames.append(df_year)

        df = pd.concat(frames, ignore_index=True)
        self.logger.info(f"Registros totales leidos (nacional): {len(df)}, columnas: {list(df.columns)}")

        # Normalizar headers a minusculas y renombrar
        df.columns = [c.strip().lower() for c in df.columns]
        df = df.rename(columns=COLUMN_RENAME_MAP)

        # Limpiar valores nulos
        df = list_values_to_null(df, rm_list=NULL_VALUES)

        # Filtrar solo Jalisco antes de cualquier tipado costoso
        df["cve_ent"] = df["cve_ent"].str.strip()
        df = df[df["cve_ent"] == JALISCO_CVE_ENT].copy()
        self.logger.info(f"Registros Jalisco (cve_ent={JALISCO_CVE_ENT}): {len(df)}")

        if df.empty:
            raise ValueError(f"No se encontraron registros para Jalisco (cve_ent={JALISCO_CVE_ENT})")

        # Tipar numericas
        df["anio"] = df["anio"].astype(int)
        df["cve_ent"] = pd.to_numeric(df["cve_ent"], errors="coerce").astype("Int64")
        df["cve_mun"] = pd.to_numeric(df["cve_mun"].str.strip(), errors="coerce").astype("Int64")
        df["valor"] = pd.to_numeric(df["valor"], errors="coerce").astype("Int64")

        # cvegeo: normalizar a exactamente 5 caracteres con ceros a la izquierda
        df["cvegeo"] = df["cvegeo"].str.strip().str.zfill(5)

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
        self.logger.info(f"Transformacion completa. {input_data['row_count']} registros de Jalisco procesados.")

        extract_dir = Path(f"data/extract/{PIPELINE_NAME}")
        clean_directory(extract_dir, self.logger)
        clean_directory(self.work_dir, self.logger)

        return input_data
