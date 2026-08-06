import re

import pytest

from core.utils.zip_members import resolve_member, resolve_year_member

TEMPLATE = "conjunto_de_datos/dataset_{}.csv"
PATTERN = re.compile(r"dataset_(\d{4})\.csv$")
CATALOG_PATTERN = re.compile(r"catalog\.csv$")


class TestResolveYearMember:
    def test_the_configured_path_wins_when_it_is_present(self):
        names = [TEMPLATE.format(2026), TEMPLATE.format(2027)]

        assert resolve_year_member(names, TEMPLATE, PATTERN, year=2026) == TEMPLATE.format(2026)

    def test_falls_back_to_the_newest_edition_when_the_configured_one_is_gone(self):
        """This is the whole point: the edition rolls over and nobody edits the .env."""
        names = [TEMPLATE.format(2027)]

        assert resolve_year_member(names, TEMPLATE, PATTERN, year=2026) == TEMPLATE.format(2027)

    def test_newest_wins_among_several_editions(self):
        names = [TEMPLATE.format(2024), TEMPLATE.format(2027), TEMPLATE.format(2025)]

        assert resolve_year_member(names, TEMPLATE, PATTERN, year=2020) == TEMPLATE.format(2027)

    def test_years_are_compared_as_numbers_not_as_strings(self):
        names = [TEMPLATE.format(9999), TEMPLATE.format(2027)]

        assert resolve_year_member(names, TEMPLATE, PATTERN, year=2020) == TEMPLATE.format(9999)

    def test_defaults_to_the_current_year(self):
        from datetime import date

        names = [TEMPLATE.format(date.today().year)]

        assert resolve_year_member(names, TEMPLATE, PATTERN) == names[0]

    def test_no_match_raises_with_the_zip_contents(self):
        with pytest.raises(FileNotFoundError, match="otra_cosa.txt"):
            resolve_year_member(["otra_cosa.txt"], TEMPLATE, PATTERN)

    def test_error_names_what_was_being_looked_for(self):
        with pytest.raises(FileNotFoundError, match="the yearly dataset"):
            resolve_year_member([], TEMPLATE, PATTERN, description="the yearly dataset")


class TestResolveMember:
    def test_the_configured_path_wins_when_it_is_present(self):
        names = ["catalogos/catalog.csv", "otro/catalog.csv"]

        assert resolve_member(names, "catalogos/catalog.csv", CATALOG_PATTERN) == "catalogos/catalog.csv"

    def test_falls_back_to_the_pattern_when_the_path_moved(self):
        names = ["catalogos/2018/catalog.csv"]

        assert resolve_member(names, "catalogos/catalog.csv", CATALOG_PATTERN) == "catalogos/2018/catalog.csv"

    def test_no_match_raises(self):
        with pytest.raises(FileNotFoundError):
            resolve_member(["datos.csv"], "catalogos/catalog.csv", CATALOG_PATTERN)
