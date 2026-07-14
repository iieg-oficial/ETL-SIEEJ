import pandas as pd

from core.pipelines.defunciones.helpers import catalogs
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
    records = catalogs.build_edad_catalog(df)
    ids = {r["id"] for r in records}
    assert ids == {1001, 4998}
    assert all(isinstance(r["id"], int) for r in records)
    assert records[0]["nombre_edad"] == "Una hora"


def test_build_catalog_int_key_coerces_and_dedups():
    df = pd.DataFrame({"clave": ["1", "1", "x", "9"], "descripcion": ["a", "a", "b", "c"]})
    records = catalogs.build_catalog(df, text_key=False)
    assert {r["id"] for r in records} == {1, 9}
    assert all(isinstance(r["id"], int) for r in records)


def test_build_catalog_text_key_preserves_alphanumeric():
    df = pd.DataFrame({"clave": ["A00", "", "11D"], "descripcion": ["x", "empty", "y"]})
    records = catalogs.build_catalog(df, text_key=True)
    ids = {r["id"] for r in records}
    assert ids == {"A00", "11D"}


def test_build_localidades_builds_nine_digit_key_and_keeps_sentinels():
    df = pd.DataFrame(
        {
            "cve_ent": ["01", "88", "99", "x"],
            "cve_mun": ["001", "999", "999", "001"],
            "cve_loc": ["0001", "9999", "7777", "0001"],
            "descripcion": ["Aguascalientes", "Localidad no especificada", "Cifra confidencial", "malo"],
            "edicion": [2022, 2022, 2022, 2022],
        }
    )
    records = catalogs.build_localidades(df)
    codes = {r["codigo"] for r in records}
    assert codes == {10010001, 889999999, 999997777}
    sentinel = next(r for r in records if r["codigo"] == 889999999)
    assert sentinel["cve_ent"] == 88
    assert sentinel["cve_mun"] == 999
    assert sentinel["cve_loc"] == 9999
    assert sentinel["anio"] == 2022
    assert sentinel["descripcion"] == "No especificado"


def test_build_localidades_dedups_by_codigo_and_edicion():
    df = pd.DataFrame(
        {
            "cve_ent": ["01", "01"],
            "cve_mun": ["001", "001"],
            "cve_loc": ["0001", "0001"],
            "descripcion": ["Aguascalientes", "Aguascalientes"],
            "edicion": [2022, 2022],
        }
    )
    records = catalogs.build_localidades(df)
    assert len(records) == 1


def test_static_catalog_maps_code_to_descripcion():
    records = catalogs.static_catalog(RAZON_MATERNA)
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


def test_sentinel_descriptions_collapse_to_a_single_label():
    df = pd.DataFrame(
        {
            "cve_ent": ["88", "88", "88", "99", "99", "99", "14"],
            "cve_mun": ["000", "888", "888", "000", "999", "999", "039"],
            "cve_loc": ["0000", "0000", "8888", "0000", "0000", "9999", "0000"],
            "descripcion": [
                "Entidad no aplica para A00 - R99 Y V90 - Y89",
                "Municipio no aplica para A00 - R99 Y V90 - Y89",
                "Localidad no aplica para A00 a R99",
                "Entidad no especificada",
                "Municipio no especificado",
                "Localidad no especificada",
                "Guadalajara",
            ],
            "edicion": [2022] * 7,
        }
    )
    labels = {r["codigo"]: r["descripcion"] for r in catalogs.build_localidades(df)}

    assert labels[880000000] == "No aplica"
    assert labels[888880000] == "No aplica"
    assert labels[888888888] == "No aplica"
    assert labels[990000000] == "No especificado"
    assert labels[999990000] == "No especificado"
    assert labels[999999999] == "No especificado"
    assert labels[140390000] == "Guadalajara"
