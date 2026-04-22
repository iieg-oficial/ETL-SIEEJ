from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from core.pipelines.censo_poblacion.attributes.censo_poblacion import CensoPoblacionTables as T


class CensoPoblacionBase(DeclarativeBase):
    @classmethod
    def columns(cls) -> list[str]:
        return [c.key for c in cls.__table__.columns]


class Localidades(CensoPoblacionBase):
    __tablename__ = T.LOCALIDADES

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    localidad: Mapped[str] = mapped_column(Text, nullable=False)


class Fuentes(CensoPoblacionBase):
    __tablename__ = T.FUENTES

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    fecha: Mapped[int] = mapped_column(Integer, nullable=False)


class Poblacion(CensoPoblacionBase):
    __tablename__ = T.POBLACION

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entidad_id: Mapped[int] = mapped_column(Integer, nullable=False)
    municipio_id: Mapped[int] = mapped_column(Integer, nullable=False)
    localidad_id: Mapped[int | None] = mapped_column(ForeignKey(f"{T.LOCALIDADES}.id"), nullable=True)
    fuente_id: Mapped[int] = mapped_column(ForeignKey(f"{T.FUENTES}.id"), nullable=False)
    total: Mapped[int] = mapped_column(Integer, nullable=False)
    total_mujeres: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_hombres: Mapped[int | None] = mapped_column(Integer, nullable=True)
    viviendas_habitadas: Mapped[int | None] = mapped_column(Integer, nullable=True)
