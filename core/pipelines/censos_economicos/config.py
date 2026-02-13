from pydantic import Field
from pydantic_settings import SettingsConfigDict

from core.config import BaseConfig, env_path


class Settings(BaseConfig):
    model_config = SettingsConfigDict(env_file=env_path("censos_economicos"))

    CE_DOWNLOAD_MAX_WORKERS: int = Field(default=4)
    CE_DOWNLOAD_TIMEOUT: int = Field(default=120)
    CE_DOWNLOAD_MAX_RETRIES: int = Field(default=3)
    CE_DOWNLOAD_RETRY_BACKOFF: float = Field(default=5.0)
    CE_LOAD_BATCH_SIZE: int = Field(default=5000)
    CE_YEARS: str = Field(default="2024")

    @property
    def years_list(self) -> list[int]:
        return [int(y.strip()) for y in self.CE_YEARS.split(",")]


settings = Settings()
