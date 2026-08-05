from __future__ import annotations

import io
import importlib
import json
import os
import sys
import zipfile
from pathlib import Path

import geopandas as gpd
import pandas as pd
import pyogrio
import pytest
import requests
from shapely.geometry import MultiPolygon, Polygon

from core.pipelines.edafologia.constants import (
    CONTROLLED_CATALOG_VERSION,
    EDAFOLOGIA_RESUMENES_MUNICIPALES_VIEW_COLUMNS,
)
from core.pipelines.edafologia.helpers.boundaries import (
    prepare_municipal_boundaries,
    validate_boundary_layer,
    write_boundary_layers_atomic,
)
from core.pipelines.edafologia.helpers.download import prepare_source_zip
from core.utils.files import safe_extract_zip, sha256_file, validate_zip
from core.pipelines.edafologia.helpers.inventory import select_canonical_candidate
from core.pipelines.edafologia.mappings import (
    CALIFICADORES_EDAFOLOGICOS,
    GRUPOS_EDAFOLOGICOS,
    catalog_manifest,
    catalog_sha256,
)
from core.pipelines.edafologia import schemas


def _zip_bytes(files: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name, data in files.items():
            archive.writestr(name, data)
    return buffer.getvalue()


def _write_zip(path: Path, files: dict[str, bytes]) -> Path:
    path.write_bytes(_zip_bytes(files))
    return path


def _municipal_boundaries(count: int = 125, srid: int = 6368) -> gpd.GeoDataFrame:
    rows = []
    geometries = []
    for idx in range(count):
        x = float(idx)
        polygon = Polygon([(x, 0.0), (x + 0.5, 0.0), (x + 0.5, 0.5), (x, 0.5), (x, 0.0)])
        rows.append(
            {
                "cvegeo": f"14{idx + 1:03d}",
                "cve_ent": "14",
                "cve_mun": f"{idx + 1:03d}",
                "nomgeo": f"Municipio {idx + 1}",
                "nom_ent": "Jalisco",
            }
        )
        geometries.append(MultiPolygon([polygon]))
    return gpd.GeoDataFrame(pd.DataFrame(rows), geometry=geometries, crs=f"EPSG:{srid}")


def _candidate(
    relative_path: str,
    layer: str,
    geometry_type: str,
    fields: list[str],
) -> dict[str, object]:
    return {
        "relative_path": relative_path,
        "layer": layer,
        "format": "ESRI Shapefile",
        "readable": True,
        "geometry_type": geometry_type,
        "crs": "ITRF_1992_Lambert_Conformal_Conic",
        "feature_count": 1,
        "fields": fields,
        "required_fields_found": fields,
        "required_fields_missing": [],
        "extent": [0.0, 0.0, 1.0, 1.0],
    }


class DownloadResponse:
    def __init__(self, status_code: int, headers: dict[str, str], chunks: list[bytes], error: Exception | None = None):
        self.status_code = status_code
        self.headers = headers
        self.chunks = chunks
        self.error = error

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def raise_for_status(self) -> None:
        if self.error:
            raise self.error

    def iter_content(self, chunk_size: int):
        yield from self.chunks


def test_safe_extract_zip_rejects_path_traversal(tmp_path):
    zip_path = tmp_path / "source.zip"
    _write_zip(zip_path, {"../escape.txt": b"bad"})

    with pytest.raises(ValueError, match="Unsafe ZIP member path"):
        safe_extract_zip(zip_path, tmp_path / "extract")

    assert not (tmp_path / "escape.txt").exists()


def test_select_canonical_candidate_prefers_area_over_point():
    required = ("Grupo1", "Califp_g1", "Califs_g1")
    point = _candidate(
        "conj_nac_inf_edaf_esc_250k_ser_III_pto.shp",
        "conj_nac_inf_edaf_esc_250k_ser_III_pto",
        "Point",
        list(required),
    )
    area = _candidate(
        "conj_nac_inf_edaf_esc_250k_ser_III_area.shp",
        "conj_nac_inf_edaf_esc_250k_ser_III_area",
        "Polygon",
        list(required),
    )

    selected = select_canonical_candidate([point, area], required)

    assert selected["relative_path"] == "conj_nac_inf_edaf_esc_250k_ser_III_area.shp"


def test_select_canonical_candidate_errors_when_required_fields_are_missing():
    required = ("Grupo1", "Califp_g1", "Califs_g1")
    candidate = _candidate(
        "conj_nac_inf_edaf_esc_250k_ser_III_area.shp",
        "conj_nac_inf_edaf_esc_250k_ser_III_area",
        "Polygon",
        ["Grupo1", "Califp_g1"],
    )

    with pytest.raises(ValueError, match="No canonical Edafologia polygon layer found"):
        select_canonical_candidate([candidate], required)


def test_select_canonical_candidate_errors_on_ambiguous_layers():
    required = ("Grupo1", "Califp_g1", "Califs_g1")
    candidates = [
        _candidate(
            "a/conj_nac_inf_edaf_esc_250k_ser_III_area.shp",
            "conj_nac_inf_edaf_esc_250k_ser_III_area",
            "Polygon",
            list(required),
        ),
        _candidate(
            "b/conj_nac_inf_edaf_esc_250k_ser_III_area.shp",
            "conj_nac_inf_edaf_esc_250k_ser_III_area",
            "Polygon",
            list(required),
        ),
    ]

    with pytest.raises(ValueError, match="Ambiguous canonical Edafologia layers"):
        select_canonical_candidate(candidates, required)


def test_prepare_source_zip_reuses_valid_existing_zip(tmp_path):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    zip_path = _write_zip(raw_dir / "source.zip", {"readme.txt": b"ok"})

    result = prepare_source_zip(
        source_url="https://example.test/source.zip",
        raw_dir=raw_dir,
        source_zip_path=None,
        force_download=False,
        retries=1,
        connect_timeout=1,
        read_timeout=1,
    )

    assert result["downloaded_this_run"] is False
    assert result["zip_path"] == str(zip_path)
    assert result["source_file_sha256"] == sha256_file(zip_path)


def test_sha256_file_is_stable(tmp_path):
    path = tmp_path / "sample.bin"
    path.write_bytes(b"edafologia")

    assert sha256_file(path) == sha256_file(path)
    assert sha256_file(path) == "0037667ab939dde42e6f0afd1797e652a203acebb8f0ece23826985151e9f072"


def test_download_restarts_when_server_ignores_range(tmp_path, monkeypatch):
    payload = _zip_bytes({"readme.txt": b"complete"})
    temporary = tmp_path / "source.zip.part"
    temporary.write_bytes(payload[:8])
    received_headers = []

    def fake_get(*args, **kwargs):
        received_headers.append(kwargs["headers"])
        return DownloadResponse(200, {"Content-Length": str(len(payload))}, [payload])

    monkeypatch.setattr("core.pipelines.edafologia.helpers.download.requests.get", fake_get)

    result = prepare_source_zip(
        source_url="https://example.test/source.zip",
        raw_dir=tmp_path,
        source_zip_path=None,
        force_download=False,
        retries=1,
        connect_timeout=1,
        read_timeout=1,
    )

    assert (tmp_path / "source.zip").read_bytes() == payload
    assert not temporary.exists()
    assert received_headers == [{"Range": "bytes=8-"}]
    assert result["downloaded_this_run"] is True


def test_validate_zip_rejects_corrupt_zip(tmp_path):
    zip_path = tmp_path / "source.zip"
    zip_path.write_bytes(b"not a zip")

    with pytest.raises(ValueError, match="valid ZIP"):
        validate_zip(zip_path)


def test_download_raises_after_http_failure(tmp_path, monkeypatch):
    def fake_get(*args, **kwargs):
        return DownloadResponse(500, {}, [], requests.HTTPError("server error"))

    monkeypatch.setattr("core.pipelines.edafologia.helpers.download.requests.get", fake_get)

    with pytest.raises(RuntimeError, match="Download failed"):
        prepare_source_zip(
            source_url="https://example.test/source.zip",
            raw_dir=tmp_path,
            source_zip_path=None,
            force_download=False,
            retries=1,
            connect_timeout=1,
            read_timeout=1,
        )


def test_boundary_validation_accepts_125_unique_multipolygons():
    result = validate_boundary_layer(_municipal_boundaries(), "geom_iieg", gist_index_present=True)

    assert result["count"] == 125
    assert result["unique_cvegeo"] == 125
    assert result["srid"] == 6368
    assert result["geometry_type"] == "MultiPolygon"


def test_boundary_validation_rejects_duplicate_cvegeo():
    gdf = _municipal_boundaries()
    gdf.loc[1, "cvegeo"] = gdf.loc[0, "cvegeo"]

    with pytest.raises(ValueError, match="unique_cvegeo"):
        validate_boundary_layer(gdf, "geom_iieg", gist_index_present=True)


def test_boundary_validation_rejects_wrong_srid():
    with pytest.raises(ValueError, match="srid"):
        validate_boundary_layer(_municipal_boundaries(srid=6372), "geom_iieg", gist_index_present=True)


def test_boundary_validation_rejects_null_geometry():
    gdf = _municipal_boundaries()
    gdf.loc[0, "geometry"] = None

    with pytest.raises(ValueError, match="null_geometries"):
        validate_boundary_layer(gdf, "geom_iieg", gist_index_present=True)


def test_boundary_validation_rejects_invalid_geometry():
    gdf = _municipal_boundaries()
    invalid_polygon = Polygon([(0, 0), (1, 1), (1, 0), (0, 1), (0, 0)])
    gdf.loc[0, "geometry"] = MultiPolygon([invalid_polygon])

    with pytest.raises(ValueError, match="invalid_geometries"):
        validate_boundary_layer(gdf, "geom_iieg", gist_index_present=True)


def test_write_boundary_layers_atomic_writes_two_distinct_layers(tmp_path):
    output_path = tmp_path / "municipal_boundaries.gpkg"

    write_boundary_layers_atomic(
        {
            "municipios_iieg": _municipal_boundaries(),
            "municipios_inegi": _municipal_boundaries(),
        },
        output_path,
    )

    iieg = gpd.read_file(output_path, layer="municipios_iieg")
    inegi = gpd.read_file(output_path, layer="municipios_inegi")
    assert len(iieg) == 125
    assert len(inegi) == 125
    assert iieg.geometry.name == "geometry"
    assert inegi.geometry.name == "geometry"


def test_write_boundary_layers_atomic_preserves_previous_file_on_failure(tmp_path):
    output_path = tmp_path / "municipal_boundaries.gpkg"
    output_path.write_bytes(b"previous")

    class FakeLayer:
        def __init__(self, fail: bool = False):
            self.fail = fail

        def to_file(self, path, layer, driver):
            Path(path).write_bytes(b"partial")
            if self.fail:
                raise RuntimeError("write failed")

    with pytest.raises(RuntimeError, match="write failed"):
        write_boundary_layers_atomic({"municipios_iieg": FakeLayer(), "municipios_inegi": FakeLayer(True)}, output_path)

    assert output_path.read_bytes() == b"previous"
    assert not (tmp_path / "municipal_boundaries.tmp.gpkg").exists()


def test_versioned_catalog_counts_are_exact():
    assert len(GRUPOS_EDAFOLOGICOS) == 24
    assert len(CALIFICADORES_EDAFOLOGICOS) == 87


@pytest.mark.parametrize(
    "mapping",
    [GRUPOS_EDAFOLOGICOS, CALIFICADORES_EDAFOLOGICOS],
)
def test_versioned_catalog_keys_are_unique_and_non_empty(mapping):
    assert len(mapping) == len(set(mapping))
    assert all(key != "" for key in mapping)
    assert all(description != "" for description in mapping.values())


def test_versioned_catalog_hash_is_deterministic():
    reversed_mapping = dict(reversed(list(GRUPOS_EDAFOLOGICOS.items())))
    reversed_qualifiers = dict(reversed(list(CALIFICADORES_EDAFOLOGICOS.items())))

    assert catalog_sha256(GRUPOS_EDAFOLOGICOS) == catalog_sha256(reversed_mapping)
    assert catalog_sha256(GRUPOS_EDAFOLOGICOS) == "7a4d3930bc05f59d74a2cdb20c85c41b31a166db044cb3e7668512dc24be7192"
    assert catalog_sha256(CALIFICADORES_EDAFOLOGICOS) == catalog_sha256(reversed_qualifiers)
    assert (
        catalog_sha256(CALIFICADORES_EDAFOLOGICOS) == "df479e0c8d93437717dee301e7158cf16863209f257063b862f851391019917c"
    )


def test_qualifier_catalog_resolves_fl_as_ferralico():
    assert CALIFICADORES_EDAFOLOGICOS["fl"] == "Ferrálico"


def test_qualifier_roles_reference_same_sqlalchemy_model():
    edafologias_columns = schemas.Edafologias.__table__.columns

    assert "calificador_primario_id" in edafologias_columns
    assert "calificador_secundario_id" in edafologias_columns
    assert "calificador_primario_edafologico_id" not in edafologias_columns
    assert "calificador_secundario_edafologico_id" not in edafologias_columns
    assert next(iter(edafologias_columns["calificador_primario_id"].foreign_keys)).target_fullname == (
        "calificadores_edafologicos.id"
    )
    assert next(iter(edafologias_columns["calificador_secundario_id"].foreign_keys)).target_fullname == (
        "calificadores_edafologicos.id"
    )
    assert "calificador_primario_id" in EDAFOLOGIA_RESUMENES_MUNICIPALES_VIEW_COLUMNS
    assert "calificador_secundario_id" in EDAFOLOGIA_RESUMENES_MUNICIPALES_VIEW_COLUMNS
    assert not hasattr(schemas, "EdafologiaResumenesMunicipales")


def test_separate_qualifier_catalog_models_no_longer_exist():
    assert hasattr(schemas, "CalificadoresEdafologicos")
    assert not hasattr(schemas, "CalificadoresPrimariosEdafologicos")
    assert not hasattr(schemas, "CalificadoresSecundariosEdafologicos")


def test_controlled_catalog_manifest_has_no_local_csv_paths():
    manifest = {
        "grupo1": catalog_manifest(GRUPOS_EDAFOLOGICOS, CONTROLLED_CATALOG_VERSION),
        "calificadores": catalog_manifest(CALIFICADORES_EDAFOLOGICOS, CONTROLLED_CATALOG_VERSION),
    }
    serialized = json.dumps(manifest, ensure_ascii=False)

    assert "versioned_mapping" in serialized
    assert "/home/serviciosocial" not in serialized
    assert ".csv" not in serialized


def test_extract_imports_without_dictionary_path_env(monkeypatch):
    for variable in ("GRUPO1_DICTIONARY_PATH", "CALIFP_G1_DICTIONARY_PATH", "CALIFS_G1_DICTIONARY_PATH"):
        monkeypatch.delenv(variable, raising=False)
    monkeypatch.setenv("SOURCE_URL", "https://example.test/source.zip")
    monkeypatch.setenv("CVEGEO_DB_USER", "user")
    monkeypatch.setenv("CVEGEO_DB_PASSWORD", "secret")
    monkeypatch.setenv("CVEGEO_DB_HOST", "localhost")
    monkeypatch.setenv("CVEGEO_DB_PORT", "5433")
    monkeypatch.setenv("CVEGEO_DB_NAME", "cvegeo")
    sys.modules.pop("core.pipelines.edafologia.config", None)
    sys.modules.pop("core.pipelines.edafologia.stages.extract", None)

    module = importlib.import_module("core.pipelines.edafologia.stages.extract")

    assert module.EdafologiaExtract.__name__ == "EdafologiaExtract"


def test_versioned_catalogs_cover_observed_jalisco_values():
    observed_gpkg = Path(
        os.getenv(
            "EDAFOLOGIA_OBSERVED_JALISCO_GPKG",
            "/home/serviciosocial/iieg_2026/06_cuadernillos/Insumos/capas/edafologia/edafologiav1.gpkg",
        )
    )
    if not observed_gpkg.exists():
        pytest.skip("Observed Jalisco Edafologia GPKG is not available locally")

    frame = pyogrio.read_dataframe(
        observed_gpkg,
        layer="edafologiav1",
        columns=["Grupo1", "Califp_g1", "Califs_g1"],
    )

    missing = {
        "Grupo1": sorted(set(frame["Grupo1"].dropna().astype(str)) - set(GRUPOS_EDAFOLOGICOS)),
        "Califp_g1": sorted(set(frame["Califp_g1"].dropna().astype(str)) - set(CALIFICADORES_EDAFOLOGICOS)),
        "Califs_g1": sorted(set(frame["Califs_g1"].dropna().astype(str)) - set(CALIFICADORES_EDAFOLOGICOS)),
    }

    assert missing == {"Grupo1": [], "Califp_g1": [], "Califs_g1": []}


def test_auxiliary_manifest_has_no_credentials():
    manifest = {
        "auxiliary_inputs": {
            "municipal_boundaries": {
                "database": "cvegeo",
                "table": "public.cvegeo_municipalities",
                "entity_filter": "cve_ent = 14",
            }
        }
    }

    serialized = json.dumps(manifest)

    assert "not_a_password" not in serialized
    assert "CVEGEO_DB_PASSWORD" not in serialized


@pytest.mark.integration
def test_prepare_municipal_boundaries_against_local_cvegeo(tmp_path):
    required = ["CVEGEO_DB_USER", "CVEGEO_DB_PASSWORD", "CVEGEO_DB_HOST", "CVEGEO_DB_PORT", "CVEGEO_DB_NAME"]
    if any(not os.getenv(name) for name in required):
        pytest.skip("CVEGEO_DB_* variables are required for cvegeo integration test")

    database_url = (
        f"postgresql://{os.environ['CVEGEO_DB_USER']}:{os.environ['CVEGEO_DB_PASSWORD']}"
        f"@{os.environ['CVEGEO_DB_HOST']}:{os.environ['CVEGEO_DB_PORT']}/{os.environ['CVEGEO_DB_NAME']}"
    )
    try:
        manifest = prepare_municipal_boundaries(
            database_url=database_url,
            database_name=os.environ["CVEGEO_DB_NAME"],
            output_path=tmp_path / "municipal_boundaries.gpkg",
            boundary_sources={
                "iieg": {
                    "layer": "municipios_iieg",
                    "geometry_column": "geom_iieg",
                    "expected_gist_index": "idx_cvegeo_mun_geom_iieg",
                },
                "inegi": {
                    "layer": "municipios_inegi",
                    "geometry_column": "geom_inegi",
                    "expected_gist_index": "idx_cvegeo_mun_geom_inegi",
                },
            },
            previous_manifest=None,
            force=True,
        )
    except ConnectionError as exc:
        pytest.skip(str(exc))

    assert manifest["database"] == os.environ["CVEGEO_DB_NAME"]
    assert set(manifest["layers"]) == {"municipios_iieg", "municipios_inegi"}
    assert manifest["layers"]["municipios_iieg"]["count"] == 125
    assert manifest["layers"]["municipios_inegi"]["count"] == 125
