"""Configuración del pipeline asg_imss (carga desde core/pipelines/asg_imss/.env)."""

from pydantic import Field
from pydantic_settings import SettingsConfigDict

from core.config import BaseConfig, env_path

PIPELINE_NAME = "asg_imss"


class Settings(BaseConfig):
    model_config = SettingsConfigDict(env_file=env_path(PIPELINE_NAME), extra="ignore")

    ASG_IMSS_CATALOG_URL: str = Field(
        default="http://datos.imss.gob.mx/sites/default/files/diccionario_de_datos_1.xlsx"
    )
    ASG_IMSS_DATA_URL: str = Field(default="http://datos.imss.gob.mx/sites/default/files/asg-{date}.csv")
    ASG_IMSS_DATA_START_DATE: str = Field(default="2015-01-31")
    ASG_IMSS_DATA_END_DATE: str = Field(default="")
    BATCH_SIZE: int = Field(default=5000)
    MAX_RETRIES: int = Field(default=3)
    TIMEOUT: int = Field(default=300)


settings = Settings()
