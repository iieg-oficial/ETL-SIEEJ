from __future__ import annotations

from core.pipelines.ems.config import settings
from core.pipelines.ems.constants import CATALOG_MEMBER_PATTERN, DATASET_MEMBER_PATTERN
from core.utils.zip_members import resolve_member, resolve_year_member

DATASET_DESCRIPTION = "tr_ems_entidad_federativa_indice"
CATALOG_DESCRIPTION = "tc_actividad"


def resolve_dataset_member(names: list[str], year: int | None = None) -> str:
    """Locate the EMS dataset CSV inside the ZIP, whatever year INEGI stamped on it."""
    return resolve_year_member(
        names,
        template=settings.EMS_CSV,
        pattern=DATASET_MEMBER_PATTERN,
        year=year,
        description=DATASET_DESCRIPTION,
    )


def resolve_catalog_member(names: list[str]) -> str:
    """Locate the activity catalog CSV inside the ZIP."""
    return resolve_member(
        names,
        expected=settings.EMS_CATALOG_CSV,
        pattern=CATALOG_MEMBER_PATTERN,
        description=CATALOG_DESCRIPTION,
    )
