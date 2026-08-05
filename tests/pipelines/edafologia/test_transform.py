from __future__ import annotations

import json
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import GeometryCollection, MultiPolygon, Polygon

from core.pipelines.edafologia.constants import CANONICAL_SRID, EXPECTED_SOURCE_COLUMNS
from core.pipelines.edafologia.helpers.transform import (
    apply_catalog_ids,
    validate_catalog_coverage,
)
from core.pipelines.edafologia.helpers.transform_geometry import (
    build_canonical_mask,
    clip_to_mask,
    dissolve_by_source_objectid,
    final_spatial_validation,
    polygonal_part,
    repair_and_polygonize,
    write_gpkg_atomic,
)
from core.pipelines.edafologia.helpers.transform_inputs import (
    read_source_layer,
    validate_boundary_gdf,
    validate_extract_manifest,
)
from core.pipelines.edafologia.mappings import (
    CALIFICADORES_EDAFOLOGICOS,
    GRUPOS_EDAFOLOGICOS,
    catalog_manifest,
)


def _square(xmin: float, ymin: float, xmax: float, ymax: float) -> Polygon:
    return Polygon([(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax), (xmin, ymin)])


def _source_frame(geometries, codes: tuple[str, str, str] = ("AC", "ab", "N")) -> gpd.GeoDataFrame:
    records = []
    for idx, geometry in enumerate(geometries, start=1):
        records.append(
            {
                "OBJECTID": idx,
                "Clave_wrb": f"WRB{idx}",
                "Grupo1": codes[0],
                "Califp_g1": codes[1],
                "Califs_g1": codes[2],
                "Grupo2": None,
                "Califp_g2": None,
                "Califs_g2": None,
                "Grupo3": None,
                "Califp_g3": None,
                "Clase_tex": "media",
                "Lmte_sup": None,
                "Fase_fis_u": None,
                "Fase_qui_u": None,
                "Shape_Leng": 1.0,
                "Shape_Area": 1.0,
            }
        )
    return gpd.GeoDataFrame(pd.DataFrame(records), geometry=geometries, crs=f"EPSG:{CANONICAL_SRID}")


def _boundary(geometry: Polygon, cvegeo: str = "14001") -> gpd.GeoDataFrame:
    return gpd.GeoDataFrame(
        pd.DataFrame(
            [
                {
                    "cvegeo": cvegeo,
                    "cve_ent": "14",
                    "cve_mun": cvegeo[-3:],
                    "nomgeo": "Municipio",
                    "nom_ent": "Jalisco",
                }
            ]
        ),
        geometry=[MultiPolygon([geometry])],
        crs=f"EPSG:{CANONICAL_SRID}",
    )


def _catalog_manifest() -> dict[str, object]:
    return {
        "grupo1": catalog_manifest(GRUPOS_EDAFOLOGICOS, "v1"),
        "calificadores": catalog_manifest(CALIFICADORES_EDAFOLOGICOS, "v1"),
    }


def _minimal_extract_manifest(tmp_path: Path, zip_hash: str) -> dict[str, object]:
    zip_path = tmp_path / "source.zip"
    selected_path = tmp_path / "source.gpkg"
    boundaries_path = tmp_path / "boundaries.gpkg"
    zip_path.write_bytes(b"zip")
    selected_path.write_bytes(b"selected")
    boundaries_path.write_bytes(b"boundaries")
    return {
        "source_url": "https://example.test/source.zip",
        "source_name": "source",
        "source_version": "Serie III",
        "downloaded_at": "2026-07-15T00:00:00+00:00",
        "zip_path": str(zip_path),
        "source_file_sha256": zip_hash,
        "selected_path": str(selected_path),
        "selected_layer": "layer",
        "selected_geometry_type": "Polygon",
        "selected_crs": "EPSG:6368",
        "selected_feature_count": 1,
        "selected_fields": list(EXPECTED_SOURCE_COLUMNS),
        "auxiliary_inputs": {
            "municipal_boundaries": {
                "output_gpkg": str(boundaries_path),
                "layers": {"municipios_iieg": {}, "municipios_inegi": {}},
            }
        },
        "controlled_catalogs": _catalog_manifest(),
        "pipeline_version": "0.2.0",
    }


def test_validate_extract_manifest_rejects_hash_inconsistency(tmp_path):
    manifest = _minimal_extract_manifest(tmp_path, zip_hash="bad")
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(ValueError, match="ZIP hash"):
        validate_extract_manifest(manifest_path)


def test_read_source_layer_rejects_missing_crs(monkeypatch):
    gdf = _source_frame([_square(0, 0, 1, 1)])
    gdf.crs = None
    manifest = {
        "selected_path": "source.gpkg",
        "selected_layer": "layer",
        "selected_feature_count": 1,
    }

    monkeypatch.setattr("core.pipelines.edafologia.helpers.transform.gpd.read_file", lambda *args, **kwargs: gdf)

    with pytest.raises(ValueError, match="no CRS"):
        read_source_layer(manifest)


def test_repair_geometries_repairs_invalid_polygon():
    invalid = Polygon([(0, 0), (1, 1), (1, 0), (0, 1), (0, 0)])
    gdf = _source_frame([invalid]).rename(columns={"OBJECTID": "source_objectid"})

    repaired, stats = repair_and_polygonize(gdf, "source_objectid", "test")

    assert stats["invalid_before"] == 1
    assert stats["repaired_count"] == 1
    assert repaired.geometry.is_valid.all()
    assert repaired.geometry.geom_type.tolist() == ["MultiPolygon"]


def test_polygonal_part_extracts_polygon_from_geometry_collection():
    collection = GeometryCollection([_square(0, 0, 1, 1).boundary, _square(0, 0, 1, 1)])

    result = polygonal_part(collection)

    assert isinstance(result, MultiPolygon)
    assert len(result.geoms) == 1


def test_polygonal_part_converts_polygon_to_multipolygon():
    result = polygonal_part(_square(0, 0, 1, 1))

    assert isinstance(result, MultiPolygon)


def test_clip_uses_union_of_iieg_and_inegi():
    iieg = _boundary(_square(0, 0, 1, 1))
    inegi = _boundary(_square(2, 0, 3, 1))
    mask, _ = build_canonical_mask(iieg, inegi)
    source = _source_frame([_square(0, 0, 3, 1)]).rename(columns={"OBJECTID": "source_objectid"})

    clipped, selected_count = clip_to_mask(source, mask)

    assert selected_count == 1
    assert round(float(clipped.geometry.iloc[0].area), 6) == 2.0


def test_canonical_mask_preserves_iieg_only_area():
    iieg = _boundary(_square(0, 0, 1, 1))
    inegi = _boundary(_square(0.5, 0, 1.5, 1))
    _, stats = build_canonical_mask(iieg, inegi)

    assert stats["area_exclusive_iieg_m2"] > 0


def test_canonical_mask_preserves_inegi_only_area():
    iieg = _boundary(_square(0, 0, 1, 1))
    inegi = _boundary(_square(0.5, 0, 1.5, 1))
    _, stats = build_canonical_mask(iieg, inegi)

    assert stats["area_exclusive_inegi_m2"] > 0


def test_transform_boundary_validation_rejects_incoherent_municipal_key():
    boundary = _boundary(_square(0, 0, 1, 1))
    boundary.loc[0, "cve_mun"] = "002"

    with pytest.raises(ValueError, match="coherent_cvegeo"):
        validate_boundary_gdf(boundary, "municipios_iieg")


def test_dissolve_keeps_one_row_per_source_objectid():
    gdf = _source_frame([_square(0, 0, 1, 1), _square(2, 0, 3, 1)]).rename(columns={"OBJECTID": "source_objectid"})
    gdf.loc[1, "source_objectid"] = 1

    dissolved = dissolve_by_source_objectid(gdf)

    assert len(dissolved) == 1
    assert dissolved["source_objectid"].tolist() == [1]
    assert dissolved.geometry.iloc[0].geom_type == "MultiPolygon"


def test_catalog_mapping_applies_after_clip():
    gdf = _source_frame([_square(0, 0, 1, 1)], ("AC", "ab", "N")).rename(
        columns={
            "OBJECTID": "source_objectid",
            "Grupo1": "grupo1_origen",
            "Califp_g1": "califp_g1_origen",
            "Califs_g1": "califs_g1_origen",
        }
    )

    result = validate_catalog_coverage(gdf)

    assert result["coverage"]["grupo1_origen"]["unmapped_codes"] == 0


def test_catalog_ids_preserve_primary_and_secondary_roles_with_same_mapping():
    gdf = _source_frame([_square(0, 0, 1, 1)], ("AC", "ab", "ab")).rename(
        columns={
            "OBJECTID": "source_objectid",
            "Grupo1": "grupo1_origen",
            "Califp_g1": "califp_g1_origen",
            "Califs_g1": "califs_g1_origen",
        }
    )

    result = apply_catalog_ids(gdf)

    assert result["calificador_primario_id"].iloc[0] == result["calificador_secundario_id"].iloc[0]
    assert "califp_g1_origen" in result
    assert "califs_g1_origen" in result


def test_catalog_ids_resolve_fl_as_secondary_qualifier():
    gdf = _source_frame([_square(0, 0, 1, 1)], ("CM", "lep", "fl")).rename(
        columns={
            "OBJECTID": "source_objectid",
            "Grupo1": "grupo1_origen",
            "Califp_g1": "califp_g1_origen",
            "Califs_g1": "califs_g1_origen",
        }
    )

    result = apply_catalog_ids(gdf)

    assert CALIFICADORES_EDAFOLOGICOS["fl"] == "Ferrálico"
    assert result["calificador_secundario_id"].iloc[0] > 0


def test_unmapped_code_inside_jalisco_raises():
    gdf = _source_frame([_square(0, 0, 1, 1)], ("ZZ", "ab", "N")).rename(
        columns={
            "OBJECTID": "source_objectid",
            "Grupo1": "grupo1_origen",
            "Califp_g1": "califp_g1_origen",
            "Califs_g1": "califs_g1_origen",
        }
    )

    with pytest.raises(ValueError, match="Unmapped"):
        validate_catalog_coverage(gdf)


def test_unmapped_code_outside_mask_does_not_block():
    iieg = _boundary(_square(0, 0, 1, 1))
    inegi = _boundary(_square(0, 0, 1, 1))
    mask, _ = build_canonical_mask(iieg, inegi)
    source = _source_frame([_square(0, 0, 1, 1), _square(10, 10, 11, 11)], ("AC", "ab", "N")).rename(
        columns={
            "OBJECTID": "source_objectid",
            "Grupo1": "grupo1_origen",
            "Califp_g1": "califp_g1_origen",
            "Califs_g1": "califs_g1_origen",
        }
    )
    source.loc[1, "grupo1_origen"] = "ZZ"

    clipped, _ = clip_to_mask(source, mask)
    result = validate_catalog_coverage(clipped)

    assert result["unmapped_codes"]["grupo1_origen"] == {}


def test_write_gpkg_atomic_preserves_previous_file_on_failure(tmp_path):
    output_path = tmp_path / "out.gpkg"
    output_path.write_bytes(b"previous")

    class BrokenFrame:
        def to_file(self, path, layer, driver):
            Path(path).write_bytes(b"partial")
            raise RuntimeError("write failed")

    with pytest.raises(RuntimeError, match="write failed"):
        write_gpkg_atomic(BrokenFrame(), output_path, "layer")

    assert output_path.read_bytes() == b"previous"
    assert not (tmp_path / "out.tmp.gpkg").exists()


def test_final_spatial_validation_accepts_valid_product():
    iieg = _boundary(_square(0, 0, 1, 1))
    inegi = _boundary(_square(0, 0, 1, 1))
    mask, _ = build_canonical_mask(iieg, inegi)
    gdf = gpd.GeoDataFrame(
        pd.DataFrame({"source_objectid": [1]}),
        geometry=[MultiPolygon([_square(0, 0, 1, 1)])],
        crs=f"EPSG:{CANONICAL_SRID}",
    )

    result = final_spatial_validation(gdf, mask, iieg.geometry.union_all(), inegi.geometry.union_all())

    assert result["crs"] == CANONICAL_SRID
    assert result["geometry_types"] == ["MultiPolygon"]


def test_transform_import_does_not_require_network_or_database(monkeypatch):
    def fail(*args, **kwargs):
        raise AssertionError("network or database access is not allowed")

    monkeypatch.setattr("requests.get", fail)
    monkeypatch.setenv("SOURCE_URL", "https://example.test/source.zip")
    monkeypatch.setenv("CVEGEO_DB_USER", "user")
    monkeypatch.setenv("CVEGEO_DB_PASSWORD", "secret")
    monkeypatch.setenv("CVEGEO_DB_HOST", "localhost")
    monkeypatch.setenv("CVEGEO_DB_PORT", "5433")
    monkeypatch.setenv("CVEGEO_DB_NAME", "cvegeo")
    sys.modules.pop("core.pipelines.edafologia.stages.transform", None)

    from core.pipelines.edafologia.stages.transform import EdafologiaTransform

    assert EdafologiaTransform.__name__ == "EdafologiaTransform"
