import pandas as pd
from typing import Dict, List

from core.utils.normalize import normalize_text


def records_to_map(records: List[Dict], key: str) -> Dict:
    return {normalize_text(r[key]): r["id"] for r in records}


def map_multiindex(mapping: dict, key_arrays: list[pd.Series]) -> pd.Series:
    return pd.MultiIndex.from_arrays(key_arrays).map(mapping)
