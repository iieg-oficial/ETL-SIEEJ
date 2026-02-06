import pandas as pd
from typing import List, Dict, Any


def df_to_records(
    df: pd.DataFrame,
    columns: list
) -> List[Dict[str, Any]]:

    return (
        df[columns].to_dict("records")
    )

