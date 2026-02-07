from pydantic import Field
from pydantic_settings import BaseSettings


def env_path(pipeline_name: str) -> str:
    return f"core/pipelines/{pipeline_name}/.env"

class BaseConfig(BaseSettings):
    # Variables comunes a todos los pipelines
    DB_USER: str = Field(default="postgres")
    DB_PASSWORD: str = Field(default="postgres")
    DB_HOST: str = Field(default="localhost")
    DB_PORT: str = Field(default="5432")
    DB_NAME: str = Field(default="sieej")
    LOG_LEVEL: str = Field(default="INFO")

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
