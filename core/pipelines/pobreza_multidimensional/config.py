from pydantic import Field
from pydantic_settings import SettingsConfigDict

from core.config import BaseConfig, env_path


class Settings(BaseConfig):
    model_config = SettingsConfigDict(env_file=env_path("pobreza_multidimensional"))

    POBREZA_MULTIDIMENSIONAL_LOAD_BATCH_SIZE: int = Field(default=5000)
    SOURCE_URL_TEMPLATE: str = Field(...)


settings = Settings()
