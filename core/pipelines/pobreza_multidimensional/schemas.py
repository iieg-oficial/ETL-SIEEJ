from datetime import datetime
from typing import Optional

from sqlalchemy import Float, Index, Integer, SmallInteger, String, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class PobrezaMultidimensionalBase(DeclarativeBase):
    pass


class CatEntidad(PobrezaMultidimensionalBase):
    """Catálogo de entidades federativas."""

    __tablename__ = "stg_pobreza_multidimensional_cat_entidad"
    __table_args__ = (UniqueConstraint("cve_ent", name="uq_pobreza_multidimensional_cat_entidad_cve"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cve_ent: Mapped[str] = mapped_column(String(2), nullable=False)
    nombre_entidad: Mapped[str] = mapped_column(String(100), nullable=False)


class PobrezaMultidimensionalDatos(PobrezaMultidimensionalBase):
    """Indicadores de pobreza municipal CONEVAL — una fila por municipio × año."""

    __tablename__ = "stg_pobreza_multidimensional_datos"
    __table_args__ = (
        UniqueConstraint(
            "cve_mun",
            "anio",
            name="uq_pobreza_multidimensional_datos_cve_anio",
        ),
        Index("ix_pobreza_multidimensional_datos_cve_anio", "cve_mun", "anio", unique=True),
        Index("ix_pobreza_multidimensional_datos_anio", "anio"),
        Index("ix_pobreza_multidimensional_datos_entidad", "cat_entidad_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Identificadores geográficos
    cve_mun: Mapped[str] = mapped_column(String(5), nullable=False)
    nombre_municipio: Mapped[Optional[str]] = mapped_column(String(150))
    cat_entidad_id: Mapped[int] = mapped_column(Integer, nullable=False)

    # Temporalidad
    anio: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    poblacion: Mapped[Optional[int]] = mapped_column(Integer)

    # Pobreza total
    pobreza_porcentaje: Mapped[Optional[float]] = mapped_column(Float)
    pobreza_personas: Mapped[Optional[int]] = mapped_column(Integer)
    pobreza_promedio: Mapped[Optional[float]] = mapped_column(Float)

    # Pobreza extrema
    pobreza_ext_porcentaje: Mapped[Optional[float]] = mapped_column(Float)
    pobreza_ext_personas: Mapped[Optional[int]] = mapped_column(Integer)
    pobreza_ext_promedio: Mapped[Optional[float]] = mapped_column(Float)

    # Pobreza moderada
    pobreza_mod_porcentaje: Mapped[Optional[float]] = mapped_column(Float)
    pobreza_mod_personas: Mapped[Optional[int]] = mapped_column(Integer)
    pobreza_mod_promedio: Mapped[Optional[float]] = mapped_column(Float)

    # Vulnerables por carencia social
    vul_carencia_porcentaje: Mapped[Optional[float]] = mapped_column(Float)
    vul_carencia_personas: Mapped[Optional[int]] = mapped_column(Integer)
    vul_carencia_promedio: Mapped[Optional[float]] = mapped_column(Float)

    # Vulnerables por ingreso (sin carencias_promedio en fuente)
    vul_ingreso_porcentaje: Mapped[Optional[float]] = mapped_column(Float)
    vul_ingreso_personas: Mapped[Optional[int]] = mapped_column(Integer)

    # No pobre y no vulnerable (sin carencias_promedio en fuente)
    no_pobre_porcentaje: Mapped[Optional[float]] = mapped_column(Float)
    no_pobre_personas: Mapped[Optional[int]] = mapped_column(Integer)

    # Rezago educativo
    rez_edu_porcentaje: Mapped[Optional[float]] = mapped_column(Float)
    rez_edu_personas: Mapped[Optional[int]] = mapped_column(Integer)
    rez_edu_promedio: Mapped[Optional[float]] = mapped_column(Float)

    # Carencia por acceso a servicios de salud
    car_salud_porcentaje: Mapped[Optional[float]] = mapped_column(Float)
    car_salud_personas: Mapped[Optional[int]] = mapped_column(Integer)
    car_salud_promedio: Mapped[Optional[float]] = mapped_column(Float)

    # Carencia por acceso a seguridad social
    car_seg_soc_porcentaje: Mapped[Optional[float]] = mapped_column(Float)
    car_seg_soc_personas: Mapped[Optional[int]] = mapped_column(Integer)
    car_seg_soc_promedio: Mapped[Optional[float]] = mapped_column(Float)

    # Carencia por calidad y espacios de la vivienda
    car_viv_porcentaje: Mapped[Optional[float]] = mapped_column(Float)
    car_viv_personas: Mapped[Optional[int]] = mapped_column(Integer)
    car_viv_promedio: Mapped[Optional[float]] = mapped_column(Float)

    # Carencia por acceso a servicios básicos de la vivienda
    car_sbv_porcentaje: Mapped[Optional[float]] = mapped_column(Float)
    car_sbv_personas: Mapped[Optional[int]] = mapped_column(Integer)
    car_sbv_promedio: Mapped[Optional[float]] = mapped_column(Float)

    # Carencia por acceso a la alimentación
    car_ali_porcentaje: Mapped[Optional[float]] = mapped_column(Float)
    car_ali_personas: Mapped[Optional[int]] = mapped_column(Integer)
    car_ali_promedio: Mapped[Optional[float]] = mapped_column(Float)

    # Población con al menos una carencia social
    al_1_car_porcentaje: Mapped[Optional[float]] = mapped_column(Float)
    al_1_car_personas: Mapped[Optional[int]] = mapped_column(Integer)
    al_1_car_promedio: Mapped[Optional[float]] = mapped_column(Float)

    # Población con tres o más carencias sociales
    tres_mas_car_porcentaje: Mapped[Optional[float]] = mapped_column(Float)
    tres_mas_car_personas: Mapped[Optional[int]] = mapped_column(Integer)
    tres_mas_car_promedio: Mapped[Optional[float]] = mapped_column(Float)

    # Ingreso < línea de pobreza
    lpi_porcentaje: Mapped[Optional[float]] = mapped_column(Float)
    lpi_personas: Mapped[Optional[int]] = mapped_column(Integer)
    lpi_promedio: Mapped[Optional[float]] = mapped_column(Float)

    # Ingreso < línea de pobreza extrema
    lpei_porcentaje: Mapped[Optional[float]] = mapped_column(Float)
    lpei_personas: Mapped[Optional[int]] = mapped_column(Integer)
    lpei_promedio: Mapped[Optional[float]] = mapped_column(Float)

    created_at: Mapped[Optional[datetime]] = mapped_column(server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(server_default=func.now(), onupdate=func.now())


CATALOG_MODELS: dict[str, type] = {
    "entidad": CatEntidad,
}
