"""
Template de schemas.py para un pipeline ETL.
Sustituir {flujo} y los nombres de tablas/columnas con los del pipeline real.
No referenciar pipelines existentes en el código generado.
"""
from datetime import date
from sqlalchemy import ForeignKey, String, Numeric
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


# ---------------------------------------------------------------------------
# Constantes de nombres de tabla (evitar strings hardcodeados en los stages)
# ---------------------------------------------------------------------------
class {Flujo}Tables:
    ESTADO_TRAMITE   = "cat_estado_tramite"
    TIPO_SOLICITANTE = "cat_tipo_solicitante"
    PRINCIPAL        = "stg_{flujo}"


# ---------------------------------------------------------------------------
# Base declarativa
# ---------------------------------------------------------------------------
class {Flujo}Base(DeclarativeBase):
    pass


# ---------------------------------------------------------------------------
# Tablas catálogo
# ---------------------------------------------------------------------------
class EstadoTramite({Flujo}Base):
    __tablename__ = {Flujo}Tables.ESTADO_TRAMITE

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    estado_tramite: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    # Relación inversa desde la tabla principal
    registros: Mapped[list["Stg{Flujo}"]] = relationship(back_populates="estado_tramite_rel")


class TipoSolicitante({Flujo}Base):
    __tablename__ = {Flujo}Tables.TIPO_SOLICITANTE

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tipo_solicitante: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)

    registros: Mapped[list["Stg{Flujo}"]] = relationship(back_populates="tipo_solicitante_rel")


# ---------------------------------------------------------------------------
# Tabla principal
# ---------------------------------------------------------------------------
class Stg{Flujo}({Flujo}Base):
    __tablename__ = {Flujo}Tables.PRINCIPAL

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Claves foráneas
    id_estado_tramite: Mapped[int] = mapped_column(
        ForeignKey(f"{{{Flujo}Tables.ESTADO_TRAMITE}}.id"), nullable=False
    )
    id_tipo_solicitante: Mapped[int] = mapped_column(
        ForeignKey(f"{{{Flujo}Tables.TIPO_SOLICITANTE}}.id"), nullable=False
    )

    # Columnas de datos
    descripcion: Mapped[str | None] = mapped_column(String(500))
    valor_numerico: Mapped[float | None] = mapped_column(Numeric(12, 2))
    fecha_registro: Mapped[date] = mapped_column(nullable=False)

    # Relaciones ORM
    estado_tramite_rel: Mapped["EstadoTramite"] = relationship(back_populates="registros")
    tipo_solicitante_rel: Mapped["TipoSolicitante"] = relationship(back_populates="registros")
