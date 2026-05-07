from pydantic import Field
from pydantic_settings import SettingsConfigDict

from core.config import BaseConfig, env_path


class Settings(BaseConfig):
    model_config = SettingsConfigDict(env_file=env_path("pobreza_multidimensional"))

    # Fuente de datos (ZIP con XLSX adentro)
    POBREZA_MULTIDIMENSIONAL_SOURCE_URL: str = Field(
        default="https://www.coneval.org.mx/Medicion/Documents/Pobreza_municipal/2020/Concentrado_indicadores_de_pobreza_2020.zip"
    )

    # Nombre del XLSX dentro del ZIP
    XLSX_FILENAME: str = Field(default="Concentrado_indicadores_de_pobreza_2020.xlsx")

    # Carga
    POBREZA_MULTIDIMENSIONAL_LOAD_BATCH_SIZE: int = Field(default=2000)


settings = Settings()
