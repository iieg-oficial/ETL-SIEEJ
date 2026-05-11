from pydantic import Field
from pydantic_settings import SettingsConfigDict

from core.config import BaseConfig, env_path


class Settings(BaseConfig):
    model_config = SettingsConfigDict(env_file=env_path("agropecuario_siap"))

    PIPELINE_NAME: str = Field(default="agropecuario_siap")
    SIAP_URL: str = Field(
        default="https://nube.agricultura.gob.mx/index.php?view=10AE434F-A2158368-A120BC5A-EDF4AFAA&ANIO={anio}"
    )
    START_DATE: int = Field(default=2003)
    END_DATE: int = Field(default=2024)
    CHUNK_SIZE: int = Field(default=10_000)


settings = Settings()
