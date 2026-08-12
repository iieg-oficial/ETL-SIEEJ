from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Integer, Numeric, SmallInteger, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from core.pipelines.indice_shf_vivienda.attributes import IndiceShfViviendaTables as T
from core.pipelines.indice_shf_vivienda.constants import (
    ESTATAL_CONFLICT_KEYS,
    GLOBAL_CONFLICT_KEYS,
    LEVEL_ESTATAL,
    LEVEL_GLOBAL,
    LEVEL_MUNICIPAL,
    MUNICIPAL_CONFLICT_KEYS,
)


class IndiceShfViviendaBase(DeclarativeBase):
    @classmethod
    def columns(cls) -> list[str]:
        return [c.key for c in cls.__table__.columns]


class CatSerieGlobal(IndiceShfViviendaBase):
    """Las 15 series sin desglose geográfico que la fuente agrupa bajo 'Global'."""

    __tablename__ = T.CAT_SERIE_GLOBAL

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    tipo: Mapped[str] = mapped_column(Text, nullable=False)


class IndiceTrimestral:
    """El periodo y la medición, idénticos en los tres niveles.

    Vive en un mixin porque las tres tablas difieren solo en su llave geográfica:
    escribir las mismas cinco columnas tres veces es como se separan con el tiempo.

    Numeric y no Float: el índice es un valor publicado a dos decimales exactos
    (32.59 - 267.83) y el redondeo binario le movería el último dígito.
    """

    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    anio: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    trimestre: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    indice: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    fecha_actualizacion: Mapped[date] = mapped_column(Date, nullable=False)


class StgIndiceShfViviendaGlobal(IndiceTrimestral, IndiceShfViviendaBase):
    """Series nacionales, por condición, tipo, segmento y zona metropolitana."""

    __tablename__ = T.STG_INDICE_SHF_VIVIENDA_GLOBAL
    __table_args__ = (
        UniqueConstraint("serie_global_id", "anio", "trimestre", name="uq_stg_indice_shf_vivienda_global"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    serie_global_id: Mapped[int] = mapped_column(ForeignKey(f"{T.CAT_SERIE_GLOBAL}.id"), nullable=False)


class StgIndiceShfViviendaEstatal(IndiceTrimestral, IndiceShfViviendaBase):
    """Desglose por entidad federativa."""

    __tablename__ = T.STG_INDICE_SHF_VIVIENDA_ESTATAL
    __table_args__ = (UniqueConstraint("cve_ent", "anio", "trimestre", name="uq_stg_indice_shf_vivienda_estatal"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cve_ent: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # ref. cvegeo_states.cve_ent


class StgIndiceShfViviendaMunicipal(IndiceTrimestral, IndiceShfViviendaBase):
    """Desglose de los 74 municipios que SHF publica, no de los 2,469 del país."""

    __tablename__ = T.STG_INDICE_SHF_VIVIENDA_MUNICIPAL
    __table_args__ = (UniqueConstraint("cvegeo", "anio", "trimestre", name="uq_stg_indice_shf_vivienda_municipal"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cvegeo: Mapped[int] = mapped_column(Integer, nullable=False)  # ref. cvegeo_municipalities.cvegeo
    cve_ent: Mapped[int] = mapped_column(SmallInteger, nullable=False)


# El destino de cada nivel y la llave con la que se resuelve el conflicto al
# reescribir una edición. Vive aquí y no en constants.py porque nombra modelos.
LEVEL_MODELS: dict[str, tuple[type[IndiceShfViviendaBase], list[str]]] = {
    LEVEL_GLOBAL: (StgIndiceShfViviendaGlobal, GLOBAL_CONFLICT_KEYS),
    LEVEL_ESTATAL: (StgIndiceShfViviendaEstatal, ESTATAL_CONFLICT_KEYS),
    LEVEL_MUNICIPAL: (StgIndiceShfViviendaMunicipal, MUNICIPAL_CONFLICT_KEYS),
}
