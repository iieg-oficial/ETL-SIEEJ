import pandas as pd

from core.pipelines.defunciones.mappings import RAZON_MATERNA
from core.pipelines.defunciones.stages.transform import DefuncionesTransform


def _transform() -> DefuncionesTransform:
    return DefuncionesTransform()


def test_build_edad_catalog_coerces_dedups_and_drops_invalid():
    df = pd.DataFrame(
        {
            "clave": ["1001", "1001", "abc", "4998"],
            "descripcion": ["Una hora", "Una hora", "malo", "No especificada"],
        }
    )
    records = _transform()._build_edad_catalog(df)
    ids = {r["id"] for r in records}
    assert ids == {1001, 4998}
    assert all(isinstance(r["id"], int) for r in records)
    assert records[0]["nombre_edad"] == "Una hora"


def test_build_catalog_int_key_coerces_and_dedups():
    df = pd.DataFrame({"clave": ["1", "1", "x", "9"], "descripcion": ["a", "a", "b", "c"]})
    records = DefuncionesTransform._build_catalog(df, text_key=False)
    assert {r["id"] for r in records} == {1, 9}
    assert all(isinstance(r["id"], int) for r in records)


def test_build_catalog_text_key_preserves_alphanumeric():
    df = pd.DataFrame({"clave": ["A00", "", "11D"], "descripcion": ["x", "empty", "y"]})
    records = DefuncionesTransform._build_catalog(df, text_key=True)
    ids = {r["id"] for r in records}
    assert ids == {"A00", "11D"}


def test_static_catalog_maps_code_to_descripcion():
    records = DefuncionesTransform._static_catalog(RAZON_MATERNA)
    assert {"id": 0, "descripcion": "No se considera para el cálculo"} in records
    assert len(records) == len(RAZON_MATERNA)


def test_build_facts_renames_fks_types_columns_and_drops_unknown(capsys):
    df = pd.DataFrame(
        {
            "sexo": ["1", "2"],
            "edad": ["4023", ""],
            "asist_medi": ["1", "9"],
            "causa_def": ["C509", "I219"],
            "foobar": ["z", "z"],
        }
    )
    records = _transform()._build_facts(df)

    assert "sexo_id" in records[0] and "sexo" not in records[0]
    assert records[0]["sexo_id"] == 1
    assert records[0]["asist_medica_id"] == 1
    assert records[0]["causa_defuncion_id"] == "C509"
    assert records[1]["edad_id"] is None
    assert "foobar" not in records[0]
    assert "foobar" in capsys.readouterr().out


def test_apply_fk_nulls_removes_codes_absent_from_catalog():
    from core.pipelines.defunciones.stages.load import DefuncionesLoad

    records = [{"sexo_id": 1, "edad_id": 9999}, {"sexo_id": 8, "edad_id": 4023}]
    valid = {"sexo_id": {1, 2, 3}, "edad_id": {4023}}
    DefuncionesLoad._apply_fk_nulls(records, valid)
    assert records[0]["edad_id"] is None
    assert records[0]["sexo_id"] == 1
    assert records[1]["sexo_id"] is None
    assert records[1]["edad_id"] == 4023
