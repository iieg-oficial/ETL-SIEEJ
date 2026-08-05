import pytest

from core.pipelines.emec.constants import CATALOG_RENAME_HEADER, RENAME_HEADER
from core.pipelines.emec.stages import extract as extract_module
from core.pipelines.emec.stages.extract import EmecExtract


class _Response:
    def __init__(self, content: bytes, status_code: int = 200):
        self.content = content
        self.status_code = status_code


@pytest.fixture
def extract() -> EmecExtract:
    return EmecExtract()


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
        """INEGI serves an HTML error page with status 200 when a path is gone.

        This is the whole reason the signature is checked: raise_for_status()
        would happily accept this response and the pipeline would parse a page.
        """
        fake_http(_Response(b"<!DOCTYPE html><html><body>No encontrado</body></html>"))

        with pytest.raises(FileNotFoundError, match="did not serve a ZIP"):
            extract.source()

    def test_error_message_points_at_the_env_var(self, extract, fake_http):
        """The failure has to tell whoever reads the Airflow log what to fix."""
        fake_http(_Response(b"<!DOCTYPE html>"))

        with pytest.raises(FileNotFoundError, match="EMEC_URL"):
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

    def test_reads_every_dataset_row(self, extract, make_dataset_zip, csv_row):
        rows = [csv_row(), csv_row(codigo="46"), csv_row(entidad="Colima")]

        result = extract.action(make_dataset_zip(rows=rows))

        assert len(result["df"]) == 3

    def test_future_edition_flows_through_without_touching_the_code(self, extract, make_dataset_zip, csv_row):
        """January 2027: the CSV is renamed and the pipeline must keep running."""
        result = extract.action(make_dataset_zip(year="2027", rows=[csv_row(anio="2027")]))

        assert result["df"]["anio"].tolist() == ["2027"]

    def test_zip_without_dataset_csv_raises(self, extract, make_zip):
        archive = make_zip({"metadatos/metadatos.txt": b"solo metadatos"})

        with pytest.raises(FileNotFoundError, match="tr_emec_entidad_federativa_indice"):
            extract.action(archive)

    def test_dataset_with_missing_columns_raises(self, extract, make_zip):
        """A silent column drop would load nulls; the source contract has to break loudly."""
        archive = make_zip(
            {
                "conjunto_de_datos/tr_emec_entidad_federativa_indice_2008_2026.csv": (
                    b"CODIGO_ACTIVIDAD,ANIO,MES\n43,2026,01"
                ),
                "catalogos/tc_actividad.csv": b"CODIGO_ACTIVIDAD,DESCRIPCION_ACTIVIDAD\n43,Comercio al por mayor",
            }
        )

        with pytest.raises(ValueError, match="expected columns missing"):
            extract.action(archive)

    def test_accented_entity_names_survive_the_read(self, extract, make_dataset_zip, csv_row):
        """Regression: EMEC ships UTF-8, unlike ESGRM which is latin-1.

        Reading it as latin-1 does not fail, it mojibakes: "Ciudad de México"
        becomes "Ciudad de MÃ©xico", which then finds no match in cvegeo_states
        and drops seven states without a single error.
        """
        rows = [csv_row(entidad="Ciudad de México"), csv_row(entidad="Nuevo León")]

        result = extract.action(make_dataset_zip(rows=rows))

        assert result["df"]["entidad"].tolist() == ["Ciudad de México", "Nuevo León"]

    def test_accented_activity_descriptions_survive_the_read(self, extract, make_dataset_zip):
        catalog = "CODIGO_ACTIVIDAD,DESCRIPCION_ACTIVIDAD\n433,Productos farmacéuticos y de perfumería"

        result = extract.action(make_dataset_zip(catalog=catalog))

        assert result["actividades"]["descripcion"].iloc[0] == "Productos farmacéuticos y de perfumería"

    def test_reads_the_activity_catalog_from_the_zip(self, extract, make_dataset_zip):
        result = extract.action(make_dataset_zip())

        assert result["actividades"]["codigo_actividad"].tolist() == ["43", "46"]
