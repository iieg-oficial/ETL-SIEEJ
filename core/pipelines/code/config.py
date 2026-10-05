from pydantic import Field
from pydantic_settings import SettingsConfigDict

from core.config import BaseConfig, env_path

PIPELINE_NAME = "code"


class Settings(BaseConfig):
    model_config = SettingsConfigDict(env_file=env_path(PIPELINE_NAME), extra="ignore")

    PIPELINE_NAME: str = Field(default=PIPELINE_NAME)
    DEPENDENCIA: str = Field(default="Consejo Estatal para el Fomento Deportivo - CODE")


settings = Settings()
