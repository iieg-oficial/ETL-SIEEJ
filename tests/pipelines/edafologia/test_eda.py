from __future__ import annotations

from core.pipelines.edafologia.eda.eda_edafologia import canonical_hash, canonical_hash_formula


def test_canonical_hash_is_independent_from_query_order():
    records = [
        {"version_fuente": "Serie III", "identificador_objeto_fuente": "2", "value": "b"},
        {"version_fuente": "Serie III", "identificador_objeto_fuente": "1", "value": "a"},
    ]
    reversed_records = list(reversed(records))

    assert canonical_hash(records, ["version_fuente", "identificador_objeto_fuente"], ["value"]) == canonical_hash(
        reversed_records, ["version_fuente", "identificador_objeto_fuente"], ["value"]
    )


def test_canonical_hash_is_stable_between_calculations():
    records = [{"version_fuente": "Serie III", "identificador_objeto_fuente": "1", "geom_ewkb_hex": "0106000020e018"}]

    first = canonical_hash(records, ["version_fuente", "identificador_objeto_fuente"], ["geom_ewkb_hex"])
    second = canonical_hash(records, ["version_fuente", "identificador_objeto_fuente"], ["geom_ewkb_hex"])

    assert first == second


def test_canonical_hash_changes_when_geometry_changes():
    key_fields = ["version_fuente", "identificador_objeto_fuente"]
    payload_fields = ["geom_ewkb_hex"]
    original = [{"version_fuente": "Serie III", "identificador_objeto_fuente": "1", "geom_ewkb_hex": "aaaa"}]
    changed = [{"version_fuente": "Serie III", "identificador_objeto_fuente": "1", "geom_ewkb_hex": "bbbb"}]

    assert canonical_hash(original, key_fields, payload_fields) != canonical_hash(changed, key_fields, payload_fields)


def test_canonical_hash_changes_when_relationship_changes():
    key_fields = ["version_fuente", "identificador_objeto_fuente"]
    payload_fields = ["grupo_clave", "calificador_primario_clave", "calificador_secundario_clave"]
    original = [
        {
            "version_fuente": "Serie III",
            "identificador_objeto_fuente": "1",
            "grupo_clave": "PH",
            "calificador_primario_clave": "ha",
            "calificador_secundario_clave": "N",
        }
    ]
    changed = [dict(original[0], calificador_secundario_clave="fl")]

    assert canonical_hash(original, key_fields, payload_fields) != canonical_hash(changed, key_fields, payload_fields)


def test_canonical_hash_does_not_depend_on_serial_ids_when_not_in_formula():
    key_fields = ["version_fuente", "identificador_objeto_fuente"]
    payload_fields = ["grupo_clave"]
    first = [{"id": 1, "version_fuente": "Serie III", "identificador_objeto_fuente": "1", "grupo_clave": "PH"}]
    second = [{"id": 999, "version_fuente": "Serie III", "identificador_objeto_fuente": "1", "grupo_clave": "PH"}]

    assert canonical_hash(first, key_fields, payload_fields) == canonical_hash(second, key_fields, payload_fields)


def test_canonical_hash_formula_documents_logical_keys_and_geometry_serialization():
    formula = canonical_hash_formula()

    assert formula["algorithm"] == "sha256"
    assert formula["canonical_key_fields"] == ["version_fuente", "identificador_objeto_fuente"]
    assert formula["overlay_key_fields"] == [
        "version_fuente",
        "identificador_objeto_fuente",
        "fuente_limite_clave",
        "municipio_id",
    ]
    assert "ST_AsEWKB" in formula["geometry_serialization"]
    assert "SERIAL" not in " ".join(formula["canonical_key_fields"] + formula["overlay_key_fields"]).upper()
