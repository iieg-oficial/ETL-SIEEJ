from typing import Any, List
from core.utils.logger import get_logger


class Pipeline:

    def __init__(self, name: str, stages: List[Any]):
        self.name = name
        self.stages = stages
        self.logger = get_logger(name)

    def run(self, mode: str = 'bootstrap') -> None:
        try:
            self.logger.info(f"🚀 Starting pipeline {mode.upper()}: {self.name}")

            data = None

            for stage in self.stages:
                stage_name = stage.__class__.__name__
                self.logger.info(f"⚙️ Running stage: {stage_name}")

                data = stage.execute(input_data=data)

            self.logger.info(f"✅ Pipeline {mode.upper()} '{self.name}' completed succesfully!")

        except Exception as e:
            self.logger.error(f"❌ Pipeline {mode.upper()} '{self.name}' failed: {str(e)}")
            raise
