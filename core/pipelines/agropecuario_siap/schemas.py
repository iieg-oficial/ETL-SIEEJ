from sqlalchemy import Float, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from core.pipelines.agropecuario_siap.attributes import AgropecuarioTables as T


class AgropecuarioBase(DeclarativeBase):
    @classmethod
    def columns(cls) -> list[str]:
        return [c.key for c in cls.__table__.columns]


class CatCultivos(AgropecuarioBase):
    __tablename__ = T.CAT_CULTIVOS

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo_siap: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cultivo: Mapped[str] = mapped_column(Text, nullable=False, unique=True)


class CatUnidadesMedida(AgropecuarioBase):
    __tablename__ = T.CAT_UNIDADES_MEDIDA

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    unidad_med: Mapped[str] = mapped_column(Text, nullable=False, unique=True)


class CatModalidades(AgropecuarioBase):
    __tablename__ = T.CAT_MODALIDADES

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    modalidad: Mapped[str] = mapped_column(Text, nullable=False, unique=True)


class CatCiclos(AgropecuarioBase):
    __tablename__ = T.CAT_CICLOS

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    tipo_ciclo: Mapped[str] = mapped_column(Text, nullable=False, unique=True)


class CatCtrsApoyoDesRural(AgropecuarioBase):
    __tablename__ = T.CAT_CTRS_APOYO_DES_RURAL

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo_siap: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ctr_apoyo_des_rural: Mapped[str] = mapped_column(Text, nullable=False, unique=True)


class CatDistritosDesRural(AgropecuarioBase):
    __tablename__ = T.CAT_DISTRITOS_DES_RURAL

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    dis_des_rural: Mapped[str] = mapped_column(Text, nullable=False, unique=True)


class StgAgricola(AgropecuarioBase):
    __tablename__ = T.STG_AGRICOLA
    __table_args__ = (
        UniqueConstraint(
            "anio",
            "entidad_id",
            "municipio_id",
            "distrito_des_rural_id",
            "ctr_apoyo_des_rural_id",
            "cultivo_id",
            "tipo_ciclo_id",
            "modalidad_id",
            name="uq_stg_agricola",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    anio: Mapped[int] = mapped_column(Integer, nullable=False)
    entidad_id: Mapped[int | None] = mapped_column(Integer, nullable=True)  # ref. cvegeo_states
    municipio_id: Mapped[int | None] = mapped_column(Integer, nullable=True)  # ref. cvegeo_municipalities
    distrito_des_rural_id: Mapped[int | None] = mapped_column(
        ForeignKey(f"{T.CAT_DISTRITOS_DES_RURAL}.id"), nullable=True
    )
    ctr_apoyo_des_rural_id: Mapped[int | None] = mapped_column(
        ForeignKey(f"{T.CAT_CTRS_APOYO_DES_RURAL}.id"), nullable=True
    )
    tipo_ciclo_id: Mapped[int | None] = mapped_column(ForeignKey(f"{T.CAT_CICLOS}.id"), nullable=True)
    modalidad_id: Mapped[int | None] = mapped_column(ForeignKey(f"{T.CAT_MODALIDADES}.id"), nullable=True)
    unidad_med_id: Mapped[int | None] = mapped_column(ForeignKey(f"{T.CAT_UNIDADES_MEDIDA}.id"), nullable=True)
    cultivo_id: Mapped[int | None] = mapped_column(ForeignKey(f"{T.CAT_CULTIVOS}.id"), nullable=True)
    sup_sembrada: Mapped[float | None] = mapped_column(Float, nullable=True)
    sup_cosechada: Mapped[float | None] = mapped_column(Float, nullable=True)
    sup_siniestrada: Mapped[float | None] = mapped_column(Float, nullable=True)
    volumen_produccion: Mapped[float | None] = mapped_column(Float, nullable=True)
    rendimiento: Mapped[float | None] = mapped_column(Float, nullable=True)
    precio_med_rural: Mapped[float | None] = mapped_column(Float, nullable=True)
    valor_produccion: Mapped[float | None] = mapped_column(Float, nullable=True)
