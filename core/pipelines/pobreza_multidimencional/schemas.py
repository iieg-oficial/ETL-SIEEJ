from typing import Optional

from sqlalchemy import BigInteger, Float, Integer, SmallInteger, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class PobrezaMultidimencionalBase(DeclarativeBase):
    pass


# ----- Catálogos -----


class CatEntidad(PobrezaMultidimencionalBase):
    """Catálogo de entidades federativas — fuente: cat_entidades_federativas.csv."""

    __tablename__ = "stg_pobreza_multidimencional_cat_entidad"
    __table_args__ = (UniqueConstraint("codigo", name="uq_pm_cat_entidad_codigo"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    nombre: Mapped[str] = mapped_column(Text, nullable=False)


class CatParentesco(PobrezaMultidimencionalBase):
    """Catálogo de parentesco — fuente: cat_parentesco.csv."""

    __tablename__ = "stg_pobreza_multidimencional_cat_parentesco"
    __table_args__ = (UniqueConstraint("codigo", name="uq_pm_cat_parentesco_codigo"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    nombre: Mapped[str] = mapped_column(Text, nullable=False)


# ----- Tabla principal -----


class PobrezaMultidimencionalDatos(PobrezaMultidimencionalBase):
    """Microdatos de pobreza multidimensional CONEVAL — Base final MMP."""

    __tablename__ = "stg_pobreza_multidimencional_datos"
    __table_args__ = (
        UniqueConstraint(
            "folioviv",
            "foliohog",
            "numren",
            "anio",
            name="uq_pm_datos_llave",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    anio: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    folioviv: Mapped[int] = mapped_column(BigInteger, nullable=False)
    foliohog: Mapped[int] = mapped_column(Integer, nullable=False)
    numren: Mapped[int] = mapped_column(Integer, nullable=False)
    est_dis: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    upm: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    factor: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    tam_loc: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)
    rururb: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ent: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ubica_geo: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    municipio_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    edad: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    sexo: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)
    parentesco: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    anac_e: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ic_rezedu: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    inas_esc: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    niv_ed: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ic_asalud: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ic_segsoc: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sa_dir: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ss_dir: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    s_salud: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    par: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    jef_ss: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cony_ss: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    hijo_ss: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    pea: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    jub: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    pam: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ing_pam: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ic_cv: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    icv_pisos: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    icv_muros: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    icv_techos: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    icv_hac: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ic_sbv: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    isb_agua: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    isb_dren: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    isb_luz: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    isb_combus: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ic_ali_nc: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    id_men: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    tot_iaad: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    tot_iamen: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ins_ali: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ic_ali: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    lca: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    dch: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    plp_e: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    plp: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    pobreza: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    pobreza_e: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    pobreza_m: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    vul_car: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    vul_ing: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    no_pobv: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    i_privacion: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    carencias: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    carencias3: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cuadrantes: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)
    prof1: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    prof_e1: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    profun: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    int_pob: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    int_pobe: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    int_vulcar: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    int_caren: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    tamhogesc: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ictpc: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ict: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ing_mon: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ing_lab: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ing_ren: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ing_tra: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    nomon: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    pago_esp: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    reg_esp: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    hli: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    discap: Mapped[Optional[float]] = mapped_column(Float, nullable=True)


CATALOG_MODELS: dict[str, type] = {
    "entidad": CatEntidad,
    "parentesco": CatParentesco,
}
