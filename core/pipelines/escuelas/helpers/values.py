from typing import Any

import pandas as pd

from core.utils.normalize import strip_accents


def clean_catalog_value(value: Any) -> str | None:
    if pd.isna(value):
        return None

    text = " ".join(str(value).strip().split())
    if not text:
        return None

    return strip_accents(text).upper()


def clean_optional_text(value: Any) -> str | None:
    if pd.isna(value):
        return None

    text = " ".join(str(value).strip().split())
    if text in {"", "0", "0.0"}:
        return None

    return text


def nullable_int(value: Any) -> int | None:
    if pd.isna(value):
        return None
    return int(value)
