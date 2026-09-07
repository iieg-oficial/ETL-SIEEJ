import pandas as pd
import numpy as np

from core.utils.normalize import normalize_col


def strip_text(series: pd.Series) -> pd.Series:
    """Recorta espacios, comillas y espacios invisibles de una columna de texto."""
    return (
        series.str.strip()
        .str.strip('"')
        .str.strip("'")
        .str.strip()
        .str.replace("\u200b", "", regex=False)
        .str.replace("\xa0", " ", regex=False)
        .str.replace(r"\s+", " ", regex=True)
    )


def to_nullable_int(series: pd.Series) -> pd.Series:
    """Castea a entero nullable; lo que no es número queda en pd.NA."""
    return pd.to_numeric(series, errors="coerce").astype("Int64")


def list_values_to_null(df: pd.DataFrame, rm_list: list = None) -> pd.DataFrame:
    rm_list = rm_list or ["NA", "N/A", "null", "nan", ""]
    rm_list_lower = [val.lower() for val in rm_list]

    df_copy = df.copy()
    string_cols = df_copy.select_dtypes(include=["object", "string"]).columns

    for col in string_cols:
        df_copy[col] = strip_text(df_copy[col])

        mask = df_copy[col].str.lower().isin(rm_list_lower) | (df_copy[col] == "")
        df_copy.loc[mask, col] = None

    return df_copy.replace({np.nan: None})


def drop_duplicates_col(df: pd.DataFrame, column: str) -> pd.DataFrame:
    normalized = normalize_col(df, column)
    mask = ~normalized.duplicated(keep="first")
    return df[mask]


def parse_boolean(val) -> "bool | None":
    if pd.isna(val) or val is None:
        return None
    v = str(val).strip().upper()
    if v in ("SI", "S"):
        return True
    if v in ("NO", "N"):
        return False
    return None


def nan_to_none(v):
    if v is None:
        return None
    if isinstance(v, float) and np.isnan(v):
        return None
    if pd.isna(v):
        return None
    return v
