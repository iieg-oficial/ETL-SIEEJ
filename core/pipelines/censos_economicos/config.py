from pydantic import Field
from pydantic_settings import SettingsConfigDict

from core.config import BaseConfig, env_path


class Settings(BaseConfig):
    model_config = SettingsConfigDict(env_file=env_path("censos_economicos"))

    PIPELINE_NAME: str = Field(default="censos_economicos")
    BULK_SIZE: int = Field(default=20_000)


settings = Settings()
