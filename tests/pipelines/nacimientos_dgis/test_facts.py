import pandas as pd
import pytest

from core.pipelines.nacimientos_dgis.helpers.facts import (
    apply_numeric_sentinels,
    apply_si_no,
    build_clues,
    build_composite_geo,
    build_diagnosticos,
    build_intervals,
    build_times,
    cast_integers,
    normalize_certificates,
    rename_columns,
)


def test_si_no_conserva_el_dominio_completo():
    """El dominio SI/NO tiene cinco valores: aplanarlo a boolean pierde tres."""
    df = pd.DataFrame({"SECONSIDERAINDIGENA": [1, 2, 0, 8, 9, None]})
    result = apply_si_no(rename_columns(df))["se_considera_indigena"]

    assert result.tolist()[:5] == [1, 2, 0, 8, 9]
    assert pd.isna(result[5])


def test_si_no_ausente_no_rompe():
    result = apply_si_no(pd.DataFrame({"otra": [1]}))
    assert result["se_considera_indigena"].isna().all()


@pytest.mark.parametrize(
    ("column", "sentinel"),
    [("numero_embarazos", 99), ("total_consultas", 99), ("edad_gestacional", 99), ("talla", 99), ("peso", 9999)],
)
def test_centinela_numerico_se_anula(column, sentinel):
    df = pd.DataFrame({column: [10, sentinel]})
    result = apply_numeric_sentinels(df)[column]

    assert result[0] == 10
    assert pd.isna(result[1])


def test_hora_9999_no_es_una_hora():
    df = pd.DataFrame({"hora_nacimiento": ["10:05", "99:99", ""]})
    result = build_times(df)["hora_nacimiento"]

    assert str(result[0]) == "10:05:00"
    assert pd.isna(result[1]) and pd.isna(result[2])


def test_tiempo_traslado_se_guarda_en_minutos():
    df = pd.DataFrame({"tiempo_traslado": ["01:40", "00:30", "99:99", None]})
    result = build_intervals(df)

    assert result["tiempo_traslado_minutos"].tolist()[:2] == [100, 30]
    assert result["tiempo_traslado_minutos"][2:].isna().all()
    assert "tiempo_traslado" not in result.columns


def test_diagnostico_0000_es_ausencia_de_anomalia():
    df = pd.DataFrame({"diagnostico_1": ["P073", "0000", ""], "diagnostico_2": ["Q909", "0000", None]})
    result = build_diagnosticos(df)

    assert result["diagnostico_1"][0] == "P073"
    assert pd.isna(result["diagnostico_1"][1])
    assert pd.isna(result["diagnostico_2"][1])


def test_clues_invalida_no_es_clave():
    """9998 es "no tiene CLUES", no una CLUES de 11 caracteres."""
    df = pd.DataFrame({"establecimiento_salud": ["JCIMS000366", "9998", ""]})
    result = build_clues(df)["establecimiento_salud"]

    assert result[0] == "JCIMS000366"
    assert pd.isna(result[1]) and pd.isna(result[2])


def test_clave_geografica_compuesta():
    """Municipio y localidad sólo son únicos junto con su entidad."""
    df = pd.DataFrame(
        {
            "ENTIDADFEDERATIVAPARTO": [14],
            "MUNICIPIOPARTO": [39],
            "LOCALIDADPARTO": [1],
            "ENTIDADRESIDENCIA": [14],
            "MUNICIPIORESIDENCIA": [120],
            "LOCALIDADRESIDENCIA": [1],
        }
    )
    result = build_composite_geo(df)

    assert result["entidad_parto"][0] == 14
    assert result["municipio_parto"][0] == 14039
    assert result["localidad_parto"][0] == 140390001
    assert result["localidad_residencia"][0] == 141200001


def test_enteros_no_salen_como_float():
    """Una columna con nulos llega como float y el COPY escribiría "23.0"."""
    df = pd.DataFrame({"edad_padre": [23.0, None], "edad_madre": [31.0, 28.0]})
    result = cast_integers(df)

    assert str(result["edad_padre"].dtype) == "Int64"
    assert result["edad_padre"][0] == 23
    assert result["edad_madre"].tolist() == [31, 28]


def test_normalize_certificates_no_deja_columnas_crudas():
    df = pd.DataFrame(
        {
            "EDAD": [31],
            "EDADPADRE": [33],
            "SEXO": [1],
            "PESO": [9999],
            "HORANACIMIENTO": ["99:99"],
            "TIEMPOTRASLADO": ["00:30"],
            "CODIGOCIEANOMALIA1": ["0000"],
            "CODIGOCIEANOMALIA2": ["P073"],
            "CLUES": ["JCIMS000366"],
            "SECONSIDERAINDIGENA": [9],
            "ENTIDADFEDERATIVAPARTO": [14],
            "MUNICIPIOPARTO": [39],
            "LOCALIDADPARTO": [1],
            "ENTIDADRESIDENCIA": [14],
            "MUNICIPIORESIDENCIA": [39],
            "LOCALIDADRESIDENCIA": [1],
        }
    )
    result = normalize_certificates(df)

    assert "PESO" not in result.columns and "TIEMPOTRASLADO" not in result.columns
    assert pd.isna(result["peso"][0])
    assert pd.isna(result["hora_nacimiento"][0])
    assert pd.isna(result["diagnostico_1"][0])
    assert result["diagnostico_2"][0] == "P073"
    assert result["se_considera_indigena"][0] == 9
    assert result["tiempo_traslado_minutos"][0] == 30
