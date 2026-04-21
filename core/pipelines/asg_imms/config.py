from pydantic import Field
from pydantic_settings import SettingsConfigDict

from core.config import BaseConfig, env_path


class Settings(BaseConfig):
    model_config = SettingsConfigDict(env_file=env_path("asg_imms"))

    ASG_DOWNLOAD_TIMEOUT: int = Field(default=300)
    ASG_DOWNLOAD_MAX_RETRIES: int = Field(default=3)
    ASG_LOAD_BATCH_SIZE: int = Field(default=50000)
    ASG_START_DATE: str = Field(default="2015-01-31")


settings = Settings()
