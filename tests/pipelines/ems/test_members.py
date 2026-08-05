import pytest

from core.pipelines.ems.helpers.members import resolve_catalog_member, resolve_dataset_member

DATASET = "conjunto_de_datos/tr_ems_entidad_federativa_indice_2013_{}.csv"


def test_uses_the_member_named_after_the_requested_year():
    names = [DATASET.format(2026), "catalogos/tc_actividad.csv"]

    assert resolve_dataset_member(names, year=2026) == DATASET.format(2026)


def test_year_rollover_is_resolved_without_touching_the_env():
    """January 2027: INEGI renames the CSV and the pipeline must keep running."""
    names = [DATASET.format(2027), "catalogos/tc_actividad.csv"]

    assert resolve_dataset_member(names, year=2026) == DATASET.format(2027)


def test_the_2013_series_prefix_is_not_confused_with_the_edition_year():
    """The name carries two years: 2013 is the series, the second one is the edition.

    A pattern anchored on the wrong one would pick 2013 as the newest edition.
    """
    names = [DATASET.format(2025), DATASET.format(2026)]

    assert resolve_dataset_member(names, year=2099) == DATASET.format(2026)


def test_emec_members_are_not_accepted_by_the_ems_pattern():
    """Both programs ship the same folder layout; the pattern must not cross over."""
    names = ["conjunto_de_datos/tr_emec_entidad_federativa_indice_2008_2026.csv"]

    with pytest.raises(FileNotFoundError, match="tr_ems_entidad_federativa_indice"):
        resolve_dataset_member(names)


def test_zip_without_dataset_csv_raises():
    with pytest.raises(FileNotFoundError, match="tr_ems_entidad_federativa_indice"):
        resolve_dataset_member(["metadatos/metadatos.txt"])


def test_catalog_is_found_by_pattern_when_the_path_changes():
    assert resolve_catalog_member(["catalogos/2018/tc_actividad.csv"]) == "catalogos/2018/tc_actividad.csv"


def test_zip_without_catalog_raises():
    with pytest.raises(FileNotFoundError, match="tc_actividad"):
        resolve_catalog_member([DATASET.format(2026)])
