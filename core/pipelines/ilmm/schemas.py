from datetime import date

from sqlalchemy import BigInteger, Date, ForeignKey, Numeric, SmallInteger, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from core.pipelines.ilmm.attributes import IlmmTables as T


class IlmmBase(DeclarativeBase):
    @classmethod
    def columns(cls) -> list[str]:
        return [c.key for c in cls.__table__.columns]


class IlmmEstimador(IlmmBase):
    __tablename__ = T.ILMM_ESTIMADOR

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, autoincrement=False)
    descripcion: Mapped[str] = mapped_column(String(60), nullable=False)


class IlmmIndicador(IlmmBase):
    __tablename__ = T.ILMM_INDICADOR

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, autoincrement=False)
    indicador: Mapped[str] = mapped_column(String(40), nullable=False, unique=True)


class Ilmm(IlmmBase):
    __tablename__ = T.ILMM
    __table_args__ = (
        UniqueConstraint("clave_municipio", "fecha", "indicador_id", name="uq_stg_ilmm"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    clave_municipio: Mapped[str] = mapped_column(String(5), nullable=False)
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    indicador_id: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey(f"{T.ILMM_INDICADOR}.id"), nullable=False
    )
    valor: Mapped[float | None] = mapped_column(Numeric(12, 4), nullable=True)
    error_estandar: Mapped[float | None] = mapped_column(Numeric(12, 4), nullable=True)
