"""Las constantes del pipeline no deben repetir lo que ya declara el enum."""

import pytest

from core.pipelines.defunciones_inegi.attributes import DefuncionesInegiTables as T
from core.pipelines.defunciones_inegi.constants import (
    CATALOG_ALIAS_OVERRIDES,
    CODED_CATALOG_TABLES,
    LEGACY_CATALOG_ALIASES,
    STRUCTURED_CATALOG_TABLES,
    TEXT_KEY_TABLES,
    VERSIONED_TABLES,
)


def test_no_override_repeats_the_alias_the_enum_already_derives():
    redundant = [str(table) for table, alias in CATALOG_ALIAS_OVERRIDES.items() if T(table).catalog_alias == alias]
    assert not redundant, f"quitar de CATALOG_ALIAS_OVERRIDES: {redundant}"


def test_every_catalog_is_either_coded_or_structured():
    assert set(CODED_CATALOG_TABLES) | set(STRUCTURED_CATALOG_TABLES) == set(T.catalogs())
    assert not set(CODED_CATALOG_TABLES) & set(STRUCTURED_CATALOG_TABLES)


def test_cat_edicion_is_not_a_source_catalog():
    """La edición la escribe el ETL, no viene de un CSV de INEGI."""
    assert T.CAT_EDICION not in T.catalogs()


@pytest.mark.parametrize(
    "declared",
    [CATALOG_ALIAS_OVERRIDES, LEGACY_CATALOG_ALIASES],
    ids=["overrides", "legacy"],
)
def test_alias_tables_are_real_catalogs(declared):
    unknown = [str(table) for table in declared if table not in T.catalogs()]
    assert not unknown, f"tablas que no son catálogos: {unknown}"


@pytest.mark.parametrize(
    "declared",
    [VERSIONED_TABLES, TEXT_KEY_TABLES, STRUCTURED_CATALOG_TABLES],
    ids=["versioned", "text_key", "structured"],
)
def test_table_groups_reference_real_catalogs(declared):
    unknown = [str(table) for table in declared if table not in T.catalogs()]
    assert not unknown, f"tablas que no son catálogos: {unknown}"


def test_every_mapped_column_points_at_a_real_catalog():
    from core.pipelines.defunciones_inegi.constants import COLUMN_CATALOG, VERSIONED_COLUMN_CATALOG

    unknown = [t for t in {**COLUMN_CATALOG, **VERSIONED_COLUMN_CATALOG}.values() if t not in T.catalogs()]
    assert not unknown, f"columnas mapeadas a tablas que no son catálogos: {unknown}"


def test_key_type_and_versioning_are_independent_axes():
    """Un catálogo puede ser versionado con clave entera, o estable con clave de texto.

    Tratarlos como un solo eje dejó `ocupacion` y `grupo_lista_mexicana` con el
    100% de sus FK en NULL sin que la carga fallara.
    """
    from core.pipelines.defunciones_inegi.constants import TEXT_KEY_TABLES, VERSIONED_TABLES

    assert T.CAT_OCUPACION in VERSIONED_TABLES and T.CAT_OCUPACION not in TEXT_KEY_TABLES
    assert T.CAT_GRUPO_LISTA_MEXICANA in TEXT_KEY_TABLES and T.CAT_GRUPO_LISTA_MEXICANA not in VERSIONED_TABLES
    assert T.CAT_CIE10 in TEXT_KEY_TABLES and T.CAT_CIE10 in VERSIONED_TABLES


def test_editions_cover_catalog_years_not_only_fact_years():
    """Los catálogos versionados pueden traer más ediciones que los hechos cargados.

    Derivar cat_edicion sólo de los hechos rompía el load con KeyError al
    resolver la FK de un catálogo de un año sin hechos.
    """
    from core.pipelines.defunciones_inegi.stages.load import DefuncionesInegiLoad

    catalogs = {
        "cat_ocupacion": [{"clave": 11, "descripcion": "x", "anio_edicion": 2018}],
        "cat_sexo": [{"clave": 1, "descripcion": "Hombre"}],
    }

    assert DefuncionesInegiLoad._edition_years([2017, 2024], catalogs) == [2017, 2018, 2024]
