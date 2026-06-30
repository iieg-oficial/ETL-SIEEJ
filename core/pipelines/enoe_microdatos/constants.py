from typing import Final

JALISCO_ENT: Final[int] = 14

JOIN_KEYS: Final[list[str]] = ["cd_a", "ent", "con", "v_sel", "n_hog", "h_mud", "n_ent", "n_ren"]

SDEM_COLS: Final[list[str]] = [
    # diseño muestral
    "r_def", "loc", "mun", "est", "est_d_tri", "est_d_men", "ageb",
    "t_loc_tri", "t_loc_men", "cd_a", "ent", "con", "upm", "d_sem",
    "n_pro_viv", "v_sel", "n_hog", "h_mud", "n_ent", "per", "n_ren",
    "c_res", "tipo", "mes_cal",
    # geografía
    "ur", "zona",
    # sociodemográfico
    "par_c", "sex", "eda", "nac_dia", "nac_mes", "nac_anio", "l_nac_c",
    # educación
    "cs_p12", "cs_p13_1", "cs_p13_2", "cs_p14_c", "cs_p15", "cs_p16", "cs_p17",
    "niv_ins", "anios_esc",
    # hijos
    "n_hij", "hij5c",
    # estado civil
    "e_con",
    # migración
    "cs_p20a_1", "cs_p20a_c", "cs_p20b_1", "cs_p20b_c", "cs_p20c_1",
    "cs_ad_mot", "cs_p21_des", "cs_ad_des", "cs_nr_mot", "cs_p23_des", "cs_nr_ori",
    # clasificación de actividad
    "clase1", "clase2", "clase3", "pos_ocu", "seg_soc",
    "rama", "c_ocu11c", "ing7c", "dur9c", "emple7c", "medica5c", "buscar5c",
    "rama_est1", "rama_est2", "dur_est", "ambito1", "ambito2", "scian",
    # búsqueda y disponibilidad
    "dispo", "nodispo", "c_inac5c", "pnea_est", "busqueda",
    "d_ant_lab", "d_cexp_est", "dur_des",
    # informalidad (TIL1)
    "tue1", "tue2", "tue3", "tue_ppal", "emp_ppal", "trans_ppal",
    "sub_o", "s_clasifi", "remune2c", "pre_asa", "tip_con",
    "sec_ins", "mh_fil2", "mh_col", "t_tra",
    # trabajo doméstico y edades derivadas
    "domestico", "eda5c", "eda7c", "eda12c", "eda19c",
    # horas e ingresos
    "hrsocup", "ingocup", "ing_x_hrs", "salario",
    # tasas y complementos
    "tpg_p8a", "tcco", "cp_anoc", "imssissste", "ma48me1sm", "p14apoyos",
    # factor de expansión
    "fac_tri", "fac_men",
    # variante de nombres históricos (presente solo en algunos años)
    "cve_ent",   # ent en 2025 T3+
    "cve_mun",   # mun en 2025 T3+
    "t_loc",     # t_loc_tri en 2005-2007
    "fac",       # fac_tri en 2005-2007
]

COE1_COLS: Final[list[str]] = JOIN_KEYS + ["p3b", "p3i"]

COE2_COLS: Final[list[str]] = JOIN_KEYS + ["p10b"]

RENAME_HEADER: Final[dict] = {
    "ent": "entidad_id",
    "cve_ent": "entidad_id",
    "mun": "municipio_id",
    "cve_mun": "municipio_id",
    "t_loc_tri": "tipo_localidad_id",
    "t_loc": "tipo_localidad_id",
    "rama_est1": "sector_id",
    "c_ocu11c": "ocupacion_id",
    "pos_ocu": "situacion_trabajo_id",
    "fac_tri": "fac",
}

NULL_VALUES: Final[list[str]] = ["", "N/A", "NA", "n/a", "na", "null", "NULL", " "]

# Columnas str en pandas que contienen códigos numéricos enteros
INT_COLS: Final[set[str]] = {
    "mun", "cve_mun", "est_d_men", "t_loc_men",
    "par_c", "sex", "eda", "nac_dia", "nac_mes", "nac_anio", "l_nac_c",
    "cs_p12", "cs_p13_1", "cs_p13_2", "cs_p14_c", "cs_p15", "cs_p16", "cs_p17",
    "n_hij", "e_con",
    "cs_p20a_1", "cs_p20a_c", "cs_p20b_1", "cs_p20b_c", "cs_p20c_1",
    "cs_ad_mot", "cs_ad_des", "cs_nr_mot", "cs_nr_ori",
    # COE1
    "p3b", "p3i",
}

FLOAT_COLS: Final[set[str]] = {"ing_x_hrs"}

# Columnas que deben permanecer como TEXT
TEXT_COLS: Final[set[str]] = {"loc", "cs_p21_des", "cs_p23_des"}
