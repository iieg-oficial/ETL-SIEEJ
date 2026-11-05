import pandas as pd

from core.pipelines.code.constants import (
    DEPORTES_SEPARATOR,
    FRAME_CAT_DEPORTE,
    FRAME_DATOS,
    NULL_VALUES,
    POLIDEPORTIVO_DEPORTES_FRAME,
    POLIDEPORTIVOS_COLUMNS,
    POLIDEPORTIVOS_FRAME,
    POLIDEPORTIVOS_INTEGER_COLUMNS,
    POLIDEPORTIVOS_RENAMES,
    POLIDEPORTIVOS_REQUIRED_COLUMNS,
    POLIDEPORTIVOS_UNIQUE_KEY,
)
from core.pipelines.code.helpers.common import add_dates, deporte_catalog, flat_frame, require, standardize
from core.utils.clean import list_values_to_null


def _bridge(df: pd.DataFrame, valid_ids: set[int]) -> pd.DataFrame:
    """One row per polideportivo and sport from the comma-separated `deportes`."""
    bridge = df[POLIDEPORTIVOS_UNIQUE_KEY].assign(deporte_id=df["deportes"].str.split(DEPORTES_SEPARATOR))
    bridge = bridge.explode("deporte_id")
    bridge["deporte_id"] = bridge["deporte_id"].str.strip()
    bridge = bridge[bridge["deporte_id"].notna() & (bridge["deporte_id"] != "")]

    numeric = pd.to_numeric(bridge["deporte_id"], errors="coerce")
    if numeric.isna().any():
        raise ValueError(f"Non numeric values in 'deportes': {sorted(bridge.loc[numeric.isna(), 'deporte_id'])}")

    bridge["deporte_id"] = numeric.astype(int).astype("Int64")
    unknown = sorted(set(bridge["deporte_id"]) - valid_ids)
    if unknown:
        raise ValueError(f"deportes ids missing from the sports catalog: {unknown}")

    return bridge.drop_duplicates().reset_index(drop=True)


def transform_polideportivos(frames: dict[str, pd.DataFrame], manifest: dict) -> tuple[dict, dict]:
    df = standardize(flat_frame(frames[FRAME_DATOS]), POLIDEPORTIVOS_RENAMES, POLIDEPORTIVOS_COLUMNS)
    df = list_values_to_null(df, rm_list=NULL_VALUES)

    for column in POLIDEPORTIVOS_INTEGER_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce").astype("Int64")
    for column in ("longitud", "latitud"):
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df = add_dates(df, manifest)
    require(df, POLIDEPORTIVOS_REQUIRED_COLUMNS)

    duplicated = df.loc[df.duplicated(POLIDEPORTIVOS_UNIQUE_KEY, keep=False), POLIDEPORTIVOS_UNIQUE_KEY]
    if not duplicated.empty:
        raise ValueError(f"Found duplicated {POLIDEPORTIVOS_UNIQUE_KEY} keys:\n{duplicated.to_string(index=False)}")

    deportes = deporte_catalog(frames[FRAME_CAT_DEPORTE])
    bridge = _bridge(df, {item["id"] for item in deportes})

    out = {POLIDEPORTIVOS_FRAME: df.drop(columns=["deportes"]), POLIDEPORTIVO_DEPORTES_FRAME: bridge}
    return out, {"deportes": deportes}
