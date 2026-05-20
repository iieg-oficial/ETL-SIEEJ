from pydantic import Field
from pydantic_settings import SettingsConfigDict

from core.config import BaseConfig, env_path


class Settings(BaseConfig):
    model_config = SettingsConfigDict(env_file=env_path("denue"))

    PIPELINE_NAME: str = Field(default="denue")
    DENUE_URL: str = Field()
    BOOTSTRAP_START_DATE: str = Field(default="01/01/2016")
    CHUNK_SIZE: int = Field(default=200_000)
    SCIAN_FILE_ID: str = Field(default="")
    SCIAN_CSV_NAME: str = Field(default="scian_2023.csv")


settings = Settings()
