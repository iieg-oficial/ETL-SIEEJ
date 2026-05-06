PIPELINE_NAME = "efipem"

# Valores adicionales que se convierten a NULL
NULL_VALUES = ["", "NA", "N/A", "null", "nan", "NO DISPONIBLE", "ND"]

# Mapeo de columnas del CSV (headers originales) a nombres internos
COLUMN_RENAME_MAP = {
    "anio": "anio",
    "trimestre": "trimestre",
    "cvegeo": "cvegeo",
    "cve_ent": "cve_ent",
    "tema": "tema",
    "clasificador": "clasificador",
    "descripcion_clasificador": "concepto",
    "valor": "valor",
    "estatus": "estatus",
}

# Columnas de catalogo simples (name-only). 'concepto' se maneja aparte por
# depender de 'clasificador'.
CATALOG_COLUMNS = ["trimestre", "tema", "clasificador", "estatus"]

# Columnas mutables para SCD2 (el hash se calcula sobre estas)
MUTABLE_COLUMNS = ["valor", "estatus"]

# Llave natural del registro (define unicidad por versión activa)
NATURAL_KEY_COLUMNS = ["anio", "trimestre_id", "cve_ent", "tema_id", "clasificador_id", "concepto_id"]

# Normalizacion de guiones en CLASIFICADOR: el CSV mezcla em-dash y hyphen.
# Canonicamos todos a em-dash con espacios: " – "
CLASIFICADOR_NORMALIZATION = {
    "CEG- Clasificación Económica del Gasto": "CEG – Clasificación Económica del Gasto",
    "CEG – Clasificación Económica del Gasto": "CEG – Clasificación Económica del Gasto",
    "CRI – Clasificación por Rubro de Ingreso": "CRI – Clasificación por Rubro de Ingreso",
    "CFG – Clasificación Funcional del Gasto": "CFG – Clasificación Funcional del Gasto",
}

# Patron glob para localizar el CSV de cifras dentro del ZIP descargado.
# El nombre incluye el rango de anios (e.g. 2023_2025) y cambia con cada publicacion.
SOURCE_CSV_GLOB = "conjunto_de_datos/efipem_trimestral_tr_cifra_*.csv"
