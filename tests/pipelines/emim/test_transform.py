from datetime import date

import pandas as pd
import pytest

from core.pipelines.emim.attributes import EmimTables as T
from core.pipelines.emim.mappings import ESTATUS_SEED
from core.pipelines.emim.stages.transform import EmimTransform


@pytest.fixture
def transform() -> EmimTransform:
    return EmimTransform()


def _raw(**overrides) -> pd.DataFrame:
    row = {
        "codigo_actividad": "31-33",
        "entidad_id": "\t14",
        "anio": "2026",
        "mes": "5",
        "per_ocu_tot": "79150",
        "horas_trabajadas": "16337.001",
        "remuneraciones": "1153818",
        "valor_produccion": "25622352",
        "valor_ventas": "24926158",
        "estatus": "Cifras preliminares",
    }
    row.update(overrides)
    return pd.DataFrame([row])


def _actividades() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"codigo_actividad": "31-33", "descripcion": "Industrias manufactureras"},
            {"codigo_actividad": "311", "descripcion": "Industria alimentaria"},
        ]
    )


def _run(transform: EmimTransform, df: pd.DataFrame, actividades: pd.DataFrame | None = None) -> dict:
    return transform.action({"df": df, "actividades": actividades if actividades is not None else _actividades()})


class TestActivityCodeIsText:
    """The sector is published as the range "31-33", so the code cannot be a number."""

    def test_the_sector_range_survives_intact(self, transform):
        result = _run(transform, _raw(codigo_actividad="31-33"))

        assert result["df"]["codigo_actividad"].iloc[0] == "31-33"

    def test_the_hyphen_is_not_swallowed_by_null_cleaning(self, transform):
        """NULL_VALUES contains "-", "--" and "---".

        list_values_to_null matches whole values and not substrings, but the
        sector code is one hyphen away from being destroyed silently, so this
        stays pinned.
        """
        result = _run(transform, _raw(codigo_actividad="31-33"))

        assert result["df"]["codigo_actividad"].iloc[0] == "31-33"
        assert len(result["df"]) == 1

    def test_subsector_codes_stay_text_and_keep_leading_shape(self, transform):
        result = _run(transform, _raw(codigo_actividad="311"))

        assert result["df"]["codigo_actividad"].iloc[0] == "311"
        assert isinstance(result["df"]["codigo_actividad"].iloc[0], str)

    def test_a_bare_hyphen_is_treated_as_missing_and_dropped(self, transform):
        result = _run(transform, pd.concat([_raw(), _raw(codigo_actividad="-")], ignore_index=True))

        assert len(result["df"]) == 1


class TestPeriod:
    def test_year_and_month_become_the_first_day_of_the_month(self, transform):
        result = _run(transform, _raw())

        assert result["df"]["fecha"].iloc[0] == date(2026, 5, 1)

    def test_unpadded_month_is_handled(self, transform):
        """EMIM ships MES without zero padding, unlike EMEC and EMS."""
        result = _run(transform, _raw(mes="1"))

        assert result["df"]["fecha"].iloc[0] == date(2026, 1, 1)

    def test_unreadable_period_is_dropped_instead_of_killing_the_edition(self, transform):
        result = _run(transform, pd.concat([_raw(), _raw(anio="basura")], ignore_index=True))

        assert len(result["df"]) == 1


class TestEntity:
    def test_tab_padded_entity_code_becomes_the_key(self, transform):
        """CODIGO_ENTIDAD ships as "\\t14" in the published CSV."""
        result = _run(transform, _raw(entidad_id="\t14"))

        assert result["df"]["entidad_id"].iloc[0] == 14

    def test_zero_padded_entity_code_is_read_as_an_integer(self, transform):
        result = _run(transform, _raw(entidad_id="\t06"))

        assert result["df"]["entidad_id"].iloc[0] == 6


class TestNumericColumns:
    def test_absolute_values_are_integers_not_indices(self, transform):
        """EMIM publishes absolute values; EMEC and EMS publish indices."""
        result = _run(transform, _raw())

        assert result["df"]["per_ocu_tot"].iloc[0] == 79150
        assert result["df"]["valor_produccion"].iloc[0] == 25622352

    def test_hours_keep_their_decimals(self, transform):
        result = _run(transform, _raw())

        assert result["df"]["horas_trabajadas"].iloc[0] == pytest.approx(16337.001)

    def test_amounts_beyond_the_documented_maximum_are_kept(self, transform):
        """The source already exceeds the 99,999,999 its own dictionary declares."""
        result = _run(transform, _raw(valor_produccion="128968800"))

        assert result["df"]["valor_produccion"].iloc[0] == 128968800

    def test_empty_measure_stays_null(self, transform):
        result = _run(transform, _raw(remuneraciones=None))

        assert pd.isna(result["df"]["remuneraciones"].iloc[0])

    def test_non_numeric_measure_becomes_null_not_a_string(self, transform):
        result = _run(transform, _raw(valor_ventas="n/e"))

        assert pd.isna(result["df"]["valor_ventas"].iloc[0])


class TestEstatusCatalog:
    def test_seeds_the_published_statuses_in_a_fixed_order(self, transform):
        result = _run(transform, _raw())

        estatus = [record["estatus"] for record in result["catalogs"][T.CAT_ESTATUS]]
        assert estatus[: len(ESTATUS_SEED)] == ESTATUS_SEED

    def test_the_fourth_documented_status_is_picked_up_from_the_data(self, transform):
        """ "Cifras ajustadas y/o corregidas" is documented but its exact label is not.

        It is deliberately absent from the seed so a guessed spelling does not
        create a junk row; when it shows up it has to be added from the data.
        """
        result = _run(transform, _raw(estatus="Cifras ajustadas"))

        estatus = [record["estatus"] for record in result["catalogs"][T.CAT_ESTATUS]]
        assert "Cifras ajustadas" in estatus

    def test_no_duplicate_statuses(self, transform):
        rows = pd.concat([_raw(), _raw(), _raw(estatus="Cifras definitivas")], ignore_index=True)

        result = _run(transform, rows)

        estatus = [record["estatus"] for record in result["catalogs"][T.CAT_ESTATUS]]
        assert len(estatus) == len(set(estatus))


class TestActividadCatalog:
    def test_catalog_comes_from_the_zip_not_from_the_data(self, transform):
        result = _run(transform, _raw())

        codigos = [record["codigo_actividad"] for record in result["catalogs"][T.CAT_ACTIVIDAD]]
        assert codigos == ["31-33", "311"]

    def test_catalog_codes_are_not_lowercased_or_cast(self, transform):
        result = _run(transform, _raw())

        assert all(isinstance(r["codigo_actividad"], str) for r in result["catalogs"][T.CAT_ACTIVIDAD])

    def test_duplicate_codes_are_collapsed(self, transform):
        actividades = pd.concat([_actividades(), _actividades()])

        result = _run(transform, _raw(), actividades)

        assert len(result["catalogs"][T.CAT_ACTIVIDAD]) == 2


class TestGuards:
    def test_empty_input_returns_the_same_empty_structure(self, transform):
        result = transform.action({"df": pd.DataFrame(), "actividades": _actividades()})

        assert result["df"].empty
        assert result["catalogs"] == {}
