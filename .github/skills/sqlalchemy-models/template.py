"""
Template de schemas.py para un pipeline ETL.
Sustituir {flujo} y los nombres de tablas/columnas con los del pipeline real.
Los nombres de tabla se importan desde attributes.py, no se definen aquí.
No referenciar pipelines existentes en el código generado.
"""
from datetime import date

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from core.pipelines.{flujo}.attributes import {Flujo}Tables as T


# ---------------------------------------------------------------------------
# Base declarativa
# columns() permite obtener los nombres de columna en los stages sin hardcodear.
# ---------------------------------------------------------------------------
class {Flujo}Base(DeclarativeBase):
    @classmethod
    def columns(cls) -> list[str]:
        return [c.key for c in cls.__table__.columns]


# ---------------------------------------------------------------------------
# Tablas catálogo
# ---------------------------------------------------------------------------
class EstadoTramite({Flujo}Base):
    __tablename__ = T.ESTADO_TRAMITE

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    estado_tramite: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    registros: Mapped[list["Stg{Flujo}"]] = relationship(back_populates="estado_tramite_rel")


class TipoSolicitante({Flujo}Base):
    __tablename__ = T.TIPO_SOLICITANTE

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tipo_solicitante: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)

    registros: Mapped[list["Stg{Flujo}"]] = relationship(back_populates="tipo_solicitante_rel")


# ---------------------------------------------------------------------------
# Tabla principal
# ---------------------------------------------------------------------------
class Stg{Flujo}({Flujo}Base):
    __tablename__ = T.PRINCIPAL

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Claves foráneas
    id_estado_tramite: Mapped[int] = mapped_column(ForeignKey(f"{T.ESTADO_TRAMITE}.id"), nullable=False)
    id_tipo_solicitante: Mapped[int] = mapped_column(ForeignKey(f"{T.TIPO_SOLICITANTE}.id"), nullable=False)

    # Columnas de datos
    descripcion: Mapped[str | None] = mapped_column(String(500))
    valor_numerico: Mapped[float | None] = mapped_column(Numeric(12, 2))
    fecha_registro: Mapped[date] = mapped_column(nullable=False)

    # Relaciones ORM
    estado_tramite_rel: Mapped["EstadoTramite"] = relationship(back_populates="registros")
    tipo_solicitante_rel: Mapped["TipoSolicitante"] = relationship(back_populates="registros")
