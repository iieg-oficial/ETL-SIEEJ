from pydantic import Field
from pydantic_settings import SettingsConfigDict
from core.config import BaseConfig, env_path

class Settings(BaseConfig):
    model_config = SettingsConfigDict(env_file=env_path("establecimientos_de_salud"))

    ESTABLECIMIENTOS_URL: str
    BOOTSTRAP_START_YEAR: int = Field(default=2017)
    BOOTSTRAP_START_MONTH: int = Field(default=5)

    def build_url(self, year: int, month: int) -> str:
        return self.ESTABLECIMIENTOS_URL.format(year=year, month=str(month).zfill(2))

settings = Settings()
