"""Forma de un slot del calendario y las reglas que el calendario debe cumplir."""

from dataclasses import dataclass
from typing import Final

from core.constants.concurrency import (
    HEAVY_PIPELINES,
    POOL_HEAVY,
    PRIORITY_HEAVY,
    PRIORITY_LIGHT_DEFAULT,
)

MIN_SEPARATION_MINUTES: Final[int] = 60
SIMULATED_YEARS: Final[int] = 5
DEFAULT_POOL: Final[str] = "default_pool"


@dataclass(frozen=True)
class Schedule:
    pipeline: str
    cron: str
    frequency: str

    # Derivados de HEAVY_PIPELINES: la clasificación vive solo en concurrency.py.
    @property
    def pool(self) -> str:
        return POOL_HEAVY if self.pipeline in HEAVY_PIPELINES else DEFAULT_POOL

    @property
    def priority(self) -> int:
        return PRIORITY_HEAVY if self.pipeline in HEAVY_PIPELINES else PRIORITY_LIGHT_DEFAULT
