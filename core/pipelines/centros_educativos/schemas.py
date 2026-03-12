from sqlalchemy import Column, Integer, String, Float, ForeignKey, UniqueConstraint, Text, Date
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import date

from core.pipelines.centros_educativos.attributes.centros_educativos import CentrosEducativosTables as T


class CentrosEducativosBase(DeclarativeBase):
    @classmethod
    def columns(cls) -> list[str]:
        return [c.key for c in cls.__table__.columns]


class Turnos(CentrosEducativosBase):
    """Catalogo de turnos educativos."""

    __tablename__ = T.TURNOS

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    turno: Mapped[str] = mapped_column(Text, nullable=False)


class TiposEducativos(CentrosEducativosBase):
    """Catalogo de tipos educativos."""

    __tablename__ = T.TIPOS_EDUCATIVOS

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    tipo_educativo: Mapped[str] = mapped_column(Text, nullable=False)


class NivelesEducativos(CentrosEducativosBase):
    """Catalogo de niveles educativos."""

    __tablename__ = T.NIVELES_EDUCATIVOS

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    nivel_educativo: Mapped[str] = mapped_column(Text, nullable=False)


class ServiciosEducativos(CentrosEducativosBase):
    """Catalogo de servicios educativos."""

    __tablename__ = T.SERVICIOS_EDUCATIVOS

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    servicio_educativo: Mapped[str] = mapped_column(Text, nullable=False)


class TiposControles(CentrosEducativosBase):
    """Catalogo de tipos de control."""

    __tablename__ = T.TIPOS_CONTROLES

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    tipo_control: Mapped[str] = mapped_column(Text, nullable=False)


class TiposSostenimiento(CentrosEducativosBase):
    """Catalogo de tipos de sostenimiento."""

    __tablename__ = T.TIPOS_SOSTENIMIENTO

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    tipo_sostenimiento: Mapped[str] = mapped_column(Text, nullable=False)


class Localidades(CentrosEducativosBase):
    """Catalogo de localidades."""

    __tablename__ = T.LOCALIDADES
    __table_args__ = (
        UniqueConstraint("municipio_id", "entidad_id", "clave_localidad", name="uq_localidades_clave"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cve_geo_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    clave_localidad: Mapped[int] = mapped_column(Integer, nullable=False)
    municipio_id: Mapped[int] = mapped_column(Integer, nullable=False)  # ref. cvegeo_municipalities
    entidad_id: Mapped[int] = mapped_column(Integer, nullable=False)    # ref. cvegeo_states
    localidad: Mapped[str | None] = mapped_column(Text, nullable=True)


class Domicilios(CentrosEducativosBase):
    """Catalogo de domicilios."""

    __tablename__ = T.DOMICILIOS

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    domicilio: Mapped[str] = mapped_column(Text, nullable=False)
    numero_exterior: Mapped[str | None] = mapped_column(Text, nullable=True)
    codigo_postal: Mapped[str | None] = mapped_column(String(10), nullable=True)
    entre_calle: Mapped[str | None] = mapped_column(Text, nullable=True)
    y_calle: Mapped[str | None] = mapped_column(Text, nullable=True)
    calle_posterior: Mapped[str | None] = mapped_column(Text, nullable=True)


class Colonias(CentrosEducativosBase):
    """Catalogo de colonias."""

    __tablename__ = T.COLONIAS

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    colonia: Mapped[str] = mapped_column(Text, nullable=False)
    localidad_id: Mapped[int] = mapped_column(Integer, ForeignKey(f"{T.LOCALIDADES}.id"), nullable=False)


class Centros(CentrosEducativosBase):
    """Tabla principal de centros educativos."""

    __tablename__ = T.CENTROS

    clave_centro_trabajo: Mapped[str] = mapped_column(String(20), primary_key=True)
    nombre_centro_trabajo: Mapped[str] = mapped_column(Text, nullable=False)
    turno_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.TURNOS}.id"), nullable=True)
    tipos_educativos_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.TIPOS_EDUCATIVOS}.id"), nullable=True)
    nivel_educativo_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.NIVELES_EDUCATIVOS}.id"), nullable=True)
    servicio_educativo_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.SERVICIOS_EDUCATIVOS}.id"), nullable=True)
    tipo_control_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.TIPOS_CONTROLES}.id"), nullable=True)
    tipo_sostenimiento_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.TIPOS_SOSTENIMIENTO}.id"), nullable=True)
    entidad_id: Mapped[int | None] = mapped_column(Integer, nullable=True)     # ref. cvegeo_states
    municipio_id: Mapped[int | None] = mapped_column(Integer, nullable=True)   # ref. cvegeo_municipalities
    localidades_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.LOCALIDADES}.id"), nullable=True)
    domicilios_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.DOMICILIOS}.id"), nullable=True)
    colonias_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.COLONIAS}.id"), nullable=True)
    total_alumnos_hombres: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_alumnas_mujeres: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_docentes_hombres: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_docentes_mujeres: Mapped[int | None] = mapped_column(Integer, nullable=True)
    aulas_en_uso: Mapped[int | None] = mapped_column(Integer, nullable=True)
    aulas_existentes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    latitud: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitud: Mapped[float | None] = mapped_column(Float, nullable=True)
    fecha_actualizacion: Mapped[date] = mapped_column(Date, nullable=False)


