from datetime import date

import pandas as pd
import pytest

from core.pipelines.indice_shf_vivienda.constants import LEVEL_ESTATAL, LEVEL_GLOBAL, LEVEL_MUNICIPAL
from core.pipelines.indice_shf_vivienda.stages.transform import IndiceShfViviendaTransform


@pytest.fixture
def transform() -> IndiceShfViviendaTransform:
    return IndiceShfViviendaTransform()


def _frame(rows: list[dict]) -> pd.DataFrame:
    columns = ["serie_global", "estado", "municipio", "trimestre", "anio", "indice"]
    df = pd.DataFrame(rows).reindex(columns=columns)
    return df.astype(object).where(df.notna(), None).astype("string")


def test_splits_the_sheet_into_three_disjoint_levels(transform, extracted):
    levels = transform.action(extracted)

    assert len(levels[LEVEL_GLOBAL]) == 2
    assert len(levels[LEVEL_ESTATAL]) == 2
    assert len(levels[LEVEL_MUNICIPAL]) == 3
    assert sum(len(frame) for frame in levels.values()) == len(extracted)


def test_municipal_keeps_the_state_so_repeated_names_stay_apart(transform, extracted):
    municipal = transform.action(extracted)[LEVEL_MUNICIPAL]
    benito = municipal[municipal["municipio"] == "Benito Juárez"]

    assert sorted(benito["estado"]) == ["Ciudad de México", "Quintana Roo"]


def test_strips_the_trailing_space_the_source_ships(transform, extracted):
    municipal = transform.action(extracted)[LEVEL_MUNICIPAL]

    assert "Jesús María" in set(municipal["municipio"])
    assert "Jesús María " not in set(municipal["municipio"])


@pytest.mark.parametrize(
    ("trimestre", "esperado"),
    [(1, date(2026, 1, 1)), (2, date(2026, 4, 1)), (3, date(2026, 7, 1)), (4, date(2026, 10, 1))],
)
def test_quarter_becomes_the_first_day_of_its_quarter(transform, trimestre, esperado):
    df = _frame([{"serie_global": "Nacional", "trimestre": trimestre, "anio": 2026, "indice": 100.0}])

    assert transform.action(df)[LEVEL_GLOBAL]["fecha"].iloc[0] == esperado


def test_drops_rows_with_an_unreadable_period(transform):
    df = _frame(
        [
            {"serie_global": "Nacional", "trimestre": 5, "anio": 2026, "indice": 100.0},
            {"serie_global": "Nacional", "trimestre": 2, "anio": 2026, "indice": 110.0},
        ]
    )

    assert len(transform.action(df)[LEVEL_GLOBAL]) == 1


def test_raises_when_the_levels_stop_being_mutually_exclusive(transform):
    """Si SHF llena 'Global' y 'Estado' en la misma fila, la partición ya no es válida."""
    df = _frame([{"serie_global": "Nacional", "estado": "Jalisco", "trimestre": 1, "anio": 2026, "indice": 100.0}])

    with pytest.raises(ValueError, match="exactly one level"):
        transform.action(df)


def test_whitespace_only_names_do_not_pass_as_a_level(transform):
    df = _frame([{"serie_global": "Nacional", "municipio": "   ", "trimestre": 1, "anio": 2026, "indice": 100.0}])

    levels = transform.action(df)

    assert len(levels[LEVEL_GLOBAL]) == 1
    assert levels[LEVEL_MUNICIPAL].empty
