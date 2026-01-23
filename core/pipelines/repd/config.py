# core/pipelines/repd/config.py
from core.config import BaseConfig

class REPDConfig(BaseConfig):
    """Configuración del pipeline REPD"""
    
    def __init__(self):
        super().__init__('repd')
    
    # ========== API Configuration ==========
    @property
    def REPD_DATA_URL(self) -> str:
        return self.get('REPD_DATA_URL', required=True)
    
    # ========== Database Configuration ==========
    @property
    def DB_HOST(self) -> str:
        return self.get('REPD_DB_HOST', required=True)
    
    @property
    def DB_PORT(self) -> int:
        return self.get_int('REPD_DB_PORT', default=5432)
    
    @property
    def DB_NAME(self) -> str:
        return self.get('REPD_DB_NAME', required=True)
    
    @property
    def DB_USER(self) -> str:
        return self.get('REPD_DB_USER', required=True)
    
    @property
    def DB_PASSWORD(self) -> str:
        return self.get('REPD_DB_PASSWORD', required=True)
    
    @property
    def DB_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"