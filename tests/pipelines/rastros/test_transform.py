import pandas as pd
import pytest

from core.pipelines.rastros.attributes import RastrosTables as T
from core.pipelines.rastros.constants import NULL_VALUES
from core.pipelines.rastros.stages.transform import RastrosTransform
from core.utils.clean import list_values_to_null

# Etiquetas del catálogo de estatus según el diccionario de datos del INEGI.
ESTATUS_LABELS = ["Disponible", "No disponible", "No aplicable", "No significativo", "Confidencial"]


@pytest.fixture
def transform() -> RastrosTransform:
    return RastrosTransform()


def _raw(**overrides) -> pd.DataFrame:
    row = {
        "anio": "2026",
        "mes": "\t\t05",
        "entidad_id": "14",
        "especie_ganadera": "Ganado bovino",
        "numero_cabezas": "100",
        "estatus_cabeza": "Disponible",
        "produccion_carne": "10",
        "estatus_produccion": "Disponible",
        "vproduccion": "500",
        "estatus_vproduccion": "Disponible",
        "tipo_cifra": "Cifras Preliminares",
    }
    row.update(overrides)
    return pd.DataFrame([row])


class TestEstatusLabelsSurviveNullCleaning:
    """Regression: `No disponible` is a real catalog value, not a missing value.

    list_values_to_null() sweeps every text column, so any token in NULL_VALUES
    that collides with a catalog label silently destroys real data.
    """

    @pytest.mark.parametrize("label", ESTATUS_LABELS)
    def test_label_is_not_treated_as_null(self, label):
        cleaned = list_values_to_null(pd.DataFrame({"estatus_cabeza": [label]}), rm_list=NULL_VALUES)

        assert cleaned["estatus_cabeza"].iloc[0] == label

    @pytest.mark.parametrize("token", ["nd", "na", "n/a", "n/d", "no disponible", "no aplicable"])
    def test_null_values_does_not_contain_status_like_tokens(self, token):
        assert token not in [v.lower() for v in NULL_VALUES]

    def test_status_reaches_the_catalog(self, transform):
        result = transform.action(_raw(estatus_produccion="No disponible"))

        estatus = {r["estatus"] for r in result["catalogs"][T.CAT_ESTATUS]}
        assert "No disponible" in estatus


class TestNumericColumns:
    def test_blank_measure_becomes_null(self, transform):
        """The source ships ' ' for produccion_carne when it is not significant."""
        result = transform.action(_raw(produccion_carne=" "))

        assert pd.isna(result["df"]["produccion_carne"].iloc[0])

    def test_measures_are_nullable_integers(self, transform):
        result = transform.action(_raw())

        assert result["df"]["numero_cabezas"].dtype == "Int64"
        assert result["df"]["numero_cabezas"].iloc[0] == 100


class TestCatalogs:
    def test_catalogs_are_derived_from_the_data(self, transform):
        result = transform.action(_raw(especie_ganadera="Ganado porcino"))

        especies = {r["especie_ganadera"] for r in result["catalogs"][T.CAT_ESPECIES_GANADERAS]}
        assert especies == {"Ganado porcino"}

    def test_the_three_status_columns_share_one_catalog(self, transform):
        result = transform.action(
            _raw(estatus_cabeza="Disponible", estatus_produccion="No significativo", estatus_vproduccion="Disponible")
        )

        estatus = {r["estatus"] for r in result["catalogs"][T.CAT_ESTATUS]}
        assert estatus == {"Disponible", "No significativo"}

    def test_catalog_entries_are_deduplicated(self, transform):
        df = pd.concat([_raw(), _raw(mes="\t\t06")], ignore_index=True)

        result = transform.action(df)

        assert len(result["catalogs"][T.CAT_ESPECIES_GANADERAS]) == 1


class TestGrain:
    def test_period_becomes_a_date(self, transform):
        from datetime import date

        result = transform.action(_raw())

        assert result["df"]["fecha"].iloc[0] == date(2026, 5, 1)

    def test_months_stay_distinct_rows(self, transform):
        """Collapsing months would make the upsert overwrite itself."""
        df = pd.concat([_raw(mes="\t\t01"), _raw(mes="\t\t02")], ignore_index=True)

        result = transform.action(df)

        assert result["df"]["fecha"].nunique() == 2

    def test_rows_without_a_readable_period_are_dropped(self, transform):
        df = pd.concat([_raw(), _raw(mes="99")], ignore_index=True)

        result = transform.action(df)

        assert len(result["df"]) == 1


def test_empty_input_returns_the_same_empty_structure(transform):
    result = transform.action(pd.DataFrame())

    assert result["df"].empty
    assert result["catalogs"] == {}
