# core/config.py
from abc import ABC
from pathlib import Path
from dotenv import load_dotenv
import os


class BaseConfig(ABC):
  
    _env_loaded = False
    
    def __init__(self, pipeline_name: str):
        self.pipeline_name = pipeline_name
        
        if not self.__class__._env_loaded:
            self._load_env()
            self.__class__._env_loaded = True
    
    def _load_env(self) -> None:
        env_file = Path(__file__).parent / 'pipelines' / self.pipeline_name / '.env'
        
        if not env_file.exists():
            raise FileNotFoundError(f"Environment file not found: {env_file}")
        
        load_dotenv(env_file, override=True)
    
    @staticmethod
    def get(key: str, default=None, required: bool = False):
        value = os.getenv(key, default)
        
        if required and value is None:
            raise ValueError(f"Required environment variable '{key}' not found")
        
        return value
    
    @staticmethod
    def get_int(key: str, default: int = None, required: bool = False):
        value = BaseConfig.get(key, default, required)
        return int(value) if value is not None else None
    
    @staticmethod
    def get_bool(key: str, default: bool = False, required: bool = False):
        value = BaseConfig.get(key, str(default) if default is not None else None, required)
        if value is None:
            return default
        return value.lower() in ('true', '1', 'yes')