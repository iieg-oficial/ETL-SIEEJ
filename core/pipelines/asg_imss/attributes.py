"""Constantes y mapeos del pipeline asg_imss.

Define:
    * `AsgImssTables` — nombres canónicos de las tablas (sin literales).
    * Listas de columnas por rol (catálogos FK, métricas int, métricas float).
    * `CSV_HEADER_RENAMES` — mapa del header crudo del CSV (incluyendo la
      variante con el REPLACEMENT CHARACTER U+FFFD en `tamano_patron`) hacia
      el nombre normalizado usado en transform/load.
    * `CSV_TO_TABLE_COLUMN` — mapeo entre nombres del CSV normalizado y los
      nombres físicos de columna en `stg_asg_imss` (FK ids y métricas).

Nota: los catálogos son auto-poblables desde el load. Cuando aparece una
clave nueva, el load inserta un registro con `descripcion = 'SIN DESCRIPCION'`
salvo en los catálogos de sector, donde la clave puede ser NULL en la tabla
de hechos.
"""

from enum import StrEnum, auto


class AsgImssTables(StrEnum):
    """Nombres de las tablas físicas del pipeline asg_imss."""

    CAT_DELEGACION = auto()
    CAT_SUBDELEGACION = auto()
    CAT_ENTIDAD = auto()
    CAT_MUNICIPIO = auto()
    CAT_SECTOR_1 = auto()
    CAT_SECTOR_2 = auto()
    CAT_SECTOR_4 = auto()
    CAT_TAMANO_REGISTRO_PATRONAL = auto()
    CAT_SEXO = auto()
    CAT_RANGO_EDAD = auto()
    CAT_RANGO_SALARIO = auto()
    CAT_RANGO_UMA = auto()
    STG_ASG_IMSS = auto()


# ---------------------------------------------------------------------------
# Columnas (post-transform, pre-load)
# ---------------------------------------------------------------------------

CATALOG_FK_COLUMNS_CSV: list[str] = [
    "cve_subdelegacion",
    "cve_municipio",
    "sector_economico_4",
    "tamano_patron",
    "sexo",
    "rango_edad",
    "rango_salarial",
    "rango_uma",
]

METRIC_INT_COLUMNS: list[str] = [
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

METRIC_FLOAT_COLUMNS: list[str] = [
    "masa_sal_ta",
    "masa_sal_teu",
    "masa_sal_tec",
    "masa_sal_tpu",
    "masa_sal_tpc",
]

# Catálogos cuyas FK en stg_asg_imss admiten NULL (solo sector_4).
NULLABLE_CATALOG_FK_COLUMNS: list[str] = [
    "sector_economico_4",
]

# Longitudes fijas que transform debe garantizar para las claves de sector.
SECTOR_KEY_LENGTHS: dict[str, int] = {
    "sector_economico_1": 1,
    "sector_economico_2": 2,
    "sector_economico_4": 4,
}

# Catálogos donde el literal "NA" es valor válido (no nulo). Los sectores
# NO están en esta lista: ahí el faltante es NULL real.
NA_LITERAL_VALID_CATALOGS: list[str] = [
    "cat_delegacion",
    "cat_subdelegacion",
    "cat_entidad",
    "cat_municipio",
    "cat_tamano_registro_patronal",
    "cat_sexo",
    "cat_rango_edad",
    "cat_rango_salario",
    "cat_rango_uma",
]

# Filtro geográfico aplicado en transform.
ENTIDAD_FILTRO_CVE: str = "14"

# ---------------------------------------------------------------------------
# Aliases de municipio: claves IMSS no-canónicas → clave canónica
#
# El IMSS usa varias claves internas para subdivisiones del mismo municipio
# geográfico. El catálogo almacena una única entrada canónica por municipio;
# el load remapea automáticamente las claves alias al canónico al resolver FKs.
#
#   Guadalajara  canónico: B90
#     R12 Guadalajara Juárez        → B90
#     R13 Guadalajara Hidalgo       → B90
#     R14 Guadalajara Libertad Reforma → B90
#     R15 Guadalajara Libertad Reforma → B90
#     Z62 Guadalajara Juárez        → B90
#     Z67 Guadalajara Hidalgo       → B90
#
#   Zapopan  canónico: C16
#     Z29 Zapopan → C16
#     Z60 Zapopan → C16
# ---------------------------------------------------------------------------
MUNICIPIO_ALIASES: dict[str, str] = {
    "R12": "B90",
    "R13": "B90",
    "R14": "B90",
    "R15": "B90",
    "Z62": "B90",
    "Z67": "B90",
    "Z29": "C16",
    "Z60": "C16",
}

# ---------------------------------------------------------------------------
# Mapeos de header del CSV original → nombre normalizado
# El CSV publicado por IMSS llega con el caracter U+FFFD en lugar de la 'ñ'
# en algunas publicaciones; transform normaliza ambos variantes a
# `tamano_patron`.
# ---------------------------------------------------------------------------

CSV_HEADER_RENAMES: dict[str, str] = {
    "tamaño_patron": "tamano_patron",
    "tama\ufffdo_patron": "tamano_patron",
}

# Mapeo entre nombre del CSV (post-rename) y la columna FK en stg_asg_imss.
CSV_FK_TO_STG_COLUMN: dict[str, str] = {
    "cve_subdelegacion": "subdelegacion_id",
    "cve_municipio": "municipio_id",
    "sector_economico_4": "sector_4_id",
    "tamano_patron": "tamano_registro_patronal_id",
    "sexo": "sexo_id",
    "rango_edad": "rango_edad_id",
    "rango_salarial": "rango_salario_id",
    "rango_uma": "rango_uma_id",
}

# Mapeo CSV → columna física para métricas (los nombres coinciden, se
# expone como dict por simetría con CSV_FK_TO_STG_COLUMN).
CSV_METRIC_TO_STG_COLUMN: dict[str, str] = {col: col for col in METRIC_INT_COLUMNS + METRIC_FLOAT_COLUMNS}
