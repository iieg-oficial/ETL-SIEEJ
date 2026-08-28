from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np

Conditioner = Callable[[np.ndarray, float | None], np.ndarray]


def raw_conditioner(elevation: np.ndarray, nodata: float | None = None) -> np.ndarray:
    """Unmodified baseline for later experiments."""
    return elevation.copy()


@dataclass(frozen=True)
class ConditioningCandidate:
    name: str
    callable: Conditioner
    description: str


class ConditioningExperiment:
    """Registry for explicit future candidates; this phase only defines RAW."""

    def __init__(self) -> None:
        self._candidates: dict[str, ConditioningCandidate] = {
            "raw": ConditioningCandidate("raw", raw_conditioner, "DEM reproyectado sin acondicionamiento")
        }

    def register(self, candidate: ConditioningCandidate) -> None:
        if candidate.name in self._candidates:
            raise ValueError(f"Conditioning candidate already registered: {candidate.name}")
        self._candidates[candidate.name] = candidate

    def names(self) -> tuple[str, ...]:
        return tuple(self._candidates)

    def comparison_design(self) -> dict[str, object]:
        return {
            "common_input_contract": {
                "crs": "EPSG:6368",
                "resolution_m": 15,
                "dtype": "Float32",
            },
            "registered_candidates": list(self.names()),
            "required_future_slots": ["candidate_a", "candidate_b", "candidate_c"],
            "winner_selected": False,
        }

    def run(self, name: str, elevation: np.ndarray, nodata: float | None = None) -> np.ndarray:
        try:
            candidate = self._candidates[name]
        except KeyError:
            raise ValueError(f"Unknown conditioning candidate: {name}") from None
        return candidate.callable(elevation, nodata)
