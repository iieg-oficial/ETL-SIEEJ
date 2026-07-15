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

    GRUPO1_DICTIONARY_PATH: str
    CALIFP_G1_DICTIONARY_PATH: str
    CALIFS_G1_DICTIONARY_PATH: str

    CHUNK_SIZE: int = Field(default=10_000)


settings = Settings()
