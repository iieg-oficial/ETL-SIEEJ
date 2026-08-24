import pytest

from core.indicadores import registro


INDICATOR_IDS = (
    "superficie_grupo_edafologico_municipal",
    "porcentaje_grupo_edafologico_municipal",
)


def test_edafologia_indicators_follow_approved_metadata():
    indicators = [registro.obtener(indicator_id) for indicator_id in INDICATOR_IDS]

    assert [indicator.unidad for indicator in indicators] == ["hectáreas", "porcentaje"]
    for indicator in indicators:
        assert indicator.tema == "medio_ambiente"
        assert indicator.pipeline == "edafologia"
        assert indicator.origen == "edafologia_resumenes_municipales"
        assert indicator.nivel == "municipal"
        assert indicator.periodicidad == "no periódica"
        assert indicator.cobertura.geografica == "Jalisco"
        assert indicator.cobertura.temporal == "2021"


def test_edafologia_indicators_require_boundary_source():
    for indicator_id in INDICATOR_IDS:
        indicator = registro.obtener(indicator_id)
        parameters = {parameter.nombre: parameter for parameter in indicator.parametros}

        assert parameters["cve_geo"].requerido is False
        assert parameters["fuente_limite"].requerido is True
        with pytest.raises(ValueError, match="fuente_limite"):
            registro._binds(indicator, {})
        assert registro._binds(indicator, {"fuente_limite": "iieg"}) == {
            "cve_geo": None,
            "fuente_limite": "iieg",
        }


def test_edafologia_indicators_aggregate_qualifiers_by_group():
    expected_measure = {
        "superficie_grupo_edafologico_municipal": "SUM(r.superficie_ha)::numeric",
        "porcentaje_grupo_edafologico_municipal": "SUM(r.porcentaje_municipio)::numeric",
    }

    for indicator_id, measure in expected_measure.items():
        sql = registro.obtener(indicator_id).sql

        assert measure in sql
        assert "AS valor" in sql
        assert "r.calificador_primario_id" not in sql
        assert "r.calificador_secundario_id" not in sql
        assert "r.grupo_edafologico_id" in sql
        assert "flm.clave = CAST(:fuente_limite AS text)" in sql
        assert "r.municipality_id = m.cve_mun" in sql
        assert "m.cve_ent = 14" in sql
        assert "'2021'::text" in sql


def test_edafologia_category_comes_from_group_catalog():
    for indicator_id in INDICATOR_IDS:
        sql = registro.obtener(indicator_id).sql

        assert "JOIN grupos_edafologicos AS g" in sql
        assert "g.clave || ' — ' || g.descripcion" in sql
