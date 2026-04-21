from datetime import date, datetime
from typing import Optional

from sqlalchemy import Index, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class AsgImssBase(DeclarativeBase):
    pass


# ---------------------------------------------------------------------------
# Catálogos
# ---------------------------------------------------------------------------


class CatDelegacion(AsgImssBase):
    __tablename__ = "stg_asg_imss_cat_delegacion"
    __table_args__ = (UniqueConstraint("cve_delegacion", name="uq_asg_imss_cat_delegacion_cve"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cve_delegacion: Mapped[int] = mapped_column(unique=True)
    descripcion: Mapped[str] = mapped_column(String(100))


class CatSubdelegacion(AsgImssBase):
    __tablename__ = "stg_asg_imss_cat_subdelegacion"
    __table_args__ = (
        UniqueConstraint("cve_delegacion", "cve_subdelegacion", name="uq_asg_imss_cat_subdelegacion_cve"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cve_delegacion: Mapped[int]
    cve_subdelegacion: Mapped[int]
    descripcion: Mapped[str] = mapped_column(String(100))


class CatEntidadMunicipio(AsgImssBase):
    __tablename__ = "stg_asg_imss_cat_entidad_municipio"
    __table_args__ = (UniqueConstraint("cve_municipio", name="uq_asg_imss_cat_entidad_municipio_cve"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cve_municipio: Mapped[str] = mapped_column(String(10), unique=True)
    cve_delegacion: Mapped[int]
    cve_entidad: Mapped[int]
    desc_entidad: Mapped[str] = mapped_column(String(100))
    desc_municipio: Mapped[str] = mapped_column(String(200))


class CatSector1(AsgImssBase):
    __tablename__ = "stg_asg_imss_cat_sector_1"
    __table_args__ = (UniqueConstraint("cve_sector_1", name="uq_asg_imss_cat_sector_1_cve"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cve_sector_1: Mapped[int] = mapped_column(unique=True)
    descripcion: Mapped[str] = mapped_column(String(300))


class CatSector2(AsgImssBase):
    __tablename__ = "stg_asg_imss_cat_sector_2"
    __table_args__ = (UniqueConstraint("cve_sector_1", "cve_sector_2", name="uq_asg_imss_cat_sector_2_cve"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cve_sector_1: Mapped[int]
    cve_sector_2: Mapped[int]
    cve_sector_2_2pos: Mapped[int]
    descripcion: Mapped[str] = mapped_column(String(500))


class CatSector4(AsgImssBase):
    __tablename__ = "stg_asg_imss_cat_sector_4"
    __table_args__ = (UniqueConstraint("cve_sector_2", "cve_sector_4", name="uq_asg_imss_cat_sector_4_cve"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cve_sector_2: Mapped[int]
    cve_sector_4: Mapped[int]
    cve_sector_4_4pos: Mapped[str] = mapped_column(String(10))
    descripcion: Mapped[str] = mapped_column(String(500))


class CatTamanioPatron(AsgImssBase):
    __tablename__ = "stg_asg_imss_cat_tamanio_patron"
    __table_args__ = (UniqueConstraint("cve", name="uq_asg_imss_cat_tamanio_patron_cve"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cve: Mapped[str] = mapped_column(String(5), unique=True)
    descripcion: Mapped[str] = mapped_column(String(100))


class CatSexo(AsgImssBase):
    __tablename__ = "stg_asg_imss_cat_sexo"
    __table_args__ = (UniqueConstraint("cve", name="uq_asg_imss_cat_sexo_cve"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cve: Mapped[int] = mapped_column(unique=True)
    descripcion: Mapped[str] = mapped_column(String(50))


class CatRangoEdad(AsgImssBase):
    __tablename__ = "stg_asg_imss_cat_rango_edad"
    __table_args__ = (UniqueConstraint("cve", name="uq_asg_imss_cat_rango_edad_cve"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cve: Mapped[str] = mapped_column(String(5), unique=True)
    descripcion: Mapped[str] = mapped_column(String(200))


class CatRangoSalarial(AsgImssBase):
    __tablename__ = "stg_asg_imss_cat_rango_salarial"
    __table_args__ = (UniqueConstraint("cve", name="uq_asg_imss_cat_rango_salarial_cve"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cve: Mapped[str] = mapped_column(String(5), unique=True)
    descripcion: Mapped[str] = mapped_column(String(200))


class CatRangoUma(AsgImssBase):
    __tablename__ = "stg_asg_imss_cat_rango_uma"
    __table_args__ = (UniqueConstraint("cve", name="uq_asg_imss_cat_rango_uma_cve"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cve: Mapped[str] = mapped_column(String(5), unique=True)
    descripcion: Mapped[str] = mapped_column(String(200))


# ---------------------------------------------------------------------------
# Tabla principal
# ---------------------------------------------------------------------------


class AsgImssDatos(AsgImssBase):
    __tablename__ = "stg_asg_imss_datos"
    __table_args__ = (
        UniqueConstraint("record_hash", name="uq_asg_imss_datos_record_hash"),
        Index("ix_asg_imss_datos_record_hash", "record_hash", unique=True),
        Index("ix_asg_imss_datos_fecha_corte", "fecha_corte"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Dimensiones
    cve_delegacion: Mapped[int]
    cve_subdelegacion: Mapped[int]
    cve_entidad: Mapped[int]
    cve_municipio: Mapped[str] = mapped_column(String(10))
    sector_economico_1: Mapped[Optional[int]]
    sector_economico_2: Mapped[Optional[int]]
    sector_economico_4: Mapped[Optional[int]]
    tamanio_patron: Mapped[Optional[str]] = mapped_column(String(5))
    sexo: Mapped[int]
    rango_edad: Mapped[str] = mapped_column(String(5))
    rango_salarial: Mapped[Optional[str]] = mapped_column(String(5))
    rango_uma: Mapped[Optional[str]] = mapped_column(String(5))
    fecha_corte: Mapped[date]

    # Métricas — conteos
    asegurados: Mapped[int] = mapped_column(default=0)
    no_trabajadores: Mapped[int] = mapped_column(default=0)
    ta: Mapped[int] = mapped_column(default=0)
    teu: Mapped[int] = mapped_column(default=0)
    tec: Mapped[int] = mapped_column(default=0)
    tpu: Mapped[int] = mapped_column(default=0)
    tpc: Mapped[int] = mapped_column(default=0)
    ta_sal: Mapped[int] = mapped_column(default=0)
    teu_sal: Mapped[int] = mapped_column(default=0)
    tec_sal: Mapped[int] = mapped_column(default=0)
    tpu_sal: Mapped[int] = mapped_column(default=0)
    tpc_sal: Mapped[int] = mapped_column(default=0)

    # Métricas — masa salarial
    masa_sal_ta: Mapped[float] = mapped_column(Numeric(16, 2), default=0)
    masa_sal_teu: Mapped[float] = mapped_column(Numeric(16, 2), default=0)
    masa_sal_tec: Mapped[float] = mapped_column(Numeric(16, 2), default=0)
    masa_sal_tpu: Mapped[float] = mapped_column(Numeric(16, 2), default=0)
    masa_sal_tpc: Mapped[float] = mapped_column(Numeric(16, 2), default=0)

    # Auditoría
    record_hash: Mapped[str] = mapped_column(String(64), unique=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(server_default=func.now())


# ---------------------------------------------------------------------------
# Registro de catálogos para iteración dinámica
# ---------------------------------------------------------------------------

CATALOG_MODELS: dict[str, type] = {
    "cve_delegacion": CatDelegacion,
    "cve_subdelegacion": CatSubdelegacion,
    "cve_municipio": CatEntidadMunicipio,
    "sector_economico_1": CatSector1,
    "sector_economico_2": CatSector2,
    "sector_economico_4": CatSector4,
    "tamanio_patron": CatTamanioPatron,
    "sexo": CatSexo,
    "rango_edad": CatRangoEdad,
    "rango_salarial": CatRangoSalarial,
    "rango_uma": CatRangoUma,
}
