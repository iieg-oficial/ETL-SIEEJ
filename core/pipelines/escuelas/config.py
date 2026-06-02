from pydantic import Field
from pydantic_settings import SettingsConfigDict

from core.config import BaseConfig, env_path
from core.pipelines.escuelas.constants import DEFAULT_SOURCE_YEAR


class Settings(BaseConfig):
    model_config = SettingsConfigDict(env_file=env_path("escuelas"))

    DB_NAME: str = Field(default="escuelas")
    SOURCE_YEAR: int = Field(default=DEFAULT_SOURCE_YEAR)
    DIRECTORIO_FILENAME: str = Field(default="directorio_escuelas.csv")
    ESTADISTICA_FILENAME: str = Field(default="estadistica_escuelas.csv")
    GDRIVE_FOLDER_ID: str
    GDRIVE_CLIENT_EMAIL: str
    GDRIVE_PRIVATE_KEY: str


settings = Settings()
