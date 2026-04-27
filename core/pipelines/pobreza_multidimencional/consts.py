PIPELINE_NAME = "pobreza_multidimencional"

DATA_YEARS: list[int] = [2016, 2018, 2020, 2022]

# Ruta del directorio que contiene el CSV dentro del ZIP
ZIP_CSV_DIR_TEMPLATE: str = "python/Python_MMP_{year}/Base final"

# Strings que representan nulos en la fuente
NULL_VALUES: list[str] = ["N/A", "n/a", "S/N", "s/n", "ND", "n.d.", "-", "--", ""]

# Directorio de catálogos ENIGH
CATALOG_CSV_DIR: str = "catalogos_enigh"

# Columnas que se castean a float
FLOAT_COLS: list[str] = [
    "factor",
    "ic_rezedu",
    "inas_esc",
    "niv_ed",
    "ic_asalud",
    "ic_segsoc",
    "sa_dir",
    "ss_dir",
    "s_salud",
    "par",
    "jef_ss",
    "cony_ss",
    "hijo_ss",
    "pea",
    "jub",
    "pam",
    "ing_pam",
    "ic_cv",
    "icv_pisos",
    "icv_muros",
    "icv_techos",
    "icv_hac",
    "ic_sbv",
    "isb_agua",
    "isb_dren",
    "isb_luz",
    "isb_combus",
    "ic_ali_nc",
    "id_men",
    "tot_iaad",
    "tot_iamen",
    "ins_ali",
    "ic_ali",
    "lca",
    "dch",
    "plp_e",
    "plp",
    "pobreza",
    "pobreza_e",
    "pobreza_m",
    "vul_car",
    "vul_ing",
    "no_pobv",
    "i_privacion",
    "carencias",
    "carencias3",
    "prof1",
    "prof_e1",
    "profun",
    "int_pob",
    "int_pobe",
    "int_vulcar",
    "int_caren",
    "tamhogesc",
    "ictpc",
    "ict",
    "ing_mon",
    "ing_lab",
    "ing_ren",
    "ing_tra",
    "nomon",
    "pago_esp",
    "reg_esp",
    "hli",
    "discap",
    "rururb",
]

# Columnas que se castean a entero
INT_COLS: list[str] = [
    "folioviv",
    "foliohog",
    "numren",
    "est_dis",
    "upm",
    "ent",
    "ubica_geo",
    "edad",
    "sexo",
    "parentesco",
    "anac_e",
    "tam_loc",
    "cuadrantes",
]
