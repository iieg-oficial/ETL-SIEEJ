from datetime import date

import pandas as pd
import pytest

from core.pipelines.ems.attributes import EmsTables as T
from core.pipelines.ems.mappings import ESTATUS_SEED
from core.pipelines.ems.stages.transform import EmsTransform


@pytest.fixture
def transform() -> EmsTransform:
    return EmsTransform()


def _raw(**overrides) -> pd.DataFrame:
    row = {
        "codigo_actividad": "51",
        "entidad_id": "14",
        "anio": "2026",
        "mes": "\t05",
        "ind_ingresos_bienes_serv": "29.8498949",
        "ind_gastos_consumo": "27.35093621",
        "per_ocu_tot": "77.25054857",
        "per_ocu_dependiente": None,
        "per_ocu_no_dependiente": None,
        "remuneraciones_tot": "85.41058831",
        "estatus": "Cifras preliminares",
    }
    row.update(overrides)
    return pd.DataFrame([row])


def _actividades() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"codigo_actividad": "51", "descripcion": "Información en medios masivos"},
            {"codigo_actividad": "61", "descripcion": "Servicios educativos"},
        ]
    )


def _run(transform: EmsTransform, df: pd.DataFrame, actividades: pd.DataFrame | None = None) -> dict:
    return transform.action({"df": df, "actividades": actividades if actividades is not None else _actividades()})


class TestPeriod:
    def test_year_and_month_become_the_first_day_of_the_month(self, transform):
        result = _run(transform, _raw())

        assert result["df"]["fecha"].iloc[0] == date(2026, 5, 1)

    def test_tab_padding_the_source_ships_is_stripped(self, transform):
        """MES arrives as "\\t01" in the published CSV."""
        result = _run(transform, _raw(mes="\t01"))

        assert result["df"]["fecha"].iloc[0] == date(2026, 1, 1)

    def test_unreadable_period_is_dropped_instead_of_killing_the_edition(self, transform):
        result = _run(transform, pd.concat([_raw(), _raw(anio="basura")], ignore_index=True))

        assert len(result["df"]) == 1


class TestEntity:
    def test_cvegeo_becomes_the_entity_key_without_a_lookup(self, transform):
        """EMS publishes CVEGEO, so there is no name to resolve — unlike EMEC."""
        result = _run(transform, _raw(entidad_id="14"))

        assert result["df"]["entidad_id"].iloc[0] == 14

    def test_zero_padded_cvegeo_is_read_as_an_integer(self, transform):
        result = _run(transform, _raw(entidad_id="06"))

        assert result["df"]["entidad_id"].iloc[0] == 6

    def test_row_without_a_usable_cvegeo_is_dropped(self, transform):
        result = _run(transform, pd.concat([_raw(), _raw(entidad_id="n/e")], ignore_index=True))

        assert len(result["df"]) == 1


class TestNumericColumns:
    def test_index_columns_keep_their_full_precision(self, transform):
        result = _run(transform, _raw())

        assert result["df"]["ind_ingresos_bienes_serv"].iloc[0] == pytest.approx(29.8498949)
        assert result["df"]["ind_gastos_consumo"].iloc[0] == pytest.approx(27.35093621)

    def test_empty_personal_breakdown_stays_null(self, transform):
        """H000 and I000A are empty in ~37% of the source; that is real absence."""
        result = _run(transform, _raw())

        assert pd.isna(result["df"]["per_ocu_dependiente"].iloc[0])
        assert pd.isna(result["df"]["per_ocu_no_dependiente"].iloc[0])

    def test_populated_personal_breakdown_is_kept(self, transform):
        result = _run(transform, _raw(per_ocu_dependiente="70.5", per_ocu_no_dependiente="6.75"))

        assert result["df"]["per_ocu_dependiente"].iloc[0] == pytest.approx(70.5)
        assert result["df"]["per_ocu_no_dependiente"].iloc[0] == pytest.approx(6.75)

    def test_non_numeric_index_value_becomes_null_not_a_string(self, transform):
        """The columns are DOUBLE PRECISION; a leftover string would fail the insert."""
        result = _run(transform, _raw(remuneraciones_tot="n/e"))

        assert pd.isna(result["df"]["remuneraciones_tot"].iloc[0])


class TestEstatusCatalog:
    def test_seeds_the_three_documented_statuses(self, transform):
        result = _run(transform, _raw())

        estatus = [record["estatus"] for record in result["catalogs"][T.CAT_ESTATUS]]
        assert set(ESTATUS_SEED).issubset(estatus)

    def test_seed_order_is_preserved_so_ids_stay_stable(self, transform):
        result = _run(transform, _raw())

        estatus = [record["estatus"] for record in result["catalogs"][T.CAT_ESTATUS]]
        assert estatus[: len(ESTATUS_SEED)] == ESTATUS_SEED

    def test_an_unforeseen_status_is_added_instead_of_dropped(self, transform):
        result = _run(transform, _raw(estatus="Cifras reexpresadas"))

        estatus = [record["estatus"] for record in result["catalogs"][T.CAT_ESTATUS]]
        assert "Cifras reexpresadas" in estatus

    def test_no_duplicate_statuses(self, transform):
        rows = pd.concat([_raw(), _raw(), _raw(estatus="Cifras definitivas")], ignore_index=True)

        result = _run(transform, rows)

        estatus = [record["estatus"] for record in result["catalogs"][T.CAT_ESTATUS]]
        assert len(estatus) == len(set(estatus))


class TestActividadCatalog:
    def test_catalog_comes_from_the_zip_not_from_the_data(self, transform):
        result = _run(transform, _raw())

        codigos = [record["codigo_actividad"] for record in result["catalogs"][T.CAT_ACTIVIDAD]]
        assert codigos == [51, 61]

    def test_duplicate_codes_are_collapsed(self, transform):
        actividades = pd.concat([_actividades(), _actividades()])

        result = _run(transform, _raw(), actividades)

        assert len(result["catalogs"][T.CAT_ACTIVIDAD]) == 2


class TestGuards:
    def test_empty_input_returns_the_same_empty_structure(self, transform):
        result = transform.action({"df": pd.DataFrame(), "actividades": _actividades()})

        assert result["df"].empty
        assert result["catalogs"] == {}
