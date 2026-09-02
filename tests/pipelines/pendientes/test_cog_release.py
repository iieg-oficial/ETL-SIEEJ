import errno
from pathlib import Path

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

from core.pipelines.pendientes.constants import DEGREES_CLASSIFICATION
from core.pipelines.pendientes.helpers.classification import classify_values, create_classified_raster
from core.pipelines.pendientes.helpers.cog import (
    create_cog,
    inspect_cog_driver,
    validate_cog_structure,
    validate_lossless_cog,
)
from core.pipelines.pendientes.helpers.release import materialize_release_file
from core.utils.files import sha256_file


def _continuous_raster(path: Path, size: int = 1024) -> None:
    values = np.arange(size * size, dtype=np.float32).reshape(size, size) / 1000.0
    values[:20, :30] = -9999.0
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        width=size,
        height=size,
        count=1,
        dtype="float32",
        crs="EPSG:6368",
        transform=from_origin(600_000, 2_400_000, 15, 15),
        nodata=-9999.0,
        tiled=True,
        blockxsize=256,
        blockysize=256,
    ) as dataset:
        dataset.write(values, 1)
        dataset.set_band_unit(1, "degree")


def test_cog_driver_options_are_supported_by_installed_gdal() -> None:
    report = inspect_cog_driver()
    assert report["driver"] == "COG"
    assert "BLOCKSIZE" in report["creation_options_supported"]
    assert "OVERVIEW_RESAMPLING" in report["creation_options_supported"]


def test_continuous_and_classified_cogs_are_lossless(tmp_path: Path) -> None:
    continuous = tmp_path / "continuous.tif"
    continuous_cog = tmp_path / "continuous_cog.tif"
    classified = tmp_path / "classified.tif"
    classified_cog = tmp_path / "classified_cog.tif"
    _continuous_raster(continuous)

    create_cog(continuous, continuous_cog, classified=False)
    continuous_qa = validate_lossless_cog(continuous, continuous_cog, classified=False, processing_window_size=256)
    assert continuous_qa["hard_gates"]["all_passed"]
    assert continuous_qa["compression"] == "DEFLATE"
    assert continuous_qa["overview_resampling"] == "AVERAGE"

    class_qa = create_classified_raster(
        continuous, classified, DEGREES_CLASSIFICATION, "test", processing_window_size=256
    )
    assert class_qa["hard_gates"]["all_passed"]
    create_cog(classified, classified_cog, classified=True)
    packaged_qa = validate_lossless_cog(classified, classified_cog, classified=True, processing_window_size=256)
    assert packaged_qa["hard_gates"]["all_passed"]
    assert packaged_qa["overview_resampling"] == "MODE"
    with rasterio.open(classified_cog) as dataset:
        assert dataset.dtypes == ("uint8",)
        assert dataset.nodata == 255
        valid = dataset.read(1) != 255
        assert not np.any(dataset.read(1)[valid] == 0)


def test_thresholds_are_lower_inclusive_and_upper_exclusive() -> None:
    values = np.asarray([0, 1.999999, 2, 4.999999, 5, 10, 15, 25, 50], dtype=np.float64)
    assert classify_values(values, DEGREES_CLASSIFICATION).tolist() == [1, 1, 2, 2, 3, 4, 5, 6, 7]


def test_release_materializes_same_cog_without_conversion(tmp_path: Path) -> None:
    source = tmp_path / "source.tif"
    cog = tmp_path / "source_cog.tif"
    release = tmp_path / "release" / "source_cog.tif"
    _continuous_raster(source)
    create_cog(source, cog, classified=False)
    checksum = sha256_file(cog)

    report = materialize_release_file(cog, release, checksum)
    assert report["strategy"] in {"hardlink_atomic", "copy_atomic"}
    assert sha256_file(release) == checksum
    assert validate_cog_structure(release)["layout"] == "COG"
    assert materialize_release_file(cog, release, checksum)["strategy"] == "existing_validated"


def test_release_falls_back_to_atomic_copy_and_rejects_corrupt_destination(tmp_path: Path, monkeypatch) -> None:
    source = tmp_path / "source.tif"
    cog = tmp_path / "source_cog.tif"
    release = tmp_path / "release" / "source_cog.tif"
    _continuous_raster(source)
    create_cog(source, cog, classified=False)
    checksum = sha256_file(cog)

    def cross_device_link(*args, **kwargs):
        raise OSError(errno.EXDEV, "different filesystem")

    monkeypatch.setattr("core.pipelines.pendientes.helpers.release.os.link", cross_device_link)
    assert materialize_release_file(cog, release, checksum)["strategy"] == "copy_atomic"
    release.write_bytes(b"corrupt release")
    with pytest.raises(ValueError, match="corrupt or incompatible"):
        materialize_release_file(cog, release, checksum)


def test_corrupt_cog_is_rejected(tmp_path: Path) -> None:
    corrupt = tmp_path / "corrupt.tif"
    corrupt.write_bytes(b"not-a-raster")
    with pytest.raises(ValueError, match="Invalid or corrupt COG"):
        validate_cog_structure(corrupt)
