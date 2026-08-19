from pydantic import Field
from pydantic_settings import SettingsConfigDict

from core.config import BaseConfig, env_path

PIPELINE_NAME = "indice_shf_vivienda"


class Settings(BaseConfig):
    model_config = SettingsConfigDict(env_file=env_path(PIPELINE_NAME))

    PIPELINE_NAME: str = Field(default=PIPELINE_NAME)
    # La URL carga el id de archivo y la temporalidad, y SHF cambia ambos en cada
    # publicación trimestral. No hay plantilla que sirva: se actualiza a mano.
    SHF_URL: str = Field(
        default="https://www.gob.mx/cms/uploads/attachment/file/1097035/Indice_SHF_datos_abiertos_2_trim_2026.xlsx"
    )
    DOWNLOAD_TIMEOUT: int = Field(default=300)
    CHUNK_SIZE: int = Field(default=10_000)


settings = Settings()
