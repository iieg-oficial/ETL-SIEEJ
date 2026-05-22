from pydantic_settings import SettingsConfigDict

from core.config import BaseConfig, env_path


class Settings(BaseConfig):
    model_config = SettingsConfigDict(env_file=env_path("participacion_ciudadana"))

    GDRIVE_FILE_ID: str


settings = Settings()
