from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import geopandas as gpd
import pandas as pd

from core.pipelines.edafologia.constants import RENAME_HEADER
from core.pipelines.edafologia.mappings import CALIFICADORES_EDAFOLOGICOS, GRUPOS_EDAFOLOGICOS


def validate_catalog_coverage(gdf: gpd.GeoDataFrame) -> dict[str, Any]:
    checks = {
        "grupo1_origen": GRUPOS_EDAFOLOGICOS,
        "califp_g1_origen": CALIFICADORES_EDAFOLOGICOS,
        "califs_g1_origen": CALIFICADORES_EDAFOLOGICOS,
    }
    missing: dict[str, dict[str, int]] = {}
    coverage: dict[str, dict[str, int]] = {}
    for field, mapping in checks.items():
        counts = gdf[field].astype(str).value_counts().to_dict()
        missing[field] = {key: int(value) for key, value in counts.items() if key not in mapping}
        coverage[field] = {
            "observed_codes": len(counts),
            "mapped_codes": len([key for key in counts if key in mapping]),
            "unmapped_codes": len(missing[field]),
        }
    if any(missing[field] for field in missing):
        raise ValueError(f"Unmapped edafologia catalog codes inside Jalisco: {missing}")
    return {"coverage": coverage, "unmapped_codes": missing}


def catalog_id_lookup(mapping: dict[str, str]) -> dict[str, int]:
    return {key: idx for idx, key in enumerate(mapping, start=1)}


def apply_catalog_ids(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    result = gdf.copy()
    grupo_ids = catalog_id_lookup(GRUPOS_EDAFOLOGICOS)
    calificador_ids = catalog_id_lookup(CALIFICADORES_EDAFOLOGICOS)
    result["grupo_edafologico_id"] = result["grupo1_origen"].map(grupo_ids)
    result["calificador_primario_id"] = result["califp_g1_origen"].map(calificador_ids)
    result["calificador_secundario_id"] = result["califs_g1_origen"].map(calificador_ids)
    id_columns = ["grupo_edafologico_id", "calificador_primario_id", "calificador_secundario_id"]
    if result[id_columns].isna().any().any():
        missing = {column: int(result[column].isna().sum()) for column in id_columns if result[column].isna().any()}
        raise ValueError(f"Could not resolve catalog ids after coverage validation: {missing}")
    for column in id_columns:
        result[column] = result[column].astype(int)
    return result


def add_traceability(gdf: gpd.GeoDataFrame, manifest: dict[str, Any], processed_at: datetime) -> gpd.GeoDataFrame:
    result = gdf.copy()
    downloaded_at = manifest.get("downloaded_at")
    if not downloaded_at:
        raise ValueError("Extract manifest has no downloaded_at value for traceability")
    downloaded_ts = pd.to_datetime(downloaded_at)
    result["source_name"] = manifest["source_name"]
    result["source_url"] = manifest["source_url"]
    result["source_version"] = manifest["source_version"]
    result["source_file_name"] = Path(str(manifest["zip_path"])).name
    result["source_file_sha256"] = manifest["source_file_sha256"]
    result["source_downloaded_at"] = downloaded_ts.isoformat()
    result["processed_at"] = processed_at.isoformat()
    result["fecha_actualizacion"] = downloaded_ts.date().isoformat()
    result["pipeline_version"] = manifest["pipeline_version"]
    return result


def prepare_attributes(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    result = gdf.rename(columns=RENAME_HEADER).copy()
    result["source_objectid"] = pd.to_numeric(result["source_objectid"], errors="raise").astype(int)
    for column in ("shape_leng_origen", "shape_area_origen"):
        result[column] = pd.to_numeric(result[column], errors="coerce")
    return result
