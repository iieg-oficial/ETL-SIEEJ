from pydantic import Field
from pydantic_settings import SettingsConfigDict

from core.config import BaseConfig, env_path

PIPELINE_NAME = "rastros"


class Settings(BaseConfig):
    model_config = SettingsConfigDict(env_file=env_path(PIPELINE_NAME))

    PIPELINE_NAME: str = Field(default=PIPELINE_NAME)
    ESGRM_URL: str = Field(
        default="https://www.inegi.org.mx/contenidos/programas/sacrificioganado/datosabiertos/conjunto_de_datos_esgrm_mensual_csv.zip"
    )
    DOWNLOAD_TIMEOUT: int = Field(default=300)
    CHUNK_SIZE: int = Field(default=10_000)


settings = Settings()
