from pydantic_settings import SettingsConfigDict

from core.config import BaseConfig, env_path


class Settings(BaseConfig):
    model_config = SettingsConfigDict(env_file=env_path("censo_poblacion"))

    CENSO_URL_2010: str
    CENSO_URL_2015: str
    CENSO_URL_2020: str


settings = Settings()
