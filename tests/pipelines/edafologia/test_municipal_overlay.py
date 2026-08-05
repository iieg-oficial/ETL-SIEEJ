from __future__ import annotations

import importlib
import sys
from pathlib import Path
import geopandas as gpd
import pytest
from shapely.geometry import GeometryCollection, LineString, MultiPolygon, Polygon
from sqlalchemy import create_engine, text

from core.pipelines.edafologia.constants import CANONICAL_SRID
from core.pipelines.edafologia.helpers.municipal_overlay import (
    calculate_municipal_overlay,
    calculate_overlay_for_source,
    validate_overlay_frame,
)
from core.pipelines.edafologia.helpers.transform_geometry import polygonal_part


def _mpoly(coords) -> MultiPolygon:
    return MultiPolygon([Polygon(coords)])


def _edafologias() -> gpd.GeoDataFrame:
    return gpd.GeoDataFrame(
        [
            {
                "source_version": "Serie III",
                "source_objectid": 1,
                "source_file_sha256": "a" * 64,
            }
        ],
        geometry=[_mpoly([(0, 0), (2, 0), (2, 2), (0, 2), (0, 0)])],
        crs=f"EPSG:{CANONICAL_SRID}",
    )


def _municipios(offset: float = 0) -> gpd.GeoDataFrame:
    return gpd.GeoDataFrame(
        [{"cvegeo": 14001}, {"cvegeo": 14002}],
        geometry=[
            _mpoly([(0 + offset, 0), (1 + offset, 0), (1 + offset, 2), (0 + offset, 2), (0 + offset, 0)]),
            _mpoly([(1 + offset, 0), (3 + offset, 0), (3 + offset, 2), (1 + offset, 2), (1 + offset, 0)]),
        ],
        crs=f"EPSG:{CANONICAL_SRID}",
    )


def test_polygonal_part_extracts_polygons_from_geometry_collection():
    collection = GeometryCollection(
        [
            LineString([(0, 0), (1, 1)]),
            Polygon([(0, 0), (1, 0), (1, 1), (0, 0)]),
        ]
    )

    result = polygonal_part(collection)

    assert isinstance(result, MultiPolygon)
    assert result.area > 0


def test_overlay_discards_line_contacts_and_keeps_polygonal_intersections():
    edafologias = _edafologias()
    municipios = gpd.GeoDataFrame(
        [{"cvegeo": 14001}, {"cvegeo": 14002}],
        geometry=[
            _mpoly([(0, 0), (1, 0), (1, 2), (0, 2), (0, 0)]),
            _mpoly([(2, 0), (3, 0), (3, 2), (2, 2), (2, 0)]),
        ],
        crs=f"EPSG:{CANONICAL_SRID}",
    )

    fragments, metrics = calculate_overlay_for_source(edafologias, municipios, "iieg")

    assert len(fragments) == 1
    assert fragments["municipality_cvegeo"].tolist() == [14001]
    assert metrics["non_polygonal_discarded"] == 1


def test_overlay_denominators_and_multipart_grouping():
    edafologias = _edafologias()
    municipalities = _municipios()

    fragments, metrics = calculate_overlay_for_source(edafologias, municipalities, "iieg")

    assert len(fragments) == 2
    assert pytest.approx(fragments["area_m2"].sum()) == 4.0
    first = fragments.loc[fragments["municipality_cvegeo"] == 14001].iloc[0]
    second = fragments.loc[fragments["municipality_cvegeo"] == 14002].iloc[0]
    assert pytest.approx(first["pct_poligono_fuente"]) == 50.0
    assert pytest.approx(first["pct_municipio_total"]) == 100.0
    assert pytest.approx(second["pct_poligono_fuente"]) == 50.0
    assert pytest.approx(second["pct_municipio_total"]) == 50.0
    assert metrics["final_fragments"] == 2


def test_overlay_rejects_duplicate_logical_keys():
    fragments, _metrics = calculate_overlay_for_source(_edafologias(), _municipios(), "iieg")
    duplicated = gpd.GeoDataFrame(
        list(fragments.to_dict("records")) + [fragments.iloc[0].to_dict()],
        geometry=list(fragments.geometry) + [fragments.geometry.iloc[0]],
        crs=fragments.crs,
    )

    with pytest.raises(ValueError, match="duplicated logical keys"):
        validate_overlay_frame(duplicated)


def test_overlay_manifest_covers_both_sources(tmp_path):
    extract_manifest = tmp_path / "extract.json"
    transform_manifest = tmp_path / "transform.json"
    eda = tmp_path / "eda.gpkg"
    muni = tmp_path / "muni.gpkg"
    extract_manifest.write_text("{}", encoding="utf-8")
    transform_manifest.write_text("{}", encoding="utf-8")
    eda.write_bytes(b"eda")
    muni.write_bytes(b"muni")
    inputs = {
        "transform_manifest_path": transform_manifest,
        "extract_manifest_path": extract_manifest,
        "transform_manifest": {"output_path": str(eda)},
        "extract_manifest": {"auxiliary_inputs": {"municipal_boundaries": {"output_gpkg": str(muni)}}},
        "edafologias": _edafologias(),
        "boundaries": {"iieg": _municipios(), "inegi": _municipios()},
    }

    fragments, manifest = calculate_municipal_overlay(inputs)

    assert set(fragments["fuente_limite_clave"]) == {"iieg", "inegi"}
    assert manifest["fragments_by_source"] == {"iieg": 2, "inegi": 2}
    assert manifest["input_counts"]["municipios_iieg"] == 2
    assert manifest["input_counts"]["municipios_inegi"] == 2


def _load_env_file(env_path: Path, monkeypatch) -> None:
    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        monkeypatch.setenv(key.strip(), value.strip().strip('"').strip("'"))


@pytest.mark.integration
def test_edafologia_municipal_overlay_real_integration(monkeypatch):
    env_path = Path("migrations/edafologia/.env")
    transform_manifest = Path("data/transform/edafologia/transform_manifest.json")
    extract_manifest = Path("data/extract/edafologia/manifest.json")
    if not env_path.exists() or not transform_manifest.exists() or not extract_manifest.exists():
        pytest.skip("Local env and extract/transform manifests are required for municipal overlay integration")

    _load_env_file(env_path, monkeypatch)
    monkeypatch.setenv("SOURCE_URL", "https://example.test/source.zip")
    monkeypatch.setenv("CVEGEO_DB_USER", "user")
    monkeypatch.setenv("CVEGEO_DB_PASSWORD", "secret")
    monkeypatch.setenv("CVEGEO_DB_HOST", "localhost")
    monkeypatch.setenv("CVEGEO_DB_PORT", "5433")
    monkeypatch.setenv("CVEGEO_DB_NAME", "cvegeo")
    for module in (
        "core.pipelines.edafologia.config",
        "core.pipelines.edafologia.stages.transform",
        "core.pipelines.edafologia.stages.load",
    ):
        sys.modules.pop(module, None)

    transform_stage = importlib.import_module("core.pipelines.edafologia.stages.transform")
    load_stage = importlib.import_module("core.pipelines.edafologia.stages.load")
    transform_result = transform_stage.EdafologiaTransform().execute()
    load_result = load_stage.EdafologiaLoad().execute()

    settings = importlib.import_module("core.pipelines.edafologia.config").settings
    engine = create_engine(settings.database_url)
    with engine.connect() as connection:
        counts = dict(
            connection.execute(
                text(
                    """
                    SELECT flm.clave, count(*)::integer
                    FROM edafologia_fragmentos_municipales efm
                    JOIN fuentes_limites_municipales flm
                        ON flm.id = efm.fuente_limite_municipal_id
                    GROUP BY flm.clave
                    ORDER BY flm.clave
                    """
                )
            ).all()
        )
        view_count = connection.execute(
            text("SELECT count(*)::integer FROM edafologia_resumenes_municipales")
        ).scalar_one()
    engine.dispose()

    assert set(transform_result["overlay_manifest"]["fragments_by_source"]) == {"iieg", "inegi"}
    assert counts["iieg"] > 0
    assert counts["inegi"] > 0
    assert load_result["overlay"]["records"] == counts["iieg"] + counts["inegi"]
    assert view_count > 0
