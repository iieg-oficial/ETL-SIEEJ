import pytest

from core.pipelines.enec.constants import ENTIDAD_RENAME, NACIONAL_RENAME
from core.pipelines.enec.stages import extract as extract_module
from core.pipelines.enec.stages.extract import EnecExtract


class _Response:
    def __init__(self, content: bytes, status_code: int = 200):
        self.content = content
        self.status_code = status_code


@pytest.fixture
def extract() -> EnecExtract:
    return EnecExtract()


@pytest.fixture
def fake_http(monkeypatch):
    def _install(response: _Response):
        monkeypatch.setattr(extract_module, "http_get", lambda url, timeout: response)
        return response

    return _install


class TestDownload:
    def test_returns_content_when_response_is_a_zip(self, extract, fake_http, make_dataset_zip):
        archive = make_dataset_zip()
        fake_http(_Response(archive))

        assert extract.source() == archive

    def test_html_error_page_with_status_200_raises(self, extract, fake_http):
        """INEGI serves an HTML error page with status 200 when a path is gone."""
        fake_http(_Response(b"<!DOCTYPE html><html><body>No encontrado</body></html>"))

        with pytest.raises(FileNotFoundError, match="did not serve a ZIP"):
            extract.source()

    def test_error_message_points_at_the_env_var(self, extract, fake_http):
        fake_http(_Response(b"<!DOCTYPE html>"))

        with pytest.raises(FileNotFoundError, match="ENEC_URL"):
            extract.source()

    def test_non_200_status_raises(self, extract, fake_http, make_dataset_zip):
        fake_http(_Response(make_dataset_zip(), status_code=404))

        with pytest.raises(FileNotFoundError):
            extract.source()


class TestTrailingSpaceInHeader:
    """Regression: the source header is "J000A ", with a trailing space.

    Without stripping the headers the rename silently misses it and
    remuneraciones_tot loads as all nulls — no error, no warning.
    """

    def test_the_remunerations_column_is_not_lost(self, extract, make_dataset_zip):
        result = extract.action(make_dataset_zip())

        assert "remuneraciones_tot" in result["nacional"].columns
        assert result["nacional"]["remuneraciones_tot"].iloc[0] == "1000"

    def test_it_is_not_lost_in_the_state_dataset_either(self, extract, make_dataset_zip):
        result = extract.action(make_dataset_zip())

        assert result["entidad"]["remuneraciones_tot"].iloc[0] == "1000"


class TestParsing:
    def test_keeps_only_the_renamed_columns(self, extract, make_dataset_zip):
        result = extract.action(make_dataset_zip())

        assert list(result["nacional"].columns) == list(NACIONAL_RENAME.values())
        assert list(result["entidad"].columns) == list(ENTIDAD_RENAME.values())

    def test_the_state_dataset_drops_the_activity_columns(self, extract, make_dataset_zip):
        """The state file only covers sector 23, so the code is constant noise."""
        result = extract.action(make_dataset_zip())

        assert "codigo_actividad" not in result["entidad"].columns
        assert "codigo_actividad" in result["nacional"].columns

    def test_o110b_is_not_carried_over(self, extract, make_dataset_zip):
        """O110B is byte-identical to O110A; it repeats the total as a header."""
        result = extract.action(make_dataset_zip())

        assert not [c for c in result["nacional"].columns if c.endswith("o110b")]

    def test_both_datasets_are_read(self, extract, make_dataset_zip, csv_row):
        result = extract.action(
            make_dataset_zip(
                nacional=[csv_row(codigo="23"), csv_row(codigo="236")],
                entidad=[csv_row(), csv_row(cvegeo="\t06", nom_ent="Colima")],
            )
        )

        assert len(result["nacional"]) == 2
        assert len(result["entidad"]) == 2

    def test_future_edition_flows_through_without_touching_the_code(self, extract, make_dataset_zip, csv_row):
        result = extract.action(make_dataset_zip(year="2027", entidad=[csv_row(anio="2027")]))

        assert result["entidad"]["anio"].tolist() == ["2027"]

    def test_zip_without_the_national_csv_raises(self, extract, make_zip, nacional_header, csv_row):
        archive = make_zip(
            {
                "conjunto_de_datos/enec_absoluto_entidad_2018_2026.csv": "\n".join([nacional_header, csv_row()]).encode(
                    "utf-8"
                )
            }
        )

        with pytest.raises(FileNotFoundError, match="enec_absoluto_nacional"):
            extract.action(archive)

    def test_dataset_with_missing_columns_raises(self, extract, make_zip):
        archive = make_zip(
            {
                "conjunto_de_datos/enec_absoluto_nacional_2018_2026.csv": b"CODIGO_ACTIVIDAD,ANIO,MES\n23,2026,01",
                "conjunto_de_datos/enec_absoluto_entidad_2018_2026.csv": b"CVEGEO,ANIO,MES\n14,2026,01",
            }
        )

        with pytest.raises(ValueError, match="expected columns missing"):
            extract.action(archive)
