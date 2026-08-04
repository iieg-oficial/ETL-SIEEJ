from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from core.pipelines.scian.attributes import ScianTables as T


class ScianBase(DeclarativeBase):
    @classmethod
    def columns(cls) -> list[str]:
        return [c.key for c in cls.__table__.columns]


class Sectores(ScianBase):
    __tablename__ = T.SECTORES

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String(5), nullable=False, unique=True)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    comparable_trinacional: Mapped[bool] = mapped_column(Boolean, nullable=False)


class Subsectores(ScianBase):
    __tablename__ = T.SUBSECTORES

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String(3), nullable=False, unique=True)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    comparable_trinacional: Mapped[bool] = mapped_column(Boolean, nullable=False)
    sector_id: Mapped[int] = mapped_column(ForeignKey(f"{T.SECTORES}.id"), nullable=False)


class Ramas(ScianBase):
    __tablename__ = T.RAMAS

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String(4), nullable=False, unique=True)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    comparable_trinacional: Mapped[bool] = mapped_column(Boolean, nullable=False)
    subsector_id: Mapped[int] = mapped_column(ForeignKey(f"{T.SUBSECTORES}.id"), nullable=False)


class Subramas(ScianBase):
    __tablename__ = T.SUBRAMAS

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String(5), nullable=False, unique=True)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    comparable_trinacional: Mapped[bool] = mapped_column(Boolean, nullable=False)
    rama_id: Mapped[int] = mapped_column(ForeignKey(f"{T.RAMAS}.id"), nullable=False)


class Clases(ScianBase):
    __tablename__ = T.CLASES

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String(6), nullable=False, unique=True)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    subrama_id: Mapped[int] = mapped_column(ForeignKey(f"{T.SUBRAMAS}.id"), nullable=False)
