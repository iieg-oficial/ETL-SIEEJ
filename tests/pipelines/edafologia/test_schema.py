from pathlib import Path

from core.pipelines.edafologia.schemas import (
    EdafologiaFragmentosMunicipales,
    Edafologias,
    FuentesLimitesMunicipales,
)


MIGRATIONS = Path("migrations/edafologia/sql")


def test_sqlalchemy_columns_follow_physical_alignment_order():
    assert FuentesLimitesMunicipales.columns() == [
        "id",
        "clave",
        "nombre_fuente",
        "descripcion",
        "version",
        "procedencia",
    ]
    assert Edafologias.columns() == [
        "id",
        "identificador_objeto_fuente",
        "grupo_edafologico_id",
        "calificador_primario_id",
        "calificador_secundario_id",
        "longitud_origen",
        "superficie_origen",
        "version_fuente",
        "clave_wrb",
        "grupo1_origen",
        "califp_g1_origen",
        "califs_g1_origen",
        "grupo2_origen",
        "califp_g2_origen",
        "califs_g2_origen",
        "grupo3_origen",
        "califp_g3_origen",
        "clase_textural_origen",
        "limite_superior_origen",
        "fase_fisica_origen",
        "fase_quimica_origen",
        "nombre_fuente",
        "url_fuente",
        "nombre_archivo_fuente",
        "sha256_archivo_fuente",
        "fecha_descarga_fuente",
        "fecha_procesamiento",
        "fecha_actualizacion",
        "geometria",
    ]
    assert EdafologiaFragmentosMunicipales.columns() == [
        "id",
        "edafologia_id",
        "municipio_id",
        "fuente_limite_municipal_id",
        "superficie_m2",
        "superficie_ha",
        "porcentaje_poligono_fuente",
        "porcentaje_municipio_total",
        "porcentaje_cobertura_edafologica",
        "es_fragmento_pequenio",
        "version_fuente",
        "geometria",
    ]


def test_flyway_contract_keeps_logical_municipality_reference():
    fragments = (MIGRATIONS / "V4__municipal_products_edafologia.sql").read_text(encoding="utf-8")
    fdw = (MIGRATIONS / "V7__municipality_reference_edafologia.sql").read_text(encoding="utf-8")

    assert "municipio_id INTEGER NOT NULL" in fragments
    assert "edafologia_id,\n        municipio_id,\n        fuente_limite_municipal_id" in fragments
    assert "REFERENCES cvegeo" not in fragments
    assert "f.municipio_id = m.cve_mun" in fdw
    assert "m.cve_ent = 14" in fdw


def test_flyway_contract_uses_spanish_persisted_names_and_nonempty_boundary_version():
    catalogs = (MIGRATIONS / "V2__catalogs_edafologia.sql").read_text(encoding="utf-8")
    canonical = (MIGRATIONS / "V3__tables_edafologia.sql").read_text(encoding="utf-8")
    fragments = (MIGRATIONS / "V4__municipal_products_edafologia.sql").read_text(encoding="utf-8")

    assert "version VARCHAR(120) NOT NULL" in catalogs
    assert "nombre_fuente VARCHAR(120) NOT NULL" in catalogs
    assert "geometria geometry(MultiPolygon, 6368) NOT NULL" in canonical
    assert "geometria geometry(MultiPolygon, 6368) NOT NULL" in fragments
    forbidden = ("source_version", "source_objectid", "area_m2", "pct_municipio", "fragment_count")
    assert not any(name in canonical or name in fragments for name in forbidden)
