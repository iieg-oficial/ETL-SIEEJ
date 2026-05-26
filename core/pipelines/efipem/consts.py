PIPELINE_NAME = "efipem"

# Clave estatal de Jalisco (filtro de carga). El CSV almacena el valor como
# cadena de dos caracteres con cero inicial (e.g. "14").
JALISCO_CVE_ENT = "14"

# Valores adicionales que se convierten a NULL
NULL_VALUES = ["", "NA", "N/A", "null", "nan", "NO DISPONIBLE", "ND"]

# Mapeo de columnas del CSV (headers originales) a nombres internos.
# El dataset municipal usa CATEGORIA / DESCRIPCION_CATEGORIA en lugar de
# CLASIFICADOR / DESCRIPCION_CLASIFICADOR del dataset trimestral anterior.
COLUMN_RENAME_MAP = {
    "anio": "anio",
    "cvegeo": "cvegeo",
    "cve_ent": "cve_ent",
    "cve_mun": "cve_mun",
    "tema": "tema",
    "categoria": "clasificador",
    "descripcion_categoria": "concepto",
    "valor": "valor",
    "estatus": "estatus",
}

# Columnas de catalogo simples (name-only). 'concepto' se maneja aparte por
# depender de 'clasificador'.
CATALOG_COLUMNS = ["tema", "clasificador", "estatus"]

# Llave natural del registro (define unicidad en la tabla municipal)
NATURAL_KEY_COLUMNS = ["anio", "cvegeo", "tema_id", "clasificador_id", "concepto_id"]

# Patron glob para localizar los CSVs anuales dentro del ZIP descargado.
# El dataset municipal tiene un archivo por año: efipem_municipal_anual_tr_cifra_<ANIO>.csv
SOURCE_CSV_GLOB = "conjunto_de_datos/efipem_municipal_anual_tr_cifra_*.csv"
