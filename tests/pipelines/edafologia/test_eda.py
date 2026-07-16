from __future__ import annotations

from core.pipelines.edafologia.eda.eda_edafologia import canonical_hash, canonical_hash_formula


def test_canonical_hash_is_independent_from_query_order():
    records = [
        {"source_version": "Serie III", "source_objectid": "2", "value": "b"},
        {"source_version": "Serie III", "source_objectid": "1", "value": "a"},
    ]
    reversed_records = list(reversed(records))

    assert canonical_hash(records, ["source_version", "source_objectid"], ["value"]) == canonical_hash(
        reversed_records, ["source_version", "source_objectid"], ["value"]
    )


def test_canonical_hash_is_stable_between_calculations():
    records = [{"source_version": "Serie III", "source_objectid": "1", "geom_ewkb_hex": "0106000020e018"}]

    first = canonical_hash(records, ["source_version", "source_objectid"], ["geom_ewkb_hex"])
    second = canonical_hash(records, ["source_version", "source_objectid"], ["geom_ewkb_hex"])

    assert first == second


def test_canonical_hash_changes_when_geometry_changes():
    key_fields = ["source_version", "source_objectid"]
    payload_fields = ["geom_ewkb_hex"]
    original = [{"source_version": "Serie III", "source_objectid": "1", "geom_ewkb_hex": "aaaa"}]
    changed = [{"source_version": "Serie III", "source_objectid": "1", "geom_ewkb_hex": "bbbb"}]

    assert canonical_hash(original, key_fields, payload_fields) != canonical_hash(changed, key_fields, payload_fields)


def test_canonical_hash_changes_when_relationship_changes():
    key_fields = ["source_version", "source_objectid"]
    payload_fields = ["grupo_clave", "calificador_primario_clave", "calificador_secundario_clave"]
    original = [
        {
            "source_version": "Serie III",
            "source_objectid": "1",
            "grupo_clave": "PH",
            "calificador_primario_clave": "ha",
            "calificador_secundario_clave": "N",
        }
    ]
    changed = [dict(original[0], calificador_secundario_clave="fl")]

    assert canonical_hash(original, key_fields, payload_fields) != canonical_hash(changed, key_fields, payload_fields)


def test_canonical_hash_does_not_depend_on_serial_ids_when_not_in_formula():
    key_fields = ["source_version", "source_objectid"]
    payload_fields = ["grupo_clave"]
    first = [{"id": 1, "source_version": "Serie III", "source_objectid": "1", "grupo_clave": "PH"}]
    second = [{"id": 999, "source_version": "Serie III", "source_objectid": "1", "grupo_clave": "PH"}]

    assert canonical_hash(first, key_fields, payload_fields) == canonical_hash(second, key_fields, payload_fields)


def test_canonical_hash_formula_documents_logical_keys_and_geometry_serialization():
    formula = canonical_hash_formula()

    assert formula["algorithm"] == "sha256"
    assert formula["canonical_key_fields"] == ["source_version", "source_objectid"]
    assert formula["overlay_key_fields"] == [
        "source_version",
        "source_objectid",
        "fuente_limite_clave",
        "municipality_cvegeo",
    ]
    assert "ST_AsEWKB" in formula["geometry_serialization"]
    assert "SERIAL" not in " ".join(formula["canonical_key_fields"] + formula["overlay_key_fields"]).upper()
