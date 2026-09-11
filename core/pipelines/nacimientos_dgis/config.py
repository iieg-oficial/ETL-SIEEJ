from pydantic import Field
from pydantic_settings import SettingsConfigDict

from core.config import BaseConfig, env_path


class Settings(BaseConfig):
    model_config = SettingsConfigDict(env_file=env_path("nacimientos_dgis"), extra="ignore")

    PIPELINE_NAME: str = Field(default="nacimientos_dgis")
    SOURCE_URL: str = Field(default="http://www.dgis.salud.gob.mx/descargas/datosabiertos/nacimientos/sinac_{year}.zip")
    # Los catálogos se publican aparte del microdato, por rango de ediciones.
    CATALOG_URL: str = Field(default="http://www.dgis.salud.gob.mx/descargas/datosabiertos/nacimientos/{package}")
    START_YEAR: int = Field(default=2020)


settings = Settings()
