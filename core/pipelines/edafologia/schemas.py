from datetime import date, datetime
from typing import Any

from geoalchemy2 import Geometry
from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from core.pipelines.edafologia.attributes import EdafologiaTables as T
from core.pipelines.edafologia.constants import CANONICAL_SRID


class EdafologiaBase(DeclarativeBase):
    @classmethod
    def columns(cls) -> list[str]:
        return [c.key for c in cls.__table__.columns]


class GruposEdafologicos(EdafologiaBase):
    __tablename__ = T.GRUPOS_EDAFOLOGICOS

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    clave: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    descripcion: Mapped[str] = mapped_column(String(255), nullable=False)


class CalificadoresEdafologicos(EdafologiaBase):
    __tablename__ = T.CALIFICADORES_EDAFOLOGICOS

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    clave: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    descripcion: Mapped[str] = mapped_column(String(255), nullable=False)


class FuentesLimitesMunicipales(EdafologiaBase):
    __tablename__ = T.FUENTES_LIMITES_MUNICIPALES

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    clave: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    nombre_fuente: Mapped[str] = mapped_column(String(120), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[str] = mapped_column(String(120), nullable=False)
    procedencia: Mapped[str | None] = mapped_column(Text, nullable=True)


class Edafologias(EdafologiaBase):
    __tablename__ = T.EDAFOLOGIAS
    __table_args__ = (
        UniqueConstraint(
            "version_fuente",
            "identificador_objeto_fuente",
            name="uq_edafologias_version_fuente_identificador_objeto",
        ),
        Index("idx_edafologias_version_fuente", "version_fuente"),
        Index("idx_edafologias_grupo_edafologico_id", "grupo_edafologico_id"),
        Index("idx_edafologias_geometria", "geometria", postgresql_using="gist"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    identificador_objeto_fuente: Mapped[int] = mapped_column(Integer, nullable=False)
    grupo_edafologico_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(f"{T.GRUPOS_EDAFOLOGICOS}.id"), nullable=False
    )
    calificador_primario_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(f"{T.CALIFICADORES_EDAFOLOGICOS}.id"), nullable=False
    )
    calificador_secundario_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(f"{T.CALIFICADORES_EDAFOLOGICOS}.id"), nullable=False
    )
    longitud_origen: Mapped[float | None] = mapped_column(Float, nullable=True)
    superficie_origen: Mapped[float | None] = mapped_column(Float, nullable=True)
    version_fuente: Mapped[str] = mapped_column(String(80), nullable=False)
    clave_wrb: Mapped[str] = mapped_column(String(80), nullable=False)
    grupo1_origen: Mapped[str] = mapped_column(String(20), nullable=False)
    califp_g1_origen: Mapped[str] = mapped_column(String(20), nullable=False)
    califs_g1_origen: Mapped[str] = mapped_column(String(20), nullable=False)
    grupo2_origen: Mapped[str | None] = mapped_column(String(20), nullable=True)
    califp_g2_origen: Mapped[str | None] = mapped_column(String(20), nullable=True)
    califs_g2_origen: Mapped[str | None] = mapped_column(String(20), nullable=True)
    grupo3_origen: Mapped[str | None] = mapped_column(String(20), nullable=True)
    califp_g3_origen: Mapped[str | None] = mapped_column(String(20), nullable=True)
    clase_textural_origen: Mapped[str | None] = mapped_column(String(80), nullable=True)
    limite_superior_origen: Mapped[str | None] = mapped_column(String(80), nullable=True)
    fase_fisica_origen: Mapped[str | None] = mapped_column(String(80), nullable=True)
    fase_quimica_origen: Mapped[str | None] = mapped_column(String(80), nullable=True)
    nombre_fuente: Mapped[str] = mapped_column(String(160), nullable=False)
    url_fuente: Mapped[str] = mapped_column(Text, nullable=False)
    nombre_archivo_fuente: Mapped[str] = mapped_column(String(160), nullable=False)
    sha256_archivo_fuente: Mapped[str] = mapped_column(String(64), nullable=False)
    fecha_descarga_fuente: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    fecha_procesamiento: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    fecha_actualizacion: Mapped[date] = mapped_column(Date, nullable=False)
    geometria: Mapped[Any] = mapped_column(
        Geometry("MULTIPOLYGON", srid=CANONICAL_SRID, spatial_index=False), nullable=False
    )


class EdafologiaFragmentosMunicipales(EdafologiaBase):
    __tablename__ = T.EDAFOLOGIA_FRAGMENTOS_MUNICIPALES
    __table_args__ = (
        UniqueConstraint(
            "edafologia_id",
            "municipio_id",
            "fuente_limite_municipal_id",
            name="uq_edafologia_fragmentos_fuente_municipio",
        ),
        CheckConstraint("superficie_m2 > 0", name="ck_edafologia_fragmentos_superficie_m2_positiva"),
        CheckConstraint("superficie_ha > 0", name="ck_edafologia_fragmentos_superficie_ha_positiva"),
        CheckConstraint(
            "porcentaje_poligono_fuente >= 0",
            name="ck_edafologia_fragmentos_porcentaje_poligono_no_negativo",
        ),
        CheckConstraint(
            "porcentaje_municipio_total >= 0",
            name="ck_edafologia_fragmentos_porcentaje_municipio_no_negativo",
        ),
        CheckConstraint(
            "porcentaje_cobertura_edafologica >= 0",
            name="ck_edafologia_fragmentos_porcentaje_cobertura_no_negativo",
        ),
        Index("idx_edafologia_fragmentos_municipio_id", "municipio_id"),
        Index("idx_edafologia_fragmentos_version_fuente", "version_fuente"),
        Index(
            "idx_edafologia_fragmentos_fuente_municipio_version",
            "fuente_limite_municipal_id",
            "municipio_id",
            "version_fuente",
        ),
        Index("idx_edafologia_fragmentos_edafologia_id", "edafologia_id"),
        Index("idx_edafologia_fragmentos_fuente_limite", "fuente_limite_municipal_id"),
        Index("idx_edafologia_fragmentos_geometria", "geometria", postgresql_using="gist"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    edafologia_id: Mapped[int] = mapped_column(Integer, ForeignKey(f"{T.EDAFOLOGIAS}.id"), nullable=False)
    municipio_id: Mapped[int] = mapped_column(Integer, nullable=False)
    fuente_limite_municipal_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(f"{T.FUENTES_LIMITES_MUNICIPALES}.id"), nullable=False
    )
    superficie_m2: Mapped[float] = mapped_column(Float, nullable=False)
    superficie_ha: Mapped[float] = mapped_column(Float, nullable=False)
    porcentaje_poligono_fuente: Mapped[float] = mapped_column(Float, nullable=False)
    porcentaje_municipio_total: Mapped[float] = mapped_column(Float, nullable=False)
    porcentaje_cobertura_edafologica: Mapped[float] = mapped_column(Float, nullable=False)
    es_fragmento_pequenio: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    version_fuente: Mapped[str] = mapped_column(String(80), nullable=False)
    geometria: Mapped[Any] = mapped_column(
        Geometry("MULTIPOLYGON", srid=CANONICAL_SRID, spatial_index=False), nullable=False
    )
