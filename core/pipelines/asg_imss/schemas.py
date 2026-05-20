"""Modelos SQLAlchemy del pipeline asg_imss.

Sincronizado con las migraciones Flyway:
    * migrations/asg_imss/sql/V1__catalogs_asg_imss.sql
    * migrations/asg_imss/sql/V2__table_asg_imss.sql
    * migrations/asg_imss/sql/V3__view_asg_imss.sql

Convenciones del pipeline:
    * Modelo append-only: PK sintética BIGSERIAL en `stg_asg_imss`, sin
      UNIQUE sobre llaves naturales ni columna hash.
    * Catálogos auto-poblables: el load inserta claves nuevas con
      `descripcion = 'SIN DESCRIPCION'` (sectores admiten NULL en la FK
      de la tabla de hechos).
    * Los nombres de tabla provienen de `AsgImssTables`; no se usan
      literales string en `__tablename__`.
"""

from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    CHAR,
    BigInteger,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    TIMESTAMP,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from core.pipelines.asg_imss.attributes import AsgImssTables as T


class AsgImssBase(DeclarativeBase):
    """Base declarativa del pipeline asg_imss."""

    @classmethod
    def columns(cls) -> list[str]:
        return [c.key for c in cls.__table__.columns]


# ---------------------------------------------------------------------------
# Catálogos
# ---------------------------------------------------------------------------


class CatDelegacion(AsgImssBase):
    __tablename__ = T.CAT_DELEGACION
    __table_args__ = (UniqueConstraint("clave", name="uq_cat_delegacion_clave"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    clave: Mapped[str] = mapped_column(String(3), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)

    subdelegaciones: Mapped[list["CatSubdelegacion"]] = relationship(back_populates="delegacion_rel")
    registros: Mapped[list["StgAsgImss"]] = relationship(back_populates="delegacion_rel")


class CatSubdelegacion(AsgImssBase):
    __tablename__ = T.CAT_SUBDELEGACION
    __table_args__ = (
        UniqueConstraint("delegacion_id", "clave", name="uq_cat_subdelegacion_deleg_clave"),
        Index("ix_cat_subdelegacion_delegacion", "delegacion_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    clave: Mapped[str] = mapped_column(String(3), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    delegacion_id: Mapped[int] = mapped_column(ForeignKey(f"{T.CAT_DELEGACION}.id"), nullable=False)

    delegacion_rel: Mapped["CatDelegacion"] = relationship(back_populates="subdelegaciones")
    registros: Mapped[list["StgAsgImss"]] = relationship(back_populates="subdelegacion_rel")


class CatEntidad(AsgImssBase):
    __tablename__ = T.CAT_ENTIDAD
    __table_args__ = (UniqueConstraint("clave", name="uq_cat_entidad_clave"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    clave: Mapped[str] = mapped_column(CHAR(2), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)

    municipios: Mapped[list["CatMunicipio"]] = relationship(back_populates="entidad_rel")
    registros: Mapped[list["StgAsgImss"]] = relationship(back_populates="entidad_rel")


class CatMunicipio(AsgImssBase):
    __tablename__ = T.CAT_MUNICIPIO
    __table_args__ = (
        UniqueConstraint("entidad_id", "clave", name="uq_cat_municipio_entidad_clave"),
        Index("ix_cat_municipio_entidad", "entidad_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    clave: Mapped[str] = mapped_column(String(4), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    entidad_id: Mapped[int] = mapped_column(ForeignKey(f"{T.CAT_ENTIDAD}.id"), nullable=False)

    entidad_rel: Mapped["CatEntidad"] = relationship(back_populates="municipios")
    registros: Mapped[list["StgAsgImss"]] = relationship(back_populates="municipio_rel")


class CatSector1(AsgImssBase):
    __tablename__ = T.CAT_SECTOR_1
    __table_args__ = (UniqueConstraint("clave", name="uq_cat_sector_1_clave"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    clave: Mapped[str] = mapped_column(CHAR(1), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)

    sectores_2: Mapped[list["CatSector2"]] = relationship(back_populates="sector_1_rel")
    registros: Mapped[list["StgAsgImss"]] = relationship(back_populates="sector_1_rel")


class CatSector2(AsgImssBase):
    __tablename__ = T.CAT_SECTOR_2
    __table_args__ = (
        UniqueConstraint("clave", name="uq_cat_sector_2_clave"),
        Index("ix_cat_sector_2_sector_1", "sector_1_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    clave: Mapped[str] = mapped_column(CHAR(2), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    sector_1_id: Mapped[int] = mapped_column(ForeignKey(f"{T.CAT_SECTOR_1}.id"), nullable=False)

    sector_1_rel: Mapped["CatSector1"] = relationship(back_populates="sectores_2")
    sectores_4: Mapped[list["CatSector4"]] = relationship(back_populates="sector_2_rel")
    registros: Mapped[list["StgAsgImss"]] = relationship(back_populates="sector_2_rel")


class CatSector4(AsgImssBase):
    __tablename__ = T.CAT_SECTOR_4
    __table_args__ = (
        UniqueConstraint("clave", name="uq_cat_sector_4_clave"),
        Index("ix_cat_sector_4_sector_2", "sector_2_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    clave: Mapped[str] = mapped_column(CHAR(4), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    sector_2_id: Mapped[int] = mapped_column(ForeignKey(f"{T.CAT_SECTOR_2}.id"), nullable=False)

    sector_2_rel: Mapped["CatSector2"] = relationship(back_populates="sectores_4")
    registros: Mapped[list["StgAsgImss"]] = relationship(back_populates="sector_4_rel")


class CatTamanoRegistroPatronal(AsgImssBase):
    __tablename__ = T.CAT_TAMANO_REGISTRO_PATRONAL
    __table_args__ = (UniqueConstraint("clave", name="uq_cat_tamano_registro_patronal_clave"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    clave: Mapped[str] = mapped_column(String(2), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)

    registros: Mapped[list["StgAsgImss"]] = relationship(back_populates="tamano_registro_patronal_rel")


class CatSexo(AsgImssBase):
    __tablename__ = T.CAT_SEXO
    __table_args__ = (UniqueConstraint("clave", name="uq_cat_sexo_clave"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    clave: Mapped[str] = mapped_column(String(2), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)

    registros: Mapped[list["StgAsgImss"]] = relationship(back_populates="sexo_rel")


class CatRangoEdad(AsgImssBase):
    __tablename__ = T.CAT_RANGO_EDAD
    __table_args__ = (UniqueConstraint("clave", name="uq_cat_rango_edad_clave"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    clave: Mapped[str] = mapped_column(String(3), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)

    registros: Mapped[list["StgAsgImss"]] = relationship(back_populates="rango_edad_rel")


class CatRangoSalario(AsgImssBase):
    __tablename__ = T.CAT_RANGO_SALARIO
    __table_args__ = (UniqueConstraint("clave", name="uq_cat_rango_salario_clave"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    clave: Mapped[str] = mapped_column(String(3), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)

    registros: Mapped[list["StgAsgImss"]] = relationship(back_populates="rango_salario_rel")


class CatRangoUma(AsgImssBase):
    __tablename__ = T.CAT_RANGO_UMA
    __table_args__ = (UniqueConstraint("clave", name="uq_cat_rango_uma_clave"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    clave: Mapped[str] = mapped_column(String(3), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)

    registros: Mapped[list["StgAsgImss"]] = relationship(back_populates="rango_uma_rel")


# ---------------------------------------------------------------------------
# Tabla principal (append-only)
# ---------------------------------------------------------------------------


class StgAsgImss(AsgImssBase):
    __tablename__ = T.STG_ASG_IMSS
    __table_args__ = (
        Index("ix_stg_asg_imss_fecha_corte", "fecha_corte"),
        Index("ix_stg_asg_imss_delegacion", "delegacion_id"),
        Index("ix_stg_asg_imss_subdelegacion", "subdelegacion_id"),
        Index("ix_stg_asg_imss_entidad", "entidad_id"),
        Index("ix_stg_asg_imss_municipio", "municipio_id"),
        Index("ix_stg_asg_imss_sector_4", "sector_4_id"),
        Index("ix_stg_asg_imss_tamano_registro_patronal", "tamano_registro_patronal_id"),
        Index("ix_stg_asg_imss_sexo", "sexo_id"),
        Index("ix_stg_asg_imss_rango_edad", "rango_edad_id"),
        Index("ix_stg_asg_imss_rango_salario", "rango_salario_id"),
        Index("ix_stg_asg_imss_rango_uma", "rango_uma_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    fecha_corte: Mapped[date] = mapped_column(nullable=False)

    # FKs (sectores nullable)
    delegacion_id: Mapped[int] = mapped_column(ForeignKey(f"{T.CAT_DELEGACION}.id"), nullable=False)
    subdelegacion_id: Mapped[int] = mapped_column(ForeignKey(f"{T.CAT_SUBDELEGACION}.id"), nullable=False)
    entidad_id: Mapped[int] = mapped_column(ForeignKey(f"{T.CAT_ENTIDAD}.id"), nullable=False)
    municipio_id: Mapped[int] = mapped_column(ForeignKey(f"{T.CAT_MUNICIPIO}.id"), nullable=False)
    sector_1_id: Mapped[Optional[int]] = mapped_column(ForeignKey(f"{T.CAT_SECTOR_1}.id"), nullable=True)
    sector_2_id: Mapped[Optional[int]] = mapped_column(ForeignKey(f"{T.CAT_SECTOR_2}.id"), nullable=True)
    sector_4_id: Mapped[Optional[int]] = mapped_column(ForeignKey(f"{T.CAT_SECTOR_4}.id"), nullable=True)
    tamano_registro_patronal_id: Mapped[int] = mapped_column(
        ForeignKey(f"{T.CAT_TAMANO_REGISTRO_PATRONAL}.id"), nullable=False
    )
    sexo_id: Mapped[int] = mapped_column(ForeignKey(f"{T.CAT_SEXO}.id"), nullable=False)
    rango_edad_id: Mapped[int] = mapped_column(ForeignKey(f"{T.CAT_RANGO_EDAD}.id"), nullable=False)
    rango_salario_id: Mapped[int] = mapped_column(ForeignKey(f"{T.CAT_RANGO_SALARIO}.id"), nullable=False)
    rango_uma_id: Mapped[int] = mapped_column(ForeignKey(f"{T.CAT_RANGO_UMA}.id"), nullable=False)

    # Métricas enteras
    asegurados: Mapped[int] = mapped_column(Integer, nullable=False)
    no_trabajadores: Mapped[int] = mapped_column(Integer, nullable=False)
    ta: Mapped[int] = mapped_column(Integer, nullable=False)
    teu: Mapped[int] = mapped_column(Integer, nullable=False)
    tec: Mapped[int] = mapped_column(Integer, nullable=False)
    tpu: Mapped[int] = mapped_column(Integer, nullable=False)
    tpc: Mapped[int] = mapped_column(Integer, nullable=False)
    ta_sal: Mapped[int] = mapped_column(Integer, nullable=False)
    teu_sal: Mapped[int] = mapped_column(Integer, nullable=False)
    tec_sal: Mapped[int] = mapped_column(Integer, nullable=False)
    tpu_sal: Mapped[int] = mapped_column(Integer, nullable=False)
    tpc_sal: Mapped[int] = mapped_column(Integer, nullable=False)

    # Métricas decimales
    masa_sal_ta: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    masa_sal_teu: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    masa_sal_tec: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    masa_sal_tpu: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    masa_sal_tpc: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)

    # Auditoría
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    # Relaciones ORM
    delegacion_rel: Mapped["CatDelegacion"] = relationship(back_populates="registros")
    subdelegacion_rel: Mapped["CatSubdelegacion"] = relationship(back_populates="registros")
    entidad_rel: Mapped["CatEntidad"] = relationship(back_populates="registros")
    municipio_rel: Mapped["CatMunicipio"] = relationship(back_populates="registros")
    sector_1_rel: Mapped[Optional["CatSector1"]] = relationship(back_populates="registros")
    sector_2_rel: Mapped[Optional["CatSector2"]] = relationship(back_populates="registros")
    sector_4_rel: Mapped[Optional["CatSector4"]] = relationship(back_populates="registros")
    tamano_registro_patronal_rel: Mapped["CatTamanoRegistroPatronal"] = relationship(back_populates="registros")
    sexo_rel: Mapped["CatSexo"] = relationship(back_populates="registros")
    rango_edad_rel: Mapped["CatRangoEdad"] = relationship(back_populates="registros")
    rango_salario_rel: Mapped["CatRangoSalario"] = relationship(back_populates="registros")
    rango_uma_rel: Mapped["CatRangoUma"] = relationship(back_populates="registros")
