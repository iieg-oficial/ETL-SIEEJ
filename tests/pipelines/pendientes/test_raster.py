from __future__ import annotations

import zipfile
from pathlib import Path

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

from core.pipelines.pendientes.helpers.download import extract_tiff_member, identify_tiff_member
from core.pipelines.pendientes.helpers.raster import (
    inspect_raster,
    reproject_dem,
    validate_analytic_grid,
    validate_source_contract,
)

SOURCE_RESOLUTION = 1 / 7200


def _write_raster(
    path: Path,
    values: np.ndarray,
    crs: str | None = "EPSG:6368",
    resolution: float = 15,
    nodata: float = -9999,
    unit: str | None = "metre",
) -> Path:
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        width=values.shape[1],
        height=values.shape[0],
        count=1,
        dtype=values.dtype,
        crs=crs,
        transform=from_origin(0, values.shape[0] * resolution, resolution, resolution),
        nodata=nodata,
    ) as dataset:
        dataset.write(values, 1)
        if unit is not None:
            dataset.set_band_unit(1, unit)
    return path


def _validate_real_source(path: Path) -> None:
    validate_source_contract(
        inspect_raster(path),
        expected_bands=1,
        allowed_srids=(6365,),
        expected_dtype="Int16",
        expected_nodata=32767,
        expected_pixel_size=SOURCE_RESOLUTION,
        pixel_size_tolerance=1e-10,
    )


def test_inspect_raster_reports_real_metadata_and_statistics(tmp_path):
    path = _write_raster(tmp_path / "dem.tif", np.arange(9, dtype=np.float32).reshape(3, 3))
    metadata = inspect_raster(path)
    assert metadata.epsg == 6368
    assert metadata.pixel_size == (15.0, 15.0)
    assert metadata.extent == (0.0, 0.0, 45.0, 45.0)
    assert metadata.data_types == ("Float32",)
    assert metadata.z_units == ("metre",)
    assert metadata.statistics["band_1"]["mean"] == pytest.approx(4.0)


def test_source_contract_rejects_missing_crs(tmp_path):
    path = _write_raster(tmp_path / "dem.tif", np.ones((3, 3), dtype=np.float32), crs=None)
    with pytest.raises(ValueError, match="missing CRS"):
        validate_source_contract(inspect_raster(path))


def test_source_contract_can_restrict_srid_after_real_inspection(tmp_path):
    path = _write_raster(tmp_path / "dem.tif", np.ones((3, 3), dtype=np.float32))
    with pytest.raises(ValueError, match="not in admitted SRIDs"):
        validate_source_contract(inspect_raster(path), allowed_srids=(6365,))


def test_real_source_contract_accepts_epsg6365_half_arcsecond_int16_and_nodata(tmp_path):
    path = _write_raster(
        tmp_path / "cem.tif",
        np.arange(9, dtype=np.int16).reshape(3, 3),
        crs="EPSG:6365",
        resolution=0.000138888889,
        nodata=32767,
        unit=None,
    )
    _validate_real_source(path)


def test_real_source_contract_rejects_unexpected_crs(tmp_path):
    path = _write_raster(
        tmp_path / "cem.tif",
        np.ones((3, 3), dtype=np.int16),
        crs="EPSG:4326",
        resolution=SOURCE_RESOLUTION,
        nodata=32767,
    )
    with pytest.raises(ValueError, match="not in admitted SRIDs"):
        _validate_real_source(path)


def test_real_source_contract_rejects_incompatible_resolution(tmp_path):
    path = _write_raster(
        tmp_path / "cem.tif",
        np.ones((3, 3), dtype=np.int16),
        crs="EPSG:6365",
        resolution=1 / 3600,
        nodata=32767,
    )
    with pytest.raises(ValueError, match="expected pixel size approximately"):
        _validate_real_source(path)


def test_real_source_contract_rejects_unexpected_dtype(tmp_path):
    path = _write_raster(
        tmp_path / "cem.tif",
        np.ones((3, 3), dtype=np.float32),
        crs="EPSG:6365",
        resolution=SOURCE_RESOLUTION,
        nodata=32767,
    )
    with pytest.raises(ValueError, match="expected dtype Int16"):
        _validate_real_source(path)


def test_real_source_contract_rejects_unexpected_nodata(tmp_path):
    path = _write_raster(
        tmp_path / "cem.tif",
        np.ones((3, 3), dtype=np.int16),
        crs="EPSG:6365",
        resolution=SOURCE_RESOLUTION,
        nodata=-9999,
    )
    with pytest.raises(ValueError, match="expected NoData 32767"):
        _validate_real_source(path)


def test_reproject_dem_enforces_epsg_resolution_and_extent(tmp_path):
    source = _write_raster(tmp_path / "source.tif", np.arange(9, dtype=np.float32).reshape(3, 3))
    destination = tmp_path / "analytic.tif"
    bounds = (0.0, 0.0, 45.0, 45.0)
    report = reproject_dem(source, destination, target_srid=6368, resolution=15, aligned_bounds=bounds)
    metadata = inspect_raster(destination)
    validate_analytic_grid(metadata, 6368, 15, bounds)
    assert metadata.data_types == ("Float32",)
    assert metadata.nodata == (-9999.0,)
    assert report["full_source_array_materialized"] is False


def test_reproject_dem_limits_processing_to_required_source_window(tmp_path):
    source = _write_raster(tmp_path / "national.tif", np.ones((100, 100), dtype=np.float32))
    destination = tmp_path / "aoi.tif"
    report = reproject_dem(
        source,
        destination,
        target_srid=6368,
        resolution=15,
        aligned_bounds=(0, 0, 45, 45),
    )
    assert report["source_window"]["cells"] < report["source_dataset_cells"]
    assert report["maximum_materialized_block_cells"] <= 256 * 256


def test_analytic_grid_rejects_wrong_resolution(tmp_path):
    path = _write_raster(tmp_path / "dem.tif", np.ones((3, 3), dtype=np.float32), resolution=30)
    with pytest.raises(ValueError, match="15"):
        validate_analytic_grid(inspect_raster(path), 6368, 15, (0, 0, 90, 90))


def test_zip_inventory_selects_one_tiff_case_insensitively(tmp_path):
    zip_path = tmp_path / "source.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.writestr("nested/CEM.TIFF", b"raster-bytes")
        archive.writestr("metadata.txt", b"metadata")
    member = identify_tiff_member(zip_path)
    assert member.filename == "nested/CEM.TIFF"
    extracted = extract_tiff_member(zip_path, member, tmp_path / "extracted")
    assert extracted.read_bytes() == b"raster-bytes"


def test_zip_inventory_enforces_real_cem_member_path(tmp_path):
    zip_path = tmp_path / "source.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.writestr("other/cem.tif", b"raster")
    with pytest.raises(ValueError, match="does not match the CEM 4.0 contract"):
        identify_tiff_member(zip_path, expected_member="conjunto_de_datos/continuonacional_15m.tif")


def test_zip_inventory_rejects_ambiguous_tiffs(tmp_path):
    zip_path = tmp_path / "source.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.writestr("a.tif", b"a")
        archive.writestr("b.tif", b"b")
    with pytest.raises(ValueError, match="ambiguous"):
        identify_tiff_member(zip_path)
