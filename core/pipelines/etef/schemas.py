from datetime import datetime
from typing import Optional

from sqlalchemy import Index, String, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class EtefBase(DeclarativeBase):
    pass


# ----- Catálogos -----


class CatCodigoScian(EtefBase):
    __tablename__ = "stg_etef_cat_codigo_scian"
    __table_args__ = (
        UniqueConstraint("codigo", name="uq_etef_cat_codigo_scian_codigo"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String(3), unique=True)
    descripcion: Mapped[Optional[str]] = mapped_column(String(255))
    version: Mapped[Optional[str]] = mapped_column(String(10))


# ----- Tabla principal -----


class EtefDatos(EtefBase):
    __tablename__ = "stg_etef_datos"
    __table_args__ = (
        UniqueConstraint(
            "anio", "trimestre", "cve_ent", "codigo_scian_id",
            name="uq_etef_datos_llave"
        ),
        Index("ix_etef_datos_anio_trimestre", "anio", "trimestre"),
        Index("ix_etef_datos_cve_ent", "cve_ent"),
        Index("ix_etef_datos_codigo_scian_id", "codigo_scian_id"),
        Index("ix_etef_datos_llave", "anio", "trimestre", "cve_ent", "codigo_scian_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    anio: Mapped[int]
    trimestre: Mapped[str] = mapped_column(String(2))
    mes: Mapped[str] = mapped_column(String(5))
    cve_ent: Mapped[int]
    codigo_scian_id: Mapped[int]
    val_usd: Mapped[Optional[float]]
    estatus_cifra: Mapped[Optional[str]] = mapped_column(String(20))
    estatus: Mapped[Optional[str]] = mapped_column(String(30))
    created_at: Mapped[Optional[datetime]] = mapped_column(server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(server_default=func.now(), onupdate=func.now())


# Registro de catálogos para iteración dinámica en load.py
CATALOG_MODELS: dict[str, type] = {
    "codigo_scian": CatCodigoScian,
}
