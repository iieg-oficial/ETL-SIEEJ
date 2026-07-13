from datetime import date

from sqlalchemy import Date, Integer, SmallInteger, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from core.pipelines.nacimientos_dgis.attributes import NacimientosDgisTables as T


class NacimientosDgisBase(DeclarativeBase):
    @classmethod
    def columns(cls) -> list[str]:
        return [c.key for c in cls.__table__.columns]


class StgNacimientos(NacimientosDgisBase):
    __tablename__ = T.STG_NACIMIENTOS
    __table_args__ = (UniqueConstraint("anio", "cve_geo", "edad_madre", name="uq_nacimientos_anio_geo_edad"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    anio: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    cve_geo: Mapped[int] = mapped_column(Integer, nullable=False)
    edad_madre: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    tot_nac: Mapped[int] = mapped_column(Integer, nullable=False)
    nac_padre_conocido: Mapped[int] = mapped_column(Integer, nullable=False)
    nac_padre_18_mas: Mapped[int] = mapped_column(Integer, nullable=False)
    nac_padre_25_mas: Mapped[int] = mapped_column(Integer, nullable=False)
    fecha_actualizacion: Mapped[date] = mapped_column(Date, nullable=False)
