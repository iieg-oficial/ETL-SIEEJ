from pydantic import Field
from pydantic_settings import SettingsConfigDict

from core.config import BaseConfig, env_path

PIPELINE_NAME = "emim"


class Settings(BaseConfig):
    model_config = SettingsConfigDict(env_file=env_path(PIPELINE_NAME))

    PIPELINE_NAME: str = Field(default=PIPELINE_NAME)
    EMIM_URL: str = Field(
        default="https://www.inegi.org.mx/contenidos/programas/emim/2018/datosabiertos/conjunto_de_datos_emim_variables_entidad_csv.zip"
    )
    EMIM_CSV: str = Field(default="conjunto_de_datos/tr_variable_total_entidad_mensual_2018_{}.csv")
    EMIM_CATALOG_CSV: str = Field(default="catalogos/tc_actividad.csv")
    DOWNLOAD_TIMEOUT: int = Field(default=300)
    CHUNK_SIZE: int = Field(default=10_000)


settings = Settings()
