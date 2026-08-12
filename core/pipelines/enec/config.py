from pydantic import Field
from pydantic_settings import SettingsConfigDict

from core.config import BaseConfig, env_path

PIPELINE_NAME = "enec"


class Settings(BaseConfig):
    model_config = SettingsConfigDict(env_file=env_path(PIPELINE_NAME))

    PIPELINE_NAME: str = Field(default=PIPELINE_NAME)
    ENEC_URL: str = Field(
        default="https://www.inegi.org.mx/contenidos/programas/enec/2018/datosabiertos/conjunto_de_datos_enec_mensual_csv.zip"
    )
    # The published year is part of the member name, not of the URL. Both are
    # format templates so a new edition needs no code change, only the year.
    ENEC_NACIONAL_CSV: str = Field(default="conjunto_de_datos/enec_absoluto_nacional_2018_{}.csv")
    ENEC_ENTIDAD_CSV: str = Field(default="conjunto_de_datos/enec_absoluto_entidad_2018_{}.csv")
    DOWNLOAD_TIMEOUT: int = Field(default=300)
    CHUNK_SIZE: int = Field(default=10_000)


settings = Settings()
