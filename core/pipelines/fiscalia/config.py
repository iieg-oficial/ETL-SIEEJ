import json
from typing import Literal, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="core/pipelines/fiscalia/.env")
    LOG_LEVEL: str = "INFO"
    DB_USER: Optional[str] = Field(default="Test")
    DB_PASSWORD: Optional[str] = Field(default="Test")
    DB_HOST: Optional[str] = Field(default="Test")
    DB_PORT: Optional[str] = Field(default="Test")
    DB_NAME: Optional[str] = Field(default="Test")

    G_FOLDER_URL: str



    @property
    def get_database_url(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

settings = Settings()
