import pandas as pd
import unicodedata


def lowercase_headers(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = map(str.lower, df.columns)


def lowercase_df(df: pd.DataFrame) -> pd.DataFrame:
    string_cols = df.select_dtypes(include=["object", "string"]).columns
    df[string_cols] = df[string_cols].apply(lambda x: x.str.lower())
    return df


def titlecase_df(df: pd.DataFrame) -> pd.DataFrame:
    string_cols = df.select_dtypes(include=["object", "string"]).columns
    df[string_cols] = df[string_cols].apply(lambda x: x.str.title())
    return df


def lowercase_col(df: pd.DataFrame, col: str) -> None:
    df[col] = df[col].str.lower()


def uppercase_col(df: pd.DataFrame, col: str) -> None:
    df[col] = df[col].str.upper()


def title_col(df: pd.DataFrame, col: str) -> None:
    df[col] = df[col].str.title()


def capitalize_col(df: pd.DataFrame, col: str) -> None:
    df[col] = df[col].str.capitalize()


def normalize_col(df: pd.DataFrame, col: str) -> pd.Series:
    normalized = df[col].str.lower()
    normalized = normalized.str.normalize("NFKD").str.encode("ascii", errors="ignore").str.decode("utf-8")
    normalized = normalized.str.replace(" ", "_")
    return normalized


def strip_accents(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn")


def normalize_text(text):
    if not isinstance(text, str):
        return None
    text = " ".join(text.split()).replace(" ", "_").lower()
    return strip_accents(text)
