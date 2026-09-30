"""Text casing for a source that arrives in all caps and without accents.

`str.title()` alone capitalizes prepositions ("Centro De Desarrollo"), so these
helpers lower them back. Order matters: `apply_accents` returns `.capitalize()`
when the input is not `istitle()`, so accents go in while the text is still fully
title cased, and prepositions come down afterwards.
"""

from typing import Any

import pandas as pd

from core.constants.accent_mappings import ACCENT_MAP
from core.pipelines.secretaria_educacion.constants import (
    CANONICAL_TOKENS,
    LOWERCASE_WORDS,
    SEJ_ACCENT_MAP,
)
from core.utils.accents import apply_accents

ACCENTS = {**ACCENT_MAP, **SEJ_ACCENT_MAP}


def _clean(value: Any) -> str | None:
    if pd.isna(value):
        return None

    text = " ".join(str(value).split())
    return text or None


def _restore_tokens(text: str) -> str:
    """Put acronyms and proper nouns back in their canonical spelling."""
    words = text.split(" ")
    canonical = {token.lower(): token for token in CANONICAL_TOKENS}
    return " ".join(canonical.get(word.lower(), word) for word in words)


def _lower_particles(text: str) -> str:
    """Lowercase prepositions and articles, never the first word."""
    words = text.split(" ")
    kept = [words[0]]
    kept += [word.lower() if word.lower() in LOWERCASE_WORDS else word for word in words[1:]]
    return " ".join(kept)


def title_es(value: Any) -> str | None:
    """Title case following Spanish rules, with accents restored."""
    text = _clean(value)
    if text is None:
        return None

    text = apply_accents(text.title(), ACCENTS)
    return _restore_tokens(_lower_particles(text))


def capitalize_es(value: Any) -> str | None:
    """Capitalize the first letter only, with accents restored."""
    text = _clean(value)
    if text is None:
        return None

    text = apply_accents(text.capitalize(), ACCENTS)
    return _restore_tokens(text)


def plain_title(value: Any) -> str | None:
    """Title case for person names, without guessing accents.

    Particles go lowercase per the RAE: a surname's preposition is written in
    lowercase when it follows the given name ("Luis de Torres", "Juana de la
    Rosa"), which is always the case here since the column holds full names.

    Accents are left alone on purpose: the source strips them and these are
    thousands of distinct surnames, so guessing would misspell real people.
    """
    text = _clean(value)
    if text is None:
        return None

    return _restore_tokens(_lower_particles(text.title()))
