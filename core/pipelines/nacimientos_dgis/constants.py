PIPELINE_NAME = "nacimientos_dgis"

USECOLS = [
    "ENTIDADRESIDENCIA",
    "MUNICIPIORESIDENCIA",
    "EDAD",
    "EDADPADRE",
    "FECHANACIMIENTO",
]

EDADPADRE_INVALID = {888, 999}

DOWNLOAD_TIMEOUT = 300

COPY_COLS = [
    "anio",
    "cve_geo",
    "edad_madre",
    "tot_nac",
    "nac_padre_conocido",
    "nac_padre_18_mas",
    "nac_padre_25_mas",
    "fecha_actualizacion",
]
