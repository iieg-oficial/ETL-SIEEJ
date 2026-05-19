from pydantic import Field
from pydantic_settings import SettingsConfigDict

from core.config import BaseConfig, env_path


class Settings(BaseConfig):
    model_config = SettingsConfigDict(env_file=env_path("produccion_ganadera"))

    PIPELINE_NAME: str = Field(default="produccion_ganadera")
    SIAP_URL: str = Field(
        default="https://nube.agricultura.gob.mx/index.php?view=E370DEBE-390827E8-72838350-94616860&ANIO={anio}"
    )
    START_DATE: int = Field(default=2003)
    END_DATE: int = Field(default=2024)
    CHUNK_SIZE: int = Field(default=10_000)


settings = Settings()
