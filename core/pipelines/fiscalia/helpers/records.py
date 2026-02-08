import pandas as pd
from typing import List, Dict, Any


def df_to_records(df: pd.DataFrame, columns: list) -> List[Dict[str, Any]]:
    return df[columns].to_dict("records")


def df_to_records_with_id(df: pd.DataFrame, columns: list) -> List[Dict[str, Any]]:
    df = df.reset_index(drop=True)
    records = df[columns].to_dict("records")
    return [{"id": i, **record} for i, record in enumerate(records, start=1)]
