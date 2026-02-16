from pydantic_settings import SettingsConfigDict
from core.config import BaseConfig, env_path

class Settings(BaseConfig):
    model_config = SettingsConfigDict(env_file=env_path("fiscalia"))

    GDRIVE_FOLDER_ID: str
    GDRIVE_CLIENT_EMAIL: str
    GDRIVE_PRIVATE_KEY: str
    HISTORICAL_FILENAME: str

settings = Settings()
