from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from core.pipelines.code.attributes import CodeTables as T


class CodeBase(DeclarativeBase):
    @classmethod
    def columns(cls) -> list[str]:
        return [c.key for c in cls.__table__.columns]


class CatActividades(CodeBase):
    __tablename__ = T.CAT_ACTIVIDADES

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    actividad: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)


class CatRegiones(CodeBase):
    __tablename__ = T.CAT_REGIONES

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    region: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)


class StgPuntosActivacionReto(CodeBase):
    __tablename__ = T.STG_PUNTOS_ACTIVACION_RETO
    __table_args__ = (
        UniqueConstraint("fecha_corte", "municipio_id", "nombre_espacio", name="uq_stg_puntos_activacion_reto"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    clave_punto: Mapped[int] = mapped_column(Integer, nullable=False)
    entidad_id: Mapped[int] = mapped_column(Integer, nullable=False)
    municipio_id: Mapped[int] = mapped_column(Integer, nullable=False)
    region_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_REGIONES}.id"), nullable=True)
    nombre_espacio: Mapped[str] = mapped_column(String(255), nullable=False)
    dias_horarios: Mapped[str | None] = mapped_column(Text, nullable=True)
    actividad_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_ACTIVIDADES}.id"), nullable=True)
    cantidad_usuarios: Mapped[int | None] = mapped_column(Integer, nullable=True)
    longitud: Mapped[float | None] = mapped_column(Float, nullable=True)
    latitud: Mapped[float | None] = mapped_column(Float, nullable=True)
    fecha_corte: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_actualizacion_fuente: Mapped[date | None] = mapped_column(Date, nullable=True)
    fecha_actualizacion: Mapped[date] = mapped_column(Date, nullable=False)

    region: Mapped["CatRegiones"] = relationship()
    actividad: Mapped["CatActividades"] = relationship()


class CargasAcervo(CodeBase):
    """Processed submissions: gives the watermark and skips unchanged reloads."""

    __tablename__ = T.CARGAS_ACERVO
    __table_args__ = (UniqueConstraint("envio_id", "object_key", name="uq_cargas_acervo"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    envio_id: Mapped[int] = mapped_column(Integer, nullable=False)
    conjunto: Mapped[str] = mapped_column(String(255), nullable=False)
    object_key: Mapped[str] = mapped_column(Text, nullable=False)
    etag: Mapped[str | None] = mapped_column(String(64), nullable=True)
    fecha_corte: Mapped[date | None] = mapped_column(Date, nullable=True)
    fecha_actualizacion_fuente: Mapped[date | None] = mapped_column(Date, nullable=True)
    actualizado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    procesado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
