from sqlalchemy import Boolean, Float, Integer, SmallInteger, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from core.pipelines.enoe_microdatos.attributes import EnoeMicrodatosTables as T


class EnoeMicrodatosBase(DeclarativeBase):
    @classmethod
    def columns(cls) -> list[str]:
        return [c.key for c in cls.__table__.columns]


class CatEnoeSecor(EnoeMicrodatosBase):
    __tablename__ = T.CAT_ENOE_SECTOR

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)


class CatEnoeOcupacion(EnoeMicrodatosBase):
    __tablename__ = T.CAT_ENOE_OCUPACION

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)


class CatEnoeSituacionTrabajo(EnoeMicrodatosBase):
    __tablename__ = T.CAT_ENOE_SITUACION_TRABAJO

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)


class StgEnoeMicrodatos(EnoeMicrodatosBase):
    __tablename__ = T.STG_ENOE_MICRODATOS
    __table_args__ = (
        UniqueConstraint(
            "anio",
            "trimestre",
            "cd_a",
            "entidad_id",
            "con",
            "v_sel",
            "n_hog",
            "h_mud",
            "n_ent",
            "n_ren",
            name="uq_stg_enoe_microdatos_persona",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    anio: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    trimestre: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    # SDEM: diseño muestral
    r_def: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    est: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    est_d_tri: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    est_d_men: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    ageb: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    upm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    d_sem: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    n_pro_viv: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    per: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    tipo: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    mes_cal: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    # SDEM: identificadores de persona (clave natural)
    cd_a: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    entidad_id: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    con: Mapped[int] = mapped_column(Integer, nullable=False)
    v_sel: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    n_hog: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    h_mud: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    n_ent: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    n_ren: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    # SDEM: geografía
    loc: Mapped[str | None] = mapped_column(Text, nullable=True)
    municipio_id: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    tipo_localidad_id: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    t_loc_men: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    ur: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    zona: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    # SDEM: sociodemográfico
    c_res: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    par_c: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    sex: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    eda: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    nac_dia: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    nac_mes: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    nac_anio: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    l_nac_c: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    # SDEM: educación
    cs_p12: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    cs_p13_1: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    cs_p13_2: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    cs_p14_c: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cs_p15: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    cs_p16: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    cs_p17: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    niv_ins: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    anios_esc: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    # SDEM: hijos
    n_hij: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    hij5c: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    # SDEM: estado civil
    e_con: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    # SDEM: migración
    cs_p20a_1: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    cs_p20a_c: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    cs_p20b_1: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    cs_p20b_c: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    cs_p20c_1: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    cs_ad_mot: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    cs_p21_des: Mapped[str | None] = mapped_column(Text, nullable=True)
    cs_ad_des: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    cs_nr_mot: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    cs_p23_des: Mapped[str | None] = mapped_column(Text, nullable=True)
    cs_nr_ori: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    # SDEM: clasificación de actividad
    clase1: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    clase2: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    clase3: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    seg_soc: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    rama: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    rama_est2: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    ing7c: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    dur9c: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    emple7c: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    medica5c: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    buscar5c: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    dur_est: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    ambito1: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    ambito2: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    scian: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    # SDEM: búsqueda y disponibilidad
    dispo: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    nodispo: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    c_inac5c: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    pnea_est: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    busqueda: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    d_ant_lab: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    d_cexp_est: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    dur_des: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    # SDEM: informalidad (TIL1)
    tue1: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    tue2: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    tue3: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    tue_ppal: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    emp_ppal: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    trans_ppal: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    sub_o: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    s_clasifi: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    remune2c: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    pre_asa: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    tip_con: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    sec_ins: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    mh_fil2: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    mh_col: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    t_tra: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    # SDEM: trabajo doméstico y edades derivadas
    domestico: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    eda5c: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    eda7c: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    eda12c: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    eda19c: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    # SDEM: horas e ingresos
    hrsocup: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    ingocup: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ing_x_hrs: Mapped[float | None] = mapped_column(Float, nullable=True)
    salario: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # SDEM: tasas y complementos
    tpg_p8a: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    tcco: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    cp_anoc: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    imssissste: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    ma48me1sm: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    p14apoyos: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    # SDEM: factor de expansión
    fac: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fac_men: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # FKs a catálogos
    sector_id: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    ocupacion_id: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    situacion_trabajo_id: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    # De COE1
    p3b: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    p3i: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    # De COE2
    p10b: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    # Indicadores derivados
    es_pea: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    es_ocupado: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    es_desocupado: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    es_informal: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
