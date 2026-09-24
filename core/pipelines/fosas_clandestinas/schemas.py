from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, SmallInteger, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from core.pipelines.fosas_clandestinas.attributes import FosasClandestinasTables as T


class FosasClandestinasBase(DeclarativeBase):
    @classmethod
    def columns(cls) -> list[str]:
        return [c.key for c in cls.__table__.columns]


class CatPublicaciones(FosasClandestinasBase):
    __tablename__ = T.CAT_PUBLICACIONES

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fecha_corte: Mapped[date] = mapped_column(Date, nullable=False, unique=True)
    archivo: Mapped[str] = mapped_column(Text, nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    modificado: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class StgFosasClandestinas(FosasClandestinasBase):
    __tablename__ = T.STG_FOSAS_CLANDESTINAS

    publicacion_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(f"{T.CAT_PUBLICACIONES}.id", ondelete="CASCADE"), primary_key=True
    )
    consecutivo: Mapped[int] = mapped_column(Integer, primary_key=True)
    periodo: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    denominacion: Mapped[str | None] = mapped_column(Text, nullable=True)
    cve_ent: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # ref. cvegeo_municipalities
    cve_mun: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)  # ref. cvegeo_municipalities
    fecha_inicio: Mapped[date | None] = mapped_column(Date, nullable=True)
    fecha_fin: Mapped[date | None] = mapped_column(Date, nullable=True)
    en_proceso: Mapped[bool] = mapped_column(Boolean, nullable=False)
    pre_victimas_loc: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pre_victimas_ide: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pre_hom_ide: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pre_muj_ide: Mapped[int | None] = mapped_column(Integer, nullable=True)
    estatus_loc: Mapped[str | None] = mapped_column(Text, nullable=True)
