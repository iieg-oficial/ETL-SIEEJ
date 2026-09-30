from pydantic import Field
from pydantic_settings import SettingsConfigDict

from core.config import BaseConfig

ENV_FILE = "core/acervo/.env"


class Settings(BaseConfig):
    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    ACERVO_ENDPOINT: str = Field(default="")
    ACERVO_ACCESS_KEY: str = Field(default="")
    ACERVO_SECRET_KEY: str = Field(default="")
    ACERVO_BUCKET: str = Field(default="sieej")
    ACERVO_REGION: str = Field(default="us-east-1")
    ACERVO_FORM_PREFIX: str
    ACERVO_ENVIO_FILENAME: str


settings = Settings()
