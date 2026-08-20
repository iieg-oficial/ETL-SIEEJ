from pydantic import Field
from pydantic_settings import SettingsConfigDict
from sqlalchemy.engine import make_url

from core.config import BaseConfig, env_path
from core.pipelines.edafologia.constants import CANONICAL_SRID, CVEGEO_DATABASE_NAME, SOURCE_VERSION


class Settings(BaseConfig):
    model_config = SettingsConfigDict(env_file=env_path("edafologia"))

    DB_NAME: str = Field(default="edafologia")

    SOURCE_URL: str
    SOURCE_VERSION: str = Field(default=SOURCE_VERSION)
    CANONICAL_SRID: int = Field(default=CANONICAL_SRID)
    FORCE_DOWNLOAD: bool = Field(default=False)
    DOWNLOAD_RETRIES: int = Field(default=5)
    DOWNLOAD_CONNECT_TIMEOUT: int = Field(default=30)
    DOWNLOAD_READ_TIMEOUT: int = Field(default=300)

    CHUNK_SIZE: int = Field(default=10_000)

    @property
    def cvegeo_database_url(self) -> str:
        return make_url(self.database_url).set(database=CVEGEO_DATABASE_NAME).render_as_string(hide_password=False)


settings = Settings()
