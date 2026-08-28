"""Contrato de los ZIP que publica INEGI en el programa EDR.

La ubicación y los tiempos de descarga son configuración y viven en `config.py`.
Aquí queda lo que describe el formato del archivo, que no depende del entorno.
"""

from typing import Final

# INEGI responde 200 con una página de error cuando el año no existe, así que el
# descubrimiento se valida por Content-Type y no por código HTTP.
ZIP_CONTENT_TYPES: Final[tuple[str, ...]] = (
    "application/zip",
    "application/x-zip-compressed",
    "application/octet-stream",
)

# Las ediciones 2017-2024 son UTF-8; latin-1 queda como red por si INEGI
# vuelve al encoding que usa en otros programas.
SOURCE_ENCODINGS: Final[tuple[str, ...]] = ("utf-8", "latin-1")

FACT_MEMBER_DIR: Final[str] = "conjunto_de_datos/"
CATALOG_MEMBER_DIR: Final[str] = "catalogos/"

# `Nota.txt` y la bitácora de cambios viven junto al CSV de hechos.
FACT_MEMBER_EXCLUDE: Final[tuple[str, ...]] = ("nota", "bitacora")

CLAVE_ALIASES: Final[tuple[str, ...]] = ("cve", "clave", "cvegeo", "cap")
DESCRIPCION_ALIASES: Final[tuple[str, ...]] = ("descrip", "descripcion", "nom_loc")
