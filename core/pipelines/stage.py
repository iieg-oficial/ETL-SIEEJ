# core/pipelines/stage.py
from abc import ABC, abstractmethod
from typing import Any, Optional
from pathlib import Path
from core.utils.logger import get_logger

class Stage(ABC):

    def __init__(self, pipeline_name: str, stage_name: str):
        """
        Args:
            pipeline_name: Nombre del pipeline (ej: 'etef', 'repd')
            stage_name: Nombre del stage (ej: 'extract', 'transform', 'load')
        """
        self.pipeline_name = pipeline_name
        self.stage_name = stage_name

        # Logger específico del stage
        self.logger = get_logger(f"{pipeline_name}.{stage_name}")

        # Directorio de trabajo
        self.work_dir = Path(f"data/{stage_name}/{pipeline_name}")
        self.work_dir.mkdir(parents=True, exist_ok=True)

    def execute(self, input_data: Optional[Any] = None) -> Any:
        try:
            self.logger.info(f"✨ Starting stage: {self.stage_name}")

            # Step 1: Source - Define y valida la fuente de datos
            self.logger.debug("Step 1: Extracting data")
            source_out = self.source(input_data)

            # Step 2: Action - Ejecuta la lógica principal
            self.logger.debug("⚙️ Step 2: Processing action")
            action_out = self.action(source_out)

            # Step 3: Finalization - Limpieza y persistencia
            self.logger.debug("📤 Step 3: Finishing")
            final_out = self.finalization(action_out)

            self.logger.info(f"🟢 Stage '{self.stage_name}' successfully completed")
            return final_out

        except Exception as e:
            self.logger.error(f"🔴 Stage '{self.stage_name}' failed: {str(e)}")
            raise

    @abstractmethod
    def source(self, input_data: Optional[Any] = None) -> Any | None:
        pass

    @abstractmethod
    def action(self, input_data: Optional[Any] = None) -> Any | None:
        pass

    @abstractmethod
    def finalization(self, input_data: Optional[Any] = None) -> Any | None:
        pass
