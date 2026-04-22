from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, ForeignKey, Index, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class EfipemBase(DeclarativeBase):
    pass


# Catalogos


class CatTrimestre(EfipemBase):
    __tablename__ = "stg_efipem_cat_trimestre"
    __table_args__ = (UniqueConstraint("name", name="uq_efipem_cat_trimestre_name"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(10), unique=True)


class CatTema(EfipemBase):
    __tablename__ = "stg_efipem_cat_tema"
    __table_args__ = (UniqueConstraint("name", name="uq_efipem_cat_tema_name"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)


class CatClasificador(EfipemBase):
    __tablename__ = "stg_efipem_cat_clasificador"
    __table_args__ = (UniqueConstraint("name", name="uq_efipem_cat_clasificador_name"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), unique=True)


class CatConcepto(EfipemBase):
    __tablename__ = "stg_efipem_cat_concepto"
    __table_args__ = (
        UniqueConstraint("clasificador_id", "name", name="uq_efipem_cat_concepto_clasif_name"),
        Index("ix_efipem_cat_concepto_clasificador", "clasificador_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    clasificador_id: Mapped[int] = mapped_column(ForeignKey("stg_efipem_cat_clasificador.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255))


class CatEstatus(EfipemBase):
    __tablename__ = "stg_efipem_cat_estatus"
    __table_args__ = (UniqueConstraint("name", name="uq_efipem_cat_estatus_name"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)


# Tabla principal


class FinanzasTrimestral(EfipemBase):
    __tablename__ = "stg_efipem_finanzas_trimestral"
    __table_args__ = (
        UniqueConstraint(
            "anio",
            "trimestre_id",
            "cve_ent",
            "tema_id",
            "clasificador_id",
            "concepto_id",
            name="uq_efipem_finanzas_trimestral_key",
        ),
        Index("ix_efipem_finanzas_trimestral_anio_trim", "anio", "trimestre_id"),
        Index("ix_efipem_finanzas_trimestral_cve_ent", "cve_ent"),
        Index("ix_efipem_finanzas_trimestral_tema", "tema_id"),
        Index("ix_efipem_finanzas_trimestral_clasificador", "clasificador_id"),
        Index("ix_efipem_finanzas_trimestral_concepto", "concepto_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    anio: Mapped[int] = mapped_column(Integer, nullable=False)
    trimestre_id: Mapped[int] = mapped_column(ForeignKey("stg_efipem_cat_trimestre.id"), nullable=False)
    cve_ent: Mapped[str] = mapped_column(String(2), nullable=False)
    entidad_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    tema_id: Mapped[int] = mapped_column(ForeignKey("stg_efipem_cat_tema.id"), nullable=False)
    clasificador_id: Mapped[int] = mapped_column(ForeignKey("stg_efipem_cat_clasificador.id"), nullable=False)
    concepto_id: Mapped[int] = mapped_column(ForeignKey("stg_efipem_cat_concepto.id"), nullable=False)
    valor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    estatus_id: Mapped[int] = mapped_column(ForeignKey("stg_efipem_cat_estatus.id"), nullable=False)
    created_at: Mapped[Optional[datetime]] = mapped_column(server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(server_default=func.now(), onupdate=func.now())


# Registro de modelos catalogo simples (tabla nombre-solo) para iteracion dinamica.
# 'concepto' se maneja aparte por depender de clasificador_id.
CATALOG_MODELS = {
    "trimestre": CatTrimestre,
    "tema": CatTema,
    "clasificador": CatClasificador,
    "estatus": CatEstatus,
}
