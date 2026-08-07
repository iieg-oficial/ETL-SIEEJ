from datetime import date

import pandas as pd
import pytest

from core.pipelines.enec.attributes import EnecTables as T
from core.pipelines.enec.constants import ENTIDAD_RENAME, MEASURE_RENAME, NACIONAL_RENAME
from core.pipelines.enec.mappings import ESTATUS_SEED
from core.pipelines.enec.stages.transform import EnecTransform


@pytest.fixture
def transform() -> EnecTransform:
    return EnecTransform()


def _measures(**overrides) -> dict:
    row = {}
    for name in MEASURE_RENAME.values():
        decimal = name.startswith(("dias_", "horas_", "remuneracion_media", "salario_medio", "sueldo_medio"))
        row[name] = "123.456" if decimal else "1000"
    row.update(overrides)
    return row


def _nacional(**overrides) -> pd.DataFrame:
    row = {
        "codigo_actividad": "23",
        "descripcion_actividad": "Construcción",
        "anio": "2026",
        "mes": "\t01",
        "estatus": "Cifras preliminares",
        **_measures(),
    }
    row.update(overrides)
    return pd.DataFrame([row])[list(NACIONAL_RENAME.values())]


def _entidad(**overrides) -> pd.DataFrame:
    row = {
        "entidad_id": "\t14",
        "anio": "2026",
        "mes": "\t01",
        "estatus": "Cifras preliminares",
        **_measures(),
    }
    row.update(overrides)
    return pd.DataFrame([row])[list(ENTIDAD_RENAME.values())]


def _run(transform, nacional=None, entidad=None) -> dict:
    return transform.action(
        {
            "nacional": _nacional() if nacional is None else nacional,
            "entidad": _entidad() if entidad is None else entidad,
        }
    )


class TestNationalRowsAreNotDuplicated:
    """The state dataset ships the national aggregate as CVEGEO 00.

    Those rows are byte-identical to the activity-23 rows of the national file.
    Keeping them would store the national total in two tables that could drift.
    """

    def test_cvegeo_00_is_dropped_from_the_state_table(self, transform):
        entidad = pd.concat([_entidad(entidad_id="\t00"), _entidad(entidad_id="\t14")], ignore_index=True)

        result = _run(transform, entidad=entidad)

        assert result["entidad"]["entidad_id"].tolist() == [14]

    def test_obra_en_el_extranjero_is_kept(self, transform):
        """CVEGEO 33 is not a state, but the national total does not add up without it."""
        entidad = pd.concat([_entidad(entidad_id="\t14"), _entidad(entidad_id="\t33")], ignore_index=True)

        result = _run(transform, entidad=entidad)

        assert sorted(result["entidad"]["entidad_id"].tolist()) == [14, 33]

    def test_the_national_table_keeps_its_own_rows(self, transform):
        result = _run(transform)

        assert len(result["nacional"]) == 1


class TestPeriod:
    def test_year_and_month_become_the_first_day_of_the_month(self, transform):
        result = _run(transform, entidad=_entidad(mes="\t05"))

        assert result["entidad"]["fecha"].iloc[0] == date(2026, 5, 1)

    def test_unreadable_period_is_dropped(self, transform):
        entidad = pd.concat([_entidad(), _entidad(anio="basura")], ignore_index=True)

        result = _run(transform, entidad=entidad)

        assert len(result["entidad"]) == 1


class TestTypes:
    def test_tab_padded_entity_code_becomes_an_integer(self, transform):
        result = _run(transform, entidad=_entidad(entidad_id="\t06"))

        assert result["entidad"]["entidad_id"].iloc[0] == 6

    def test_counts_and_amounts_are_integers(self, transform):
        result = _run(transform)

        assert result["entidad"]["per_ocu_tot"].iloc[0] == 1000
        assert result["entidad"]["valor_produccion"].iloc[0] == 1000

    def test_rates_keep_their_decimals(self, transform):
        result = _run(transform)

        assert result["entidad"]["dias_trabajados"].iloc[0] == pytest.approx(123.456)
        assert result["entidad"]["remuneracion_media_hora"].iloc[0] == pytest.approx(123.456)

    def test_non_numeric_measure_becomes_null(self, transform):
        result = _run(transform, entidad=_entidad(**{"ingresos_tot": "n/e"}))

        assert pd.isna(result["entidad"]["ingresos_tot"].iloc[0])


class TestCatalogs:
    def test_activity_catalog_is_derived_from_the_data(self, transform):
        """This ZIP ships no catalogs folder; the description comes inline."""
        nacional = pd.concat(
            [
                _nacional(codigo_actividad="23", descripcion_actividad="Construcción"),
                _nacional(codigo_actividad="236", descripcion_actividad="Edificación"),
            ],
            ignore_index=True,
        )

        result = _run(transform, nacional=nacional)

        assert result["catalogs"][T.CAT_ACTIVIDAD] == [
            {"codigo_actividad": 23, "descripcion": "Construcción"},
            {"codigo_actividad": 236, "descripcion": "Edificación"},
        ]

    def test_duplicate_activity_codes_are_collapsed(self, transform):
        nacional = pd.concat([_nacional(), _nacional()], ignore_index=True)

        result = _run(transform, nacional=nacional)

        assert len(result["catalogs"][T.CAT_ACTIVIDAD]) == 1

    def test_seeds_the_documented_statuses_in_a_fixed_order(self, transform):
        result = _run(transform)

        estatus = [r["estatus"] for r in result["catalogs"][T.CAT_ESTATUS]]
        assert estatus[: len(ESTATUS_SEED)] == ESTATUS_SEED

    def test_statuses_from_both_datasets_are_collected(self, transform):
        result = _run(
            transform,
            nacional=_nacional(estatus="Cifras ajustadas"),
            entidad=_entidad(estatus="Cifras corregidas"),
        )

        estatus = [r["estatus"] for r in result["catalogs"][T.CAT_ESTATUS]]
        assert "Cifras ajustadas" in estatus and "Cifras corregidas" in estatus


class TestGuards:
    def test_empty_input_returns_the_same_empty_structure(self, transform):
        result = transform.action({"nacional": pd.DataFrame(), "entidad": pd.DataFrame()})

        assert result["nacional"].empty
        assert result["entidad"].empty
        assert result["catalogs"] == {}
