"""Steps shared by the gpkg datasets."""

from datetime import date
from typing import Any

import geopandas as gpd
import pandas as pd

from core.pipelines.code.constants import GEO_DATE_FORMAT, NULL_VALUES, WGS84
from core.utils.clean import list_values_to_null
from core.utils.normalize import normalize_text


def lon_lat(gdf: gpd.GeoDataFrame) -> tuple[pd.Series, pd.Series]:
    """Coordinates in WGS84 from the geometry.

    The `x_6368`/`y_6368` columns are not trusted: they hold degrees under an
    EPSG:6368 (UTM metres) name. The geometry carries the real CRS.
    """
    points = gdf.geometry.to_crs(WGS84)
    return points.x, points.y


def flat_frame(gdf: gpd.GeoDataFrame) -> pd.DataFrame:
    """Plain frame with `longitud`/`latitud` in place of the geometry."""
    df = pd.DataFrame(gdf.drop(columns=gdf.geometry.name))
    df["longitud"], df["latitud"] = lon_lat(gdf)
    return df


def standardize(df: pd.DataFrame, renames: dict[str, str], columns: list[str]) -> pd.DataFrame:
    """Normalize headers, rename to the schema names and keep the modeled columns."""
    df = df.dropna(how="all")
    df.columns = [normalize_text(column) for column in df.columns]
    df = df.rename(columns=renames)

    missing = [column for column in columns if column not in df.columns]
    if missing:
        raise KeyError(f"Source is missing modeled columns: {missing}")

    return df[columns].copy()


def add_dates(df: pd.DataFrame, manifest: dict[str, Any]) -> pd.DataFrame:
    cut = pd.to_datetime(df["fecha_corte"], format=GEO_DATE_FORMAT, errors="coerce")
    if cut.isna().any():
        raise ValueError(f"The source has {int(cut.isna().sum())} row(s) without a valid fecha (dd/mm/yyyy)")

    df["fecha_corte"] = cut.dt.date
    df["fecha_actualizacion_fuente"] = (
        pd.to_datetime(manifest["actualizado_en"]).date() if manifest.get("actualizado_en") else None
    )
    df["fecha_actualizacion"] = date.today()
    return df


def require(df: pd.DataFrame, columns: list[str]) -> None:
    """Fail here with the offending column, not later as a database error."""
    for column in columns:
        if df[column].isna().any():
            raise ValueError(f"Column '{column}' has {int(df[column].isna().sum())} row(s) without a value")


def deporte_catalog(cat_deporte: pd.DataFrame) -> list[dict]:
    """Sports with the id the dependency assigns them."""
    catalog = list_values_to_null(cat_deporte[["id", "deporte"]], rm_list=NULL_VALUES).dropna()
    catalog["id"] = catalog["id"].astype(int)
    return catalog.sort_values("id").to_dict("records")


def catalog_conflicts(incoming: list[dict], known: dict[int, str]) -> list[str]:
    """Pairs that would silently relabel a sport: same id with another name, or same name with another id.

    Names compare normalized, so a case or accent fix is an update, not a conflict.
    `known` is the stored catalog (or another dataset's) as `{id: name}`; the
    incoming pairs are also checked against each other.
    """
    ids = dict(known)
    names = {normalize_text(name): (id_, name) for id_, name in known.items()}
    conflicts = []

    for item in incoming:
        id_, name = item["id"], item["deporte"]
        key = normalize_text(name)
        if id_ in ids and normalize_text(ids[id_]) != key:
            conflicts.append(f"id {id_} is '{ids[id_]}', incoming '{name}'")
        elif key in names and names[key][0] != id_:
            conflicts.append(f"'{names[key][1]}' is id {names[key][0]}, incoming '{name}' with id {id_}")
        ids.setdefault(id_, name)
        names.setdefault(key, (id_, name))

    return conflicts
