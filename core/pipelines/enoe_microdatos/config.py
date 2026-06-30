from pydantic import Field
from pydantic_settings import SettingsConfigDict

from core.config import BaseConfig, env_path


class Settings(BaseConfig):
    model_config = SettingsConfigDict(env_file=env_path("enoe_microdatos"))

    PIPELINE_NAME: str = Field(default="enoe_microdatos")
    MICRODATOS_URL: str = Field(
        default="https://www.inegi.org.mx/contenidos/programas/enoe/15ymas/microdatos/enoe_{anio}_trim{trimestre}_csv.zip"
    )
    BOOTSTRAP_START_YEAR: int = Field(default=2005)
    BOOTSTRAP_START_TRIMESTRE: int = Field(default=1)

    def build_url(self, anio: int, trimestre: int) -> str:
        return self.MICRODATOS_URL.format(anio=anio, trimestre=trimestre)


settings = Settings()
