"""El origen llega en mayúsculas y sin acentos; estos helpers lo vuelven legible."""

import pandas as pd
import pytest

from core.pipelines.secretaria_educacion.helpers.values import capitalize_es, plain_title, title_es


def test_title_es_baja_las_preposiciones_menos_la_primera_palabra():
    assert title_es("CENTRO DE DESARROLLO INFANTIL 1") == "Centro de Desarrollo Infantil 1"


def test_title_es_nunca_baja_la_primera_palabra():
    assert title_es("DEL RIO") == "Del Río"


def test_title_es_restituye_acentos_del_mapa_global():
    assert title_es("ZAPOTLAN EL GRANDE") == "Zapotlán el Grande"


def test_title_es_restituye_acentos_del_mapa_propio_del_pipeline():
    # AUTONOMO y BILINGUE no están en el ACCENT_MAP global.
    assert title_es("AUTONOMO") == "Autónomo"


def test_title_es_deja_las_siglas_en_su_forma_canonica():
    assert title_es("CENDI INFANTIL 2") == "CENDI Infantil 2"
    assert title_es("CENTRO ZMG") == "Centro ZMG"


def test_title_es_capitaliza_despues_del_guion():
    assert title_es("MAT-VESP") == "Mat-Vesp"


def test_capitalize_es_solo_sube_la_primera_letra():
    assert capitalize_es("BACH. TECNOLOGICO SEMIESCOLARIZADO") == "Bach. tecnológico semiescolarizado"


def test_capitalize_es_conserva_jalisco_como_nombre_propio():
    assert capitalize_es("talento al estilo jalisco") == "Talento al estilo Jalisco"


def test_plain_title_baja_particulas_segun_la_rae():
    # La RAE escribe la partícula en minúscula cuando sigue al nombre de pila.
    assert plain_title("GLORIA DEL PILAR TZINTZUN RUBIO") == "Gloria del Pilar Tzintzun Rubio"
    assert plain_title("MARIA DE LOURDES PEREZ ANDRADE") == "Maria de Lourdes Perez Andrade"


def test_plain_title_no_inventa_acentos_en_apellidos():
    # El origen los omite y son miles de valores: adivinarlos escribiría mal a personas reales.
    assert plain_title("PAOLA GARCIA MACIAS") == "Paola Garcia Macias"


@pytest.mark.parametrize("vacio", [None, pd.NA, "", "   "])
def test_los_helpers_devuelven_none_ante_valores_vacios(vacio):
    assert title_es(vacio) is None
    assert capitalize_es(vacio) is None
    assert plain_title(vacio) is None


def test_title_es_colapsa_espacios_repetidos():
    assert title_es("  ZAPOPAN   CENTRO  ") == "Zapopan Centro"
