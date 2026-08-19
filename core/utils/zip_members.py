"""Locate a member inside a ZIP whose path the publisher renames between editions.

INEGI stamps the edition year on the file name instead of the URL, so the same
stable download serves `..._indice_2008_2026.csv` this year and
`..._indice_2008_2027.csv` the next. A configured path is the documented
contract; a pattern is the safety net that keeps a pipeline alive the day the
edition rolls over without anyone editing the .env.
"""

from __future__ import annotations

import re
from datetime import date

from core.utils.logger import get_console_logger

logger = get_console_logger(__name__)


def resolve_year_member(
    names: list[str],
    template: str,
    pattern: re.Pattern[str],
    year: int | None = None,
    description: str | None = None,
) -> str:
    """Locate the member for a given year, falling back to the newest one published.

    Args:
        names: members contained in the ZIP.
        template: configured path with a single `{}` placeholder for the year.
        pattern: regex whose first group captures the year, used for the fallback.
        year: edition to look for; defaults to the current year.
        description: what is being looked for, used in the error message.

    Raises:
        FileNotFoundError: if no member matches the pattern at all.
    """
    expected = template.format(year or date.today().year)
    if expected in names:
        return expected

    published = {int(match.group(1)): name for name in names if (match := pattern.search(name))}
    if not published:
        raise FileNotFoundError(f"The ZIP has no {description or pattern.pattern} member. Contents: {sorted(names)}")

    latest = max(published)
    logger.warning(f"'{expected}' is not in the ZIP; falling back to the {latest} edition ('{published[latest]}')")
    return published[latest]


def resolve_member(
    names: list[str],
    expected: str,
    pattern: re.Pattern[str],
    description: str | None = None,
) -> str:
    """Locate a member whose path does not carry the edition year.

    Raises:
        FileNotFoundError: if no member matches the pattern.
    """
    if expected in names:
        return expected

    matches = [name for name in names if pattern.search(name)]
    if not matches:
        raise FileNotFoundError(f"The ZIP has no {description or pattern.pattern} member. Contents: {sorted(names)}")

    return matches[0]
