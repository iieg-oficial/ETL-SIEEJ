NULL_VALUES = [
    "no especificado", "sin información", "sin informacion",
    "sin información", "00", "*", "****", "---", "n/a", "na",
    "nan", "null", "ninguno", "sin dato", "nd", "s/d", "s/n",
    "9999", "9999.0", "ne",
]

SIN_NUMERO_RAW = [
    "sin número", "sin numero", "sin número interior",
    "sin interior", "sin nterior", "sin inúmero",
    "sin núm", "sin núm.", "sin número.", "sin num",
    "sin úmero", "sin number", "sin nterior",
]

CAPITALIZE_COLS = [
    "institucion",
    "tipo_establecimiento",
    "tipologia", "subtipologia",
    "tipo_vialidad", "vialidad", "tipo_asentamiento",
    "estatus_establecimiento", "nivel_atencion", "estrato_unidad", "tipo_obra",
    "programa_movil", "tipo_unidad_movil", "tipologia_movil",
    "instituto_administracion", "movimiento", "motivo_baja",
    "nombre_unidad_movil", "nombre_comercial",
    "marca", "marca_especifica",
]

TITLE_COLS = ["localidad", "jurisdiccion"]

DATE_COLS = [
    "fecha_construccion",
    "fecha_inicio_operacion",
    "fecha_ultimo_movimiento",
    "fecha_efectiva_baja",
]

GEO_CLAVE_COLS = ["entidad_id", "municipio_id", "clave_localidad"]
