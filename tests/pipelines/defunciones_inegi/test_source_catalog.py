"""Regresión de #379: las URLs de las ediciones salen del catálogo de INEGI.

INEGI publicó 2025 en `datosabiertos/` y no en `datosabiertos/defunciones/2025/`,
así que las plantillas de nombre ya no la encuentran.
"""

import json
from pathlib import Path

import pytest
from requests.exceptions import ConnectionError

from core.pipelines.defunciones_inegi.config import settings
from core.pipelines.defunciones_inegi.helpers import source

FIXTURE = Path(__file__).parent / "fixtures" / "catalogo_datos_abiertos.json"

CATALOG_URL = "https://inegi.test/catalogo"
CONTENT_URL = "https://www.inegi.org.mx/contenidos"
BASE_URL = f"{CONTENT_URL}/programas/edr/datosabiertos/defunciones"

URL_2024 = f"{BASE_URL}/2024/conjunto_de_datos_edr2024_csv.zip"
URL_2025 = f"{CONTENT_URL}/programas/edr/datosabiertos/conjunto_de_datos_edr2025_csv.zip"
TEMPLATE_URL_2025 = f"{BASE_URL}/2025/conjunto_de_datos_edr2025_csv.zip"

ZIP_BODY = b"PK\x03\x04" + b"\x00" * 64
HTML_BODY = b"<!DOCTYPE html><html>no existe</html>"


@pytest.fixture
def catalog_records() -> list[dict]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


@pytest.fixture(autouse=True)
def isolated_settings(monkeypatch):
    """El .env local puede cambiar estos valores; las pruebas no deben depender de él."""
    monkeypatch.setattr(settings, "SOURCE_CATALOG_URL", CATALOG_URL)
    monkeypatch.setattr(settings, "SOURCE_CONTENT_URL", CONTENT_URL)
    monkeypatch.setattr(settings, "SOURCE_BASE_URL", BASE_URL)
    monkeypatch.setattr(settings, "SOURCE_URL_TEMPLATES", "{year}/conjunto_de_datos_edr{year}_csv.zip")
    monkeypatch.setattr(settings, "BACKFILL_MIN_YEAR", 2017)


class FakeResponse:
    def __init__(self, body: bytes = b"", status: int = 200, payload=None, json_error: bool = False):
        self.body = body
        self.status_code = status
        self.payload = payload
        self.json_error = json_error
        self.read_sizes: list[int] = []
        self.closed = False

    @property
    def ok(self) -> bool:
        return self.status_code < 400

    def raise_for_status(self) -> None:
        if not self.ok:
            from requests.exceptions import HTTPError

            raise HTTPError(f"{self.status_code}", response=self)

    def json(self):
        if self.json_error:
            raise ValueError("Expecting value")
        return self.payload

    def iter_content(self, chunk_size: int = 1):
        self.read_sizes.append(chunk_size)
        for start in range(0, len(self.body), chunk_size):
            yield self.body[start : start + chunk_size]

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.closed = True
        return False


class FakeInegi:
    """Sirve el catálogo y responde ZIP sólo para las URLs publicadas.

    Cualquier otra URL recibe la página de error con 200, como hace INEGI.
    """

    def __init__(self, catalog: FakeResponse | Exception, published: set[str]):
        self.catalog = catalog
        self.published = published
        self.calls: list[tuple[str, bool]] = []
        self.responses: dict[str, FakeResponse] = {}

    def __call__(self, url: str, timeout: int, stream: bool = False):
        self.calls.append((url, stream))
        if url == CATALOG_URL:
            if isinstance(self.catalog, Exception):
                raise self.catalog
            return self.catalog
        response = FakeResponse(ZIP_BODY if url in self.published else HTML_BODY)
        self.responses[url] = response
        return response

    def probed(self) -> list[str]:
        return [url for url, _ in self.calls if url != CATALOG_URL]


def _serve(monkeypatch, catalog, published) -> FakeInegi:
    fake = FakeInegi(catalog, set(published))
    monkeypatch.setattr(source, "http_get", fake)
    return fake


# --- catálogo -----------------------------------------------------------------


def test_catalog_builds_2025_url_outside_the_year_folder(monkeypatch, catalog_records):
    _serve(monkeypatch, FakeResponse(payload=catalog_records), published=[])

    editions = source.catalog_editions()

    assert editions[2025] == URL_2025
    assert editions[2024] == URL_2024


@pytest.mark.parametrize(
    "broken",
    [
        {"anioInformacion": "|2030", "formato": "_csv.zip&1 MB|", "tipoInformacion": "Datos abiertos"},
        {
            "anioInformacion": "|2030",
            "formato": "_csv.zip&1 MB|",
            "pathLogico": "",
            "tipoInformacion": "Datos abiertos",
        },
        {
            "anioInformacion": "|2030",
            "formato": "_xlsx.zip&1 MB|",
            "pathLogico": "/x",
            "tipoInformacion": "Datos abiertos",
        },
        {"anioInformacion": "|2030", "formato": "_csv.zip&1 MB|", "pathLogico": "/x", "tipoInformacion": "Microdatos"},
        {
            "anioInformacion": "|2030|2031",
            "formato": "_csv.zip&1 MB|",
            "pathLogico": "/x",
            "tipoInformacion": "Datos abiertos",
        },
        {"anioInformacion": None, "formato": "_csv.zip&1 MB|", "pathLogico": "/x", "tipoInformacion": "Datos abiertos"},
        "no soy un registro",
    ],
    ids=["sin-path", "path-vacio", "no-csv", "otro-tipo", "varios-anios", "anio-nulo", "no-dict"],
)
def test_catalog_skips_records_it_cannot_trust(monkeypatch, catalog_records, broken):
    _serve(monkeypatch, FakeResponse(payload=[*catalog_records, broken]), published=[])

    editions = source.catalog_editions()

    assert 2030 not in editions and 2031 not in editions
    assert editions[2025] == URL_2025


@pytest.mark.parametrize(
    "catalog",
    [
        ConnectionError("sin red"),
        FakeResponse(status=503),
        FakeResponse(json_error=True),
        FakeResponse(payload={"error": "no es una lista"}),
        FakeResponse(payload=[]),
    ],
    ids=["sin-red", "http-503", "json-invalido", "no-lista", "vacio"],
)
def test_catalog_failure_returns_empty(monkeypatch, catalog):
    _serve(monkeypatch, catalog, published=[])

    assert source.catalog_editions() == {}


# --- descubrimiento -----------------------------------------------------------


def test_available_editions_finds_2025_through_the_catalog(monkeypatch, catalog_records):
    _serve(monkeypatch, FakeResponse(payload=catalog_records), published=[URL_2024, URL_2025])

    editions = source.available_editions(since_year=2024, until_year=2026)

    assert editions == {2024: URL_2024, 2025: URL_2025}


def test_backfill_floor_and_since_year_are_respected(monkeypatch, catalog_records):
    fake = _serve(monkeypatch, FakeResponse(payload=catalog_records), published=[URL_2024, URL_2025])

    editions = source.available_editions(since_year=2010, until_year=2025)

    # 2016 está en el catálogo pero es anterior a BACKFILL_MIN_YEAR (2017).
    assert 2016 not in editions
    assert not any("2016" in url for url in fake.probed())
    assert source.available_editions(since_year=2025, until_year=2025) == {2025: URL_2025}


def test_falls_back_to_templates_when_catalog_is_down(monkeypatch):
    fake = _serve(monkeypatch, ConnectionError("sin red"), published=[URL_2024])

    editions = source.available_editions(since_year=2024, until_year=2025)

    assert editions == {2024: URL_2024}
    assert TEMPLATE_URL_2025 in fake.probed()


def test_falls_back_to_templates_when_catalog_url_is_not_a_zip(monkeypatch, catalog_records):
    # El catálogo lista 2025 pero esa ruta todavía da la página de error;
    # la plantilla sí responde un ZIP.
    _serve(monkeypatch, FakeResponse(payload=catalog_records), published=[TEMPLATE_URL_2025])

    assert source.edition_url(2025, source.catalog_editions()) == (TEMPLATE_URL_2025, "plantilla")


def test_catalog_url_is_tried_before_templates(monkeypatch, catalog_records):
    fake = _serve(monkeypatch, FakeResponse(payload=catalog_records), published=[URL_2025, TEMPLATE_URL_2025])

    assert source.edition_url(2025, source.catalog_editions()) == (URL_2025, "catalogo")
    assert fake.probed() == [URL_2025]


def test_edition_not_published_anywhere(monkeypatch, catalog_records):
    _serve(monkeypatch, FakeResponse(payload=catalog_records), published=[])

    assert source.edition_url(2026, source.catalog_editions()) is None


# --- validación del ZIP -------------------------------------------------------


def test_zip_check_streams_and_reads_only_the_signature(monkeypatch):
    fake = _serve(monkeypatch, FakeResponse(payload=[]), published=[URL_2025])

    assert source._is_zip_url(URL_2025) is True

    assert fake.calls == [(URL_2025, True)]
    response = fake.responses[URL_2025]
    assert response.read_sizes == [2]
    assert response.closed


def test_zip_check_rejects_inegi_error_page(monkeypatch):
    _serve(monkeypatch, FakeResponse(payload=[]), published=[])

    assert source._is_zip_url(TEMPLATE_URL_2025) is False


def test_zip_check_rejects_http_errors(monkeypatch):
    monkeypatch.setattr(source, "http_get", lambda *_, **__: FakeResponse(ZIP_BODY, status=404))

    assert source._is_zip_url(URL_2025) is False
