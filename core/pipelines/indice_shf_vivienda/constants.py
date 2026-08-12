from typing import Literal

SHEET_NAME: str = "Indice SHF datos abiertos"

# Firma de un archivo XLSX (es un ZIP). gob.mx responde 200 con el HTML de su
# reto de WAF cuando decide bloquear al cliente, así que el status code no
# distingue una descarga buena de una página de error.
XLSX_MAGIC: Literal[b"PK"] = b"PK"

# "Consecutivo" se descarta a propósito: es el número de renglón del Excel, no
# un dato de la serie, y se reinicia en cada publicación.
RENAME_HEADER: dict[str, str] = {
    "Global": "serie_global",
    "Estado": "estado",
    "Municipio": "municipio",
    "Trimestre": "trimestre",
    "Año": "anio",
    "Indice": "indice",
}

# 22 municipios se publican con un espacio al final ("Jesús María ",
# "Zihuatanejo de Azueta "). Sin el strip, el nombre no cruza contra cvegeo.
STRIP_COLS: list[str] = ["serie_global", "estado", "municipio"]

INT_COLS: list[str] = ["anio", "trimestre"]
FLOAT_COLS: list[str] = ["indice"]

GLOBAL_CONFLICT_KEYS: list[str] = ["serie_global_id", "anio", "trimestre"]
ESTATAL_CONFLICT_KEYS: list[str] = ["cve_ent", "anio", "trimestre"]
MUNICIPAL_CONFLICT_KEYS: list[str] = ["cvegeo", "anio", "trimestre"]

# Los tres niveles del Excel viven en columnas mutuamente excluyentes: cuando
# una trae valor las otras van vacías. Son las máscaras que parten la hoja.
LEVEL_GLOBAL: str = "global"
LEVEL_ESTATAL: str = "estatal"
LEVEL_MUNICIPAL: str = "municipal"

# Columnas que identifican a cada nivel, más las que los tres comparten.
LEVEL_COLUMNS: dict[str, list[str]] = {
    LEVEL_GLOBAL: ["serie_global"],
    LEVEL_ESTATAL: ["estado"],
    # El municipio conserva su entidad: la fuente lo identifica solo por nombre y
    # hay nombres repetidos entre entidades ("Benito Juárez", "Juárez").
    LEVEL_MUNICIPAL: ["estado", "municipio"],
}
PERIOD_COLUMNS: list[str] = ["fecha", "anio", "trimestre", "indice"]
