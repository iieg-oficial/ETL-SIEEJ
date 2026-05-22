"""Transform stages para el pipeline asg_imss.

* `AsgImssCatalogTransformer` parsea el XLSX de IMSS y arma los 12 catálogos
  en estructuras intermedias (con jerarquía resuelta por clave).
* `AsgImssDataTransformer` normaliza el CSV mensual: rename de headers,
  filtro Jalisco, padding de sectores, casteo de métricas, fecha_corte.
"""

from datetime import date
from pathlib import Path
from typing import Any, Optional

import numpy as np
import pandas as pd

from core.pipelines.asg_imss.attributes import (
    CSV_FK_TO_STG_COLUMN,
    CSV_HEADER_RENAMES,
    ENTIDAD_FILTRO_CVE,
    METRIC_FLOAT_COLUMNS,
    METRIC_INT_COLUMNS,
    MUNICIPIO_ALIASES,
    SECTOR_KEY_LENGTHS,
)
from core.pipelines.asg_imss.config import PIPELINE_NAME
from core.pipelines.stage import Stage


# Mapeo hoja XLSX → estructura lógica de catálogo
# Cada entrada describe: (nombre lógico, parser_key)
# El parser_key indica el shape: 'delegacion_subdelegacion',
# 'entidad_municipio', 'sector_1', 'sector_2', 'sector_4', 'simple',
# 'rango_uma_typo'.
CATALOG_SHEETS: list[tuple[str, str]] = [
    ("delegación-subdelegación", "delegacion_subdelegacion"),
    ("entidad-municipio", "entidad_municipio"),
    ("sector 1", "sector 1"),
    ("sector 2", "sector 2"),
    ("sector 4", "sector 4"),
    ("Tamaño de registro patronal", "Tamaño de registro patronal"),
    ("sexo", "simple"),
    ("Rango edad", "rango_edad"),
    ("Rango salario", "rango_salarial"),
    ("Rango UMA", "rango_uma_typo"),
]


def _read_sheet(file_path: Path, sheet_name: str) -> pd.DataFrame:
    """Lee una hoja del XLSX con skiprows=1 y todo como string."""
    df = pd.read_excel(
        file_path,
        sheet_name=sheet_name,
        skiprows=1,
        dtype=str,
        keep_default_na=False,
        engine="openpyxl",
    )
    # Normaliza nombres de columna
    df.columns = [str(c).strip() for c in df.columns]
    # Strip a todas las celdas
    for c in df.columns:
        df[c] = df[c].astype(str).str.strip()
    return df


def _expand_sector_1_ranges(df: pd.DataFrame, clave_col: str) -> pd.DataFrame:
    """Expande filas como '2 - 3' en dos filas individuales con la misma
    descripción.
    """
    rows: list[dict] = []
    for _, row in df.iterrows():
        clave = row[clave_col]
        if "-" in clave:
            try:
                start, end = [int(p.strip()) for p in clave.split("-")]
                for v in range(start, end + 1):
                    new_row = row.copy()
                    new_row[clave_col] = str(v)
                    rows.append(new_row.to_dict())
            except ValueError:
                rows.append(row.to_dict())
        else:
            rows.append(row.to_dict())
    return pd.DataFrame(rows)


class AsgImssCatalogTransformer(Stage):
    """Construye estructuras intermedias de catálogos a partir del XLSX."""

    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "transform")
        self.mode = mode

    def source(self, input_data: Optional[Any] = None) -> dict:
        if not input_data or "file_path" not in input_data:
            raise ValueError("AsgImssCatalogTransformer requiere 'file_path'.")
        return {"file_path": Path(input_data["file_path"])}

    def action(self, input_data: Optional[Any] = None) -> dict:
        file_path: Path = input_data["file_path"]
        self.logger.info(f"Parseando XLSX: {file_path}")

        out: dict[str, list[dict]] = {}

        # ----- delegacion + subdelegacion -----
        df = _read_sheet(file_path, "delegación-subdelegación")
        df = df.rename(columns={c: c.lower() for c in df.columns})
        # Columnas reales: id_deleg_rp, descripcion delegación, id_subdel_rp, descripcion subdelegación
        delegaciones: dict[str, str] = {}
        subdelegaciones: list[dict] = []
        for _, row in df.iterrows():
            cve_d = row.get("id_deleg_rp", "").strip()
            desc_d = row.get("descripcion delegación", "").strip()
            cve_s = row.get("id_subdel_rp", "").strip()
            desc_s = row.get("descripcion subdelegación", "").strip()
            if not cve_d or not cve_d.isdigit():
                continue
            delegaciones.setdefault(cve_d, desc_d)
            if cve_s and cve_s.isdigit():
                subdelegaciones.append({"clave": cve_s, "descripcion": desc_s, "delegacion_clave": cve_d})
        out["delegacion"] = [{"clave": k, "descripcion": v} for k, v in delegaciones.items()]
        out["subdelegacion"] = subdelegaciones

        # ----- entidad + municipio (solo Jalisco) -----
        df = _read_sheet(file_path, "entidad-municipio")
        df = df.rename(columns={c: c.lower() for c in df.columns})
        # Columnas reales: cve_municipio, cve_delegacion, cve_entidad, descripción entidad, descripción municipio
        # Se filtra a ENTIDAD_FILTRO_CVE y se excluyen las claves alias
        # (ver MUNICIPIO_ALIASES en attributes.py).
        entidades: dict[str, str] = {}
        municipios: list[dict] = []
        for _, row in df.iterrows():
            cve_e = row.get("cve_entidad", "").strip().zfill(2) if row.get("cve_entidad", "").strip() else ""
            desc_e = row.get("descripción entidad", "").strip()
            cve_m = row.get("cve_municipio", "").strip()
            desc_m = row.get("descripción municipio", "").strip()
            if not cve_e or cve_e != ENTIDAD_FILTRO_CVE:
                continue
            entidades.setdefault(cve_e, desc_e)
            if cve_m and cve_m not in MUNICIPIO_ALIASES:
                municipios.append({"clave": cve_m, "descripcion": desc_m, "entidad_clave": cve_e})
        out["entidad"] = [{"clave": k, "descripcion": v} for k, v in entidades.items()]
        out["municipio"] = municipios

        # ----- sector_1 -----
        df = _read_sheet(file_path, "sector 1")
        df.columns = [c.lower() for c in df.columns]
        clave_col = "sector_economico_1" if "sector_economico_1" in df.columns else df.columns[0]
        desc_col = "desc_sector_economico_1" if "desc_sector_economico_1" in df.columns else df.columns[1]
        df = _expand_sector_1_ranges(df, clave_col)
        out["sector_1"] = [
            {"clave": row[clave_col].zfill(1), "descripcion": row[desc_col]}
            for _, row in df.iterrows()
            if row[clave_col]
        ]

        # ----- sector_2 (jerárquico) -----
        df = _read_sheet(file_path, "sector 2")
        df.columns = [c.lower() for c in df.columns]
        clave_col = "sector_economico_2_2pos"
        desc_col = next((c for c in df.columns if "descripci" in c), df.columns[-1])
        s1_col = "sector_economico_1"
        out["sector_2"] = [
            {
                "clave": str(row[clave_col]).zfill(2),
                "descripcion": row[desc_col],
                "sector_1_clave": str(row[s1_col]).zfill(1),
            }
            for _, row in df.iterrows()
            if row[clave_col]
        ]

        # ----- sector_4 (jerárquico) -----
        df = _read_sheet(file_path, "sector 4")
        df.columns = [c.lower() for c in df.columns]
        clave_col = "sector_economico_4_4_pos"
        desc_col = next((c for c in df.columns if "descripci" in c), df.columns[-1])
        s2_col = "sector_economico_2_2pos"
        out["sector_4"] = [
            {
                "clave": str(row[clave_col]).zfill(4),
                "descripcion": row[desc_col],
                "sector_2_clave": str(row[s2_col]).zfill(2),
            }
            for _, row in df.iterrows()
            if row[clave_col]
        ]

        # ----- catálogos simples -----
        simple_sheets = {
            "tamano_registro_patronal": (
                "Tamaño de registro patronal",
                "Tamaño de registro patronal",
                "desc_tamano_patron",
            ),
            "sexo": ("sexo", "sexo", "desc_sexo"),
            "rango_edad": ("Rango edad", "rango_edad", "desc_rango_edad"),
            "rango_salario": ("Rango salario", "rango_salarial", "descripción"),
            "rango_uma": ("Rango UMA", "rango_salarial", "descripción"),
        }
        for cat_key, (sheet, clave_col_expected, desc_col_expected) in simple_sheets.items():
            df = _read_sheet(file_path, sheet)
            df.columns = [c.lower() for c in df.columns]
            # Localiza columnas tolerando variantes
            clave_col = next((c for c in df.columns if c == clave_col_expected.lower()), df.columns[0])
            desc_col = next(
                (c for c in df.columns if c.startswith("desc") or c == desc_col_expected.lower()),
                df.columns[1] if len(df.columns) > 1 else df.columns[0],
            )
            registros: list[dict] = []
            for _, row in df.iterrows():
                clave = row[clave_col].strip()
                desc = row[desc_col].strip()
                # Salta filas vacías o notas al pie (clave sin descripción)
                if not clave or not desc:
                    continue
                # tamano_patron: normaliza a uppercase (alineado con el CSV de hechos)
                if cat_key == "tamano_registro_patronal":
                    clave = clave.upper()
                registros.append({"clave": clave, "descripcion": desc})
            out[cat_key] = registros

        self.logger.info("Catálogos parseados: " + ", ".join(f"{k}={len(v)}" for k, v in out.items()))
        return out

    def finalization(self, input_data: Optional[Any] = None) -> dict:
        return input_data


class AsgImssDataTransformer(Stage):
    """Normaliza un CSV mensual y deja un DataFrame listo para load."""

    def __init__(self, mode: str = "bootstrap"):
        super().__init__(PIPELINE_NAME, "transform")
        self.mode = mode

    def source(self, input_data: Optional[Any] = None) -> dict:
        if not input_data or "file_path" not in input_data:
            raise ValueError("AsgImssDataTransformer requiere 'file_path'.")
        return {
            "file_path": Path(input_data["file_path"]),
            "target_date": input_data["target_date"],
        }

    def action(self, input_data: Optional[Any] = None) -> dict:
        file_path: Path = input_data["file_path"]
        target_date: date = input_data["target_date"]
        self.logger.info(f"Transformando {file_path.name} (fecha_corte={target_date})")

        try:
            df = pd.read_csv(file_path, sep="|", dtype=str, keep_default_na=False, encoding="utf-8")
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, sep="|", dtype=str, keep_default_na=False, encoding="latin-1")

        # Normaliza headers (caracter U+FFFD en `tamano_patron`)
        df = df.rename(columns=CSV_HEADER_RENAMES)
        df.columns = [c.strip() for c in df.columns]

        rows_in = len(df)

        # Strip y filtros
        for c in df.columns:
            df[c] = df[c].astype(str).str.strip()

        # Drop filas completamente vacías
        df = df.replace("", np.nan)
        df = df.dropna(how="all")
        df = df.fillna("")

        # Drop duplicados
        before = len(df)
        df = df.drop_duplicates()
        if before != len(df):
            self.logger.info(f"  duplicados eliminados: {before - len(df):,}")

        # Normaliza cve_entidad y filtra Jalisco
        df["cve_entidad"] = df["cve_entidad"].str.zfill(2)
        df = df[df["cve_entidad"] == ENTIDAD_FILTRO_CVE].copy()
        self.logger.info(f"  filas tras filtro Jalisco ({ENTIDAD_FILTRO_CVE}): {len(df):,}")

        # Padding de sectores (None cuando viene vacío)
        for col, length in SECTOR_KEY_LENGTHS.items():
            mask = df[col] != ""
            df.loc[mask, col] = df.loc[mask, col].str.zfill(length)

        # tamano_patron uppercase
        df["tamano_patron"] = df["tamano_patron"].str.upper()

        # Casteo de métricas
        for c in METRIC_INT_COLUMNS:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)
        for c in METRIC_FLOAT_COLUMNS:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0).astype(float)

        # fecha_corte
        df["fecha_corte"] = target_date

        self.logger.info(
            f"  filas entrada={rows_in:,} → salida={len(df):,}; FKs CSV={list(CSV_FK_TO_STG_COLUMN.keys())}"
        )

        return {"dataframe": df, "target_date": target_date}

    def finalization(self, input_data: Optional[Any] = None) -> dict:
        return input_data
