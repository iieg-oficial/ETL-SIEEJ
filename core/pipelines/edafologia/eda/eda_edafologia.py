"""Reproducible EDA report for the Edafologia pipeline."""

from __future__ import annotations

import hashlib
import json
import os
import sys
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).resolve().parents[4]))

import psycopg2
from psycopg2.extras import RealDictCursor

from core.pipelines.edafologia.constants import (
    CANONICAL_HASH_ALGORITHM,
    CANONICAL_HASH_FIELD_SEPARATOR,
    CANONICAL_HASH_FORMULA_VERSION,
    CANONICAL_HASH_GEOMETRY_SERIALIZATION,
    CANONICAL_HASH_NULL_TOKEN,
    CANONICAL_HASH_ROW_SEPARATOR,
    CANONICAL_SRID,
    CONTROLLED_CATALOG_FL_REFERENCE_PAGE,
    CONTROLLED_CATALOG_REFERENCE_DOCUMENT,
    CONTROLLED_CATALOG_REFERENCE_DOCUMENT_VERSION,
    CONTROLLED_CATALOG_REFERENCE_INSTITUTION,
    CONTROLLED_CATALOG_REFERENCE_SCALE,
    CONTROLLED_CATALOG_REFERENCE_YEAR,
    EDA_REPORT_FILENAME,
    PIPELINE_NAME,
    PIPELINE_VERSION,
    SOURCE_FILENAME,
    SOURCE_NAME,
    SOURCE_VERSION,
)
from core.utils.files import sha256_file
from core.pipelines.edafologia.mappings import (
    CALIFICADORES_EDAFOLOGICOS,
    GRUPOS_EDAFOLOGICOS,
    catalog_sha256,
)
from core.utils.logger import get_logger


def repo_root() -> Path:
    """Return the repository root for this pipeline checkout."""
    return Path(__file__).resolve().parents[4]


def relative_path(path: Path) -> str:
    """Return a repository-relative path when possible."""
    root = repo_root()
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(root))
    except ValueError:
        return str(path)


def read_json(path: Path) -> dict[str, Any]:
    """Read a JSON object from a required artifact path."""
    if not path.exists():
        raise FileNotFoundError(f"Required EDA artifact is missing: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def validate_sha256(path: Path, expected: str, label: str) -> str:
    """Validate a file SHA-256 and return the computed digest."""
    if not path.exists():
        raise FileNotFoundError(f"Required {label} artifact is missing: {path}")
    actual = sha256_file(path)
    if actual != expected:
        raise ValueError(f"{label} SHA-256 mismatch: expected {expected}, got {actual}")
    return actual


def read_local_db_env() -> dict[str, str]:
    """Read local database settings from environment or the ignored Flyway env file."""
    keys = ("DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT", "DB_NAME")
    values = {key: os.getenv(key, "") for key in keys}
    if all(values.values()):
        return values
    env_path = repo_root() / "migrations" / PIPELINE_NAME / ".env"
    if not env_path.exists():
        missing = ", ".join(key for key, value in values.items() if not value)
        raise RuntimeError(f"Missing database settings ({missing}) and {env_path} does not exist")
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if "=" not in line or line.lstrip().startswith("#"):
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key in values and not values[key]:
            values[key] = value.strip().strip('"')
    missing = [key for key, value in values.items() if not value]
    if missing:
        raise RuntimeError(f"Missing database settings: {', '.join(missing)}")
    return values


def connect_database():
    """Open a PostgreSQL connection using local ignored credentials."""
    settings = read_local_db_env()
    return psycopg2.connect(
        host=settings["DB_HOST"],
        port=settings["DB_PORT"],
        dbname=settings["DB_NAME"],
        user=settings["DB_USER"],
        password=settings["DB_PASSWORD"],
    )


def canonical_hash_formula() -> dict[str, Any]:
    """Return the documented canonical hash formula."""
    return {
        "version": CANONICAL_HASH_FORMULA_VERSION,
        "algorithm": CANONICAL_HASH_ALGORITHM,
        "encoding": "utf-8",
        "row_separator": "\\n",
        "field_separator": "U+001F",
        "null_token": CANONICAL_HASH_NULL_TOKEN,
        "row_order": "lexicographic order by the declared logical key fields",
        "field_order": "logical key fields followed by payload fields exactly as listed per hash",
        "geometry_serialization": CANONICAL_HASH_GEOMETRY_SERIALIZATION,
        "serial_ids": "excluded from keys and payloads; catalog and boundary source claves are used instead",
        "canonical_key_fields": ["source_version", "source_objectid"],
        "overlay_key_fields": ["source_version", "source_objectid", "fuente_limite_clave", "municipality_id"],
    }


def canonical_hash(
    records: Iterable[Mapping[str, Any]], key_fields: Sequence[str], payload_fields: Sequence[str]
) -> str:
    """Hash records deterministically using logical keys and explicit payload fields."""
    rows = []
    for record in records:
        ordered = [record.get(field) for field in (*key_fields, *payload_fields)]
        rows.append(tuple(format_hash_value(value) for value in ordered))
    rows.sort()
    payload = CANONICAL_HASH_ROW_SEPARATOR.join(CANONICAL_HASH_FIELD_SEPARATOR.join(row) for row in rows)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def format_hash_value(value: Any) -> str:
    """Format one value for canonical hash serialization."""
    if value is None:
        return CANONICAL_HASH_NULL_TOKEN
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def fetch_records(sql: str) -> list[dict[str, Any]]:
    """Fetch query rows as dictionaries from the local edafologia database."""
    with connect_database() as connection, connection.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(sql)
        return [dict(row) for row in cursor.fetchall()]


def compute_database_hashes() -> dict[str, str]:
    """Compute canonical validation hashes from PostgreSQL without SERIAL IDs."""
    canonical_geom = fetch_records(
        """
        SELECT
            source_version,
            source_objectid::text AS source_objectid,
            lower(encode(ST_AsEWKB(geom, 'NDR'), 'hex')) AS geom_ewkb_hex
        FROM edafologias
        """
    )
    canonical_rel = fetch_records(
        """
        SELECT
            e.source_version,
            e.source_objectid::text AS source_objectid,
            e.clave_wrb,
            g.clave AS grupo_clave,
            cp.clave AS calificador_primario_clave,
            cs.clave AS calificador_secundario_clave,
            e.grupo1_origen,
            e.califp_g1_origen,
            e.califs_g1_origen,
            e.source_file_sha256
        FROM edafologias AS e
        JOIN grupos_edafologicos AS g ON g.id = e.grupo_edafologico_id
        JOIN calificadores_edafologicos AS cp ON cp.id = e.calificador_primario_id
        JOIN calificadores_edafologicos AS cs ON cs.id = e.calificador_secundario_id
        """
    )
    overlay_geom = fetch_records(
        """
        SELECT
            f.source_version,
            e.source_objectid::text AS source_objectid,
            l.clave AS fuente_limite_clave,
            f.municipality_id::text AS municipality_id,
            lower(encode(ST_AsEWKB(f.geom, 'NDR'), 'hex')) AS geom_ewkb_hex
        FROM edafologia_fragmentos_municipales AS f
        JOIN edafologias AS e ON e.id = f.edafologia_id
        JOIN fuentes_limites_municipales AS l ON l.id = f.fuente_limite_municipal_id
        """
    )
    overlay_rel = fetch_records(
        """
        SELECT
            f.source_version,
            e.source_objectid::text AS source_objectid,
            l.clave AS fuente_limite_clave,
            f.municipality_id::text AS municipality_id,
            to_char(f.area_m2, 'FM999999999999999990.999999999999999') AS area_m2,
            to_char(f.area_ha, 'FM999999999999999990.999999999999999') AS area_ha,
            to_char(f.pct_poligono_fuente, 'FM999999999999999990.999999999999999') AS pct_poligono_fuente,
            to_char(f.pct_municipio_total, 'FM999999999999999990.999999999999999') AS pct_municipio_total,
            to_char(f.pct_cobertura_edafologica, 'FM999999999999999990.999999999999999') AS pct_cobertura_edafologica,
            f.es_fragmento_pequenio
        FROM edafologia_fragmentos_municipales AS f
        JOIN edafologias AS e ON e.id = f.edafologia_id
        JOIN fuentes_limites_municipales AS l ON l.id = f.fuente_limite_municipal_id
        """
    )
    key_canonical = ["source_version", "source_objectid"]
    key_overlay = ["source_version", "source_objectid", "fuente_limite_clave", "municipality_id"]
    return {
        "canonical_geometry": canonical_hash(canonical_geom, key_canonical, ["geom_ewkb_hex"]),
        "canonical_relations": canonical_hash(
            canonical_rel,
            key_canonical,
            [
                "clave_wrb",
                "grupo_clave",
                "calificador_primario_clave",
                "calificador_secundario_clave",
                "grupo1_origen",
                "califp_g1_origen",
                "califs_g1_origen",
                "source_file_sha256",
            ],
        ),
        "overlay_geometry_iieg": canonical_hash(
            [row for row in overlay_geom if row["fuente_limite_clave"] == "iieg"], key_overlay, ["geom_ewkb_hex"]
        ),
        "overlay_geometry_inegi": canonical_hash(
            [row for row in overlay_geom if row["fuente_limite_clave"] == "inegi"], key_overlay, ["geom_ewkb_hex"]
        ),
        "overlay_logical_iieg": canonical_hash(
            [row for row in overlay_rel if row["fuente_limite_clave"] == "iieg"],
            key_overlay,
            [
                "area_m2",
                "area_ha",
                "pct_poligono_fuente",
                "pct_municipio_total",
                "pct_cobertura_edafologica",
                "es_fragmento_pequenio",
            ],
        ),
        "overlay_logical_inegi": canonical_hash(
            [row for row in overlay_rel if row["fuente_limite_clave"] == "inegi"],
            key_overlay,
            [
                "area_m2",
                "area_ha",
                "pct_poligono_fuente",
                "pct_municipio_total",
                "pct_cobertura_edafologica",
                "es_fragmento_pequenio",
            ],
        ),
    }


def database_summary() -> dict[str, Any]:
    """Collect database counts, constraints, indexes and comment coverage."""
    sql = """
    WITH counts AS (
      SELECT 'grupos_edafologicos' metric, count(*)::text value FROM grupos_edafologicos
      UNION ALL SELECT 'calificadores_edafologicos', count(*)::text FROM calificadores_edafologicos
      UNION ALL SELECT 'fuentes_limites_municipales', count(*)::text FROM fuentes_limites_municipales
      UNION ALL SELECT 'edafologias', count(*)::text FROM edafologias
      UNION ALL SELECT 'fragmentos_total', count(*)::text FROM edafologia_fragmentos_municipales
      UNION ALL SELECT 'resumen_total', count(*)::text FROM edafologia_resumenes_municipales
    ), rels AS (
      SELECT c.oid, c.relname
      FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
      WHERE n.nspname='public'
        AND c.relname IN ('grupos_edafologicos','calificadores_edafologicos','fuentes_limites_municipales','edafologias','edafologia_fragmentos_municipales','edafologia_resumenes_municipales')
    ), comments AS (
      SELECT 'objects_expected' metric, count(*)::text value FROM rels
      UNION ALL SELECT 'objects_commented', count(*) FILTER (WHERE obj_description(oid, 'pg_class') IS NOT NULL)::text FROM rels
      UNION ALL SELECT 'columns_expected', count(*)::text FROM information_schema.columns WHERE table_schema='public' AND table_name IN (SELECT relname FROM rels)
      UNION ALL SELECT 'columns_commented', count(*) FILTER (WHERE col_description((quote_ident(table_name))::regclass::oid, ordinal_position) IS NOT NULL)::text
      FROM information_schema.columns WHERE table_schema='public' AND table_name IN (SELECT relname FROM rels)
    ), idx AS (
      SELECT 'gist_indexes' metric, count(*)::text value FROM pg_indexes WHERE schemaname='public' AND indexdef ILIKE '%USING gist%' AND (tablename='edafologias' OR tablename='edafologia_fragmentos_municipales')
      UNION ALL SELECT 'btree_indexes', count(*)::text FROM pg_indexes WHERE schemaname='public' AND indexdef NOT ILIKE '%USING gist%' AND tablename IN ('grupos_edafologicos','calificadores_edafologicos','fuentes_limites_municipales','edafologias','edafologia_fragmentos_municipales')
      UNION ALL SELECT 'constraints', count(*)::text FROM information_schema.table_constraints WHERE table_schema='public' AND table_name IN ('grupos_edafologicos','calificadores_edafologicos','fuentes_limites_municipales','edafologias','edafologia_fragmentos_municipales')
    )
    SELECT * FROM counts UNION ALL SELECT * FROM comments UNION ALL SELECT * FROM idx ORDER BY metric;
    """
    return {row["metric"]: int(row["value"]) for row in fetch_records(sql)}


def build_report() -> dict[str, Any]:
    """Build the deterministic EDA report from manifests, artifacts and database state."""
    root = repo_root()
    extract_manifest_path = root / "data" / "extract" / PIPELINE_NAME / "manifest.json"
    transform_manifest_path = root / "data" / "transform" / PIPELINE_NAME / "transform_manifest.json"
    overlay_manifest_path = root / "data" / "transform" / PIPELINE_NAME / "municipal_overlay" / "overlay_manifest.json"
    extract_manifest = read_json(extract_manifest_path)
    transform_manifest = read_json(transform_manifest_path)
    overlay_manifest = read_json(overlay_manifest_path)

    zip_path = Path(extract_manifest["zip_path"])
    if not zip_path.is_absolute():
        zip_path = root / zip_path
    zip_sha = validate_sha256(zip_path, extract_manifest["source_file_sha256"], "source ZIP")
    boundaries_path = root / extract_manifest["auxiliary_inputs"]["municipal_boundaries"]["output_gpkg"]
    boundaries_sha = validate_sha256(
        boundaries_path,
        extract_manifest["auxiliary_inputs"]["municipal_boundaries"]["gpkg_sha256"],
        "municipal boundaries",
    )
    transform_output = root / transform_manifest["output_path"]
    transform_sha = validate_sha256(transform_output, transform_manifest["output_sha256"], "transform output")
    overlay_output = root / overlay_manifest["output_path"]
    overlay_sha = validate_sha256(overlay_output, overlay_manifest["output_sha256"], "overlay output")
    pdf_path = root / "data" / "extract" / PIPELINE_NAME / "extracted" / "diccionario_de_datos" / "702825092023.pdf"
    pdf_sha = sha256_file(pdf_path) if pdf_path.exists() else None

    db = database_summary()
    hashes = compute_database_hashes()
    inventory = extract_manifest["inventory"]
    selected = next(item for item in inventory if item["layer"] == extract_manifest["selected_layer"])
    overlay_sources = overlay_manifest["sources"]
    report = {
        "pipeline": PIPELINE_NAME,
        "pipeline_version": PIPELINE_VERSION,
        "source": {
            "institution": "INEGI",
            "product": SOURCE_NAME,
            "scale": "1:250,000",
            "source_version": SOURCE_VERSION,
            "zip_file": SOURCE_FILENAME,
            "source_url": extract_manifest["source_url"],
            "zip_sha256": zip_sha,
            "documentary_pdf": relative_path(pdf_path),
            "documentary_pdf_sha256": pdf_sha,
            "documentary_reference": {
                "institution": CONTROLLED_CATALOG_REFERENCE_INSTITUTION,
                "document": CONTROLLED_CATALOG_REFERENCE_DOCUMENT,
                "scale": CONTROLLED_CATALOG_REFERENCE_SCALE,
                "document_version": CONTROLLED_CATALOG_REFERENCE_DOCUMENT_VERSION,
                "year": CONTROLLED_CATALOG_REFERENCE_YEAR,
                "fl_reference_page": CONTROLLED_CATALOG_FL_REFERENCE_PAGE,
            },
        },
        "inventory": {
            "candidate_count": len(inventory),
            "national_feature_count": extract_manifest["selected_feature_count"],
            "selected_layer": extract_manifest["selected_layer"],
            "selected_path": relative_path(root / extract_manifest["selected_path"]),
            "format": selected["format"],
            "fields": extract_manifest["selected_fields"],
            "original_crs": extract_manifest["selected_crs"],
            "geometry_type": extract_manifest["selected_geometry_type"],
            "initial_invalid_geometries": transform_manifest["geometry_repair"]["initial"]["invalid_before"],
            "selection_criteria": [
                "polygonal layer",
                "contains Grupo1, Califp_g1 and Califs_g1",
                "matches *_area",
                "excludes *_pto",
            ],
        },
        "transform": {
            "final_feature_count": transform_manifest["final_feature_count"],
            "canonical_srid": CANONICAL_SRID,
            "geometry_types": transform_manifest["final_geometry_types"],
            "null_geometries": transform_manifest["spatial_validation"]["null_geometries"],
            "empty_geometries": transform_manifest["spatial_validation"]["empty_geometries"],
            "invalid_geometries": transform_manifest["spatial_validation"]["invalid_geometries"],
            "final_area_m2": transform_manifest["spatial_validation"]["area_sum_m2"],
            "repair_policy": "Repair invalid source geometries, extract polygonal components, clip to canonical coverage and keep positive-area MultiPolygons.",
            "source_invalid_repaired": transform_manifest["geometry_repair"]["initial"]["repaired_count"],
            "output_gpkg": relative_path(transform_output),
            "output_sha256": transform_sha,
        },
        "catalogs": {
            "groups": {"count": len(GRUPOS_EDAFOLOGICOS), "sha256": catalog_sha256(GRUPOS_EDAFOLOGICOS)},
            "qualifiers": {
                "count": len(CALIFICADORES_EDAFOLOGICOS),
                "sha256": catalog_sha256(CALIFICADORES_EDAFOLOGICOS),
            },
            "unified_qualifier_catalog": True,
            "fl": CALIFICADORES_EDAFOLOGICOS["fl"],
            "operational_values": {"N": CALIFICADORES_EDAFOLOGICOS["N"], "N/A": CALIFICADORES_EDAFOLOGICOS["N/A"]},
            "limitations": "Mappings are transcribed and versioned in code; N and N/A are operational controlled values, not official documentary codes.",
            "coverage": transform_manifest["catalog_coverage"],
        },
        "boundaries": {
            "gpkg": relative_path(boundaries_path),
            "gpkg_sha256": boundaries_sha,
            "municipios_iieg": extract_manifest["auxiliary_inputs"]["municipal_boundaries"]["layers"][
                "municipios_iieg"
            ],
            "municipios_inegi": extract_manifest["auxiliary_inputs"]["municipal_boundaries"]["layers"][
                "municipios_inegi"
            ],
            "symmetric_difference_m2": transform_manifest["mask_statistics"]["area_symmetric_difference_m2"],
            "symmetric_difference_km2": transform_manifest["mask_statistics"]["area_symmetric_difference_m2"]
            / 1_000_000,
            "method_note": "IIEG and INEGI boundaries are both preserved; neither source is declared correct.",
        },
        "overlay": {
            "output_gpkg": relative_path(overlay_output),
            "output_sha256": overlay_sha,
            "fragments_iieg": overlay_manifest["fragments_by_source"]["iieg"],
            "fragments_inegi": overlay_manifest["fragments_by_source"]["inegi"],
            "fragments_total": overlay_manifest["final_fragments"],
            "coverage_iieg_pct": overlay_sources["iieg"]["territorial_closure"]["coverage_pct"],
            "coverage_inegi_pct": overlay_sources["inegi"]["territorial_closure"]["coverage_pct"],
            "contacts_policy": "Non-polygonal and non-positive components are discarded; all positive-area polygonal fragments are kept.",
            "small_fragments_iieg": overlay_sources["iieg"]["small_fragments"]["thresholds"],
            "small_fragments_inegi": overlay_sources["inegi"]["small_fragments"]["thresholds"],
        },
        "database": {
            "tables": [
                "grupos_edafologicos",
                "calificadores_edafologicos",
                "fuentes_limites_municipales",
                "edafologias",
                "edafologia_fragmentos_municipales",
            ],
            "view": "edafologia_resumenes_municipales",
            "counts": db,
            "strategy": "Bootstrap-only load with upsert for catalogs/canonical records and idempotent replacement of municipal fragments by source_version and boundary source.",
        },
        "canonical_hashes": {
            "formula": canonical_hash_formula(),
            "source_version": SOURCE_VERSION,
            "values": hashes,
        },
        "limitations": [
            "Historical non-iterable publication; only bootstrap is implemented.",
            "No automatic update schedule exists for new INEGI publications.",
            "source_objectid is not guaranteed to remain stable across future publications.",
            "IIEG and INEGI municipal boundaries differ and are both retained.",
            "Mappings are transcribed and versioned; they are not regenerated from the PDF at runtime.",
            "Positive-area sliver fragments are preserved and monitored instead of removed by tolerance.",
            "Intermediate artifacts are ignored by Git but preserved during execution for traceability.",
        ],
    }
    return report


def write_report(report: Mapping[str, Any], path: Path) -> None:
    """Write a deterministic JSON report."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp.json")
    temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def main() -> dict[str, Any]:
    """Generate the Edafologia EDA JSON report."""
    report = build_report()
    output = Path(__file__).resolve().parent / EDA_REPORT_FILENAME
    write_report(report, output)
    logger = get_logger("edafologia.eda")
    logger.info("Wrote Edafologia EDA report to %s", output)
    return report


if __name__ == "__main__":
    main()
