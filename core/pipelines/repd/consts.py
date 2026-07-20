PIPELINE_NAME = "repd"

# Valores adicionales que se convierten a NULL
NULL_VALUES = ["NO APLICA", "NA", "N/A", "null", "nan", ""]

# Mapeo columnas del Excel a nombres internos
COLUMN_RENAME_MAP = {
    "folio_estatal_de_busqueda": "feb",
    "sexo": "sexo",
    "nacionalidad": "nacionalidad",
    "rango_de_edad": "rango_edad",
    "fecha_reporte": "fecha_reporte",
    "fecha_desaparicion": "fecha_desaparicion",
    "estado_desaparicion": "estado_desaparicion",
    "municipio_desaparicion": "municipio_desaparicion",
    "estatus": "estatus",
    "fecha_de_localizacion": "fecha_localizacion",
    "condicion_localizacion": "condicion_localizacion",
    "clasificacion_localizacion": "clasificacion_localizacion",
    "estado_localizacion": "estado_localizacion",
    "municipio_localizacion": "municipio_localizacion",
    "fecha_de_cierre": "fecha_cierre",
    "tipo_de_cierre": "tipo_cierre",
    "folio_estatal_de_busqueda_vinculado": "feb_vinculado",
    "carpeta_de_investigacion": "tiene_carpeta_investigacion",
}

# Columnas de fecha con formato MM/YYYY
DATE_COLUMNS = [
    "fecha_reporte",
    "fecha_desaparicion",
    "fecha_localizacion",
    "fecha_cierre",
]

# Columnas de catalogo del DataFrame (deben coincidir con las llaves de CATALOG_MODELS)
CATALOG_COLUMNS = [
    "sexo",
    "nacionalidad",
    "rango_edad",
    "estatus",
    "condicion_localizacion",
    "clasificacion_localizacion",
    "tipo_cierre",
]

# Municipios que NO deben resolverse contra cvegeo
SKIP_MUNICIPALITY_VALUES = frozenset(
    {
        "SE IGNORA",
        "EXTRANJERO",
    }
)

# Columnas de municipio: (col_municipio, col_estado, col_id_destino)
MUNICIPALITY_COLUMNS = [
    ("municipio_desaparicion", "estado_desaparicion", "municipio_desaparicion_id"),
    ("municipio_localizacion", "estado_localizacion", "municipio_localizacion_id"),
]

# Campos para calcular record_hash (orden determinista)
HASH_FIELDS = [
    "feb",
    "sexo_id",
    "nacionalidad_id",
    "rango_edad_id",
    "fecha_reporte",
    "fecha_desaparicion",
    "estado_desaparicion",
    "municipio_desaparicion_id",
    "estatus_id",
    "fecha_localizacion",
    "condicion_localizacion_id",
    "clasificacion_localizacion_id",
    "estado_localizacion",
    "municipio_localizacion_id",
    "fecha_cierre",
    "tipo_cierre_id",
    "feb_vinculado",
    "tiene_carpeta_investigacion",
]
