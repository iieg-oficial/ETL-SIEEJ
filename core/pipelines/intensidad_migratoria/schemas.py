from sqlalchemy import Float, Integer, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from core.pipelines.intensidad_migratoria.attributes.intensidad_migratoria import IntensidadMigratoriaTable as T


class IntensidadMigratoriaBase(DeclarativeBase):
    @classmethod
    def columns(cls) -> list[str]:
        return [c.key for c in cls.__table__.columns]


class IimMunicipal(IntensidadMigratoriaBase):
    __tablename__ = T.IIM_MUNICIPAL
    __table_args__ = (UniqueConstraint("municipio_id", "fecha", name="uq_iim_municipal"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    municipio_id: Mapped[int] = mapped_column(Integer, nullable=False)
    viv_totales: Mapped[int | None] = mapped_column(Integer, nullable=True)
    por_viv_remesas: Mapped[float | None] = mapped_column(Float, nullable=True)
    por_viv_emigrantes: Mapped[float | None] = mapped_column(Float, nullable=True)
    por_viv_circ: Mapped[float | None] = mapped_column(Float, nullable=True)
    por_viv_reto: Mapped[float | None] = mapped_column(Float, nullable=True)
    iim_dp2: Mapped[float | None] = mapped_column(Float, nullable=True)
    grado_iim: Mapped[str | None] = mapped_column(Text, nullable=True)
    lugar_contexto_nacional: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fecha: Mapped[int] = mapped_column(Integer, nullable=False)


class IimEstatal(IntensidadMigratoriaBase):
    __tablename__ = T.IIM_ESTATAL
    __table_args__ = (UniqueConstraint("entidad_id", "fecha", name="uq_iim_estatal"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entidad_id: Mapped[int] = mapped_column(Integer, nullable=False)
    viv_totales: Mapped[int | None] = mapped_column(Integer, nullable=True)
    por_viv_remesas: Mapped[float | None] = mapped_column(Float, nullable=True)
    por_viv_emigrantes: Mapped[float | None] = mapped_column(Float, nullable=True)
    por_viv_circ: Mapped[float | None] = mapped_column(Float, nullable=True)
    por_viv_reto: Mapped[float | None] = mapped_column(Float, nullable=True)
    iim_dp2: Mapped[float | None] = mapped_column(Float, nullable=True)
    grado_iim: Mapped[str | None] = mapped_column(Text, nullable=True)
    lugar_contexto_nacional: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fecha: Mapped[int] = mapped_column(Integer, nullable=False)
