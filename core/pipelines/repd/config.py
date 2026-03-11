from pydantic import Field
from pydantic_settings import SettingsConfigDict

from core.config import BaseConfig, env_path


class Settings(BaseConfig):
    model_config = SettingsConfigDict(env_file=env_path("repd"))

    REPD_DATA_URL: str = Field(
        default="https://repd.jalisco.gob.mx/api/v1/version_publica/exportrebdboptimizado/xls/"
    )
    REPD_LOAD_BATCH_SIZE: int = Field(default=5000)


settings = Settings()
