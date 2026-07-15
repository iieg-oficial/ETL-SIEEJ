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

    CVEGEO_DB_USER: str
    CVEGEO_DB_PASSWORD: str
    CVEGEO_DB_HOST: str
    CVEGEO_DB_PORT: str = Field(default="5432")
    CVEGEO_DB_NAME: str = Field(default="cvegeo")

    CHUNK_SIZE: int = Field(default=10_000)

    @property
    def cvegeo_database_url(self) -> str:
        return (
            f"postgresql://{self.CVEGEO_DB_USER}:{self.CVEGEO_DB_PASSWORD}"
            f"@{self.CVEGEO_DB_HOST}:{self.CVEGEO_DB_PORT}/{self.CVEGEO_DB_NAME}"
        )


settings = Settings()
