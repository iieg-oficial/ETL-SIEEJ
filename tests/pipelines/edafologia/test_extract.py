from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pytest
import requests

from core.pipelines.edafologia.helpers.archive import safe_extract_zip
from core.pipelines.edafologia.helpers.download import prepare_source_zip, sha256_file, validate_zip
from core.pipelines.edafologia.helpers.inventory import select_canonical_candidate


def _zip_bytes(files: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name, data in files.items():
            archive.writestr(name, data)
    return buffer.getvalue()


def _write_zip(path: Path, files: dict[str, bytes]) -> Path:
    path.write_bytes(_zip_bytes(files))
    return path


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
