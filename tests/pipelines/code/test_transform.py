"""Reglas de limpieza de Reto: puntos del gpkg y región del xlsx."""

from datetime import date

import pandas as pd
import pytest

from core.pipelines.code.constants import PUNTOS_COLUMNS
from core.pipelines.code.helpers.reto import build_catalogs, prepare_puntos, region_lookup, transform_reto
from core.pipelines.code.stages.transform import CodeTransform
from tests.pipelines.code.code_factories import gdf_from_rows

MANIFEST = {"envio_id": 28, "actualizado_en": "2026-09-09 17:16:53.235786+00:00"}

# Encabezados y valores de la capa del gpkg, incluidos los espacios sobrantes.
FILA = {
    "fecha": "01/07/2026",
    "municipio": "ZMG Zapopan",
    "cve_mun": "120",
    "nombre_centro": "  Unidad  Deportiva ",
    "horarios": "L - Mi - V de 18:00 a 19:30",
    "actividad": "Baile ",
    "cat_actividad": 1.0,
    "cantidad_de_usuarios": 14,
    "y_6368": 20.7,
    "x_6368": -103.4,
}

# Hoja `base` del xlsx: solo aporta la región de cada municipio.
BASE = pd.DataFrame({"clave_agem": [120, 121, 120], "region": ["Altos sur ", "CIENEGA ", "Altos Sur"]})

CATALOGO = pd.DataFrame({"actividad": ["Baile ", "Zumba"], "id": [1, 2]})


def _capa(*filas: dict):
    return gdf_from_rows(list(filas) or [FILA])


def _preparar(base: pd.DataFrame = BASE, **cambios) -> pd.DataFrame:
    return prepare_puntos(_capa({**FILA, **cambios}), base, MANIFEST)


def test_la_region_sale_del_xlsx_por_municipio():
    assert _preparar()["region"].item() == "Altos Sur"


def test_las_regiones_se_limpian_con_title_case_y_acentos():
    assert region_lookup(BASE) == {120: "Altos Sur", 121: "Ciénega"}


def test_un_municipio_con_dos_regiones_es_un_error():
    base = pd.DataFrame({"clave_agem": [120, 120], "region": ["Norte", "Sur"]})

    with pytest.raises(ValueError, match="more than one region"):
        region_lookup(base)


def test_un_municipio_sin_region_en_el_xlsx_es_un_error():
    with pytest.raises(ValueError, match=r"without a region.*99"):
        _preparar(cve_mun="099")


@pytest.mark.parametrize("sucio", ["NA", "null", "N/A", "nan"])
def test_una_region_nula_cuenta_como_faltante(sucio):
    base = pd.DataFrame({"clave_agem": [120], "region": [sucio]})

    with pytest.raises(ValueError, match="without a region"):
        _preparar(base=base)


def test_el_nombre_del_municipio_no_sobrevive_al_transform():
    salida = _preparar()

    assert "municipio" not in salida.columns
    assert salida["municipio_id"].item() == 120


def test_el_texto_libre_se_limpia_de_espacios():
    assert _preparar()["nombre_espacio"].item() == "Unidad Deportiva"


def test_los_horarios_no_se_parsean():
    assert _preparar()["dias_horarios"].item() == "L - Mi - V de 18:00 a 19:30"


def test_la_actividad_flotante_pasa_a_entero_nullable():
    assert _preparar()["actividad_id"].item() == 1


def test_una_actividad_faltante_queda_nula():
    assert pd.isna(_preparar(cat_actividad=float("nan"), actividad=None)["actividad_id"].item())


def test_las_coordenadas_salen_de_la_geometria_en_wgs84():
    salida = _preparar()

    assert salida["longitud"].item() == pytest.approx(-103.4)
    assert salida["latitud"].item() == pytest.approx(20.7)


def test_los_atributos_x_y_de_la_capa_no_se_usan():
    # La capa de CODE trae `x`/`y` que pueden no coincidir con la geometría.
    salida = _preparar(x=-101.16, y=22.4)

    assert salida["latitud"].item() == pytest.approx(20.7)


def test_no_se_construye_geometria():
    assert "geom" not in _preparar().columns
    assert "geometry" not in _preparar().columns


def test_no_hay_clave_punto():
    assert "clave_punto" not in _preparar().columns


def test_la_entidad_se_fija_a_jalisco():
    assert _preparar()["entidad_id"].item() == 14


def test_el_corte_sale_de_la_columna_fecha_de_los_datos():
    assert _preparar()["fecha_corte"].item() == date(2026, 7, 1)


def test_la_actualizacion_de_la_fuente_sale_de_la_fecha_del_envio():
    assert _preparar()["fecha_actualizacion_fuente"].item() == date(2026, 9, 9)


def test_la_fecha_de_actualizacion_es_hoy():
    assert _preparar()["fecha_actualizacion"].item() == date.today()


def test_una_fecha_de_corte_invalida_es_un_error():
    with pytest.raises(ValueError, match="fecha"):
        _preparar(fecha="2026-07-01")


def test_standardize_avisa_cuando_el_origen_pierde_una_columna_modelada():
    capa = _capa().drop(columns=["cantidad_de_usuarios"])

    with pytest.raises(KeyError, match="cantidad_usuarios"):
        prepare_puntos(capa, BASE, MANIFEST)


def test_las_columnas_modeladas_sobreviven_completas():
    salida = _preparar()

    assert not [c for c in PUNTOS_COLUMNS if c not in salida.columns]


def test_el_catalogo_de_actividades_conserva_el_id_del_origen():
    catalogo = build_catalogs(_preparar(), CATALOGO)["actividades"]

    assert catalogo == [{"id": 1, "actividad": "Baile"}, {"id": 2, "actividad": "Zumba"}]


def test_el_catalogo_de_regiones_sale_de_los_valores_ya_limpios():
    capa = _capa({**FILA, "nombre_centro": "A"}, {**FILA, "nombre_centro": "B", "cve_mun": "121"})
    preparado = prepare_puntos(capa, BASE, MANIFEST)

    assert build_catalogs(preparado, CATALOGO)["regiones"] == [{"region": "Altos Sur"}, {"region": "Ciénega"}]


def test_un_update_sin_cargas_nuevas_no_es_un_error():
    assert CodeTransform(mode="update").action({}) == {}


def test_un_punto_duplicado_en_la_llave_unica_es_un_error_claro():
    with pytest.raises(ValueError, match=r"(?s)duplicated.*Unidad Deportiva"):
        prepare_puntos(_capa(FILA, FILA), BASE, MANIFEST)


def test_el_mismo_espacio_en_otro_municipio_no_es_duplicado():
    assert len(prepare_puntos(_capa(FILA, {**FILA, "cve_mun": "121"}), BASE, MANIFEST)) == 2


@pytest.mark.parametrize(
    ("cambio", "columna"),
    [
        ({"cve_mun": None}, "municipio_id"),
        ({"nombre_centro": "  "}, "nombre_espacio"),
    ],
)
def test_una_columna_obligatoria_sin_valor_es_un_error_que_la_nombra(cambio, columna):
    with pytest.raises(ValueError, match=columna):
        _preparar(**cambio)


def test_una_actividad_fuera_del_catalogo_es_un_error():
    with pytest.raises(ValueError, match="99"):
        build_catalogs(_preparar(cat_actividad=99.0), CATALOGO)


def test_una_actividad_nula_no_se_valida_contra_el_catalogo():
    assert build_catalogs(_preparar(cat_actividad=float("nan")), CATALOGO)["actividades"]


def test_transform_reto_une_capa_hoja_base_y_catalogo():
    frames = {"datos": _capa(), "base": BASE, "cat_actividad": CATALOGO}

    salida, catalogos = transform_reto(frames, MANIFEST)

    assert len(salida["puntos"]) == 1
    assert set(catalogos) == {"actividades", "regiones"}
