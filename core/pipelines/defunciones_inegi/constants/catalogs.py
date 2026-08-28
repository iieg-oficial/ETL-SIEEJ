"""Cómo se lee cada catálogo y en qué se aparta del nombre de su tabla."""

from typing import Final

from core.pipelines.defunciones_inegi.attributes import DefuncionesInegiTables as T

# Archivos que INEGI no nombró como la tabla. El resto sale de `T.catalog_alias`,
# así que aquí no debe aparecer un alias que coincida con el derivado.
CATALOG_ALIAS_OVERRIDES: Final[dict[str, str]] = {
    T.CAT_AFROMEXICANO: "afromexi",
    T.CAT_CONDICION_INDIGENA: "conind",
    T.CAT_LENGUA: "lenguas",
    T.CAT_LISTA_CIE: "lista1",
    T.CAT_MUERTE_ENCEFALICA: "encefalica",
    T.CAT_RELACION_EMBARAZO: "relacion_con_embarazo",
    T.CAT_TAMANIO_LOCALIDAD: "tamano_localidad",
    T.CAT_CIE10: "causa_defuncion",
    T.CAT_LOCALIDAD: "entidad_municipio_localidad",
    T.CAT_PAIS: "paises",
}

# Sólo la edición 2017 nombra los catálogos con el prefijo `de`.
LEGACY_CATALOG_ALIASES: Final[dict[str, str]] = {
    T.CAT_AREA_URBANA_RURAL: "deurbrur",
    T.CAT_ASISTENCIA_MEDICA: "deasismed",
    T.CAT_CAPITULO_GRUPO: "decapgpo",
    T.CAT_CERTIFICANTE: "decertif",
    T.CAT_CIE10: "decatcausa",
    T.CAT_COMPLICARON_EMBARAZO: "decomplicaemba",
    T.CAT_CONDICION_ACTIVIDAD: "decondact",
    T.CAT_CONDICION_EMBARAZO: "decondemba",
    T.CAT_DERECHOHABIENCIA: "dederech",
    T.CAT_EDAD_AGRUPADA: "deedadagrup",
    T.CAT_ESCOLARIDAD: "deesco",
    T.CAT_ESTADO_CIVIL: "deedocony",
    T.CAT_GRUPO_LISTA_MEXICANA: "degpolisme",
    T.CAT_LENGUA_INDIGENA: "delengindi",
    T.CAT_LISTA_CIE: "delista1",
    T.CAT_LISTA_MEXICANA: "delistamex",
    T.CAT_LOCALIDAD: "decateml",
    T.CAT_LUGAR_OCURRENCIA: "desitiolesion",
    T.CAT_NACIONALIDAD: "denacion",
    T.CAT_NECROPSIA: "denecrop",
    T.CAT_OCUPACION: "deocupa",
    T.CAT_OCURRIO_TRABAJO: "deocutrab",
    T.CAT_PARENTESCO_AGRESOR: "deparenagresor",
    T.CAT_PRESUNTA_DEFUNCION_VIOLENTA: "depresunto",
    T.CAT_RAZON_MATERNA: "derazonm",
    T.CAT_RELACION_EMBARAZO: "derelemba",
    T.CAT_SEXO: "desexo",
    T.CAT_SITIO_OCURRENCIA: "desitiodefun",
    T.CAT_TAMANIO_LOCALIDAD: "detamloc",
    T.CAT_VIOLENCIA_FAMILIAR: "deviofam",
}

# Catálogos cuyo contenido cambia entre ediciones: se guardan por (clave, año).
VERSIONED_TABLES: Final[tuple[str, ...]] = (
    T.CAT_CIE10,
    T.CAT_DERECHOHABIENCIA,
    T.CAT_LOCALIDAD,
    T.CAT_OCUPACION,
)

# Catálogos cuya clave es alfanumérica y no admite casteo a entero.
TEXT_KEY_TABLES: Final[tuple[str, ...]] = (T.CAT_CIE10, T.CAT_GRUPO_LISTA_MEXICANA)

# Catálogos con estructura propia; el resto se lee como (clave, descripcion).
STRUCTURED_CATALOG_TABLES: Final[tuple[str, ...]] = (
    T.CAT_CIE10,
    T.CAT_LOCALIDAD,
    T.CAT_PAIS,
    T.CAT_CAPITULO_GRUPO,
)

CODED_CATALOG_TABLES: Final[tuple[str, ...]] = tuple(
    table for table in T.catalogs() if table not in STRUCTURED_CATALOG_TABLES
)

# `codigo_adicional` es el segundo archivo que alimenta cat_cie10.
CODIGO_ADICIONAL_ALIAS: Final[str] = "codigo_adicional"

# `paises.csv` mezcla entidades federativas (001-032) con países; las entidades
# ya viven en cvegeo_states, así que sólo se conserva el rango de países.
PAIS_MIN_CLAVE: Final[int] = 101
PAIS_MAX_CLAVE: Final[int] = 535

# La edición 2017 publica capítulo y grupo en una sola clave: cap * 100 + gpo.
CAPITULO_CLAVE_FACTOR: Final[int] = 100

# Llave natural de cada catálogo, para deduplicar entre ediciones.
CATALOG_KEYS: Final[dict[str, list[str]]] = {
    T.CAT_CAPITULO_GRUPO: ["capitulo", "grupo"],
    T.CAT_LOCALIDAD: ["cvegeo"],
}
DEFAULT_CATALOG_KEY: Final[list[str]] = ["clave"]

# INEGI publica estas listas en mayúsculas sostenidas; se guardan con sólo
# la primera letra en mayúscula, como el resto de las descripciones.
SENTENCE_CASE_TABLES: Final[tuple[str, ...]] = (T.CAT_GRUPO_LISTA_MEXICANA, T.CAT_LISTA_CIE)

# Siglas y nombres propios que sobreviven al cambio de caja. Los demás
# paréntesis llevan palabras normales ((PRIMARIOS), (MALARIA), (GRIPE)).
PRESERVED_TERMS: Final[tuple[str, ...]] = ("VIH", "Hodgkin", "Alzheimer", "Zika")

# En `razon_materna.csv` la clave de "no contribuye" viene literalmente vacía.
RAZON_MATERNA_EMPTY_KEY: Final[str] = "vacio"
RAZON_MATERNA_EMPTY_CLAVE: Final[int] = 0
