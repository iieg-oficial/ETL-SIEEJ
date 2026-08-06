import pandas as pd

from core.pipelines.rastros.helpers import build_fecha


def test_combines_year_and_month_into_first_day_of_month():
    fecha = build_fecha(pd.Series(["2026"]), pd.Series(["05"]))

    assert fecha.iloc[0] == pd.Timestamp("2026-05-01")


def test_strips_the_tab_padding_the_source_ships():
    """ID_MES arrives as "\\t\\t01" in the published CSVs."""
    fecha = build_fecha(pd.Series(["2012"]), pd.Series(["\t\t01"]))

    assert fecha.iloc[0] == pd.Timestamp("2012-01-01")


def test_every_month_round_trips():
    meses = [f"{m:02d}" for m in range(1, 13)]
    fecha = build_fecha(pd.Series(["2026"] * 12), pd.Series(meses))

    assert fecha.dt.month.tolist() == list(range(1, 13))
    assert (fecha.dt.day == 1).all()


def test_unparseable_period_becomes_nat_instead_of_raising():
    """The caller drops NaT rows; a raise here would kill the whole edition."""
    fecha = build_fecha(pd.Series(["2026", "basura"]), pd.Series(["05", "99"]))

    assert fecha.iloc[0] == pd.Timestamp("2026-05-01")
    assert pd.isna(fecha.iloc[1])
