"""Reglas de limpieza que salieron de inspeccionar los datos reales de la dependencia."""

import pandas as pd
import pytest

from core.pipelines.secretaria_educacion.constants import AULAS_COLUMNS, DIRECTORIO_COLUMNS
from core.pipelines.secretaria_educacion.stages.transform import SecretariaEducacionTransform

META = {"fecha_corte": "2025-09-30", "fecha_actualizacion": "2026-04-01"}

# Encabezados del origen, tal como llegan antes de renombrar.
FILA_DIRECTORIO = {
    "CLAVE DE CENTRO DE TRABAJO": "14DDI0004J",
    "TURNO": 120,
    "NOMBRE TURNO": "MAT-VESP",
    "NOMBRE DEL CENTRO DE TRABAJO": "CENTRO DE DESARROLLO INFANTIL 1",
    "DOMICILIO": "AVENIDA CENTRAL 615",
    "LOCALIDAD": 1,
    " NOMBRE LOCALIDAD": "ZAPOPAN",
    "COLONIA": 6287,
    "NOMBRE COLONIA": "RESIDENCIAL PONIENTE",
    "MUNICIPIO": 120,
    "NOMBRE MUNICIPIO": "ZAPOPAN",
    "MEDIO": "URBANA",
    "DIRECTOR": "GLORIA DEL PILAR TZINTZUN RUBIO",
    "CODIGO POSTAL": "45136",
    "TELEFONO": "3330307597",
    "ZONA ESCOLAR": 9,
    "SECTOR": 0,
    "NOMBRE SOSTENIMIENTO": "FEDERALIZADO",
    "NIVEL": "INICIAL",
    "PROGRAMA": "ESCOLARIZADO",
    "REGIÓN": 121,
    "NOMBRE REGIÓN": "CENTRO ZMG",
    "LONGITUD": -103.42852,
    "LATITUD": 20.7241951,
    "ESCUELAS": 1,
    "MATRÍCULA HOMBRES": 51,
    "MATRÍCULA MUJERES": 39,
    "MATRÍCULA TOTAL": 90,
    "TOTAL DE DOCENTES Y DIRECTIVO FRENTE A GRUPO": 22,
}


def _directorio(**overrides) -> pd.DataFrame:
    fila = {**FILA_DIRECTORIO, **overrides}
    return pd.DataFrame([fila])


def _preparar(**overrides) -> pd.DataFrame:
    return SecretariaEducacionTransform()._prepare_directorio(_directorio(**overrides), META)


def test_el_turno_mixto_se_expande_a_su_etiqueta_legible():
    assert _preparar()["turno"].item() == "Matutino - Vespertino"


def test_sector_en_cero_queda_nulo_porque_significa_no_aplica():
    assert pd.isna(_preparar()["sector"].item())


def test_zona_escolar_en_cero_queda_nula():
    assert pd.isna(_preparar(**{"ZONA ESCOLAR": 0})["zona_escolar"].item())


def test_zona_escolar_999_es_centinela_y_queda_nula():
    # 999 aparece aislado tras el 255, que es la última zona real.
    assert pd.isna(_preparar(**{"ZONA ESCOLAR": 999})["zona_escolar"].item())


def test_una_zona_escolar_valida_se_conserva():
    assert _preparar(**{"ZONA ESCOLAR": 36})["zona_escolar"].item() == 36


def test_el_nombre_del_municipio_no_sobrevive_al_transform():
    # El nombre se resuelve en la vista contra cvegeo, no se guarda.
    assert "nombre_municipio" not in _preparar().columns


def test_las_tres_fechas_se_agregan_desde_el_manifiesto():
    fila = _preparar()

    assert str(fila["fecha_corte"].item()) == "2025-09-30"
    assert str(fila["fecha_actualizacion_fuente"].item()) == "2026-04-01"
    assert fila["fecha_actualizacion"].notna().item()


def test_la_entidad_se_fija_a_jalisco():
    assert _preparar()["entidad_id"].item() == 14


def test_standardize_avisa_cuando_el_origen_pierde_una_columna_modelada():
    df = _directorio().drop(columns=["NIVEL"])

    with pytest.raises(KeyError, match="nivel"):
        SecretariaEducacionTransform()._prepare_directorio(df, META)


def test_las_filas_vacias_del_csv_de_aulas_se_descartan():
    # El export del origen arrastra miles de filas en blanco al final.
    llena = dict.fromkeys(AULAS_COLUMNS, "x") | {"aulas_asignadas": 1, "municipio": "EL SALTO"}
    vacia = dict.fromkeys(AULAS_COLUMNS, None)
    df = pd.DataFrame([llena, vacia, vacia])

    salida = SecretariaEducacionTransform()._prepare_aulas(df, META)

    assert len(salida) == 1


def test_el_catalogo_de_localidades_usa_la_clave_geoestadistica_compuesta():
    directorio = _preparar()

    localidades = SecretariaEducacionTransform()._build_localidades(directorio)

    # entidad a 2 digitos, municipio a 3, localidad a 4.
    assert localidades[0]["cve_geo_id"] == 141200001


def test_el_catalogo_de_turnos_queda_con_la_etiqueta_ya_expandida():
    catalogos = SecretariaEducacionTransform()._build_catalogs({"directorio": _preparar()})

    assert catalogos["turnos"] == [{"id": 120, "turno": "Matutino - Vespertino"}]


def test_las_columnas_modeladas_sobreviven_completas():
    salida = _preparar()

    faltantes = [column for column in DIRECTORIO_COLUMNS if column not in salida.columns]
    assert not faltantes
