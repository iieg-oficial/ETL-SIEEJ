from pydantic import Field
from pydantic_settings import SettingsConfigDict

from core.config import BaseConfig, env_path

PIPELINE_NAME = "ems"


class Settings(BaseConfig):
    model_config = SettingsConfigDict(env_file=env_path(PIPELINE_NAME))

    PIPELINE_NAME: str = Field(default=PIPELINE_NAME)
    EMS_URL: str = Field(
        default="https://www.inegi.org.mx/contenidos/programas/ems/2018/datosabiertos/conjunto_de_datos_ems_mensual_entidad_federativa_csv.zip"
    )
    EMS_CSV: str = Field(default="conjunto_de_datos/tr_ems_entidad_federativa_indice_2013_{}.csv")
    EMS_CATALOG_CSV: str = Field(default="catalogos/tc_actividad.csv")
    DOWNLOAD_TIMEOUT: int = Field(default=300)
    CHUNK_SIZE: int = Field(default=10_000)


settings = Settings()
