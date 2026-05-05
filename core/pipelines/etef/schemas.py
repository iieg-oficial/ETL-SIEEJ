from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Index, Numeric, String, TIMESTAMP, UniqueConstraint, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func

from core.pipelines.etef.attributes import EtefTables as T


class EtefBase(DeclarativeBase):
    @classmethod
    def columns(cls) -> list[str]:
        return [c.key for c in cls.__table__.columns]


# ----- Catálogos -----


class CatCodigoScian(EtefBase):
    __tablename__ = T.STG_ETEF_CAT_CODIGO_SCIAN
    __table_args__ = (UniqueConstraint("codigo", name="uq_etef_cat_codigo_scian_codigo"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String(10))
    descripcion: Mapped[Optional[str]] = mapped_column(String(255))


# ----- Tabla principal -----


class EtefDatos(EtefBase):
    __tablename__ = T.STG_ETEF_DATOS
    __table_args__ = (
        # Índice parcial de unicidad: solo la versión activa por llave natural (SCD2)
        Index(
            "uq_etef_datos_llave_activa",
            "anio",
            "trimestre",
            "cve_ent",
            "codigo_scian_id",
            unique=True,
            postgresql_where=text("is_current = TRUE"),
        ),
        Index("ix_etef_datos_anio_trimestre", "anio", "trimestre"),
        Index("ix_etef_datos_cve_ent", "cve_ent"),
        Index("ix_etef_datos_codigo_scian_id", "codigo_scian_id"),
        Index("ix_etef_datos_is_current", "is_current"),
        Index("ix_etef_datos_row_hash", "row_hash"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    anio: Mapped[int]
    trimestre: Mapped[str] = mapped_column(String(2))
    mes: Mapped[str] = mapped_column(String(5))
    prod_est: Mapped[Optional[str]] = mapped_column(String(150))
    cobertura: Mapped[Optional[str]] = mapped_column(String(50))
    cve_ent: Mapped[int]
    codigo_scian_id: Mapped[int]
    val_usd: Mapped[Optional[float]] = mapped_column(Numeric(15, 2))
    estatus_cifra: Mapped[Optional[str]] = mapped_column(String(20))
    estatus: Mapped[Optional[str]] = mapped_column(String(30))
    # SCD2
    row_hash: Mapped[str] = mapped_column(String(64), server_default=text("''"))
    valid_from: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    valid_to: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))
    is_current: Mapped[bool] = mapped_column(Boolean, server_default=text("TRUE"))
    # Auditoría
    created_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())


# Registro de catálogos para iteración dinámica en load.py
CATALOG_MODELS: dict[str, type] = {
    "codigo_scian": CatCodigoScian,
}
