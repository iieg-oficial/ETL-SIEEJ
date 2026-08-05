import pytest

from core.pipelines.emec.helpers.members import resolve_catalog_member, resolve_dataset_member

DATASET = "conjunto_de_datos/tr_emec_entidad_federativa_indice_2008_{}.csv"


def test_uses_the_member_named_after_the_requested_year():
    names = [DATASET.format(2026), "catalogos/tc_actividad.csv"]

    assert resolve_dataset_member(names, year=2026) == DATASET.format(2026)


def test_year_rollover_is_resolved_without_touching_the_env():
    """January 2027: INEGI renames the CSV and the pipeline must keep running.

    EMEC_CSV still asks for the 2026 edition until someone edits it, so the
    fallback to the newest year present in the ZIP is what avoids an outage.
    """
    names = [DATASET.format(2027), "catalogos/tc_actividad.csv"]

    assert resolve_dataset_member(names, year=2026) == DATASET.format(2027)


def test_newest_edition_wins_when_several_years_ship_together():
    names = [DATASET.format(2026), DATASET.format(2027), DATASET.format(2025)]

    assert resolve_dataset_member(names, year=2024) == DATASET.format(2027)


def test_defaults_to_the_current_year_when_none_is_given():
    names = [DATASET.format(2026)]

    assert resolve_dataset_member(names) == DATASET.format(2026)


def test_zip_without_dataset_csv_raises():
    with pytest.raises(FileNotFoundError, match="tr_emec_entidad_federativa_indice"):
        resolve_dataset_member(["metadatos/metadatos.txt"])


def test_catalog_is_found_by_pattern_when_the_path_changes():
    """The configured path is the contract; the pattern is the safety net."""
    assert resolve_catalog_member(["catalogos/2018/tc_actividad.csv"]) == "catalogos/2018/tc_actividad.csv"


def test_zip_without_catalog_raises():
    with pytest.raises(FileNotFoundError, match="tc_actividad"):
        resolve_catalog_member([DATASET.format(2026)])
