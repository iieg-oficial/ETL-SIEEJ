from datetime import date

from sqlalchemy import Date, Float, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from core.pipelines.denue.attributes import DenueTables as T


class DenueBase(DeclarativeBase):
    @classmethod
    def columns(cls) -> list[str]:
        return [c.key for c in cls.__table__.columns]


class CatActualizaciones(DenueBase):
    __tablename__ = T.CAT_ACTUALIZACIONES

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fecha_actualizacion: Mapped[date] = mapped_column(Date, nullable=False, unique=True)


class CatLocalidades(DenueBase):
    __tablename__ = T.CAT_LOCALIDADES
    __table_args__ = (UniqueConstraint("municipio_id", "entidad_id", "localidad_id", name="uq_localidades_clave"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cve_geo_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    localidad_id: Mapped[int] = mapped_column(Integer, nullable=False)
    municipio_id: Mapped[int] = mapped_column(Integer, nullable=False)
    entidad_id: Mapped[int] = mapped_column(Integer, nullable=False)
    localidad: Mapped[str | None] = mapped_column(Text, nullable=True)


class CatSectores(DenueBase):
    __tablename__ = T.CAT_SECTORES

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    sector: Mapped[str] = mapped_column(Text, nullable=False)


class CatSubsectores(DenueBase):
    __tablename__ = T.CAT_SUBSECTORES

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    subsector: Mapped[str] = mapped_column(Text, nullable=False)


class CatRamas(DenueBase):
    __tablename__ = T.CAT_RAMAS

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    rama: Mapped[str] = mapped_column(Text, nullable=False)


class CatSubramas(DenueBase):
    __tablename__ = T.CAT_SUBRAMAS

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    subrama: Mapped[str] = mapped_column(Text, nullable=False)


class CatClasesActividad(DenueBase):
    __tablename__ = T.CAT_CLASES_ACTIVIDAD

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    clase: Mapped[str] = mapped_column(Text, nullable=False)


class CatRangosPersonal(DenueBase):
    __tablename__ = T.CAT_RANGOS_PERSONAL

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)


class CatTiposEstablecimientos(DenueBase):
    __tablename__ = T.CAT_TIPOS_ESTABLECIMIENTOS

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)


class StgEstablecimientos(DenueBase):
    __tablename__ = T.STG_ESTABLECIMIENTOS

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    actualizacion_id: Mapped[int] = mapped_column(ForeignKey(f"{T.CAT_ACTUALIZACIONES}.id"), primary_key=True)
    nombre_establecimiento: Mapped[str] = mapped_column(Text, nullable=False)
    razon_social: Mapped[str | None] = mapped_column(Text, nullable=True)
    latitud: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitud: Mapped[float | None] = mapped_column(Float, nullable=True)
    fecha_alta: Mapped[date | None] = mapped_column(Date, nullable=True)
    nombre_asentamiento: Mapped[str | None] = mapped_column(Text, nullable=True)
    ageb: Mapped[str | None] = mapped_column(Text, nullable=True)
    localidad_id: Mapped[int | None] = mapped_column(ForeignKey(f"{T.CAT_LOCALIDADES}.id"), nullable=True)
    sector_id: Mapped[int | None] = mapped_column(ForeignKey(f"{T.CAT_SECTORES}.id"), nullable=True)
    subsector_id: Mapped[int | None] = mapped_column(ForeignKey(f"{T.CAT_SUBSECTORES}.id"), nullable=True)
    rama_id: Mapped[int | None] = mapped_column(ForeignKey(f"{T.CAT_RAMAS}.id"), nullable=True)
    subrama_id: Mapped[int | None] = mapped_column(ForeignKey(f"{T.CAT_SUBRAMAS}.id"), nullable=True)
    clase_actividad_id: Mapped[int | None] = mapped_column(ForeignKey(f"{T.CAT_CLASES_ACTIVIDAD}.id"), nullable=True)
    rango_personal_id: Mapped[int | None] = mapped_column(ForeignKey(f"{T.CAT_RANGOS_PERSONAL}.id"), nullable=True)
    tipo_establecimiento_id: Mapped[int | None] = mapped_column(
        ForeignKey(f"{T.CAT_TIPOS_ESTABLECIMIENTOS}.id"), nullable=True
    )
