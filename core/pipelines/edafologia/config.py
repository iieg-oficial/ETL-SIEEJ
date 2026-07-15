from pydantic import Field
from pydantic_settings import SettingsConfigDict

from core.config import BaseConfig, env_path
from core.pipelines.edafologia.constants import CANONICAL_SRID, SOURCE_VERSION


class Settings(BaseConfig):
    model_config = SettingsConfigDict(env_file=env_path("edafologia"))

    DB_NAME: str = Field(default="edafologia")

    SOURCE_URL: str
    SOURCE_VERSION: str = Field(default=SOURCE_VERSION)
    CANONICAL_SRID: int = Field(default=CANONICAL_SRID)
    SOURCE_ZIP_PATH: str | None = Field(default=None)
    FORCE_DOWNLOAD: bool = Field(default=False)
    DOWNLOAD_RETRIES: int = Field(default=5)
    DOWNLOAD_CONNECT_TIMEOUT: int = Field(default=30)
    DOWNLOAD_READ_TIMEOUT: int = Field(default=300)

    GRUPO1_DICTIONARY_PATH: str
    CALIFP_G1_DICTIONARY_PATH: str
    CALIFS_G1_DICTIONARY_PATH: str

    CHUNK_SIZE: int = Field(default=10_000)


settings = Settings()
