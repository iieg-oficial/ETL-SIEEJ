PIPELINE_NAME = "asg_imss"

SOURCE_URL_TEMPLATE = "http://datos.imss.gob.mx/sites/default/files/asg-{date}.csv"
CATALOG_DICT_URL = "http://datos.imss.gob.mx/sites/default/files/diccionario_de_datos_1.xlsx"
CATALOG_DICT_FILENAME = "diccionario_de_datos_1.xlsx"

# "NA" is intentionally excluded: it appears in IMSS source files as a valid catalog code.
NULL_VALUES = ["NO APLICA", "N/A", "null", "nan", "", "NULL", "None"]

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
