from sqlalchemy import Boolean, Float, Integer, SmallInteger, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from core.pipelines.enoe.attributes import EnoeTables as T


class EnoeBase(DeclarativeBase):
    @classmethod
    def columns(cls) -> list[str]:
        return [c.key for c in cls.__table__.columns]


class CatSector(EnoeBase):
    __tablename__ = T.CAT_SECTOR

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)


class CatOcupacion(EnoeBase):
    __tablename__ = T.CAT_OCUPACION

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)


class CatSituacionTrabajo(EnoeBase):
    __tablename__ = T.CAT_SITUACION_TRABAJO

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)


class CatTipoLocalidad(EnoeBase):
    __tablename__ = T.CAT_TIPO_LOCALIDAD

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)


class CatEstadoCivil(EnoeBase):
    __tablename__ = T.CAT_ESTADO_CIVIL

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)


class CatNivelEducativo(EnoeBase):
    __tablename__ = T.CAT_NIVEL_EDUCATIVO

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)


class StgEnoe(EnoeBase):
    __tablename__ = T.STG_ENOE
    __table_args__ = (
        UniqueConstraint(
            "anio",
            "trimestre",
            "cd_a",
            "entidad_id",
            "con",
            "v_sel",
            "n_hog",
            "h_mud",
            "n_ent",
            "n_ren",
            name="uq_stg_enoe_persona",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    anio: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    trimestre: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    # Identificadores de persona (clave natural)
    entidad_id: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    municipio_id: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    tipo_localidad_id: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    cd_a: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    con: Mapped[int] = mapped_column(Integer, nullable=False)
    v_sel: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    n_hog: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    h_mud: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    n_ent: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    n_ren: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    # Sociodemográfico
    eda: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    nac_anio: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    sex: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    habla_lengua_indigena: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    n_inf: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    estado_civil_id: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    nivel_educativo_id: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    cs_p13_2: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    # Condición de empleo
    clase1: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    clase2: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    clase3: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    dur9c: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    hrsocup: Mapped[float | None] = mapped_column(Float, nullable=True)
    ingocup: Mapped[float | None] = mapped_column(Float, nullable=True)
    ma48me1sm: Mapped[float | None] = mapped_column(Float, nullable=True)
    emp_ppal: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    sector_id: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    ocupacion_id: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    situacion_trabajo_id: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    seg_soc: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    pre_asa: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    # Factor de expansión
    fac: Mapped[float | None] = mapped_column(Float, nullable=True)
    # Indicadores derivados
    es_pea: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    es_ocupado: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    es_desocupado: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    es_informal: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
