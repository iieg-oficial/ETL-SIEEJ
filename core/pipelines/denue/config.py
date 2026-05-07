from pydantic import Field
from pydantic_settings import SettingsConfigDict

from core.config import BaseConfig, env_path


class Settings(BaseConfig):
    model_config = SettingsConfigDict(env_file=env_path("denue"))

    PIPELINE_NAME: str = Field(default="denue")
    DENUE_URL: str = Field(default="https://www.inegi.org.mx/app/descarga/?ti=6")
    BOOTSTRAP_START_DATE: str = Field(default="01/01/2016")
    CHUNK_SIZE: int = Field(default=200_000)


settings = Settings()
