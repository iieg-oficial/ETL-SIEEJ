"""Text casing for region labels that arrive with stray spaces and no accents."""

from typing import Any

import pandas as pd

from core.constants.accent_mappings import ACCENT_MAP
from core.pipelines.code.constants import LOWERCASE_WORDS
from core.utils.accents import apply_accents


def _lower_particles(text: str) -> str:
    """Lowercase prepositions and articles, never the first word."""
    first, *rest = text.split(" ")
    return " ".join([first, *(word.lower() if word.lower() in LOWERCASE_WORDS else word for word in rest)])


def title_es(value: Any) -> str | None:
    """Title case following Spanish rules, with accents restored."""
    if pd.isna(value):
        return None

    text = " ".join(str(value).split())
    if not text:
        return None

    return _lower_particles(apply_accents(text.title(), ACCENT_MAP))
