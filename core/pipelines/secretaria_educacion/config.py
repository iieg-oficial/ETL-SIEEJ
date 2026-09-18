from pydantic import Field
from pydantic_settings import SettingsConfigDict

from core.config import BaseConfig, env_path

PIPELINE_NAME = "secretaria_educacion"


class Settings(BaseConfig):
    model_config = SettingsConfigDict(env_file=env_path(PIPELINE_NAME), extra="ignore")

    PIPELINE_NAME: str = Field(default=PIPELINE_NAME)
    DEPENDENCIA: str = Field(default="Secretaría de Educación")


settings = Settings()
