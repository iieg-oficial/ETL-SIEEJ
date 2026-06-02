from datetime import date

from sqlalchemy import Date, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from core.pipelines.escuelas.attributes import EscuelasTables as T


class EscuelasBase(DeclarativeBase):
    @classmethod
    def columns(cls) -> list[str]:
        return [c.key for c in cls.__table__.columns]


class CatTurnos(EscuelasBase):
    __tablename__ = T.CAT_TURNOS

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    nombre_turno: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)


class CatSostenimientos(EscuelasBase):
    __tablename__ = T.CAT_SOSTENIMIENTOS

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sostenimiento: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)


class CatCodigosSostenimiento(EscuelasBase):
    __tablename__ = T.CAT_CODIGOS_SOSTENIMIENTO

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    sostenimiento_id: Mapped[int] = mapped_column(Integer, ForeignKey(f"{T.CAT_SOSTENIMIENTOS}.id"), nullable=False)

    sostenimiento: Mapped["CatSostenimientos"] = relationship()


class CatNiveles(EscuelasBase):
    __tablename__ = T.CAT_NIVELES

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nivel: Mapped[str] = mapped_column(String(60), nullable=False, unique=True)


class CatProgramas(EscuelasBase):
    __tablename__ = T.CAT_PROGRAMAS

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    programa: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)


class CatRegiones(EscuelasBase):
    __tablename__ = T.CAT_REGIONES

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    nombre_region: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)


class CatMedios(EscuelasBase):
    __tablename__ = T.CAT_MEDIOS

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    medio: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)


class CatNivelesPrograma(EscuelasBase):
    __tablename__ = T.CAT_NIVELES_PROGRAMA

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nivel_programa: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)


class StgDirectorioEscuelas(EscuelasBase):
    __tablename__ = T.STG_DIRECTORIO_ESCUELAS
    __table_args__ = (
        UniqueConstraint("anio", "clave_ct", "turno_id", "nivel_id", "programa_id", name="uq_stg_directorio_escuelas"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    anio: Mapped[int] = mapped_column(Integer, nullable=False)
    entidad_id: Mapped[int] = mapped_column(Integer, nullable=False)
    clave_ct: Mapped[str] = mapped_column(String(20), nullable=False)
    turno_id: Mapped[int] = mapped_column(Integer, ForeignKey(f"{T.CAT_TURNOS}.id"), nullable=False)
    nombre_ct: Mapped[str] = mapped_column(String(255), nullable=False)
    domicilio: Mapped[str | None] = mapped_column(Text, nullable=True)
    localidad_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    nombre_localidad: Mapped[str | None] = mapped_column(String(150), nullable=True)
    colonia_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    nombre_colonia: Mapped[str | None] = mapped_column(String(150), nullable=True)
    municipio_id: Mapped[int] = mapped_column(Integer, nullable=False)
    nombre_municipio: Mapped[str | None] = mapped_column(String(150), nullable=True)
    medio_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_MEDIOS}.id"), nullable=True)
    director: Mapped[str | None] = mapped_column(String(255), nullable=True)
    codigo_postal: Mapped[str | None] = mapped_column(String(10), nullable=True)
    telefono: Mapped[str | None] = mapped_column(String(20), nullable=True)
    zona_escolar: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sector: Mapped[int | None] = mapped_column(Integer, nullable=True)
    codigo_sostenimiento_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_CODIGOS_SOSTENIMIENTO}.id"), nullable=True
    )
    nivel_id: Mapped[int] = mapped_column(Integer, ForeignKey(f"{T.CAT_NIVELES}.id"), nullable=False)
    programa_id: Mapped[int] = mapped_column(Integer, ForeignKey(f"{T.CAT_PROGRAMAS}.id"), nullable=False)
    region_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{T.CAT_REGIONES}.id"), nullable=True)
    longitud: Mapped[float | None] = mapped_column(Float, nullable=True)
    latitud: Mapped[float | None] = mapped_column(Float, nullable=True)
    escuelas: Mapped[int] = mapped_column(Integer, nullable=False)
    hombres_matriculados: Mapped[int] = mapped_column(Integer, nullable=False)
    mujeres_matriculadas: Mapped[int] = mapped_column(Integer, nullable=False)
    total_matriculados: Mapped[int] = mapped_column(Integer, nullable=False)
    total_docentes_directivo: Mapped[int] = mapped_column(Integer, nullable=False)
    fecha_actualizacion: Mapped[date] = mapped_column(Date, nullable=False)

    turno: Mapped["CatTurnos"] = relationship()
    codigo_sostenimiento: Mapped["CatCodigosSostenimiento"] = relationship()
    nivel: Mapped["CatNiveles"] = relationship()
    programa: Mapped["CatProgramas"] = relationship()
    region: Mapped["CatRegiones"] = relationship()
    medio: Mapped["CatMedios"] = relationship()


class StgEstadisticaEscuelas(EscuelasBase):
    __tablename__ = T.STG_ESTADISTICA_ESCUELAS
    __table_args__ = (
        UniqueConstraint("anio", "nivel_programa_id", "sostenimiento_id", name="uq_stg_estadistica_escuelas"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    anio: Mapped[int] = mapped_column(Integer, nullable=False)
    nivel_programa_id: Mapped[int] = mapped_column(Integer, ForeignKey(f"{T.CAT_NIVELES_PROGRAMA}.id"), nullable=False)
    sostenimiento_id: Mapped[int] = mapped_column(Integer, ForeignKey(f"{T.CAT_SOSTENIMIENTOS}.id"), nullable=False)
    escuelas: Mapped[int] = mapped_column(Integer, nullable=False)
    matricula: Mapped[int] = mapped_column(Integer, nullable=False)
    docentes: Mapped[int] = mapped_column(Integer, nullable=False)
    fecha_actualizacion: Mapped[date] = mapped_column(Date, nullable=False)

    nivel_programa: Mapped["CatNivelesPrograma"] = relationship()
    sostenimiento: Mapped["CatSostenimientos"] = relationship()
