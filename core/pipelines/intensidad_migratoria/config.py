from pydantic_settings import SettingsConfigDict

from core.config import BaseConfig, env_path


class Settings(BaseConfig):
    model_config = SettingsConfigDict(env_file=env_path("intensidad_migratoria"))

    IIM_URL_MUNICIPAL_2010: str
    IIM_URL_MUNICIPAL_2020: str
    IIM_URL_ESTATAL_2020: str


settings = Settings()
