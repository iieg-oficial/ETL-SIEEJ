"""Transform de los conjuntos gpkg: Academias deportivas y Polideportivos."""

from datetime import date

import pandas as pd
import pytest

from core.pipelines.code.helpers.academias import transform_academias
from core.pipelines.code.helpers.common import lon_lat
from core.pipelines.code.helpers.polideportivos import transform_polideportivos
from tests.pipelines.code.code_factories import ACADEMIA_ROW, CAT_DEPORTE, CAT_TIPO, POLI_ROW, gdf_from_rows

MANIFEST = {"envio_id": 28, "actualizado_en": "2026-10-22 22:27:17+00:00"}


def _academias(*changes: dict, tipos=CAT_TIPO):
    rows = [{**ACADEMIA_ROW, **change} for change in (changes or ({},))]
    return transform_academias({"datos": gdf_from_rows(rows), "cat_deporte": CAT_DEPORTE, "cat_tipo": tipos}, MANIFEST)


def _polis(*changes: dict):
    rows = [{**POLI_ROW, **change} for change in (changes or ({},))]
    return transform_polideportivos({"datos": gdf_from_rows(rows), "cat_deporte": CAT_DEPORTE}, MANIFEST)


# coordenadas


def test_lon_lat_salen_de_la_geometria_convertida_a_wgs84():
    lon, lat = lon_lat(gdf_from_rows([ACADEMIA_ROW]))

    assert lon.item() == pytest.approx(-102.9, abs=1e-6)
    assert lat.item() == pytest.approx(20.78, abs=1e-6)


def test_sin_geometria_las_coordenadas_quedan_nulas():
    gdf = gdf_from_rows([ACADEMIA_ROW])
    gdf.loc[0, "geometry"] = None

    lon, lat = lon_lat(gdf)

    assert pd.isna(lon.item()) and pd.isna(lat.item())


# academias


def test_academias_el_corte_y_el_municipio_se_interpretan():
    frames, _ = _academias()
    row = frames["academias"].iloc[0]

    assert row["fecha_corte"] == date(2026, 10, 1)
    assert row["municipio_id"] == 1
    assert row["entidad_id"] == 14


def test_academias_el_deporte_se_resuelve_por_nombre_y_no_por_cat_deporte():
    """cat_deporte del archivo no coincide con el catalogo que acompana (5 contra 13)."""
    frames, _ = _academias()

    assert frames["academias"]["deporte_id"].item() == 13


def test_academias_un_deporte_desconocido_lista_los_valores():
    with pytest.raises(ValueError, match="Esgrima"):
        _academias({"deporte": "Esgrima"})


def test_academias_los_beneficiarios_son_enteros_nullables():
    frames, _ = _academias({"beneficiarios_mujeres": float("nan")})
    row = frames["academias"].iloc[0]

    assert row["beneficiarios_total"] == 75
    assert pd.isna(row["beneficiarios_mujeres"])


def test_academias_el_texto_se_limpia_pero_el_nombre_largo_conserva_su_forma():
    frames, _ = _academias()
    row = frames["academias"].iloc[0]

    assert row["domicilio"] == "Plaza Principal 1"
    assert row["deporte_nombre_largo"] == "CHARRERÍA"


def test_academias_no_conservan_nombres_ni_ids_de_catalogo_del_origen():
    frames, _ = _academias()

    assert not {"municipio", "deporte", "cat_deporte", "cat_tipo", "x_6368", "geometry"} & set(
        frames["academias"].columns
    )


def test_academias_el_catalogo_de_tipos_agrega_los_que_el_csv_no_lista():
    """'Semillero Rojiblanco' esta en los datos pero no en el catalogo que acompana."""
    _, catalogs = _academias({"tipo": "Semillero Rojiblanco"})

    assert catalogs["tipos"] == [{"tipo": "Centro Regional"}, {"tipo": "Regular"}, {"tipo": "Semillero Rojiblanco"}]


def test_academias_el_catalogo_de_tipos_ignora_la_fila_vacia_del_csv():
    _, catalogs = _academias()

    assert {"tipo": None} not in catalogs["tipos"]


def test_academias_el_catalogo_de_deportes_conserva_los_ids_del_origen():
    _, catalogs = _academias()

    assert {"id": 19, "deporte": "Natación"} in catalogs["deportes"]
    assert len(catalogs["deportes"]) == 3


def test_academias_rechazan_filas_sin_municipio():
    with pytest.raises(ValueError, match="municipio_id"):
        _academias({"cve_mun": None})


def test_academias_falla_si_falta_una_columna_modelada():
    gdf = gdf_from_rows([ACADEMIA_ROW]).drop(columns=["horarios"])

    with pytest.raises(KeyError, match="horarios"):
        transform_academias({"datos": gdf, "cat_deporte": CAT_DEPORTE, "cat_tipo": CAT_TIPO}, MANIFEST)


def test_academias_las_fechas_de_la_carga():
    frames, _ = _academias()
    row = frames["academias"].iloc[0]

    assert row["fecha_actualizacion_fuente"] == date(2026, 10, 22)
    assert row["fecha_actualizacion"] == date.today()


def test_academias_una_fecha_invalida_es_un_error():
    with pytest.raises(ValueError, match="fecha"):
        _academias({"fecha": "2026-10-01"})


# polideportivos


def test_polideportivos_los_campos_se_interpretan():
    frames, _ = _polis()
    row = frames["polideportivos"].iloc[0]

    assert row["fecha_corte"] == date(2026, 1, 1)
    assert row["entidad_id"] == 14
    assert row["municipio_id"] == 39
    assert row["nombre_centro"] == "Polideportivo Paradero"
    assert row["servicios"] == "Escuela deportiva"


def test_polideportivos_los_deportes_pasan_a_la_tabla_puente():
    frames, _ = _polis()
    bridge = frames["polideportivo_deportes"]

    assert sorted(bridge["deporte_id"]) == [13, 19]
    assert set(bridge["nombre_centro"]) == {"Polideportivo Paradero"}
    assert "deportes" not in frames["polideportivos"].columns


def test_polideportivos_la_puente_descarta_deportes_repetidos():
    frames, _ = _polis({"deportes": "19, 19,13"})

    assert len(frames["polideportivo_deportes"]) == 2


def test_polideportivos_un_id_de_deporte_desconocido_lista_los_valores():
    with pytest.raises(ValueError, match="99"):
        _polis({"deportes": "19,99"})


def test_polideportivos_un_deporte_no_numerico_es_un_error():
    with pytest.raises(ValueError, match="deportes"):
        _polis({"deportes": "19,x"})


def test_polideportivos_una_llave_duplicada_falla():
    with pytest.raises(ValueError, match="duplicated"):
        _polis({}, {})


def test_polideportivos_el_catalogo_solo_tiene_deportes():
    _, catalogs = _polis()

    assert set(catalogs) == {"deportes"}


def test_polideportivos_sin_deportes_no_genera_filas_puente():
    frames, _ = _polis({"deportes": None})

    assert frames["polideportivo_deportes"].empty


def test_academias_tipo_con_espacios_y_otra_capitalizacion_usa_la_forma_del_catalogo():
    frames, catalogs = _academias({"tipo": "  regular "})

    assert frames["academias"]["tipo"].item() == "Regular"
    assert {"tipo": "Regular"} in catalogs["tipos"]
    assert len(catalogs["tipos"]) == 2


def test_academias_tipos_que_solo_difieren_en_forma_se_unifican_en_una_entrada():
    frames, catalogs = _academias(
        {"tipo": "Semillero  Rojiblanco"}, {"tipo": "semillero rojiblanco"}, {"tipo": "SEMILLERO ROJIBLANCO"}
    )

    assert set(frames["academias"]["tipo"]) == {"Semillero Rojiblanco"}
    assert sum(item["tipo"] == "Semillero Rojiblanco" for item in catalogs["tipos"]) == 1
    assert len(catalogs["tipos"]) == 3
