from pydantic import Field
from pydantic_settings import SettingsConfigDict

from core.config import BaseConfig, env_path
from core.pipelines.{{cookiecutter.pipeline}}.constants import PIPELINE_NAME


class Settings(BaseConfig):
    model_config = SettingsConfigDict(env_file=env_path(PIPELINE_NAME))

    DB_NAME: str = Field(default=PIPELINE_NAME)


settings = Settings()
