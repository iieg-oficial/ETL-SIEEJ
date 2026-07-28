from datetime import date
from sqlalchemy import Date, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from core.pipelines.rastros.attributes import RastrosTables as T


class RastrosBase(DeclarativeBase):
    @classmethod
    def columns(cls) -> list[str]:
        return [c.key for c in cls.__table__.columns]


class CatEstatus(RastrosBase):
    __tablename__ = T.CAT_ESTATUS

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    estatus: Mapped[str] = mapped_column(Text, nullable=False, unique=True)


class CatEspeciesGanaderas(RastrosBase):
    __tablename__ = T.CAT_ESPECIES_GANADERAS

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    especie_ganadera: Mapped[str] = mapped_column(Text, nullable=False, unique=True)


class CatTipoCifra(RastrosBase):
    __tablename__ = T.CAT_TIPO_CIFRA

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tipo_cifra: Mapped[str] = mapped_column(Text, nullable=False, unique=True)


class StgRastros(RastrosBase):
    __tablename__ = T.STG_RASTROS
    __table_args__ = (UniqueConstraint("fecha", "entidad_id", "especie_ganadera_id", name="uq_stg_rastros"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    especie_ganadera_id: Mapped[int] = mapped_column(ForeignKey(f"{T.CAT_ESPECIES_GANADERAS}.id"), nullable=False)
    entidad_id: Mapped[int] = mapped_column(Integer, nullable=False)  # ref. cvegeo_states.cve_ent
    estatus_cabeza_id: Mapped[int | None] = mapped_column(ForeignKey(f"{T.CAT_ESTATUS}.id"), nullable=True)
    estatus_produccion_id: Mapped[int | None] = mapped_column(ForeignKey(f"{T.CAT_ESTATUS}.id"), nullable=True)
    estatus_vproduccion_id: Mapped[int | None] = mapped_column(ForeignKey(f"{T.CAT_ESTATUS}.id"), nullable=True)
    tipo_cifra_id: Mapped[int | None] = mapped_column(ForeignKey(f"{T.CAT_TIPO_CIFRA}.id"), nullable=True)
    numero_cabezas: Mapped[int | None] = mapped_column(Integer, nullable=True)
    produccion_carne: Mapped[int | None] = mapped_column(Integer, nullable=True)
    vproduccion: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_actualizacion: Mapped[date] = mapped_column(Date, nullable=False)
