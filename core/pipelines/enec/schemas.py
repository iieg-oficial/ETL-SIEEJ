from datetime import date

from sqlalchemy import BigInteger, Date, Float, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from core.pipelines.enec.attributes import EnecTables as T


class EnecBase(DeclarativeBase):
    @classmethod
    def columns(cls) -> list[str]:
        return [c.key for c in cls.__table__.columns]


class CatEstatus(EnecBase):
    __tablename__ = T.CAT_ESTATUS

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    estatus: Mapped[str] = mapped_column(Text, nullable=False, unique=True)


class CatActividad(EnecBase):
    __tablename__ = T.CAT_ACTIVIDAD

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo_actividad: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)


class EnecMeasures:
    """The 44 measures both datasets publish, identical in name and meaning.

    Lives in a mixin because the national and the state tables differ only in
    their key: writing the same 44 columns twice is how they drift apart.

    BigInteger for the money: the largest value published today is 110,075,469
    and these are current-peso aggregates that only grow.
    """

    # Personal ocupado
    dias_trabajados: Mapped[float | None] = mapped_column(Float, nullable=True)
    per_ocu_tot: Mapped[int | None] = mapped_column(Integer, nullable=True)
    per_ocu_dependiente: Mapped[int | None] = mapped_column(Integer, nullable=True)
    per_ocu_obreros: Mapped[int | None] = mapped_column(Integer, nullable=True)
    per_ocu_administrativos: Mapped[int | None] = mapped_column(Integer, nullable=True)
    per_ocu_no_remunerados: Mapped[int | None] = mapped_column(Integer, nullable=True)
    per_ocu_subcontratado: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Horas trabajadas
    horas_tot: Mapped[float | None] = mapped_column(Float, nullable=True)
    horas_dependiente: Mapped[float | None] = mapped_column(Float, nullable=True)
    horas_obreros: Mapped[float | None] = mapped_column(Float, nullable=True)
    horas_administrativos: Mapped[float | None] = mapped_column(Float, nullable=True)
    horas_no_remunerados: Mapped[float | None] = mapped_column(Float, nullable=True)
    horas_subcontratado: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Remuneraciones
    remuneraciones_tot: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    salarios_obreros: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    sueldos_administrativos: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    prestaciones: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    # Remuneraciones medias
    remuneracion_media_persona: Mapped[float | None] = mapped_column(Float, nullable=True)
    remuneracion_media_hora: Mapped[float | None] = mapped_column(Float, nullable=True)
    remuneracion_media_salarios: Mapped[float | None] = mapped_column(Float, nullable=True)
    salario_medio_obreros: Mapped[float | None] = mapped_column(Float, nullable=True)
    sueldo_medio_administrativos: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Gastos
    gastos_tot: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    gasto_materiales_contratista: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    gasto_materiales_subcontratista: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    gasto_suministro_personal: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    gasto_subcontratistas: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    gastos_otros: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    consumo_materiales_contratista: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    consumo_materiales_subcontratista: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    # Ingresos
    ingresos_tot: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    ingresos_contratista: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    ingresos_subcontratista: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    ingresos_administracion: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    ingresos_otros: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    # Valor de producción
    valor_produccion: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    valor_produccion_edificacion: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    valor_produccion_agua_riego: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    valor_produccion_electricidad: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    valor_produccion_transporte: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    valor_produccion_petroleo: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    valor_produccion_otras: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    valor_produccion_publico: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    valor_produccion_privado: Mapped[int | None] = mapped_column(BigInteger, nullable=True)


class StgEnecNacional(EnecMeasures, EnecBase):
    """Total nacional, desglosado por actividad de la construcción."""

    __tablename__ = T.STG_ENEC_NACIONAL
    __table_args__ = (UniqueConstraint("fecha", "codigo_actividad", name="uq_stg_enec_nacional"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    codigo_actividad: Mapped[int] = mapped_column(ForeignKey(f"{T.CAT_ACTIVIDAD}.codigo_actividad"), nullable=False)
    estatus_id: Mapped[int | None] = mapped_column(ForeignKey(f"{T.CAT_ESTATUS}.id"), nullable=True)
    fecha_actualizacion: Mapped[date] = mapped_column(Date, nullable=False)


class StgEnecEntidad(EnecMeasures, EnecBase):
    """Desglose por entidad federativa, solo del sector 23 (construcción)."""

    __tablename__ = T.STG_ENEC_ENTIDAD
    __table_args__ = (UniqueConstraint("fecha", "entidad_id", name="uq_stg_enec_entidad"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    entidad_id: Mapped[int] = mapped_column(Integer, nullable=False)  # ref. cvegeo_states.cve_ent, más el 33
    estatus_id: Mapped[int | None] = mapped_column(ForeignKey(f"{T.CAT_ESTATUS}.id"), nullable=True)
    fecha_actualizacion: Mapped[date] = mapped_column(Date, nullable=False)
