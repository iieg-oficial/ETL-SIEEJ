from pydantic_settings import SettingsConfigDict
from core.config import BaseConfig, env_path


class Settings(BaseConfig):
    model_config = SettingsConfigDict(env_file=env_path("centros_educativos"))
    CENTROS_EDUCATIVOS_URL: str
    PIPELINE_NAME: str


settings = Settings()
