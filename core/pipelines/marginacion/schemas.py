from datetime import date

from sqlalchemy import Date, Float, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from core.pipelines.marginacion.attributes import MarginacionTables as T


class MarginacionBase(DeclarativeBase):
    @classmethod
    def columns(cls) -> list[str]:
        return [c.key for c in cls.__table__.columns]


class GradosMarginacion(MarginacionBase):
    __tablename__ = T.GRADOS_MARGINACION

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    grado_marginacion: Mapped[str] = mapped_column(Text, nullable=False)


class Localidades(MarginacionBase):
    __tablename__ = T.LOCALIDADES
    __table_args__ = (UniqueConstraint("municipio_id", "entidad_id", "clave_localidad", name="uq_localidades_clave"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cve_geo_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    clave_localidad: Mapped[int] = mapped_column(Integer, nullable=False)
    municipio_id: Mapped[int] = mapped_column(Integer, nullable=False)  # ref. cvegeo_municipalities
    entidad_id: Mapped[int] = mapped_column(Integer, nullable=False)  # ref. cvegeo_states
    localidad: Mapped[str | None] = mapped_column(Text, nullable=True)


class MarginacionesMunicipales(MarginacionBase):
    __tablename__ = T.MARGINACIONES_MUNICIPALES

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    municipio_id: Mapped[int] = mapped_column(Integer, nullable=False)  # ref. cvegeo_municipalities
    grado_marginacion_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.GRADOS_MARGINACION}.id"), nullable=True
    )
    pob_total: Mapped[float | None] = mapped_column(Float, nullable=True)
    porc_pob15_analfabeta: Mapped[float | None] = mapped_column(Float, nullable=True)
    pob15_sin_educ_bas: Mapped[float | None] = mapped_column(Float, nullable=True)
    porc_viv_sin_drenaje_ni_excusado: Mapped[float | None] = mapped_column(Float, nullable=True)
    porc_viv_sin_energia: Mapped[float | None] = mapped_column(Float, nullable=True)
    porc_viv_sin_agua_entubada: Mapped[float | None] = mapped_column(Float, nullable=True)
    porc_viv_piso_tierra: Mapped[float | None] = mapped_column(Float, nullable=True)
    prom_ocup_por_cuarto: Mapped[float | None] = mapped_column(Float, nullable=True)
    porc_pob_loc_menos5000_hab: Mapped[float | None] = mapped_column(Float, nullable=True)
    pob_ocup_hasta_2_sal_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    indice_marginacion: Mapped[float | None] = mapped_column(Float, nullable=True)
    indice_marginacion_normalizado: Mapped[float | None] = mapped_column(Float, nullable=True)
    lugar_contexto_nacional: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fecha_actualizacion: Mapped[date] = mapped_column(Date, nullable=False)


class MarginacionesEstatales(MarginacionBase):
    __tablename__ = T.MARGINACIONES_ESTATALES

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entidad_id: Mapped[int] = mapped_column(Integer, nullable=False)
    grado_marginacion_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.GRADOS_MARGINACION}.id"), nullable=True
    )
    pob_total: Mapped[float | None] = mapped_column(Float, nullable=True)
    porc_pob15_analfabeta: Mapped[float | None] = mapped_column(Float, nullable=True)
    pob15_sin_educ_bas: Mapped[float | None] = mapped_column(Float, nullable=True)
    porc_viv_sin_drenaje_ni_excusado: Mapped[float | None] = mapped_column(Float, nullable=True)
    porc_viv_sin_energia: Mapped[float | None] = mapped_column(Float, nullable=True)
    porc_viv_sin_agua_entubada: Mapped[float | None] = mapped_column(Float, nullable=True)
    porc_viv_piso_tierra: Mapped[float | None] = mapped_column(Float, nullable=True)
    porc_viv_con_hacinamiento: Mapped[float | None] = mapped_column(Float, nullable=True)
    porc_pob_loc_menos5000_hab: Mapped[float | None] = mapped_column(Float, nullable=True)
    pob_ocup_hasta_2_sal_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    porc_viv_sin_refrigerador: Mapped[float | None] = mapped_column(Float, nullable=True)
    indice_marginacion: Mapped[float | None] = mapped_column(Float, nullable=True)
    indice_marginacion_normalizado: Mapped[float | None] = mapped_column(Float, nullable=True)
    lugar_contexto_nacional: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fecha_actualizacion: Mapped[date] = mapped_column(Date, nullable=False)


class MarginacionesLocalidades(MarginacionBase):
    __tablename__ = T.MARGINACIONES_LOCALIDADES

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    localidad_id: Mapped[int] = mapped_column(Integer, ForeignKey(f"{T.LOCALIDADES}.id"), nullable=False)
    grado_marginacion_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(f"{T.GRADOS_MARGINACION}.id"), nullable=True
    )
    pob_total: Mapped[float | None] = mapped_column(Float, nullable=True)
    porc_pob15_analfabeta: Mapped[float | None] = mapped_column(Float, nullable=True)
    porc_pob15_sin_educ_basica: Mapped[float | None] = mapped_column(Float, nullable=True)
    porc_viv_sin_drenaje_ni_excusado: Mapped[float | None] = mapped_column(Float, nullable=True)
    porc_viv_sin_energia: Mapped[float | None] = mapped_column(Float, nullable=True)
    porc_viv_sin_agua_entubada: Mapped[float | None] = mapped_column(Float, nullable=True)
    porc_viv_piso_tierra: Mapped[float | None] = mapped_column(Float, nullable=True)
    prom_ocup_por_cuarto: Mapped[float | None] = mapped_column(Float, nullable=True)
    porc_viv_sin_refrigerador: Mapped[float | None] = mapped_column(Float, nullable=True)
    indice_marginacion: Mapped[float | None] = mapped_column(Float, nullable=True)
    indice_marginacion_normalizado: Mapped[float | None] = mapped_column(Float, nullable=True)
    fecha_actualizacion: Mapped[date] = mapped_column(Date, nullable=False)
