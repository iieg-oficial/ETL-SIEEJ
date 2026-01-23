
from core.pipelines.stage import Stage
from typing import Any, Optional
from core.utils.logger import get_logger


class REPDExtractor(Stage):
    def __init__(self, pipeline_name: str = 'repd', mode: str = 'bootstrap'):
        super().__init__(pipeline_name, 'extract')
        self.mode = mode
        self.logger = get_logger(f"{pipeline_name}.extract")
    
    def source(self, input_data: Optional[Any]) -> Any:
        self.logger.info(f"📥 [source] Datos recibidos: {input_data}")
        return input_data

    def action(self, input_data: Optional[Any]) -> Any:
        self.logger.info(f"⚙️ [action] Extrayendo datos: {input_data}")
        return input_data

    def finalization(self, input_data: Optional[Any]) -> Any:
        self.logger.info(f"📤 [finalization] Finalizando extracción: {input_data}")
        return input_data