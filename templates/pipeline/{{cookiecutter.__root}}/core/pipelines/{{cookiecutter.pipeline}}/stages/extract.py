from typing import Any, Optional

from core.pipelines.{{cookiecutter.pipeline}}.constants import PIPELINE_NAME
from core.pipelines.stage import Stage


class {{cookiecutter.__class_prefix}}Extract(Stage):
    def __init__(self) -> None:
        super().__init__(PIPELINE_NAME, "extract")

    def source(self, input_data: Optional[Any] = None) -> Any:
        raise NotImplementedError

    def action(self, input_data: Optional[Any] = None) -> Any:
        raise NotImplementedError

    def finalization(self, input_data: Optional[Any] = None) -> Any:
        raise NotImplementedError
