import pandas as pd

from core.pipelines.pobreza_multidimencional.consts import (
    DATA_YEARS,
    EXCEL_COL_NAMES,
    EXCEL_SHEET,
    EXCEL_SKIP_ROWS,
    EXCEL_USE_COLS,
    INDICATOR_PREFIXES,
    NULL_VALUES,
)
from core.utils.clean import list_values_to_null


def read_excel(file_path: str) -> pd.DataFrame:
    """Lee el XLSX saltando los encabezados multi-nivel y asigna nombres de columna.

    Args:
        file_path: Ruta al archivo XLSX.

    Returns:
        DataFrame con columnas normalizadas y filas válidas.
    """
    df = pd.read_excel(
        file_path,
        sheet_name=EXCEL_SHEET,
        header=None,
        skiprows=EXCEL_SKIP_ROWS,
        usecols=EXCEL_USE_COLS,
        dtype=str,
    )
    df.columns = EXCEL_COL_NAMES

    df = df[df["cve_mun"].str.match(r"^\d{5}$", na=False)].copy()
    df = list_values_to_null(df, rm_list=NULL_VALUES)
    df = cast_numeric(df)

    return df.reset_index(drop=True)


def cast_numeric(df: pd.DataFrame) -> pd.DataFrame:
    """Convierte las columnas de métricas a float o int según el sufijo.

    Args:
        df: DataFrame con columnas de indicadores en formato str.

    Returns:
        DataFrame con columnas numéricas convertidas.
    """
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


def wide_to_tidy(df_wide: pd.DataFrame) -> pd.DataFrame:
    """Convierte formato wide (un municipio por fila) a tidy (municipio × año).

    Args:
        df_wide: DataFrame en formato wide con columnas por año.

    Returns:
        DataFrame tidy con una fila por municipio por año.
    """
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
