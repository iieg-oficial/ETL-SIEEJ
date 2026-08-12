from datetime import date
from sqlalchemy import BigInteger, Date, Float, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from core.pipelines.emim.attributes import EmimTables as T


class EmimBase(DeclarativeBase):
    @classmethod
    def columns(cls) -> list[str]:
        return [c.key for c in cls.__table__.columns]


class CatEstatus(EmimBase):
    __tablename__ = T.CAT_ESTATUS

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    estatus: Mapped[str] = mapped_column(Text, nullable=False, unique=True)


class CatActividad(EmimBase):
    __tablename__ = T.CAT_ACTIVIDAD

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo_actividad: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)


class StgEmim(EmimBase):
    __tablename__ = T.STG_EMIM
    __table_args__ = (UniqueConstraint("fecha", "entidad_id", "codigo_actividad", name="uq_stg_emim"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    entidad_id: Mapped[int] = mapped_column(Integer, nullable=False)  # ref. cvegeo_states.cve_ent
    codigo_actividad: Mapped[str] = mapped_column(ForeignKey(f"{T.CAT_ACTIVIDAD}.codigo_actividad"), nullable=False)
    per_ocu_tot: Mapped[int | None] = mapped_column(Integer, nullable=True)
    horas_trabajadas: Mapped[float | None] = mapped_column(Float, nullable=True)
    remuneraciones: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    valor_produccion: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    valor_ventas: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    estatus_id: Mapped[int | None] = mapped_column(ForeignKey(f"{T.CAT_ESTATUS}.id"), nullable=True)
    fecha_actualizacion: Mapped[date] = mapped_column(Date, nullable=False)
