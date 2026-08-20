"""Validación del catálogo de indicadores. No requiere base de datos."""

from pathlib import Path

import pytest

from core.indicadores import registro
from core.indicadores.registro import BINDS, COLUMNAS

PIPELINES = Path("core/pipelines")
CATALOGO = registro._catalogo()
INDICADORES = list(CATALOGO.values())


def test_catalogo_no_vacio():
    assert INDICADORES, "el catálogo no cargó ningún indicador"


def test_ids_unicos():
    # _catalogo() ya revienta con ids duplicados; esto ancla la garantía.
    ids = [ind.id for ind in INDICADORES]
    assert len(ids) == len(set(ids))


def test_id_coincide_con_nombre_de_archivo():
    for ruta in registro.CATALOGO.glob("*/*.yaml"):
        assert ruta.stem in CATALOGO, f"{ruta}: el id no coincide con el nombre del archivo"


@pytest.mark.parametrize("ind", INDICADORES, ids=lambda i: i.id)
def test_pipeline_existe(ind):
    assert (PIPELINES / ind.pipeline).is_dir(), f"{ind.id}: el pipeline '{ind.pipeline}' no existe"


@pytest.mark.parametrize("ind", INDICADORES, ids=lambda i: i.id)
def test_tema_coincide_con_carpeta(ind):
    assert (registro.CATALOGO / ind.tema / f"{ind.id}.yaml").exists()


@pytest.mark.parametrize("ind", INDICADORES, ids=lambda i: i.id)
def test_sql_es_de_solo_lectura(ind):
    assert ind.sql.lstrip().upper().startswith(("SELECT", "WITH"))


@pytest.mark.parametrize("ind", INDICADORES, ids=lambda i: i.id)
def test_parametros_y_binds_coinciden(ind):
    assert {p.nombre for p in ind.parametros} == set(BINDS.findall(ind.sql))


@pytest.mark.parametrize("ind", INDICADORES, ids=lambda i: i.id)
def test_sql_declara_las_cinco_columnas(ind):
    # _validar() ya revienta si falta alguna; esto ancla la garantía.
    for columna in COLUMNAS:
        assert f"AS {columna}" in ind.sql, f"{ind.id}: falta la columna '{columna}' en el SELECT"


def test_listar_filtra_y_oculta_el_sql():
    empleo = registro.listar(tema="empleo")
    assert empleo and all(m["tema"] == "empleo" for m in empleo)
    assert all("sql" not in m for m in empleo)
    assert all(m["nivel"] == "municipal" for m in registro.listar(nivel="municipal"))


def test_obtener_id_inexistente():
    with pytest.raises(ValueError):
        registro.obtener("no_existe")


def test_binds_ignora_los_casts_de_postgres():
    assert BINDS.findall("valor::numeric = CAST(:cve_geo AS text)") == ["cve_geo"]


def test_validar_rechaza_sql_sin_las_columnas():
    ind = CATALOGO["pobreza_municipal"].model_copy(update={"sql": "SELECT 1 AS cve_geo"})
    with pytest.raises(ValueError, match="no proyecta las columnas"):
        registro._validar(ind, Path("falso.yaml"))


def test_params_desconocidos_y_requeridos():
    ind = CATALOGO["tasa_desocupacion_municipal"]
    with pytest.raises(ValueError, match="desconocidos"):
        registro._binds(ind, {"municipio": "14039"})
    # Todos los parámetros del piloto son opcionales: sin params, todos van en None.
    assert registro._binds(ind, {}) == {"cve_geo": None, "anio_min": None}
    assert registro._binds(ind, {"anio_min": "2020"}) == {"cve_geo": None, "anio_min": 2020}
