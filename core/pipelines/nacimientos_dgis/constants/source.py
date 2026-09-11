"""Columnas del CSV de SINAC y ubicación de los catálogos publicados aparte."""

from typing import Final

PIPELINE_NAME: Final[str] = "nacimientos_dgis"

DOWNLOAD_TIMEOUT: Final[int] = 600

# Las cinco columnas que el pipeline ya usaba para el agregado por edad de la madre.
AGGREGATE_COLS: Final[tuple[str, ...]] = (
    "ENTIDADRESIDENCIA",
    "MUNICIPIORESIDENCIA",
    "EDAD",
    "EDADPADRE",
    "FECHANACIMIENTO",
)

# Los 30 campos del certificado que pide el issue #298.
CERTIFICATE_COLS: Final[tuple[str, ...]] = (
    "SECONSIDERAINDIGENA",
    "HABLALENGUAINDIGENA",
    "ESTADOCONYUGAL",
    "LOCALIDADRESIDENCIA",
    "NUMEROEMBARAZOS",
    "ATENCIONPRENATAL",
    "TOTALCONSULTAS",
    "SOBREVIVIOPARTO",
    "AFILIACION",
    "ESCOLARIDAD",
    "INTERRUMPIOESTUDIOS",
    "CLAVEOCUPACIONHABITUAL",
    "TRABAJAACTUALMENTE",
    "HORANACIMIENTO",
    "SEXO",
    "EDADGESTACIONAL",
    "TALLA",
    "PESO",
    "PRODUCTOEMBARAZO",
    "ORDENPRODUCTO",
    "TOTALPRODUCTOS",
    "CODIGOCIEANOMALIA1",
    "CODIGOCIEANOMALIA2",
    "LUGARNACIMIENTO",
    "CLUES",
    "TIEMPOTRASLADO",
    "RESOLUCIONEMBARAZO",
    "ENTIDADFEDERATIVAPARTO",
    "MUNICIPIOPARTO",
    "LOCALIDADPARTO",
)

USECOLS: Final[list[str]] = [*AGGREGATE_COLS, *CERTIFICATE_COLS]

CSV_SUFFIX: Final[str] = ".csv"
ZIP_SUFFIX: Final[str] = ".zip"
XLSX_SUFFIX: Final[str] = ".xlsx"

CATALOG_DIR: Final[str] = "catalogos"
FACTS_DIR: Final[str] = "certificados"
MANIFEST_NAME: Final[str] = "manifest.pkl"
CATALOGS_FILE: Final[str] = "catalogos.pkl"
AGGREGATE_FILE: Final[str] = "nacimientos.pkl"

# DGIS publica un paquete de catálogos por rango de ediciones, no uno por año.
# El más reciente que cubre al año pedido es el que gana.
CATALOG_EDITIONS: Final[tuple[tuple[int, int, str], ...]] = (
    (2020, 2023, "sinac_catalogos_2020_2023.zip"),
    (2024, 2024, "sinac_catalogos_2024.zip"),
    (2025, 2025, "sinac_catalogos_2025.zip"),
)

# Los nombres de archivo se mueven entre ediciones ("MUNICIPIOS_202201 (2).xlsx"
# contra "MUNICIPIOS.xlsx"), así que el miembro se busca por prefijo, no exacto.
CATALOG_MEMBERS: Final[dict[str, tuple[str, ...]]] = {
    "cat_si_no": ("SI_NO",),
    "cat_sexo": ("SEXO",),
    "cat_estado_conyugal": ("ESTADO_CONYUGAL",),
    "cat_escolaridad": ("ESCOLARIDAD",),
    "cat_afiliacion": ("AFILIACION_CERTIFICADOS", "AFILIACION"),
    "cat_ocupacion_habitual": ("OCUPACION_HABITUAL",),
    "cat_lugar_nacimiento": ("LUGAR_NACIMIENTO",),
    "cat_producto_embarazo": ("PRODUCTO_EMBARAZO",),
    "cat_resolucion_embarazo": ("RESOLUCION_EMBARAZO",),
    "cat_entidad": ("ENTIDADES",),
    "cat_municipio": ("MUNICIPIOS",),
    "cat_localidad": ("LOCALIDADES",),
    "cat_diagnostico": ("DIAGNOSTICOS",),
    "cat_establecimiento_salud": ("ESTABLECIMIENTOS_SALUD", "ESTABLECIMIENTO_SALUD"),
}

# Encabezados posibles de la columna de clave y de descripción en los XLSX.
# Los nombres cambian entre paquetes: el de 2024 publica las localidades como
# EFE_KEY/MUN_KEY/CATALOG_KEY/LOCALIDAD y el de 2020-2023 como
# CVE_ENT/CVE_MUN/CVE_LOC/NOM_LOC. Se resuelve por alias, no por posición.
CLAVE_ALIASES: Final[tuple[str, ...]] = ("clave", "catalog_key", "clues", "cve_loc", "cve_mun")
DESCRIPCION_ALIASES: Final[tuple[str, ...]] = ("descripcion", "descripción")

ENTIDAD_KEY_ALIASES: Final[tuple[str, ...]] = ("efe_key", "cve_ent")
MUNICIPIO_KEY_ALIASES: Final[tuple[str, ...]] = ("mun_key", "cve_mun")

# Clave del propio nivel, para los catálogos de clave compuesta.
MUNICIPIO_CLAVE_ALIASES: Final[tuple[str, ...]] = ("catalog_key", "cve_mun")
LOCALIDAD_CLAVE_ALIASES: Final[tuple[str, ...]] = ("catalog_key", "cve_loc")

# Los catálogos grandes no traen una columna "Descripción": traen la suya y,
# de paso, otras que se llamarían igual de bien (ESTABLECIMIENTOS_SALUD tiene
# MUNICIPIO y LOCALIDAD además del nombre de la unidad). Se nombra explícito.
DESCRIPCION_OVERRIDES: Final[dict[str, tuple[str, ...]]] = {
    "cat_municipio": ("municipio", "nom_mun"),
    "cat_localidad": ("localidad", "nom_loc"),
    "cat_diagnostico": ("nombre",),
    "cat_establecimiento_salud": ("nombre de la unidad",),
}

# El encabezado real no está en la primera fila: los XLSX traen filas en blanco
# y una fila con el nombre del catálogo antes de "Clave | Descripción".
HEADER_SCAN_ROWS: Final[int] = 8


# ---------------------------------------------------------------------------
# Normalización de las descripciones
# ---------------------------------------------------------------------------
# SINAC publica todo en MAYÚSCULAS. El repo pide primera letra en mayúscula
# para descripciones y `title()` para nombres propios.
PROPER_NOUN_TABLES: Final[frozenset[str]] = frozenset(
    {"cat_entidad", "cat_municipio", "cat_localidad", "cat_establecimiento_salud"}
)

# Siglas con vocales, que la regla general no puede detectar sola. Salen del
# propio catálogo: las claves de institución de CLUES y las afiliaciones.
PRESERVED_TERMS: Final[tuple[str, ...]] = (
    "IMSS",
    "ISSSTE",
    "ISSFAM",
    "INSABI",
    "PEMEX",
    "SEDENA",
    "SEMAR",
    "SSA",
    "DIF",
    "CIJ",
    "CRO",
    "FGE",
    "PGR",
    "SCT",
    "UMF",
    "UMAE",
    "CESSA",
)

# Una palabra española de dos a seis letras siempre tiene vocal; si no la
# tiene, es una sigla (HGZ, CSS, CMF). Cubre la cola larga que ninguna lista
# enumerada alcanza en 58 mil nombres de unidad.
ACRONYM_MAX_LEN: Final[int] = 6

# Conectores que `title()` capitaliza mal: "San Juan De Los Lagos".
LOWERCASE_CONNECTORS: Final[frozenset[str]] = frozenset(
    {"de", "del", "la", "las", "los", "el", "y", "e", "en", "al", "a"}
)
