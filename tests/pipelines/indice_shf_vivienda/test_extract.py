import pytest

from core.pipelines.indice_shf_vivienda.constants import RENAME_HEADER
from core.pipelines.indice_shf_vivienda.stages.extract import IndiceShfViviendaExtract


class _Response:
    def __init__(self, content: bytes, status_code: int = 200):
        self.content = content
        self.status_code = status_code


@pytest.fixture
def extract() -> IndiceShfViviendaExtract:
    return IndiceShfViviendaExtract()


def test_source_rejects_the_waf_challenge_page(extract, monkeypatch):
    """gob.mx answers 200 with an HTML challenge; only the signature catches it."""
    challenge = b"<!DOCTYPE html><html><head><title>Challenge Validation</title></head></html>"
    monkeypatch.setattr(
        "core.pipelines.indice_shf_vivienda.stages.extract.http_get",
        lambda url, timeout: _Response(challenge),
    )

    with pytest.raises(FileNotFoundError, match="did not serve an XLSX"):
        extract.source()


def test_source_accepts_a_workbook(extract, monkeypatch, workbook_bytes):
    monkeypatch.setattr(
        "core.pipelines.indice_shf_vivienda.stages.extract.http_get",
        lambda url, timeout: _Response(workbook_bytes),
    )

    assert extract.source() == workbook_bytes


def test_action_renames_the_columns_and_drops_consecutivo(extract, workbook_bytes):
    df = extract.action(workbook_bytes)

    assert list(df.columns) == list(RENAME_HEADER.values())
    assert "Consecutivo" not in df.columns
    assert len(df) == 7


def test_action_raises_when_a_column_is_missing(extract, make_workbook):
    rows = [{"Global": "Nacional", "Trimestre": 1, "Año": 2005, "Indice": 48.47}]
    without_indice = [c for c in ["Consecutivo", *RENAME_HEADER] if c != "Indice"]

    with pytest.raises(ValueError, match="expected columns missing"):
        extract.action(make_workbook(rows, columns=without_indice))
