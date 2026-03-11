PIPELINE_NAME = "repd"

# Valores adicionales que se convierten a NULL
NULL_VALUES = ["NO APLICA", "NA", "N/A", "null", "nan", ""]

# Mapeo columnas del Excel a nombres internos
COLUMN_RENAME_MAP = {
    "folio estatal de busqueda": "feb",
    "sexo": "sex",
    "nacionalidad": "nationality",
    "rango de edad": "age_range",
    "fecha reporte": "report_date",
    "fecha desaparicion": "disappearance_date",
    "estado desaparicion": "disappearance_state_name",
    "municipio desaparicion": "disappearance_municipality",
    "estatus": "status",
    "fecha de localizacion": "location_date",
    "condicion localizacion": "location_condition",
    "clasificacion localizacion": "location_classification",
    "estado localizacion": "location_state_name",
    "municipio localizacion": "location_municipality",
    "fecha de cierre": "closure_date",
    "tipo de cierre": "closure_type",
    "folio estatal de busqueda vinculado": "linked_feb",
    "carpeta de investigacion": "has_investigation_folder",
}

# Columnas de fecha con formato MM/YYYY
DATE_COLUMNS = [
    "report_date",
    "disappearance_date",
    "location_date",
    "closure_date",
]

# Columna del DataFrame a nombre clave del catalogo
CATALOG_COLUMN_MAP = {
    "sex": "sex",
    "nationality": "nationality",
    "age_range": "age_range",
    "status": "status",
    "location_condition": "location_condition",
    "location_classification": "location_classification",
    "closure_type": "closure_type",
}

# Municipios que NO deben resolverse contra cvegeo
SKIP_MUNICIPALITY_VALUES = frozenset({
    "SE IGNORA",
    "EXTRANJERO",
})

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
