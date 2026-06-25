from pydantic import Field
from pydantic_settings import SettingsConfigDict

from core.config import BaseConfig, env_path


class Settings(BaseConfig):
    model_config = SettingsConfigDict(env_file=env_path("enoe"))

    PIPELINE_NAME: str = Field(default="enoe")
    ENOE_URL: str = Field(
        default="https://www.inegi.org.mx/contenidos/programas/enoe/15ymas/datosabiertos/{anio}/conjunto_de_datos_enoe_{anio}_{trimestre}t_csv.zip"
    )
    ENOE_URL_ALT: str = Field(
        default="https://www.inegi.org.mx/contenidos/programas/enoe/15ymas/datosabiertos/{anio}/{anio}_trim{trimestre}_enoe_csv.zip"
    )
    BOOTSTRAP_START_YEAR: int = Field(default=2005)
    BOOTSTRAP_START_TRIMESTRE: int = Field(default=1)

    def build_url(self, anio: int, trimestre: int) -> str:
        return self.ENOE_URL.format(anio=anio, trimestre=trimestre)

    def build_url_alt(self, anio: int, trimestre: int) -> str:
        return self.ENOE_URL_ALT.format(anio=anio, trimestre=trimestre)


settings = Settings()
