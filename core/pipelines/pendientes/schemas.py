from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from typing import Any

from sqlalchemy import Date, Float, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from core.pipelines.pendientes.attributes import PendientesTables as T


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


class PendientesBase(DeclarativeBase):
    @classmethod
    def columns(cls) -> list[str]:
        return [column.key for column in cls.__table__.columns]


class FuentesLimitesMunicipales(PendientesBase):
    __tablename__ = T.FUENTES_LIMITES_MUNICIPALES

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    clave: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    nombre_fuente: Mapped[str] = mapped_column(String(120), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[str] = mapped_column(String(120), nullable=False)
    procedencia: Mapped[str] = mapped_column(Text, nullable=False)


class EstadisticasPendienteMunicipales(PendientesBase):
    __tablename__ = T.ESTADISTICAS_PENDIENTE_MUNICIPALES
    __table_args__ = (
        UniqueConstraint(
            "municipality_id",
            "fuente_limite_municipal_id",
            name="uq_estadisticas_pendiente_municipio_fuente",
        ),
        Index("idx_estadisticas_pendiente_municipality_id", "municipality_id"),
        Index("idx_estadisticas_pendiente_fuente", "fuente_limite_municipal_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    municipality_id: Mapped[int] = mapped_column(Integer, nullable=False)
    cve_mun: Mapped[int] = mapped_column(Integer, nullable=False)
    cve_ent: Mapped[int] = mapped_column(Integer, nullable=False)
    cvegeo: Mapped[str] = mapped_column(String(5), nullable=False)
    municipio: Mapped[str] = mapped_column(String(160), nullable=False)
    fuente_limite_municipal_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(f"{T.FUENTES_LIMITES_MUNICIPALES}.id"),
        nullable=False,
    )
    elevation_min_m: Mapped[float] = mapped_column(Float, nullable=False)
    elevation_max_m: Mapped[float] = mapped_column(Float, nullable=False)
    elevation_mean_m: Mapped[float] = mapped_column(Float, nullable=False)
    elevation_median_m: Mapped[float] = mapped_column(Float, nullable=False)
    elevation_std_m: Mapped[float] = mapped_column(Float, nullable=False)
    elevation_p05_m: Mapped[float] = mapped_column(Float, nullable=False)
    elevation_p95_m: Mapped[float] = mapped_column(Float, nullable=False)
    slope_degrees_min: Mapped[float] = mapped_column(Float, nullable=False)
    slope_degrees_max: Mapped[float] = mapped_column(Float, nullable=False)
    slope_degrees_mean: Mapped[float] = mapped_column(Float, nullable=False)
    slope_degrees_median: Mapped[float] = mapped_column(Float, nullable=False)
    slope_degrees_std: Mapped[float] = mapped_column(Float, nullable=False)
    slope_degrees_p05: Mapped[float] = mapped_column(Float, nullable=False)
    slope_degrees_p95: Mapped[float] = mapped_column(Float, nullable=False)
    slope_percent_mean: Mapped[float] = mapped_column(Float, nullable=False)
    slope_percent_median: Mapped[float] = mapped_column(Float, nullable=False)
    slope_percent_p95: Mapped[float] = mapped_column(Float, nullable=False)
    slope_percent_max: Mapped[float] = mapped_column(Float, nullable=False)
    valid_pixel_count: Mapped[int] = mapped_column(Integer, nullable=False)
    valid_area_ha: Mapped[float] = mapped_column(Float, nullable=False)
    coverage_percent: Mapped[float] = mapped_column(Float, nullable=False)
    fecha_actualizacion: Mapped[date] = mapped_column(Date, nullable=False)
