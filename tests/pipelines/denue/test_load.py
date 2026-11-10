"""COPY buffer encoding for DENUE: null marker, escaping and whitespace."""

import pandas as pd
import pytest

from core.pipelines.denue.constants import INT_COLS, RAW_COLS
from core.pipelines.denue.stages.load import DenueLoad

NULL = "\\N"


@pytest.fixture
def loader() -> DenueLoad:
    return object.__new__(DenueLoad)


def _row(**overrides) -> pd.DataFrame:
    base = {col: ("1" if col in INT_COLS or col == "codigo_actividad" else "x") for col in RAW_COLS}
    base.update(overrides)
    return pd.DataFrame([base])


def _fields(loader: DenueLoad, df: pd.DataFrame) -> dict[str, str]:
    line = loader._prepare_copy_buffer(df).getvalue().rstrip("\n")
    return dict(zip(RAW_COLS, line.split("\t")))


@pytest.mark.parametrize("null_value", [None, float("nan"), pd.NaT, "nan", "NaT", "None"])
def test_null_text_is_emitted_as_copy_null_marker(loader, null_value):
    assert _fields(loader, _row(telefono=null_value))["telefono"] == NULL


def test_literal_backslash_is_escaped(loader):
    assert _fields(loader, _row(razon_social="a\\b"))["razon_social"] == "a\\\\b"


def test_tabs_and_newlines_collapse_to_space(loader):
    assert _fields(loader, _row(razon_social="a\t\nb\r\nc"))["razon_social"] == "a b c"


def test_null_int_is_emitted_as_copy_null_marker(loader):
    assert _fields(loader, _row(id=None))["id"] == NULL
