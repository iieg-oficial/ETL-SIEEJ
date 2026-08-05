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
    version: Mapped[str | None] = mapped_column(String(120), nullable=True)
    procedencia: Mapped[str | None] = mapped_column(Text, nullable=True)


class Edafologias(EdafologiaBase):
    __tablename__ = T.EDAFOLOGIAS
    __table_args__ = (
        UniqueConstraint("source_version", "source_objectid", name="uq_edafologias_version_objectid"),
        Index("idx_edafologias_source_version", "source_version"),
        Index("idx_edafologias_grupo_edafologico_id", "grupo_edafologico_id"),
        Index("idx_edafologias_geom", "geom", postgresql_using="gist"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_version: Mapped[str] = mapped_column(String(80), nullable=False)
    source_objectid: Mapped[int] = mapped_column(Integer, nullable=False)
    clave_wrb: Mapped[str] = mapped_column(String(80), nullable=False)
    grupo_edafologico_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(f"{T.GRUPOS_EDAFOLOGICOS}.id"), nullable=False
    )
    calificador_primario_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(f"{T.CALIFICADORES_EDAFOLOGICOS}.id"), nullable=False
    )
    calificador_secundario_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(f"{T.CALIFICADORES_EDAFOLOGICOS}.id"), nullable=False
    )
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
    shape_leng_origen: Mapped[float | None] = mapped_column(Float, nullable=True)
    shape_area_origen: Mapped[float | None] = mapped_column(Float, nullable=True)
    source_name: Mapped[str] = mapped_column(String(160), nullable=False)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    source_file_name: Mapped[str] = mapped_column(String(160), nullable=False)
    source_file_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    source_downloaded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    processed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    fecha_actualizacion: Mapped[date] = mapped_column(Date, nullable=False)
    geom: Mapped[Any] = mapped_column(
        Geometry("MULTIPOLYGON", srid=CANONICAL_SRID, spatial_index=False), nullable=False
    )


class EdafologiaFragmentosMunicipales(EdafologiaBase):
    __tablename__ = T.EDAFOLOGIA_FRAGMENTOS_MUNICIPALES
    __table_args__ = (
        UniqueConstraint(
            "edafologia_id",
            "municipality_cvegeo",
            "fuente_limite_municipal_id",
            name="uq_edafologia_fragmentos_fuente_municipio",
        ),
        CheckConstraint("area_m2 > 0", name="ck_edafologia_fragmentos_area_m2_positive"),
        CheckConstraint("area_ha > 0", name="ck_edafologia_fragmentos_area_ha_positive"),
        CheckConstraint("pct_poligono_fuente >= 0", name="ck_edafologia_fragmentos_pct_poligono_non_negative"),
        CheckConstraint("pct_municipio_total >= 0", name="ck_edafologia_fragmentos_pct_municipio_non_negative"),
        CheckConstraint("pct_cobertura_edafologica >= 0", name="ck_edafologia_fragmentos_pct_cobertura_non_negative"),
        Index("idx_edafologia_fragmentos_municipality_cvegeo", "municipality_cvegeo"),
        Index("idx_edafologia_fragmentos_source_version", "source_version"),
        Index(
            "idx_edafologia_fragmentos_fuente_municipio_version",
            "fuente_limite_municipal_id",
            "municipality_cvegeo",
            "source_version",
        ),
        Index("idx_edafologia_fragmentos_edafologia_id", "edafologia_id"),
        Index("idx_edafologia_fragmentos_fuente_limite", "fuente_limite_municipal_id"),
        Index("idx_edafologia_fragmentos_geom", "geom", postgresql_using="gist"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    edafologia_id: Mapped[int] = mapped_column(Integer, ForeignKey(f"{T.EDAFOLOGIAS}.id"), nullable=False)
    municipality_cvegeo: Mapped[int] = mapped_column(Integer, nullable=False)
    source_version: Mapped[str] = mapped_column(String(80), nullable=False)
    fuente_limite_municipal_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(f"{T.FUENTES_LIMITES_MUNICIPALES}.id"), nullable=False
    )
    area_m2: Mapped[float] = mapped_column(Float, nullable=False)
    area_ha: Mapped[float] = mapped_column(Float, nullable=False)
    pct_poligono_fuente: Mapped[float] = mapped_column(Float, nullable=False)
    pct_municipio_total: Mapped[float] = mapped_column(Float, nullable=False)
    pct_cobertura_edafologica: Mapped[float] = mapped_column(Float, nullable=False)
    es_fragmento_pequenio: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    geom: Mapped[Any] = mapped_column(
        Geometry("MULTIPOLYGON", srid=CANONICAL_SRID, spatial_index=False), nullable=False
    )
