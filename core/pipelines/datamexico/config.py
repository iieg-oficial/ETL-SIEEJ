from pydantic_settings import SettingsConfigDict
from core.config import BaseConfig, env_path


class Settings(BaseConfig):
    model_config = SettingsConfigDict(env_file=env_path("datamexico"))

    DATAMEXICO_URL: str
    START_QUARTER: int
    CHUNK_SIZE: int


settings = Settings()
