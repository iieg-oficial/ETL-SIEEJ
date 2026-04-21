import hashlib

import pandas as pd
from typing import List, Dict, Any


def df_to_records(df: pd.DataFrame, columns: list) -> List[Dict[str, Any]]:
    """
    Converts DataFrame columns to a list of dictionaries.

    Returns:
        List of dicts where each dict represents a row
        Example: [{'cruce': '16 de Septiembre', 'zona': 'Norte'}, {'cruce': 'Autlán de Navarro', 'zona': 'Sur'}]
    """
    return df[columns].to_dict("records")


def df_to_records_with_id(df: pd.DataFrame, columns: list) -> List[Dict[str, Any]]:
    """
    Converts DataFrame to records with auto-generated sequential IDs.

    Returns:
        List of dicts with added 'id' field starting from 1
        Example: [{'id': 1, 'cruce': '16 de Septiembre'}, {'id': 2, 'cruce': 'Autlán de Navarro'}]
    """
    df = df.reset_index(drop=True)
    records = df[columns].to_dict("records")
    return [{"id": i, **record} for i, record in enumerate(records, start=1)]


def compute_record_hash(row: dict, fields: list[str]) -> str:
    parts = []
    for field in fields:
        val = row.get(field)
        parts.append("" if val is None else str(val))
    payload = "|".join(parts)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
