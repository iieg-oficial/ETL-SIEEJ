PIPELINE_NAME = "repd"

# Valores adicionales que se convierten a NULL
NULL_VALUES = ["NO APLICA", "NA", "N/A", "null", "nan", ""]

# Mapeo columnas del Excel a nombres internos
COLUMN_RENAME_MAP = {
    "folio_estatal_de_busqueda": "feb",
    "sexo": "sex",
    "nacionalidad": "nationality",
    "rango_de_edad": "age_range",
    "fecha_reporte": "report_date",
    "fecha_desaparicion": "disappearance_date",
    "estado_desaparicion": "disappearance_state_name",
    "municipio_desaparicion": "disappearance_municipality",
    "estatus": "status",
    "fecha_de_localizacion": "location_date",
    "condicion_localizacion": "location_condition",
    "clasificacion_localizacion": "location_classification",
    "estado_localizacion": "location_state_name",
    "municipio_localizacion": "location_municipality",
    "fecha_de_cierre": "closure_date",
    "tipo_de_cierre": "closure_type",
    "folio_estatal_de_busqueda_vinculado": "linked_feb",
    "carpeta_de_investigacion": "has_investigation_folder",
}

# Columnas de fecha con formato MM/YYYY
DATE_COLUMNS = [
    "report_date",
    "disappearance_date",
    "location_date",
    "closure_date",
]

# Columnas de catalogo del DataFrame
CATALOG_COLUMNS = [
    "sex",
    "nationality",
    "age_range",
    "status",
    "location_condition",
    "location_classification",
    "closure_type",
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
    ("disappearance_municipality", "disappearance_state_name", "disappearance_municipality_id"),
    ("location_municipality", "location_state_name", "location_municipality_id"),
]

# Campos para calcular record_hash (orden determinista)
HASH_FIELDS = [
    "feb",
    "sex_id",
    "nationality_id",
    "age_range_id",
    "report_date",
    "disappearance_date",
    "disappearance_state_name",
    "disappearance_municipality_id",
    "status_id",
    "location_date",
    "location_condition_id",
    "location_classification_id",
    "location_state_name",
    "location_municipality_id",
    "closure_date",
    "closure_type_id",
    "linked_feb",
    "has_investigation_folder",
]
