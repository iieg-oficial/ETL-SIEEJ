from datetime import date

from sqlalchemy import Date, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from core.pipelines.conapo.attributes import ConapoTables as T


class ConapoBase(DeclarativeBase):
    @classmethod
    def columns(cls) -> list[str]:
        return [c.key for c in cls.__table__.columns]


class CatSexo(ConapoBase):
    __tablename__ = T.CAT_SEXO

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    sexo: Mapped[str] = mapped_column(String(10), nullable=False)


class StgPoblacionMitadAnio(ConapoBase):
    __tablename__ = T.STG_POBLACION_MITAD_ANIO
    __table_args__ = (UniqueConstraint("municipio_id", "sexo_id", "anio", name="uq_pma_mun_sexo_anio"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    municipio_id: Mapped[int] = mapped_column(Integer, nullable=False)
    entidad_id: Mapped[int] = mapped_column(Integer, nullable=False)
    sexo_id: Mapped[int] = mapped_column(Integer, ForeignKey(f"{T.CAT_SEXO}.id"), nullable=False)
    anio: Mapped[int] = mapped_column(Integer, nullable=False)
    pob_00_04: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pob_05_09: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pob_10_14: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pob_15_19: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pob_20_24: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pob_25_29: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pob_30_34: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pob_35_39: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pob_40_44: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pob_45_49: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pob_50_54: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pob_55_59: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pob_60_64: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pob_65_69: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pob_70_74: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pob_75_79: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pob_80_84: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pob_85_mm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pob_total: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fecha_actualizacion: Mapped[date] = mapped_column(Date, nullable=False)


class StgGrandesGruposEdad(ConapoBase):
    __tablename__ = T.STG_GRANDES_GRUPOS_EDAD
    __table_args__ = (UniqueConstraint("municipio_id", "sexo_id", "anio", name="uq_gge_mun_sexo_anio"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    municipio_id: Mapped[int] = mapped_column(Integer, nullable=False)
    entidad_id: Mapped[int] = mapped_column(Integer, nullable=False)
    sexo_id: Mapped[int] = mapped_column(Integer, ForeignKey(f"{T.CAT_SEXO}.id"), nullable=False)
    anio: Mapped[int] = mapped_column(Integer, nullable=False)
    pob_00_11: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pob_12_29: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pob_30_59: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pob_60_mm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pob_total: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fecha_actualizacion: Mapped[date] = mapped_column(Date, nullable=False)


class StgIndicadoresDemograficos(ConapoBase):
    __tablename__ = T.STG_INDICADORES_DEMOGRAFICOS
    __table_args__ = (UniqueConstraint("municipio_id", "anio", name="uq_idd_mun_anio"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    municipio_id: Mapped[int] = mapped_column(Integer, nullable=False)
    entidad_id: Mapped[int] = mapped_column(Integer, nullable=False)
    anio: Mapped[int] = mapped_column(Integer, nullable=False)
    hom_mit_ano: Mapped[int | None] = mapped_column(Integer, nullable=True)
    muj_mit_ano: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pob_mit_mun: Mapped[int | None] = mapped_column(Integer, nullable=True)
    muj_00_14: Mapped[int | None] = mapped_column(Integer, nullable=True)
    hom_00_14: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pob_00_14: Mapped[int | None] = mapped_column(Integer, nullable=True)
    muj_15_64: Mapped[int | None] = mapped_column(Integer, nullable=True)
    hom_15_64: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pob_15_64: Mapped[int | None] = mapped_column(Integer, nullable=True)
    muj_60_mas: Mapped[int | None] = mapped_column(Integer, nullable=True)
    hom_60_mas: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pob_60_mas: Mapped[int | None] = mapped_column(Integer, nullable=True)
    muj_65_mas: Mapped[int | None] = mapped_column(Integer, nullable=True)
    hom_65_mas: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pob_65_mas: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pob_mit_ent: Mapped[int | None] = mapped_column(Integer, nullable=True)
    edad_med: Mapped[int | None] = mapped_column(Integer, nullable=True)
    por_mun: Mapped[float | None] = mapped_column(Float, nullable=True)
    ind_env_60: Mapped[float | None] = mapped_column(Float, nullable=True)
    ind_env_65: Mapped[float | None] = mapped_column(Float, nullable=True)
    rhm: Mapped[float | None] = mapped_column(Float, nullable=True)
    raz_dep_adu: Mapped[float | None] = mapped_column(Float, nullable=True)
    raz_dep_inf: Mapped[float | None] = mapped_column(Float, nullable=True)
    raz_dep: Mapped[float | None] = mapped_column(Float, nullable=True)
    fecha_actualizacion: Mapped[date] = mapped_column(Date, nullable=False)
