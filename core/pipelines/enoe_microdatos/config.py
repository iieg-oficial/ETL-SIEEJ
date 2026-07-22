from pydantic import Field
from pydantic_settings import SettingsConfigDict

from core.config import BaseConfig, env_path


class Settings(BaseConfig):
    model_config = SettingsConfigDict(env_file=env_path("enoe_microdatos"))

    PIPELINE_NAME: str = Field(default="enoe_microdatos")
    # 2023+: patrón actual
    MICRODATOS_URL: str = Field(
        default="https://www.inegi.org.mx/contenidos/programas/enoe/15ymas/microdatos/enoe_{anio}_trim{trimestre}_csv.zip"
    )
    # 2021–2022: prefijo enoe_n_
    MICRODATOS_URL_ENOE_N: str = Field(
        default="https://www.inegi.org.mx/contenidos/programas/enoe/15ymas/microdatos/enoe_n_{anio}_trim{trimestre}_csv.zip"
    )
    # 2005–2020: sin prefijo
    MICRODATOS_URL_LEGACY: str = Field(
        default="https://www.inegi.org.mx/contenidos/programas/enoe/15ymas/microdatos/{anio}trim{trimestre}_csv.zip"
    )
    BOOTSTRAP_START_YEAR: int = Field(default=2005)
    BOOTSTRAP_START_TRIMESTRE: int = Field(default=1)

    def build_urls(self, anio: int, trimestre: int) -> list[str]:
        return [
            self.MICRODATOS_URL.format(anio=anio, trimestre=trimestre),
            self.MICRODATOS_URL_ENOE_N.format(anio=anio, trimestre=trimestre),
            self.MICRODATOS_URL_LEGACY.format(anio=anio, trimestre=trimestre),
        ]


settings = Settings()
