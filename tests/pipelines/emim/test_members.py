"""What is EMIM-specific about locating its member: the pattern and the template.

The resolution behaviour itself (fallback, newest edition wins, error shape)
belongs to core/utils/zip_members.py and is covered in tests/utils.
"""

import pytest

from core.pipelines.emim.config import settings
from core.pipelines.emim.constants import (
    CATALOG_DESCRIPTION,
    CATALOG_MEMBER_PATTERN,
    DATASET_DESCRIPTION,
    DATASET_MEMBER_PATTERN,
)
from core.utils.zip_members import resolve_member, resolve_year_member

DATASET = "conjunto_de_datos/tr_variable_total_entidad_mensual_2018_{}.csv"


def _dataset(names: list[str], year: int | None = None) -> str:
    return resolve_year_member(
        names,
        template=settings.EMIM_CSV,
        pattern=DATASET_MEMBER_PATTERN,
        year=year,
        description=DATASET_DESCRIPTION,
    )


def _catalog(names: list[str]) -> str:
    return resolve_member(
        names,
        expected=settings.EMIM_CATALOG_CSV,
        pattern=CATALOG_MEMBER_PATTERN,
        description=CATALOG_DESCRIPTION,
    )


def test_the_configured_template_matches_the_real_member_name():
    """The member is NOT named after the program: no "emim" appears in it.

    EMIM_CSV has to line up with what INEGI actually ships, or every run falls
    back to the pattern and logs a warning nobody asked for.
    """
    names = [DATASET.format(2026)]

    assert _dataset(names, year=2026) == DATASET.format(2026)


def test_year_rollover_is_resolved_without_touching_the_env():
    """January 2027: INEGI renames the CSV and the pipeline must keep running."""
    names = [DATASET.format(2027)]

    assert _dataset(names, year=2026) == DATASET.format(2027)


def test_the_2018_series_prefix_is_not_taken_for_the_edition_year():
    """The name carries two years: 2018 is the series, the second one is the edition."""
    names = [DATASET.format(2025), DATASET.format(2026)]

    assert _dataset(names, year=2099) == DATASET.format(2026)


def test_sibling_programs_are_not_accepted_by_the_emim_pattern():
    """EMEC, EMS and EMIM ship the same folder layout; patterns must not cross over."""
    names = [
        "conjunto_de_datos/tr_ems_entidad_federativa_indice_2013_2026.csv",
        "conjunto_de_datos/tr_emec_entidad_federativa_indice_2008_2026.csv",
    ]

    with pytest.raises(FileNotFoundError, match="tr_variable_total_entidad_mensual"):
        _dataset(names)


def test_zip_without_dataset_csv_raises():
    with pytest.raises(FileNotFoundError, match="tr_variable_total_entidad_mensual"):
        _dataset(["metadatos/metadatos.txt"])


def test_the_configured_catalog_path_matches_the_real_one():
    assert _catalog([settings.EMIM_CATALOG_CSV]) == settings.EMIM_CATALOG_CSV


def test_catalog_is_found_by_pattern_when_the_path_changes():
    assert _catalog(["catalogos/2018/tc_actividad.csv"]) == "catalogos/2018/tc_actividad.csv"
