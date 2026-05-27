from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger,
    CHAR,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    String,
    TIMESTAMP,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class EfipemBase(DeclarativeBase):
    pass


# Catalogos


class CatTema(EfipemBase):
    __tablename__ = "cat_tema"
    __table_args__ = (UniqueConstraint("name", name="uq_cat_tema_name"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)


class CatClasificador(EfipemBase):
    __tablename__ = "cat_clasificador"
    __table_args__ = (UniqueConstraint("name", name="uq_cat_clasificador_name"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), unique=True)


class CatConcepto(EfipemBase):
    __tablename__ = "cat_concepto"
    __table_args__ = (
        UniqueConstraint("clasificador_id", "name", name="uq_cat_concepto_clasif_name"),
        Index("ix_cat_concepto_clasificador", "clasificador_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    clasificador_id: Mapped[int] = mapped_column(ForeignKey("cat_clasificador.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255))


class CatEstatus(EfipemBase):
    __tablename__ = "cat_estatus"
    __table_args__ = (UniqueConstraint("name", name="uq_cat_estatus_name"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)


# Tabla principal


class FinanzasMunicipal(EfipemBase):
    __tablename__ = "stg_efipem"
    __table_args__ = (
        UniqueConstraint(
            "anio",
            "cvegeo",
            "tema_id",
            "clasificador_id",
            "concepto_id",
            name="uq_stg_efipem_llave",
        ),
        Index("ix_stg_efipem_anio", "anio"),
        Index("ix_stg_efipem_cvegeo", "cvegeo"),
        Index("ix_stg_efipem_cve_ent", "cve_ent"),
        Index("ix_stg_efipem_tema", "tema_id"),
        Index("ix_stg_efipem_clasificador", "clasificador_id"),
        Index("ix_stg_efipem_concepto", "concepto_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    anio: Mapped[int] = mapped_column(Integer, nullable=False)
    cvegeo: Mapped[str] = mapped_column(CHAR(5), nullable=False)
    cve_ent: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    cve_mun: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    tema_id: Mapped[int] = mapped_column(ForeignKey("cat_tema.id"), nullable=False)
    clasificador_id: Mapped[int] = mapped_column(ForeignKey("cat_clasificador.id"), nullable=False)
    concepto_id: Mapped[int] = mapped_column(ForeignKey("cat_concepto.id"), nullable=False)
    valor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    estatus_id: Mapped[int] = mapped_column(ForeignKey("cat_estatus.id"), nullable=False)
    created_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())


# Registro de modelos catalogo simples (tabla nombre-solo) para iteracion dinamica.
# 'concepto' se maneja aparte por depender de clasificador_id.
CATALOG_MODELS = {
    "tema": CatTema,
    "clasificador": CatClasificador,
    "estatus": CatEstatus,
}
