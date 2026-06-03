from pydantic_settings import SettingsConfigDict

from core.config import BaseConfig, env_path


class Settings(BaseConfig):
    model_config = SettingsConfigDict(env_file=env_path("conapo"), extra="ignore")

    CONAPO_URL: str


settings = Settings()
