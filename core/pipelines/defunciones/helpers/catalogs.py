import re
from typing import Any

import pandas as pd

from core.pipelines.defunciones.constants import (
    ANIO_CATALOG,
    CHAPTER_TOTAL_GPO,
    CLAVE_COL,
    DEFUNCIONES_ACCENT_MAP,
    DEFUNCIONES_CANONICAL_TOKENS,
    DESCRIPCION_COL,
    EDAD_DATASET,
    NOMBRE_EDAD_COL,
    PROPER_NOUN_CATALOGS,
    SENTINEL_DESCRIPTIONS,
)
from core.utils.accents import apply_accents


def build_edad_catalog(df: pd.DataFrame) -> list[dict[str, Any]]:
    catalog = df.copy()
    catalog[CLAVE_COL] = pd.to_numeric(catalog[CLAVE_COL], errors="coerce")
    catalog[DESCRIPCION_COL] = catalog[DESCRIPCION_COL].str.strip()

    catalog = (
        catalog.dropna(subset=[CLAVE_COL, DESCRIPCION_COL])
        .drop_duplicates(subset=[CLAVE_COL])
        .astype({CLAVE_COL: int})
        .rename(columns={CLAVE_COL: "id", DESCRIPCION_COL: NOMBRE_EDAD_COL})
    )
    return catalog[["id", NOMBRE_EDAD_COL]].to_dict("records")


def static_catalog(mapping: dict[int, str]) -> list[dict[str, Any]]:
    return [{"id": code, "descripcion": desc} for code, desc in mapping.items()]


def build_capitulo_grupo(df: pd.DataFrame) -> list[dict[str, Any]]:
    catalog = df.copy()
    catalog["cap"] = pd.to_numeric(catalog["cap"], errors="coerce")
    catalog["gpo"] = pd.to_numeric(catalog["gpo"].replace("", str(CHAPTER_TOTAL_GPO)), errors="coerce")
    catalog["descripcion"] = catalog["descripcion"].str.strip()
    catalog = (
        catalog.dropna(subset=["cap", "gpo", "descripcion"])
        .drop_duplicates(subset=["cap", "gpo"])
        .astype({"cap": int, "gpo": int})
    )
    return catalog[["cap", "gpo", "descripcion"]].to_dict("records")


def build_edicion(df: pd.DataFrame) -> list[dict[str, Any]]:
    return [{"anio": int(a), "descripcion": f"Edición {int(a)}"} for a in df["anio"]]


def build_coded(df: pd.DataFrame) -> list[dict[str, Any]]:
    cat = df.copy()
    cat["codigo"] = cat[CLAVE_COL].str.strip()
    cat["descripcion"] = cat[DESCRIPCION_COL].str.strip()
    cat = cat[cat["codigo"] != ""].drop_duplicates(subset=["codigo"])
    return cat[["codigo", "descripcion"]].to_dict("records")


def build_versioned(df: pd.DataFrame) -> list[dict[str, Any]]:
    cat = df.copy()
    cat["codigo"] = pd.to_numeric(cat[CLAVE_COL], errors="coerce")
    cat["descripcion"] = cat[DESCRIPCION_COL].str.strip()
    cat = (
        cat.dropna(subset=["codigo", "descripcion"])
        .drop_duplicates(subset=["codigo", "edicion"])
        .astype({"codigo": int, "edicion": int})
        .rename(columns={"edicion": "anio"})
    )
    return cat[["codigo", "anio", "descripcion"]].to_dict("records")


def normalize_sentinel(descripcion: str) -> str:
    for pattern, label in SENTINEL_DESCRIPTIONS:
        if re.match(pattern, descripcion, flags=re.IGNORECASE):
            return label
    return descripcion


def build_localidades(df: pd.DataFrame) -> list[dict[str, Any]]:
    catalog = df.copy()
    for col in ("cve_ent", "cve_mun", "cve_loc"):
        catalog[col] = pd.to_numeric(catalog[col], errors="coerce")
    catalog["descripcion"] = catalog["descripcion"].str.strip().map(normalize_sentinel)
    catalog = catalog.dropna(subset=["cve_ent", "cve_mun", "cve_loc", "descripcion"]).astype(
        {"cve_ent": int, "cve_mun": int, "cve_loc": int, "edicion": int}
    )
    catalog["codigo"] = catalog.apply(
        lambda row: int(f"{row['cve_ent']:02d}{row['cve_mun']:03d}{row['cve_loc']:04d}"), axis=1
    )
    catalog = catalog.drop_duplicates(subset=["codigo", "edicion"]).rename(columns={"edicion": "anio"})
    return catalog[["codigo", "cve_ent", "cve_mun", "cve_loc", "anio", "descripcion"]].to_dict("records")


def build_catalog(df: pd.DataFrame, text_key: bool) -> list[dict[str, Any]]:
    catalog = df.copy()
    catalog[DESCRIPCION_COL] = catalog[DESCRIPCION_COL].str.strip()
    if text_key:
        catalog[CLAVE_COL] = catalog[CLAVE_COL].str.strip()
        catalog = catalog[catalog[CLAVE_COL] != ""]
    else:
        catalog[CLAVE_COL] = pd.to_numeric(catalog[CLAVE_COL], errors="coerce")

    catalog = (
        catalog.dropna(subset=[CLAVE_COL, DESCRIPCION_COL])
        .drop_duplicates(subset=[CLAVE_COL])
        .rename(columns={CLAVE_COL: "id"})
    )
    if not text_key:
        catalog["id"] = catalog["id"].astype(int)
    return catalog[["id", DESCRIPCION_COL]].to_dict("records")


def restore_acronyms(text: str) -> str:
    for token in DEFUNCIONES_CANONICAL_TOKENS:
        text = re.sub(rf"\b{token}\b", token, text, flags=re.IGNORECASE)
    return text


def normalize_descriptions(catalogs: dict[str, list[dict[str, Any]]]) -> None:
    for name, records in catalogs.items():
        if name in PROPER_NOUN_CATALOGS:
            continue
        field = NOMBRE_EDAD_COL if name == EDAD_DATASET else "descripcion"
        for record in records:
            value = record.get(field)
            if isinstance(value, str):
                value = restore_acronyms(apply_accents(value, DEFUNCIONES_ACCENT_MAP))
                if name == ANIO_CATALOG:
                    value = re.sub(r"^Año\s+", "", value)
                record[field] = value
