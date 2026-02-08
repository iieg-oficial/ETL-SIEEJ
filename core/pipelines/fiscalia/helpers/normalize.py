import pandas as pd
import unicodedata

def lowercase_headers(df: pd.DataFrame)-> pd.DataFrame:
    df.columns = map(str.lower, df.columns)

def lowercase_df(df: pd.DataFrame)-> pd.DataFrame:
    string_cols = df.select_dtypes(include=['object', 'string']).columns
    df[string_cols] = df[string_cols].apply(lambda x: x.str.lower())
    return df

def titlecase_df(df: pd.DataFrame)-> pd.DataFrame:
    string_cols = df.select_dtypes(include=['object', 'string']).columns
    df[string_cols] = df[string_cols].apply(lambda x: x.str.title())
    return df

def list_values_to_null(df: pd.DataFrame, rm_list: list = None) -> pd.DataFrame:
    df_copy = df.copy()
    string_cols = df_copy.select_dtypes(include=['object', 'string']).columns

    for col in string_cols:
        df_copy[col] = df_copy[col].str.strip().str.strip('"').str.strip("'")
        df_copy[col] = df_copy[col].replace(
            {val: None for pattern in rm_list for val in [pattern, pattern.lower(), pattern.upper(), pattern.title()]}
        )
    return df_copy

def lowercase_col(df: pd.DataFrame, col:str) -> None:
    df[col] = df[col].str.lower()

def uppercase_col(df: pd.DataFrame, col:str) -> None:
    df[col] = df[col].str.upper()

def title_col(df: pd.DataFrame, col:str) -> None:
    df[col] = df[col].str.title()

def normalize_col(df: pd.DataFrame, col: str) -> pd.Series:
    normalized = df[col].str.lower()
    normalized = normalized.str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
    normalized = normalized.str.replace(' ', '_')
    return normalized

def drop_duplicates_col(df: pd.DataFrame,column: str) -> pd.DataFrame:
    normalized = normalize_col(df, column)
    mask = ~normalized.duplicated(keep='first')
    return df[mask]

def normalize_text(text):
   text  = text.replace(' ', '_').lower()
   return ''.join(c for c in unicodedata.normalize('NFD', text)
                  if unicodedata.category(c) != 'Mn')

