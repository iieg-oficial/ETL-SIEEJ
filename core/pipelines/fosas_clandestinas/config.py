from pydantic import Field
from pydantic_settings import SettingsConfigDict

from core.config import BaseConfig, env_path


class Settings(BaseConfig):
    model_config = SettingsConfigDict(env_file=env_path("fosas_clandestinas"))

    UPLOADS_URL: str = Field(default="https://fiscaliaenpersonasdesaparecidas.jalisco.gob.mx/wp-content/uploads/")
    FIRST_YEAR: int = Field(default=2022)
    HTTP_TIMEOUT: int = Field(default=60)


settings = Settings()
