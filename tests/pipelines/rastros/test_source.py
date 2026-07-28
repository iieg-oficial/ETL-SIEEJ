import pytest

from core.pipelines.rastros.helpers import source
from core.pipelines.rastros.helpers.source import fetch_dataset


class _Response:
    def __init__(self, content: bytes, status_code: int = 200):
        self.content = content
        self.status_code = status_code


@pytest.fixture
def fake_http(monkeypatch):
    def _install(response: _Response):
        monkeypatch.setattr(source, "http_get", lambda url, timeout: response)
        return response

    return _install


def test_returns_content_when_response_is_a_zip(fake_http, make_dataset_zip):
    archive = make_dataset_zip()
    fake_http(_Response(archive))

    assert fetch_dataset() == archive


def test_html_error_page_with_status_200_raises(fake_http):
    """INEGI serves an HTML error page with status 200 when a path is gone.

    This is the whole reason the signature is checked: raise_for_status() would
    happily accept this response and the pipeline would parse a web page.
    """
    fake_http(_Response(b"<!DOCTYPE html><html><body>No encontrado</body></html>"))

    with pytest.raises(FileNotFoundError, match="did not serve a ZIP"):
        fetch_dataset()


def test_error_message_points_at_the_env_var(fake_http):
    """The failure has to tell whoever reads the Airflow log what to fix."""
    fake_http(_Response(b"<!DOCTYPE html>"))

    with pytest.raises(FileNotFoundError, match="ESGRM_URL"):
        fetch_dataset()


def test_non_200_status_raises(fake_http, make_dataset_zip):
    fake_http(_Response(make_dataset_zip(), status_code=404))

    with pytest.raises(FileNotFoundError):
        fetch_dataset()
