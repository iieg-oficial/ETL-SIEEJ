"""What is ENEC-specific about locating its members: two datasets, one ZIP.

The resolution behaviour itself belongs to core/utils/zip_members.py and is
covered in tests/utils.
"""

import pytest

from core.pipelines.enec.config import settings
from core.pipelines.enec.constants import (
    ENTIDAD_DESCRIPTION,
    ENTIDAD_MEMBER_PATTERN,
    NACIONAL_DESCRIPTION,
    NACIONAL_MEMBER_PATTERN,
)
from core.utils.zip_members import resolve_year_member

NACIONAL = "conjunto_de_datos/enec_absoluto_nacional_2018_{}.csv"
ENTIDAD = "conjunto_de_datos/enec_absoluto_entidad_2018_{}.csv"
OBRA = "conjunto_de_datos/enec_absoluto_obra_especifico_2018_{}.csv"


def _nacional(names, year=None):
    return resolve_year_member(
        names,
        template=settings.ENEC_NACIONAL_CSV,
        pattern=NACIONAL_MEMBER_PATTERN,
        year=year,
        description=NACIONAL_DESCRIPTION,
    )


def _entidad(names, year=None):
    return resolve_year_member(
        names,
        template=settings.ENEC_ENTIDAD_CSV,
        pattern=ENTIDAD_MEMBER_PATTERN,
        year=year,
        description=ENTIDAD_DESCRIPTION,
    )


def test_the_configured_templates_match_the_real_member_names():
    names = [NACIONAL.format(2026), ENTIDAD.format(2026), OBRA.format(2026)]

    assert _nacional(names, year=2026) == NACIONAL.format(2026)
    assert _entidad(names, year=2026) == ENTIDAD.format(2026)


def test_the_two_patterns_do_not_pick_each_others_member():
    """Both live in the same folder and share the enec_absoluto_ prefix."""
    assert _nacional([NACIONAL.format(2026), ENTIDAD.format(2026)]) == NACIONAL.format(2026)
    assert _entidad([NACIONAL.format(2026), ENTIDAD.format(2026)]) == ENTIDAD.format(2026)


def test_neither_pattern_picks_up_the_obra_especifico_member():
    """obra_especifico is out of scope; matching it would load the wrong shape."""
    with pytest.raises(FileNotFoundError, match="enec_absoluto_nacional"):
        _nacional([OBRA.format(2026)])
    with pytest.raises(FileNotFoundError, match="enec_absoluto_entidad"):
        _entidad([OBRA.format(2026)])


def test_year_rollover_is_resolved_without_touching_the_env():
    """January 2027: INEGI renames both CSVs and the pipeline must keep running."""
    names = [NACIONAL.format(2027), ENTIDAD.format(2027)]

    assert _nacional(names, year=2026) == NACIONAL.format(2027)
    assert _entidad(names, year=2026) == ENTIDAD.format(2027)


def test_the_2018_series_prefix_is_not_taken_for_the_edition_year():
    names = [NACIONAL.format(2025), NACIONAL.format(2026)]

    assert _nacional(names, year=2099) == NACIONAL.format(2026)
