"""INEGI publica catálogos con comas sin escapar; el parser no debe truncarlos."""

import io
import zipfile

import pandas as pd
import pytest

from core.pipelines.defunciones_inegi.helpers.source import read_catalog_csv

DESCRIPCION_CON_COMA = "Área industrial (taller, fabrica u obra)"


def _zip_with(content: str) -> zipfile.ZipFile:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("catalogos/lugar_ocurrencia.csv", content)
    return zipfile.ZipFile(buffer)


@pytest.mark.parametrize(
    ("caso", "content"),
    [
        # Edición 2023: sin coma final, pandas revienta al tokenizar.
        ("sin_coma_final", f"CVE,DESCRIP\n5,Otro\n6,{DESCRIPCION_CON_COMA}\n"),
        # Edición 2024: con coma final, pandas trunca en una columna fantasma.
        ("con_coma_final", f"CVE,DESCRIP,\n5,Otro,\n6,{DESCRIPCION_CON_COMA}\n"),
    ],
)
def test_extra_commas_stay_in_the_description(caso, content):
    df = read_catalog_csv(_zip_with(content), "catalogos/lugar_ocurrencia.csv")

    assert list(df.columns) == ["CVE", "DESCRIP"], f"columna fantasma en {caso}"
    assert df.loc[df["CVE"] == "6", "DESCRIP"].item() == DESCRIPCION_CON_COMA


def test_quoted_commas_are_respected():
    df = read_catalog_csv(_zip_with('CVE,DESCRIP\n1,"Cólera, biotipo cholerae"\n'), "catalogos/lugar_ocurrencia.csv")
    assert df.loc[0, "DESCRIP"] == "Cólera, biotipo cholerae"


def test_empty_field_reads_as_null():
    """Igual que pandas: un campo vacío es nulo, no la cadena vacía."""
    df = read_catalog_csv(_zip_with('CVE,DESCRIP\n"","Pendiente"\n'), "catalogos/lugar_ocurrencia.csv")
    assert pd.isna(df.loc[0, "CVE"])


def test_sentence_case_preserves_acronyms_and_proper_nouns():
    """INEGI publica en mayúsculas sostenidas; bajar todo daña siglas y nombres."""
    from core.pipelines.defunciones_inegi.helpers.catalogs import sentence_case

    resultado = sentence_case(
        pd.Series(
            [
                "CIERTAS  ENFERMEDADES INFECCIOSAS  Y PARASITARIAS",
                "ENFERMEDAD POR VIRUS DE LA INMUNODEFICIENCIA HUMANA (VIH)",
                "LINFOMA NO HODGKIN",
                "TUMORES (NEOPLASIAS)",
            ]
        )
    ).tolist()

    assert resultado == [
        # Los espacios dobles de la fuente se colapsan.
        "Ciertas enfermedades infecciosas y parasitarias",
        "Enfermedad por virus de la inmunodeficiencia humana (VIH)",
        "Linfoma no Hodgkin",
        # Los paréntesis con palabras normales sí se minusculizan.
        "Tumores (neoplasias)",
    ]
