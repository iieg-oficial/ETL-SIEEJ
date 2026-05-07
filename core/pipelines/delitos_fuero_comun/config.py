from pydantic import Field
from pydantic_settings import SettingsConfigDict

from core.config import BaseConfig, env_path

PIPELINE_NAME = "delitos_fuero_comun"


class Settings(BaseConfig):
    model_config = SettingsConfigDict(env_file=env_path("delitos_fuero_comun"))

    URL_HISTORICO: str = Field(default="")
    URL_2026: str = Field(default="")
    CSV_HISTORICO: str = Field(default="Municipal-Delitos-2015-2025_mar2026.csv")
    CSV_2026: str = Field(default="RNID-Delitos_Municipal-2026-mar2026.csv")
    LOAD_BATCH_SIZE: int = Field(default=5000)


settings = Settings()
