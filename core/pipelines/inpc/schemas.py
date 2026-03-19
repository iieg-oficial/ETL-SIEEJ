from datetime import date
from sqlalchemy import String, Float, Date, ForeignKey, UniqueConstraint, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from core.pipelines.inpc.attributes import InpcTables as T


class InpcBase(DeclarativeBase):
    @classmethod
    def columns(cls) -> list[str]:
        return [c.key for c in cls.__table__.columns]


class Ciudades(InpcBase):
    __tablename__ = T.CIUDADES

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ciudad: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    entidad: Mapped[str | None] = mapped_column(String(100), nullable=True)


class ObjetosGasto(InpcBase):
    __tablename__ = T.OBJETOS_GASTO

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    objeto_gasto: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)


class InpcCiudades(InpcBase):
    __tablename__ = T.INPC_CIUDADES
    __table_args__ = (UniqueConstraint("ciudad_id", "fecha", "objeto_gasto_id", name="uq_inpc_ciudades"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ciudad_id: Mapped[int] = mapped_column(ForeignKey(f"{T.CIUDADES}.id"), nullable=False)
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    objeto_gasto_id: Mapped[int] = mapped_column(ForeignKey(f"{T.OBJETOS_GASTO}.id"), nullable=False)
    indice_de_precios: Mapped[float | None] = mapped_column(Float, nullable=True)
    fecha_actualizacion: Mapped[date] = mapped_column(Date, nullable=False)


class InpcEntidades(InpcBase):
    __tablename__ = T.INPC_ENTIDADES
    __table_args__ = (UniqueConstraint("entidad_id", "fecha", "objeto_gasto_id", name="uq_inpc_entidades"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    entidad_id: Mapped[int] = mapped_column(Integer, nullable=False)  # ref. cvegeo_states.cve_ent
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    objeto_gasto_id: Mapped[int] = mapped_column(ForeignKey(f"{T.OBJETOS_GASTO}.id"), nullable=False)
    indice_de_precios: Mapped[float | None] = mapped_column(Float, nullable=True)
    fecha_actualizacion: Mapped[date] = mapped_column(Date, nullable=False)


class InpcNacional(InpcBase):
    __tablename__ = T.INPC_NACIONAL
    __table_args__ = (UniqueConstraint("fecha", "objeto_gasto_id", name="uq_inpc_nacional"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    objeto_gasto_id: Mapped[int] = mapped_column(ForeignKey(f"{T.OBJETOS_GASTO}.id"), nullable=False)
    indice_de_precios: Mapped[float | None] = mapped_column(Float, nullable=True)
    fecha_actualizacion: Mapped[date] = mapped_column(Date, nullable=False)
