from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class RasterMetadata:
    path: str
    driver: str
    crs_wkt: str
    epsg: int | None
    pixel_size: tuple[float, float]
    extent: tuple[float, float, float, float]
    width: int
    height: int
    band_count: int
    data_types: tuple[str, ...]
    nodata: tuple[float | None, ...]
    z_units: tuple[str | None, ...]
    compression: str | None
    block_shapes: tuple[tuple[int, int], ...]
    tiled: bool
    statistics: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ProcessingGrid:
    crs_epsg: int
    resolution_m: float
    bounds: tuple[float, float, float, float]
    width: int
    height: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RasterProduct:
    name: str
    path: str
    unit: str
    dtype: str
    crs_epsg: int
    resolution_m: float
    clipped_to: str
    parent_product: str | None
    parent_sha256: str | None
    conditioning_method: str | None = None
    conditioning_parameters: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
