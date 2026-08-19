import pytest

from core.pipelines.ems.constants import CATALOG_RENAME_HEADER, RENAME_HEADER
from core.pipelines.ems.stages import extract as extract_module
from core.pipelines.ems.stages.extract import EmsExtract


class _Response:
    def __init__(self, content: bytes, status_code: int = 200):
        self.content = content
        self.status_code = status_code


@pytest.fixture
def extract() -> EmsExtract:
    return EmsExtract()


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
        """The failure has to tell whoever reads the Airflow log what to fix."""
        fake_http(_Response(b"<!DOCTYPE html>"))

        with pytest.raises(FileNotFoundError, match="EMS_URL"):
            extract.source()

    def test_non_200_status_raises(self, extract, fake_http, make_dataset_zip):
        fake_http(_Response(make_dataset_zip(), status_code=404))

        with pytest.raises(FileNotFoundError):
            extract.source()


class TestParsing:
    def test_keeps_only_the_renamed_columns(self, extract, make_dataset_zip):
        result = extract.action(make_dataset_zip())

        assert list(result["df"].columns) == list(RENAME_HEADER.values())
        assert list(result["actividades"].columns) == list(CATALOG_RENAME_HEADER.values())

    def test_nom_ent_is_dropped_because_cvegeo_carries_the_key(self, extract, make_dataset_zip):
        """The name is redundant: the view gets it from cvegeo_states."""
        result = extract.action(make_dataset_zip())

        assert "nom_ent" not in result["df"].columns
        assert result["df"]["entidad_id"].iloc[0] == "14"

    def test_reads_every_dataset_row(self, extract, make_dataset_zip, csv_row):
        rows = [csv_row(), csv_row(codigo="61"), csv_row(cvegeo="06", nom_ent="Colima")]

        result = extract.action(make_dataset_zip(rows=rows))

        assert len(result["df"]) == 3

    def test_future_edition_flows_through_without_touching_the_code(self, extract, make_dataset_zip, csv_row):
        """January 2027: the CSV is renamed and the pipeline must keep running."""
        result = extract.action(make_dataset_zip(year="2027", rows=[csv_row(anio="2027")]))

        assert result["df"]["anio"].tolist() == ["2027"]

    def test_zip_without_dataset_csv_raises(self, extract, make_zip):
        archive = make_zip({"metadatos/metadatos.txt": b"solo metadatos"})

        with pytest.raises(FileNotFoundError, match="tr_ems_entidad_federativa_indice"):
            extract.action(archive)

    def test_dataset_with_missing_columns_raises(self, extract, make_zip):
        """A silent column drop would load nulls; the source contract has to break loudly."""
        archive = make_zip(
            {
                "conjunto_de_datos/tr_ems_entidad_federativa_indice_2013_2026.csv": (
                    b"CODIGO_ACTIVIDAD,ANIO,MES\n51,2026,01"
                ),
                "catalogos/tc_actividad.csv": b"CODIGO_ACTIVIDAD,DESCRIPCION_ACTIVIDAD\n51,Informacion",
            }
        )

        with pytest.raises(ValueError, match="expected columns missing"):
            extract.action(archive)

    def test_accented_names_survive_the_read(self, extract, make_dataset_zip):
        """EMS ships UTF-8. Reading it as latin-1 would not fail, it would mojibake."""
        catalog = "CODIGO_ACTIVIDAD,DESCRIPCION_ACTIVIDAD\n51,Información en medios masivos"

        result = extract.action(make_dataset_zip(catalog=catalog))

        assert result["actividades"]["descripcion"].iloc[0] == "Información en medios masivos"
