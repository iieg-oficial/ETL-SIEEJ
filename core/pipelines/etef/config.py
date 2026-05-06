from pydantic import Field
from pydantic_settings import SettingsConfigDict

from core.config import BaseConfig, env_path


class Settings(BaseConfig):
    model_config = SettingsConfigDict(env_file=env_path("etef"))

    # Fuente de datos (ZIP URL desde INEGI)
    ETEF_SOURCE_URL: str = Field(
        default="https://www.inegi.org.mx/contenidos/programas/exporta_ef/datosabiertos/conjunto_de_datos_eef_trimestral_csv.zip"
    )

    # Carga
    ETEF_LOAD_BATCH_SIZE: int = Field(default=5000)


settings = Settings()
