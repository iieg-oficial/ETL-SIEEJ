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


def _frame(*overrides: dict) -> pd.DataFrame:
    return pd.concat([_row(**o) for o in overrides], ignore_index=True)


def _lines(loader: DenueLoad, df: pd.DataFrame) -> list[list[str]]:
    text = loader._prepare_copy_buffer(df).getvalue()
    return [line.split("\t") for line in text.split("\n") if line]


@pytest.mark.parametrize("null_value", [None, float("nan")])
def test_null_text_when_astype_str_yields_nan_strings(loader, monkeypatch, null_value):
    original = pd.Series.astype

    def pandas2_astype(self, dtype, *args, **kwargs):
        if dtype is str:
            return self.map(str)
        return original(self, dtype, *args, **kwargs)

    monkeypatch.setattr(pd.Series, "astype", pandas2_astype)
    assert _fields(loader, _row(telefono=null_value))["telefono"] == NULL


def test_every_line_has_raw_cols_field_count(loader):
    df = _frame(
        {"razon_social": "a\tb", "telefono": None, "nombre": "x\ny"},
        {"razon_social": "a\\", "id": None, "codigo_actividad": None},
        {"razon_social": "\r\n", "nombre": "tail\\", "telefono": "nan"},
        {"razon_social": "", "nombre": None},
    )
    lines = _lines(loader, df)
    assert len(lines) == len(df)
    assert all(len(fields) == len(RAW_COLS) for fields in lines)


def test_trailing_backslash_is_doubled_and_keeps_field_count(loader):
    df = _row(razon_social="a\\")
    assert _fields(loader, df)["razon_social"] == "a\\\\"
    assert len(_lines(loader, df)[0]) == len(RAW_COLS)


def test_empty_string_stays_empty(loader):
    assert _fields(loader, _row(razon_social=""))["razon_social"] == ""


def test_literal_backslash_n_text_is_escaped(loader):
    assert _fields(loader, _row(razon_social="\\N"))["razon_social"] == "\\\\N"


def test_null_codigo_actividad_is_emitted_as_copy_null_marker(loader):
    assert _fields(loader, _row(codigo_actividad=None))["codigo_actividad"] == NULL


def test_all_null_text_column_is_null_in_every_row(loader):
    df = _frame({"telefono": None}, {"telefono": float("nan")}, {"telefono": "None"})
    assert [fields[RAW_COLS.index("telefono")] for fields in _lines(loader, df)] == [NULL] * 3
