from typing import Final

JALISCO_ENT: Final[int] = 14

JOIN_KEY: Final[list[str]] = ["cd_a", "ent", "con", "v_sel", "n_hog", "h_mud", "n_ent", "n_ren"]

# Columns to select from SDEM before renaming
SDEM_COLS: Final[list[str]] = [
    "cd_a", "ent", "cve_ent", "con", "v_sel", "n_hog", "h_mud", "n_ent", "n_ren",
    "mun", "cve_mun",                      # cve_mun (2025 T3+), mun (anterior)
    "t_loc_tri", "t_loc",                  # t_loc_tri (2008+), t_loc (2005-2007)
    "sex", "eda", "nac_anio", "cs_p17", "n_hij", "e_con", "cs_p13_1", "cs_p13_2",
    "clase1", "clase2", "clase3",
    "dur9c", "hrsocup", "ingocup", "ma48me1sm",
    "emp_ppal", "rama_est1", "c_ocu11c", "tue_ppal", "seg_soc", "pre_asa",
    "fac_tri", "fac",                      # fac_tri (2008+), fac (2005-2007)
]

RENAME_HEADER: Final[dict] = {
    "ent": "entidad_id",
    "cve_ent": "entidad_id",              # nombre nuevo (2025 T3+)
    "mun": "municipio_id",
    "cve_mun": "municipio_id",            # nombre nuevo (2025 T3+)
    "t_loc_tri": "tipo_localidad_id",
    "t_loc": "tipo_localidad_id",         # nombre antiguo (2005-2007)
    "n_hij": "n_inf",
    "e_con": "estado_civil_id",
    "cs_p13_1": "nivel_educativo_id",
    "rama_est1": "sector_id",
    "c_ocu11c": "ocupacion_id",
    "tue_ppal": "situacion_trabajo_id",
    "fac_tri": "fac",                     # fac_tri → fac (2008+); fac antiguo ya tiene el nombre correcto
}

NULL_VALUES: Final[list[str]] = ["", "N/A", "NA", "n/a", "na", "null", "NULL", " "]

# Nombres originales del SDEM (pre-rename), usados para cast de tipos en transform
INT_COLS: Final[set[str]] = {
    "ent", "cve_ent", "mun", "cve_mun", "t_loc_tri", "t_loc", "cd_a", "con", "v_sel",
    "n_hog", "h_mud", "n_ent", "n_ren", "sex", "eda", "nac_anio", "n_hij",
    "e_con", "cs_p13_1", "cs_p13_2", "clase1", "clase2", "clase3",
    "dur9c", "emp_ppal", "rama_est1", "c_ocu11c", "tue_ppal",
    "seg_soc", "pre_asa",
}

FLOAT_COLS: Final[set[str]] = {"hrsocup", "ingocup", "ma48me1sm", "fac_tri", "fac"}
