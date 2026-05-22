from sqlalchemy import Float, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from core.pipelines.participacion_ciudadana.attributes import ParticipacionCiudadanaTables as T


class ParticipacionCiudadanaBase(DeclarativeBase):
    @classmethod
    def columns(cls) -> list[str]:
        return [c.key for c in cls.__table__.columns]


class StgParticipacion(ParticipacionCiudadanaBase):
    __tablename__ = T.STG_PARTICIPACION

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entidad_id: Mapped[int] = mapped_column(Integer, nullable=False)
    municipio_id: Mapped[int] = mapped_column(Integer, nullable=False)
    porc_participacion: Mapped[float] = mapped_column(Float, nullable=False)
    anio: Mapped[int] = mapped_column(Integer, nullable=False)
