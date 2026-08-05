from __future__ import annotations

from datetime import date

from core.pipelines.emec.config import settings
from core.pipelines.emec.constants import CATALOG_MEMBER_PATTERN, DATASET_MEMBER_PATTERN
from core.utils.logger import get_console_logger

logger = get_console_logger(__name__)


def resolve_dataset_member(names: list[str], year: int | None = None) -> str:
    """Locate the dataset CSV inside the ZIP, whatever year INEGI stamped on it.

    The member is named after the edition (..._indice_2008_2026.csv), so it is
    renamed every January. EMEC_CSV is tried first because it is the documented
    contract; when it misses, the newest year actually present in the ZIP wins.
    Falling back is what keeps the pipeline alive on the day the edition rolls
    over without anyone touching the .env.

    Raises:
        FileNotFoundError: if the ZIP has no dataset CSV at all.
    """
    expected = settings.EMEC_CSV.format(year or date.today().year)
    if expected in names:
        return expected

    published = {int(match.group(1)): name for name in names if (match := DATASET_MEMBER_PATTERN.search(name))}
    if not published:
        raise FileNotFoundError(f"The ZIP has no tr_emec_entidad_federativa_indice CSV. Contents: {sorted(names)}")

    latest = max(published)
    logger.warning(f"'{expected}' is not in the ZIP; falling back to the {latest} edition ('{published[latest]}')")
    return published[latest]


def resolve_catalog_member(names: list[str]) -> str:
    """Locate the activity catalog CSV inside the ZIP.

    Raises:
        FileNotFoundError: if the ZIP has no activity catalog.
    """
    if settings.EMEC_CATALOG_CSV in names:
        return settings.EMEC_CATALOG_CSV

    matches = [name for name in names if CATALOG_MEMBER_PATTERN.search(name)]
    if not matches:
        raise FileNotFoundError(f"The ZIP has no tc_actividad catalog. Contents: {sorted(names)}")

    return matches[0]
