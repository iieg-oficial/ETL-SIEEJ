PIPELINE_NAME = 'repd'

columns_date = [
    'fecha_reporte',
    'fecha_desaparicion',
    'fecha_localizacion',
    'fecha_cierre'
]

columns_boolean = [
    'carpeta_investigacion'
]

repd_columns = [
    'folio_estatal_busqueda', 
    'sexo', 
    'nacionalidad', 
    'rango_edad', 
    'fecha_reporte', 
    'fecha_desaparicion', 
    'estado_desaparicion',
    'municipio_desaparicion', 
    'estatus_desaparicion', 
    'fecha_localizacion',
    'condicion_localizacion', 
    'clasificacion_localizacion',
    'estado_localizacion', 
    'municipio_localizacion', 
    'fecha_cierre',
    'tipo_cierre', 
    'folio_estatal_busqueda_vinculado',
    'carpeta_investigacion'
]

repd_columns_relation = [
    'folio_estatal_busqueda', 
    'sexo_id', 
    'nacionalidad_id', 
    'rango_edad_id', 
    'fecha_reporte', 
    'fecha_desaparicion', 
    'estado_desaparicion_id',
    'municipio_desaparicion_id', 
    'estatus_desaparicion_id', 
    'fecha_localizacion',
    'condicion_localizacion_id', 
    'clasificacion_localizacion_id',
    'estado_localizacion_id', 
    'municipio_localizacion_id', 
    'fecha_cierre',
    'tipo_cierre_id', 
    'folio_estatal_busqueda_vinculado',
    'carpeta_investigacion'
]

capitalize_columns = [
    "sexo",
    "rango_edad",
    "estatus_desaparicion",
    "condicion_localizacion",
    "clasificacion_localizacion",
    "tipo_cierre"

]
title_columns = [
    "nacionalidad",
    "estado_desaparicion",
    "municipio_desaparicion",
    "estado_localizacion",
    "municipio_localizacion",
]

