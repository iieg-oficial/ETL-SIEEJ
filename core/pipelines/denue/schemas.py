from datetime import date

from sqlalchemy import Date, Float, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from core.pipelines.denue.attributes import DenueTables as T


class DenueBase(DeclarativeBase):
    @classmethod
    def columns(cls) -> list[str]:
        return [c.key for c in cls.__table__.columns]


class Actualizaciones(DenueBase):
    __tablename__ = T.ACTUALIZACIONES

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fecha_actualizacion: Mapped[date] = mapped_column(Date, nullable=False, unique=True)


class Localidades(DenueBase):
    __tablename__ = T.LOCALIDADES
    __table_args__ = (UniqueConstraint("municipio_id", "entidad_id", "clave_localidad", name="uq_localidades_clave"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cve_geo_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    clave_localidad: Mapped[int] = mapped_column(Integer, nullable=False)
    municipio_id: Mapped[int] = mapped_column(Integer, nullable=False)
    entidad_id: Mapped[int] = mapped_column(Integer, nullable=False)
    localidad: Mapped[str | None] = mapped_column(Text, nullable=True)


class ActividadesEconomicas(DenueBase):
    __tablename__ = T.ACTIVIDADES_ECONOMICAS

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    nombre_actividad_economica: Mapped[str] = mapped_column(Text, nullable=False)


class RangosPersonal(DenueBase):
    __tablename__ = T.RANGOS_PERSONAL

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)


class TiposEstablecimientos(DenueBase):
    __tablename__ = T.TIPOS_ESTABLECIMIENTOS

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)


class Establecimientos(DenueBase):
    __tablename__ = T.ESTABLECIMIENTOS

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    actualizacion_id: Mapped[int] = mapped_column(ForeignKey(f"{T.ACTUALIZACIONES}.id"), primary_key=True)
    nombre_establecimiento: Mapped[str] = mapped_column(Text, nullable=False)
    razon_social: Mapped[str | None] = mapped_column(Text, nullable=True)
    latitud: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitud: Mapped[float | None] = mapped_column(Float, nullable=True)
    fecha_alta: Mapped[date | None] = mapped_column(Date, nullable=True)
    nombre_asentamiento: Mapped[str | None] = mapped_column(Text, nullable=True)
    ageb: Mapped[str | None] = mapped_column(Text, nullable=True)
    localidad_id: Mapped[int | None] = mapped_column(ForeignKey(f"{T.LOCALIDADES}.id"), nullable=True)
    actividad_economica_id: Mapped[int | None] = mapped_column(
        ForeignKey(f"{T.ACTIVIDADES_ECONOMICAS}.id"), nullable=True
    )
    rango_personal_id: Mapped[int | None] = mapped_column(ForeignKey(f"{T.RANGOS_PERSONAL}.id"), nullable=True)
    tipo_establecimiento_id: Mapped[int | None] = mapped_column(
        ForeignKey(f"{T.TIPOS_ESTABLECIMIENTOS}.id"), nullable=True
    )
