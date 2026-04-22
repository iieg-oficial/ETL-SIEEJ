from pydantic import field_validator
from pydantic_settings import SettingsConfigDict

from core.config import BaseConfig, env_path


class Settings(BaseConfig):
    model_config = SettingsConfigDict(env_file=env_path("marginacion"))

    URL_MUNICIPAL: str
    URL_MUNICIPAL_DP2: str
    URL_LOCALIDAD: str
    DATA_YEARS: list[int]

    @field_validator("DATA_YEARS", mode="before")
    @classmethod
    def parse_years(cls, v):
        if isinstance(v, str):
            return [int(y.strip()) for y in v.split(",")]
        if isinstance(v, int):
            return [v]
        return v


settings = Settings()
