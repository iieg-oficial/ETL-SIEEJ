import pandas as pd

from core.constants.geo import JALISCO_CVE_ENTIDAD
from core.pipelines.code.constants import (
    ACADEMIAS_COLUMNS,
    ACADEMIAS_FRAME,
    ACADEMIAS_INTEGER_COLUMNS,
    ACADEMIAS_RENAMES,
    ACADEMIAS_REQUIRED_COLUMNS,
    FRAME_CAT_DEPORTE,
    FRAME_CAT_TIPO,
    FRAME_DATOS,
    NULL_VALUES,
)
from core.pipelines.code.helpers.common import add_dates, deporte_catalog, flat_frame, require, standardize
from core.utils.clean import list_values_to_null
from core.utils.logger import get_logger
from core.utils.normalize import normalize_text

logger = get_logger("code.transform")


def _resolve_deporte(df: pd.DataFrame, catalog: list[dict]) -> pd.Series:
    """Resolve by name: `cat_deporte` in the file does not match the shipped catalog."""
    ids = {normalize_text(item["deporte"]): item["id"] for item in catalog}
    resolved = df["deporte"].map(normalize_text).map(ids)

    unknown = sorted(df.loc[resolved.isna(), "deporte"].dropna().unique())
    if unknown:
        raise ValueError(f"deporte values missing from the sports catalog: {unknown}")

    stale = int((pd.to_numeric(df["cat_deporte"], errors="coerce") != resolved).sum())
    if stale:
        logger.warning(f"[transform] {stale} row(s) have a cat_deporte that disagrees with the catalog; used the name")

    return resolved.astype("Int64")


def _tipo_display(df: pd.DataFrame, cat_tipo: pd.DataFrame | None) -> dict[str, str]:
    """Normalized key to display name: the shipped catalog's form wins, then the first one seen in the data."""
    shipped = [] if cat_tipo is None else list(cat_tipo["tipo"].dropna())
    display: dict[str, str] = {}
    for name in [*shipped, *df["tipo"].dropna()]:
        name = " ".join(str(name).split())
        display.setdefault(normalize_text(name), name)
    return display


def transform_academias(frames: dict[str, pd.DataFrame], manifest: dict) -> tuple[dict, dict]:
    df = standardize(flat_frame(frames[FRAME_DATOS]), ACADEMIAS_RENAMES, ACADEMIAS_COLUMNS)
    df = list_values_to_null(df, rm_list=NULL_VALUES)

    for column in ACADEMIAS_INTEGER_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce").astype("Int64")
    for column in ("longitud", "latitud"):
        df[column] = pd.to_numeric(df[column], errors="coerce")

    deportes = deporte_catalog(frames[FRAME_CAT_DEPORTE])
    df["deporte_id"] = _resolve_deporte(df, deportes)
    df["entidad_id"] = JALISCO_CVE_ENTIDAD
    df = add_dates(df, manifest)
    require(df, ACADEMIAS_REQUIRED_COLUMNS)

    df = df.drop(columns=["deporte", "cat_deporte"])
    tipos = _tipo_display(df, frames.get(FRAME_CAT_TIPO))
    df["tipo"] = df["tipo"].map(lambda name: tipos[normalize_text(name)] if pd.notna(name) else None)
    catalogs = {"deportes": deportes, "tipos": [{"tipo": name} for name in sorted(tipos.values())]}
    return {ACADEMIAS_FRAME: df}, catalogs
