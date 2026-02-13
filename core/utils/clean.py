import pandas as pd
import numpy as np

from core.utils.normalize import normalize_col

def list_values_to_null(df: pd.DataFrame, rm_list: list = None) -> pd.DataFrame:
    rm_list = rm_list or ['NA', 'N/A', 'null', 'nan', '']
    rm_list_lower = [val.lower() for val in rm_list]

    df_copy = df.copy()
    string_cols = df_copy.select_dtypes(include=['object', 'string']).columns

    for col in string_cols:
        df_copy[col] = (df_copy[col]
                       .str.strip()
                       .str.strip('"')
                       .str.strip("'")
                       .str.strip()
                       .str.replace('\u200b', '', regex=False)
                       .str.replace('\xa0', ' ', regex=False)
                       .str.replace(r'\s+', ' ', regex=True)
                    )

        mask = df_copy[col].str.lower().isin(rm_list_lower) | (df_copy[col] == '')
        df_copy.loc[mask, col] = None

    return df_copy.replace({np.nan: None})

def drop_duplicates_col(df: pd.DataFrame,column: str) -> pd.DataFrame:
    normalized = normalize_col(df, column)
    mask = ~normalized.duplicated(keep='first')
    return df[mask]
