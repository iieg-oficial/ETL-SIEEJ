PIPELINE_NAME = "asg_imss"

SOURCE_URL_TEMPLATE = "http://datos.imss.gob.mx/sites/default/files/asg-{date}.csv"

JALISCO_CVE_ENTIDAD = 14

DOWNLOAD_HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}

# Campos usados para calcular el record_hash (SHA-256)
HASH_FIELDS = [
    "fecha_corte",
    "cve_delegacion",
    "cve_subdelegacion",
    "cve_entidad",
    "cve_municipio",
    "sector_economico_1",
    "sector_economico_2",
    "sector_economico_4",
    "tamanio_patron",
    "sexo",
    "rango_edad",
    "rango_salarial",
    "rango_uma",
]

NULL_VALUES = ["NO APLICA", "NA", "N/A", "null", "nan", "", "NULL", "None"]

# Columnas métricas enteras
METRIC_INT_COLUMNS = [
    "asegurados",
    "no_trabajadores",
    "ta",
    "teu",
    "tec",
    "tpu",
    "tpc",
    "ta_sal",
    "teu_sal",
    "tec_sal",
    "tpu_sal",
    "tpc_sal",
]

# Columnas métricas de punto flotante (masa salarial)
METRIC_FLOAT_COLUMNS = [
    "masa_sal_ta",
    "masa_sal_teu",
    "masa_sal_tec",
    "masa_sal_tpu",
    "masa_sal_tpc",
]

# ---------------------------------------------------------------------------
# Catálogos estáticos
# ---------------------------------------------------------------------------

CATALOG_TAMANIO_PATRON = [
    {"cve": "S1", "descripcion": "Con un puesto de trabajo"},
    {"cve": "S2", "descripcion": "Con 2 y hasta 5 puestos de trabajo"},
    {"cve": "S3", "descripcion": "Con 6 y hasta 50 puestos de trabajo"},
    {"cve": "S4", "descripcion": "Con 51 y hasta 250 puestos de trabajo"},
    {"cve": "S5", "descripcion": "Con 251 y hasta 500 puestos de trabajo"},
    {"cve": "S6", "descripcion": "Con 501 y hasta 1,000 puestos de trabajo"},
    {"cve": "S7", "descripcion": "Con más de 1,000 puestos de trabajo"},
]

CATALOG_SEXO = [
    {"cve": 1, "descripcion": "Hombre"},
    {"cve": 2, "descripcion": "Mujer"},
    {"cve": 3, "descripcion": "No especificado"},
]

CATALOG_RANGO_EDAD = [
    {"cve": "E1", "descripcion": "Menores de 15 años de edad"},
    {"cve": "E2", "descripcion": "Mayor o igual a 15 y menor a 20 años de edad"},
    {"cve": "E3", "descripcion": "Mayor o igual a 20 y menor a 25 años de edad"},
    {"cve": "E4", "descripcion": "Mayor o igual a 25 y menor a 30 años de edad"},
    {"cve": "E5", "descripcion": "Mayor o igual a 30 y menor a 35 años de edad"},
    {"cve": "E6", "descripcion": "Mayor o igual a 35 y menor a 40 años de edad"},
    {"cve": "E7", "descripcion": "Mayor o igual a 40 y menor a 45 años de edad"},
    {"cve": "E8", "descripcion": "Mayor o igual a 45 y menor a 50 años de edad"},
    {"cve": "E9", "descripcion": "Mayor o igual a 50 y menor a 55 años de edad"},
    {"cve": "E10", "descripcion": "Mayor o igual a 55 y menor a 60 años de edad"},
    {"cve": "E11", "descripcion": "Mayor o igual a 60 y menor a 65 años de edad"},
    {"cve": "E12", "descripcion": "Mayor o igual a 65 y menor a 70 años de edad"},
    {"cve": "E13", "descripcion": "Mayor o igual a 70 y menor a 75 años de edad"},
    {"cve": "E14", "descripcion": "75 o más años de edad"},
]

CATALOG_RANGO_SALARIAL = [
    {"cve": "W1", "descripcion": "Hasta 1 vez el salario mínimo"},
    {"cve": "W2", "descripcion": "Mayor a 1 y hasta 2 veces el salario mínimo"},
    {"cve": "W3", "descripcion": "Mayor a 2 y hasta 3 veces el salario mínimo"},
    {"cve": "W4", "descripcion": "Mayor a 3 y hasta 4 veces el salario mínimo"},
    {"cve": "W5", "descripcion": "Mayor a 4 y hasta 5 veces el salario mínimo"},
    {"cve": "W6", "descripcion": "Mayor a 5 y hasta 6 veces el salario mínimo"},
    {"cve": "W7", "descripcion": "Mayor a 6 y hasta 7 veces el salario mínimo"},
    {"cve": "W8", "descripcion": "Mayor a 7 y hasta 8 veces el salario mínimo"},
    {"cve": "W9", "descripcion": "Mayor a 8 y hasta 9 veces el salario mínimo"},
    {"cve": "W10", "descripcion": "Mayor a 9 y hasta 10 veces el salario mínimo"},
    {"cve": "W11", "descripcion": "Mayor a 10 o más veces el salario mínimo"},
]

CATALOG_RANGO_UMA = [
    {"cve": "W1", "descripcion": "Hasta 1 vez la UMA"},
    {"cve": "W2", "descripcion": "Mayor a 1 y hasta 2 veces la UMA"},
    {"cve": "W3", "descripcion": "Mayor a 2 y hasta 3 veces la UMA"},
    {"cve": "W4", "descripcion": "Mayor a 3 y hasta 4 veces la UMA"},
    {"cve": "W5", "descripcion": "Mayor a 4 y hasta 5 veces la UMA"},
    {"cve": "W6", "descripcion": "Mayor a 5 y hasta 6 veces la UMA"},
    {"cve": "W7", "descripcion": "Mayor a 6 y hasta 7 veces la UMA"},
    {"cve": "W8", "descripcion": "Mayor a 7 y hasta 8 veces la UMA"},
    {"cve": "W9", "descripcion": "Mayor a 8 y hasta 9 veces la UMA"},
    {"cve": "W10", "descripcion": "Mayor a 9 y hasta 10 veces la UMA"},
    {"cve": "W11", "descripcion": "Mayor a 10 y hasta 11 veces la UMA"},
    {"cve": "W12", "descripcion": "Mayor a 11 y hasta 12 veces la UMA"},
    {"cve": "W13", "descripcion": "Mayor a 12 y hasta 13 veces la UMA"},
    {"cve": "W14", "descripcion": "Mayor a 13 y hasta 14 veces la UMA"},
    {"cve": "W15", "descripcion": "Mayor a 14 y hasta 15 veces la UMA"},
    {"cve": "W16", "descripcion": "Mayor a 15 y hasta 16 veces la UMA"},
    {"cve": "W17", "descripcion": "Mayor a 16 y hasta 17 veces la UMA"},
    {"cve": "W18", "descripcion": "Mayor a 17 y hasta 18 veces la UMA"},
    {"cve": "W19", "descripcion": "Mayor a 18 y hasta 19 veces la UMA"},
    {"cve": "W20", "descripcion": "Mayor a 19 y hasta 20 veces la UMA"},
    {"cve": "W21", "descripcion": "Mayor a 20 y hasta 21 veces la UMA"},
    {"cve": "W22", "descripcion": "Mayor a 21 y hasta 22 veces la UMA"},
    {"cve": "W23", "descripcion": "Mayor a 22 y hasta 23 veces la UMA"},
    {"cve": "W24", "descripcion": "Mayor a 23 y hasta 24 veces la UMA"},
    {"cve": "W25", "descripcion": "Mayor a 24 o más veces la UMA"},
]
