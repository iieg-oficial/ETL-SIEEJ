from enum import unique

from core.pipelines.{{cookiecutter.pipeline}}.attributes.base import BaseClass


@unique
class {{cookiecutter.__class_prefix}}Tables(BaseClass):
    pass
