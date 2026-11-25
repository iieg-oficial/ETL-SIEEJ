import pandas as pd

from core.constants.geo import JALISCO_CVE_ENTIDAD
from core.pipelines.code.constants import (
    ACTIVIDADES_COLUMNS,
    FRAME_DATOS,
    INTEGER_COLUMNS,
    NULL_VALUES,
    PUNTOS_COLUMNS,
    PUNTOS_FRAME,
    PUNTOS_RENAMES,
    REGION_COLUMNS,
    REGION_RENAMES,
    REQUIRED_COLUMNS,
    SHEET_ACTIVIDADES,
    SHEET_PUNTOS,
    UNIQUE_KEY,
)
from core.pipelines.code.helpers.common import add_dates, flat_frame, require, standardize
from core.pipelines.code.helpers.values import title_es
from core.utils.clean import list_values_to_null


def region_lookup(base: pd.DataFrame) -> dict[int, str]:
    """Region of each municipio from the xlsx; the gpkg does not carry it."""
    df = list_values_to_null(standardize(base, REGION_RENAMES, REGION_COLUMNS), rm_list=NULL_VALUES)
    df["municipio_id"] = pd.to_numeric(df["municipio_id"], errors="coerce").astype("Int64")
    df["region"] = df["region"].map(title_es)
    df = df.dropna().drop_duplicates()

    repeated = sorted(df.loc[df["municipio_id"].duplicated(), "municipio_id"].unique())
    if repeated:
        raise ValueError(f"municipio_id values with more than one region: {repeated}")

    return dict(zip(df["municipio_id"], df["region"]))


def prepare_puntos(points: pd.DataFrame, base: pd.DataFrame, manifest: dict) -> pd.DataFrame:
    df = standardize(flat_frame(points), PUNTOS_RENAMES, PUNTOS_COLUMNS)
    df = list_values_to_null(df, rm_list=NULL_VALUES)

    for column in INTEGER_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce").astype("Int64")

    df["entidad_id"] = JALISCO_CVE_ENTIDAD
    df = add_dates(df, manifest)
    require(df, REQUIRED_COLUMNS)

    regions = region_lookup(base)
    df["region"] = df["municipio_id"].map(regions)
    unknown = sorted(df.loc[df["region"].isna(), "municipio_id"].unique())
    if unknown:
        raise ValueError(f"municipio_id values without a region in the xlsx: {unknown}")

    duplicated = df.loc[df.duplicated(UNIQUE_KEY, keep=False), UNIQUE_KEY].drop_duplicates()
    if not duplicated.empty:
        raise ValueError(f"Found duplicated {UNIQUE_KEY} keys:\n{duplicated.to_string(index=False)}")

    return df


def build_catalogs(puntos: pd.DataFrame, actividades: pd.DataFrame) -> dict[str, list[dict]]:
    actividades = list_values_to_null(actividades[ACTIVIDADES_COLUMNS], rm_list=NULL_VALUES).dropna()
    actividades["id"] = actividades["id"].astype(int)

    unknown = sorted(set(puntos["actividad_id"].dropna()) - set(actividades["id"]))
    if unknown:
        raise ValueError(f"actividad_id values missing from the activities catalog: {unknown}")

    return {
        "actividades": actividades.sort_values("id").to_dict("records"),
        "regiones": [{"region": value} for value in sorted(puntos["region"].dropna().unique())],
    }


def transform_reto(frames: dict[str, pd.DataFrame], manifest: dict) -> tuple[dict, dict]:
    puntos = prepare_puntos(frames[FRAME_DATOS], frames[SHEET_PUNTOS], manifest)
    return {PUNTOS_FRAME: puntos}, build_catalogs(puntos, frames[SHEET_ACTIVIDADES])
