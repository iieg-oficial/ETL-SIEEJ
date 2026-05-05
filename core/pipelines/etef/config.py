from pydantic import Field
from pydantic_settings import SettingsConfigDict

from core.config import BaseConfig, env_path


class Settings(BaseConfig):
    model_config = SettingsConfigDict(env_file=env_path("etef"))

    # Base de datos del pipeline
    ETEF_DB_HOST: str = Field(default="localhost")
    ETEF_DB_PORT: int = Field(default=5432)
    ETEF_DB_USER: str = Field(default="bi_iieg")
    ETEF_DB_PASS: str = Field(default="changeme")
    ETEF_DB_NAME: str = Field(default="etef")

    # Fuente de datos (ZIP URL desde INEGI)
    ETEF_SOURCE_URL: str = Field(
        default="https://www.inegi.org.mx/contenidos/programas/exporta_ef/datosabiertos/conjunto_de_datos_eef_trimestral_csv.zip"
    )

    # Carga
    ETEF_LOAD_BATCH_SIZE: int = Field(default=5000)


settings = Settings()
