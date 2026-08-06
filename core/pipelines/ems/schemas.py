from datetime import date

from sqlalchemy import Date, Float, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from core.pipelines.ems.attributes import EmsTables as T


class EmsBase(DeclarativeBase):
    @classmethod
    def columns(cls) -> list[str]:
        return [c.key for c in cls.__table__.columns]


class CatEstatus(EmsBase):
    __tablename__ = T.CAT_ESTATUS

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    estatus: Mapped[str] = mapped_column(Text, nullable=False, unique=True)


class CatActividad(EmsBase):
    __tablename__ = T.CAT_ACTIVIDAD

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo_actividad: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)


class StgEms(EmsBase):
    __tablename__ = T.STG_EMS
    __table_args__ = (UniqueConstraint("fecha", "entidad_id", "codigo_actividad", name="uq_stg_ems"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    entidad_id: Mapped[int] = mapped_column(Integer, nullable=False)  # ref. cvegeo_states.cve_ent
    codigo_actividad: Mapped[int] = mapped_column(ForeignKey(f"{T.CAT_ACTIVIDAD}.codigo_actividad"), nullable=False)
    ind_ingresos_bienes_serv: Mapped[float | None] = mapped_column(Float, nullable=True)
    ind_gastos_consumo: Mapped[float | None] = mapped_column(Float, nullable=True)
    per_ocu_tot: Mapped[float | None] = mapped_column(Float, nullable=True)
    per_ocu_dependiente: Mapped[float | None] = mapped_column(Float, nullable=True)
    per_ocu_no_dependiente: Mapped[float | None] = mapped_column(Float, nullable=True)
    remuneraciones_tot: Mapped[float | None] = mapped_column(Float, nullable=True)
    estatus_id: Mapped[int | None] = mapped_column(ForeignKey(f"{T.CAT_ESTATUS}.id"), nullable=True)
    fecha_actualizacion: Mapped[date] = mapped_column(Date, nullable=False)
