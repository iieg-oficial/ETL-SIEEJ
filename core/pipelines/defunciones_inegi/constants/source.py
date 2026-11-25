"""Contrato de los ZIP que publica INEGI en el programa EDR.

La ubicación y los tiempos de descarga son configuración y viven en `config.py`.
Aquí queda lo que describe el formato del archivo, que no depende del entorno.
"""

from typing import Final

# Las ediciones 2017-2024 son UTF-8; latin-1 queda como red por si INEGI
# vuelve al encoding que usa en otros programas.
SOURCE_ENCODINGS: Final[tuple[str, ...]] = ("utf-8", "latin-1")

# INEGI responde 200 con una página de error cuando el año no existe, así que el
# código HTTP no basta. Todo ZIP empieza con la firma `PK\x03\x04`: leer los
# primeros bytes lo distingue de esa página sin bajar el archivo.
ZIP_SIGNATURE: Final[bytes] = b"PK"

# Contrato del catálogo de descarga masiva (`SOURCE_CATALOG_URL`). Un registro:
#   {"anioInformacion": "|2025",
#    "formato": "_csv.zip&29.2  MB&CON_ESTANDAR|",
#    "pathLogico": "/programas/edr/datosabiertos/conjunto_de_datos_edr2025",
#    "tipoInformacion": "Datos abiertos"}
# URL del archivo = SOURCE_CONTENT_URL + pathLogico + sufijo del formato.
CATALOG_YEAR_FIELD: Final[str] = "anioInformacion"
CATALOG_PATH_FIELD: Final[str] = "pathLogico"
CATALOG_FORMAT_FIELD: Final[str] = "formato"
CATALOG_TYPE_FIELD: Final[str] = "tipoInformacion"

CATALOG_OPEN_DATA_TYPE: Final[str] = "Datos abiertos"
CATALOG_FORMAT_SUFFIX: Final[str] = "_csv.zip"

# `anioInformacion` y `formato` son listas separadas por `|`; cada entrada de
# `formato` es `sufijo&peso&estándar`.
CATALOG_LIST_SEPARATOR: Final[str] = "|"
CATALOG_FORMAT_PART_SEPARATOR: Final[str] = "&"

FACT_MEMBER_DIR: Final[str] = "conjunto_de_datos/"
CATALOG_MEMBER_DIR: Final[str] = "catalogos/"

# `Nota.txt` y la bitácora de cambios viven junto al CSV de hechos.
FACT_MEMBER_EXCLUDE: Final[tuple[str, ...]] = ("nota", "bitacora")

CLAVE_ALIASES: Final[tuple[str, ...]] = ("cve", "clave", "cvegeo", "cap")
DESCRIPCION_ALIASES: Final[tuple[str, ...]] = ("descrip", "descripcion", "nom_loc")
