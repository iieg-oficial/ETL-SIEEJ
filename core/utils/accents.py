import re

from core.constants.accent_mappings import ACCENT_MAP


def apply_accents(value: str, accent_map: dict | None = None) -> str:
    if not isinstance(value, str):
        return value
    upper_val = value.upper()
    for pattern, replacement in (accent_map or ACCENT_MAP).items():
        upper_val = re.sub(pattern, replacement, upper_val)
    if value.istitle():
        return upper_val.title()
    return upper_val.capitalize()
