from pydantic import Field
from pydantic_settings import SettingsConfigDict

from core.config import BaseConfig, env_path


class Settings(BaseConfig):
    model_config = SettingsConfigDict(env_file=env_path("inpc"))
    INPC_BASE_URL: str
    INPC_URL_NODOS: str
    BOOTSTRAP_START_YEAR: int = Field(default=1979)


settings = Settings()
