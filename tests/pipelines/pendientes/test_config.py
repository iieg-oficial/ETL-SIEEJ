from pathlib import Path

from core.pipelines.pendientes.config import Settings

_REQUIRED_DB = {
    "DB_USER": "test",
    "DB_PASSWORD": "test",
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
}


def _settings(**overrides: str) -> Settings:
    return Settings(_env_file=None, **(_REQUIRED_DB | overrides))


def test_blank_optional_path_becomes_none() -> None:
    """An empty assignment in the .env means "unset", not the current directory."""
    settings = _settings(SOURCE_TIFF_PATH="", CVEGEO_MUNICIPAL_BOUNDARY_SNAPSHOT_PATH="   ")

    assert settings.SOURCE_TIFF_PATH is None
    assert settings.CVEGEO_MUNICIPAL_BOUNDARY_SNAPSHOT_PATH is None


def test_optional_path_is_preserved_when_set() -> None:
    settings = _settings(SOURCE_TIFF_PATH="data/extract/pendientes/continuonacional_15m.tif")

    assert settings.SOURCE_TIFF_PATH == Path("data/extract/pendientes/continuonacional_15m.tif")
