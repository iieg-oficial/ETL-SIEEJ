from datetime import date, datetime

from sqlalchemy import DateTime, Date, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from core.pipelines.secretaria_educacion.attributes import SecretariaEducacionTables as T


class SecretariaEducacionBase(DeclarativeBase):
    @classmethod
    def columns(cls) -> list[str]:
        return [c.key for c in cls.__table__.columns]


class CatTurnos(SecretariaEducacionBase):
    __tablename__ = T.CAT_TURNOS

    # El id es el código de la fuente y no es secuencial: 120 corresponde a MAT-VESP.
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    nombre_turno: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)


class CatMedios(SecretariaEducacionBase):
    __tablename__ = T.CAT_MEDIOS

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    medio: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)


class CatSostenimientos(SecretariaEducacionBase):
    __tablename__ = T.CAT_SOSTENIMIENTOS

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sostenimiento: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)


class CatNiveles(SecretariaEducacionBase):
    __tablename__ = T.CAT_NIVELES

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nivel: Mapped[str] = mapped_column(String(60), nullable=False, unique=True)


class CatProgramas(SecretariaEducacionBase):
    __tablename__ = T.CAT_PROGRAMAS

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    programa: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)


class CatRegiones(SecretariaEducacionBase):
    __tablename__ = T.CAT_REGIONES

    # El id es el código regional de la fuente: 121 corresponde a CENTRO ZMG.
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    nombre_region: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)


class CatProgramasEstrategicos(SecretariaEducacionBase):
    __tablename__ = T.CAT_PROGRAMAS_ESTRATEGICOS

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    programa_estrategico: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)


class CatRegionesOperativas(SecretariaEducacionBase):
    """Regionalización propia de la SEJ, distinta de la estatal de cat_regiones."""

    __tablename__ = T.CAT_REGIONES_OPERATIVAS

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    region_operativa: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)


class StgDirectorioCentrosTrabajo(SecretariaEducacionBase):
    __tablename__ = T.STG_DIRECTORIO_CENTROS_TRABAJO
    __table_args__ = (
        UniqueConstraint(
            "fecha_corte",
            "clave_ct",
            "turno_id",
            "nivel_id",
            "programa_id",
            name="uq_stg_directorio_centros_trabajo",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fecha_corte: Mapped[date] = mapped_column(Date, nullable=False)
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
    sostenimiento_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_SOSTENIMIENTOS}.id"), nullable=True
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
    fecha_actualizacion_fuente: Mapped[date | None] = mapped_column(Date, nullable=True)
    fecha_actualizacion: Mapped[date] = mapped_column(Date, nullable=False)

    turno: Mapped["CatTurnos"] = relationship()
    medio: Mapped["CatMedios"] = relationship()
    sostenimiento: Mapped["CatSostenimientos"] = relationship()
    nivel: Mapped["CatNiveles"] = relationship()
    programa: Mapped["CatProgramas"] = relationship()
    region: Mapped["CatRegiones"] = relationship()


class StgEscuelasProgramas(SecretariaEducacionBase):
    """Relación entre centros de trabajo y programas estratégicos."""

    __tablename__ = T.STG_ESCUELAS_PROGRAMAS
    __table_args__ = (
        UniqueConstraint(
            "fecha_corte",
            "clave_ct",
            "programa_estrategico_id",
            name="uq_stg_escuelas_programas",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fecha_corte: Mapped[date] = mapped_column(Date, nullable=False)
    clave_ct: Mapped[str] = mapped_column(String(20), nullable=False)
    programa_estrategico_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_PROGRAMAS_ESTRATEGICOS}.id"), nullable=False
    )
    fecha_actualizacion_fuente: Mapped[date | None] = mapped_column(Date, nullable=True)
    fecha_actualizacion: Mapped[date] = mapped_column(Date, nullable=False)

    programa_estrategico: Mapped["CatProgramasEstrategicos"] = relationship()


class StgAulasGoogle(SecretariaEducacionBase):
    __tablename__ = T.STG_AULAS_GOOGLE
    __table_args__ = (UniqueConstraint("fecha_corte", "clave_ct", "nombre_ct", name="uq_stg_aulas_google"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fecha_corte: Mapped[date] = mapped_column(Date, nullable=False)
    clave_ct: Mapped[str] = mapped_column(String(20), nullable=False)
    nombre_ct: Mapped[str] = mapped_column(String(255), nullable=False)
    inmueble: Mapped[str | None] = mapped_column(String(20), nullable=True)
    region_operativa_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_REGIONES_OPERATIVAS}.id"), nullable=True
    )
    nombre_municipio: Mapped[str | None] = mapped_column(String(150), nullable=True)
    aulas_asignadas: Mapped[int] = mapped_column(Integer, nullable=False)
    fecha_actualizacion_fuente: Mapped[date | None] = mapped_column(Date, nullable=True)
    fecha_actualizacion: Mapped[date] = mapped_column(Date, nullable=False)

    region_operativa: Mapped["CatRegionesOperativas"] = relationship()


class CargasAcervo(SecretariaEducacionBase):
    """Control de envíos procesados: da el watermark y evita recargas sin cambios."""

    __tablename__ = T.CARGAS_ACERVO
    __table_args__ = (UniqueConstraint("envio_id", "object_key", name="uq_cargas_acervo"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    envio_id: Mapped[int] = mapped_column(Integer, nullable=False)
    conjunto: Mapped[str] = mapped_column(String(255), nullable=False)
    object_key: Mapped[str] = mapped_column(Text, nullable=False)
    etag: Mapped[str | None] = mapped_column(String(64), nullable=True)
    fecha_corte: Mapped[date | None] = mapped_column(Date, nullable=True)
    fecha_actualizacion_fuente: Mapped[date | None] = mapped_column(Date, nullable=True)
    actualizado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    procesado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
