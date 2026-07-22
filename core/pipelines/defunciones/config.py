from pydantic import Field
from pydantic_settings import SettingsConfigDict

from core.config import BaseConfig, env_path


class Settings(BaseConfig):
    model_config = SettingsConfigDict(env_file=env_path("defunciones"))

    DB_NAME: str = Field(default="defunciones")

    CATALOG_URL: str | None = Field(default=None)
    REGISTRO_URL: str | None = Field(default=None)

    CATALOGO_2021_FILE_ID: str

    BACKFILL_MIN_YEAR: int = Field(default=2019)

    CHUNK_SIZE: int = Field(default=10_000)


settings = Settings()
