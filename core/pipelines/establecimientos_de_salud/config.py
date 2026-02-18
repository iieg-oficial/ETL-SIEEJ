from pydantic_settings import SettingsConfigDict
from core.config import BaseConfig, env_path

class Settings(BaseConfig):
    model_config = SettingsConfigDict(env_file=env_path("establecimientos_de_salud"))

    ESTABLECIMIENTOS_URL: str

settings = Settings()
