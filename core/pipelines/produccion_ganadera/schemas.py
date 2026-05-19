from sqlalchemy import Float, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from core.pipelines.produccion_ganadera.attributes import GanaderaTables as T


class GanaderaBase(DeclarativeBase):
    @classmethod
    def columns(cls) -> list[str]:
        return [c.key for c in cls.__table__.columns]


class CatEspecies(GanaderaBase):
    __tablename__ = T.CAT_ESPECIES

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    especie: Mapped[str] = mapped_column(Text, nullable=False, unique=True)


class CatProductos(GanaderaBase):
    __tablename__ = T.CAT_PRODUCTOS

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    producto: Mapped[str] = mapped_column(Text, nullable=False)


class CatDistritosDesRural(GanaderaBase):
    __tablename__ = T.CAT_DISTRITOS_DES_RURAL

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    dis_des_rural: Mapped[str] = mapped_column(Text, nullable=False, unique=True)


class StgGanadera(GanaderaBase):
    __tablename__ = T.STG_GANADERA
    __table_args__ = (
        UniqueConstraint(
            "anio",
            "entidad_id",
            "municipio_id",
            "distrito_des_rural_id",
            "especie_id",
            "producto_id",
            name="uq_stg_ganadera",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    anio: Mapped[int] = mapped_column(Integer, nullable=False)
    entidad_id: Mapped[int | None] = mapped_column(Integer, nullable=True)  # ref. cvegeo_states
    municipio_id: Mapped[int | None] = mapped_column(Integer, nullable=True)  # ref. cvegeo_municipalities
    distrito_des_rural_id: Mapped[int | None] = mapped_column(
        ForeignKey(f"{T.CAT_DISTRITOS_DES_RURAL}.id"), nullable=True
    )
    especie_id: Mapped[int | None] = mapped_column(ForeignKey(f"{T.CAT_ESPECIES}.id"), nullable=True)
    producto_id: Mapped[int | None] = mapped_column(ForeignKey(f"{T.CAT_PRODUCTOS}.id"), nullable=True)
    volumen_produccion: Mapped[float | None] = mapped_column(Float, nullable=True)
    peso_sacrificio: Mapped[float | None] = mapped_column(Float, nullable=True)
    precio_med_rural: Mapped[float | None] = mapped_column(Float, nullable=True)
    valor_produccion: Mapped[float | None] = mapped_column(Float, nullable=True)
    animales_sacrificados: Mapped[float | None] = mapped_column(Float, nullable=True)
