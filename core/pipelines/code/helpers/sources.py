"""Readers for the files inside the CODE zips. File and layer names are never fixed."""

from pathlib import Path

import geopandas as gpd
import pandas as pd
from pyogrio import list_layers

from core.pipelines.code.constants import (
    CATALOG_HEADERS,
    CSV_GLOB,
    FRAME_DATOS,
    GPKG_GLOB,
    SHEET_ACTIVIDADES,
    SHEET_PUNTOS,
    XLSX_GLOB,
)


def read_reto_zip(extract_dir: Path) -> dict[str, pd.DataFrame]:
    sheets = sorted(extract_dir.rglob(XLSX_GLOB))
    if not sheets:
        raise FileNotFoundError(f"No .xlsx inside {extract_dir.name}")

    return pd.read_excel(sheets[0], sheet_name=[SHEET_PUNTOS, SHEET_ACTIVIDADES])


def _read_catalogs(extract_dir: Path) -> dict[str, pd.DataFrame]:
    """Classify each CSV by its header: a catalog is `<name>,id`."""
    catalogs: dict[str, pd.DataFrame] = {}
    for path in sorted(extract_dir.rglob(CSV_GLOB)):
        df = pd.read_csv(path, encoding="utf-8-sig")
        for frame, header in CATALOG_HEADERS.items():
            if frozenset(df.columns) == header:
                catalogs[frame] = df
    return catalogs


def read_geo_zip(extract_dir: Path) -> dict[str, pd.DataFrame]:
    """The gpkg with the data plus whichever catalogs the zip ships."""
    gpkgs = sorted(extract_dir.rglob(GPKG_GLOB))
    if not gpkgs:
        raise FileNotFoundError(f"No .gpkg inside {extract_dir.name}")

    layers = list_layers(gpkgs[0])
    if len(layers) != 1:
        raise ValueError(f"{gpkgs[0].name} has {len(layers)} layer(s), expected exactly one")

    return {FRAME_DATOS: gpd.read_file(gpkgs[0], layer=layers[0][0]), **_read_catalogs(extract_dir)}
