from pydantic import Field
from pydantic_settings import SettingsConfigDict

from core.config import BaseConfig, env_path


class Settings(BaseConfig):
    model_config = SettingsConfigDict(env_file=env_path("efipem"))

    EFIPEM_SOURCE_URL: str = Field(
        default="https://www.inegi.org.mx/contenidos/programas/finanzas/datosabiertos/conjunto_de_datos_efipem_trimestral_csv.zip"
    )
    EFIPEM_LOAD_BATCH_SIZE: int = Field(default=5000)


settings = Settings()
