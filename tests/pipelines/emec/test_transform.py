from datetime import date

import pandas as pd
import pytest

from core.pipelines.emec.attributes import EmecTables as T
from core.pipelines.emec.mappings import ESTATUS_SEED
from core.pipelines.emec.stages.transform import EmecTransform


@pytest.fixture
def transform() -> EmecTransform:
    return EmecTransform()


def _raw(**overrides) -> pd.DataFrame:
    row = {
        "codigo_actividad": "43",
        "anio": "2026",
        "mes": "\t05",
        "entidad": "Jalisco",
        "per_ocu_tot": "79.39817072",
        "remuneraciones_tot": "70.43033482",
        "remuneraciones_media": "88.70523613",
        "ind_ingresos_bienes_serv": "50.80201758",
        "ind_compras_reventa": "54.37760289",
        "estatus": "Cifras preliminares",
    }
    row.update(overrides)
    return pd.DataFrame([row])


def _actividades() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"codigo_actividad": "43", "descripcion": "Comercio al por mayor"},
            {"codigo_actividad": "46", "descripcion": "Comercio al por menor"},
        ]
    )


def _run(transform: EmecTransform, df: pd.DataFrame, actividades: pd.DataFrame | None = None) -> dict:
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


class TestNumericColumns:
    def test_index_columns_keep_their_full_precision(self, transform):
        result = _run(transform, _raw())

        assert result["df"]["per_ocu_tot"].iloc[0] == pytest.approx(79.39817072)
        assert result["df"]["ind_compras_reventa"].iloc[0] == pytest.approx(54.37760289)

    def test_non_numeric_index_value_becomes_null_not_a_string(self, transform):
        """The columns are DOUBLE PRECISION; a leftover string would fail the insert."""
        result = _run(transform, _raw(per_ocu_tot="n/e"))

        assert pd.isna(result["df"]["per_ocu_tot"].iloc[0])

    def test_activity_code_is_an_integer(self, transform):
        result = _run(transform, _raw(codigo_actividad="46"))

        assert result["df"]["codigo_actividad"].iloc[0] == 46


class TestEstatusCatalog:
    def test_seeds_the_three_documented_statuses(self, transform):
        """ "Cifras revisadas" is absent from today's edition but arrives on revision.

        Seeding it now keeps the ids stable when it finally shows up, so rows
        already loaded do not end up pointing at a different status.
        """
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
        """The entity dataset only holds sectors 43 and 46; the catalog holds them all."""
        actividades = pd.concat(
            [_actividades(), pd.DataFrame([{"codigo_actividad": "431", "descripcion": "Abarrotes"}])]
        )

        result = _run(transform, _raw(), actividades)

        codigos = [record["codigo_actividad"] for record in result["catalogs"][T.CAT_ACTIVIDAD]]
        assert codigos == [43, 46, 431]

    def test_duplicate_codes_are_collapsed(self, transform):
        actividades = pd.concat([_actividades(), _actividades()])

        result = _run(transform, _raw(), actividades)

        assert len(result["catalogs"][T.CAT_ACTIVIDAD]) == 2


class TestGuards:
    def test_empty_input_returns_the_same_empty_structure(self, transform):
        result = transform.action({"df": pd.DataFrame(), "actividades": _actividades()})

        assert result["df"].empty
        assert result["catalogs"] == {}

    def test_rows_without_an_entity_are_dropped(self, transform):
        """entidad is the only link to cvegeo_states; without it the row cannot load."""
        result = _run(transform, pd.concat([_raw(), _raw(entidad=None)], ignore_index=True))

        assert len(result["df"]) == 1
