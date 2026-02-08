from pydantic_settings import SettingsConfigDict
from core.config import BaseConfig, env_path

class Settings(BaseConfig):
    model_config = SettingsConfigDict(env_file=env_path("fiscalia"))

    BOOTSTRAP_CSV_FOLDER: str
    UPDATE_EXCEL_FOLDER: str

settings = Settings()
