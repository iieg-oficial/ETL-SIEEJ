SESNSP_URL: str = "https://www.gob.mx/sesnsp/acciones-y-programas/datos-abiertos-de-incidencia-delictiva"

NK_COLS: list[str] = [
    "anio",
    "cvegeo",
    "bien_juridico_afectado_id",
    "tipo_delito_id",
    "subtipo_delito_id",
    "modalidad_id",
]
UPDATE_COLS: list[str] = [
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "agosto",
    "septiembre",
    "octubre",
    "noviembre",
    "diciembre",
    "updated_at",
]

RENAME: dict[str, str] = {
    "Año": "anio",
    "Clave_Ent": "clave_ent",
    "Entidad": "entidad",
    "Cve. Municipio": "cve_municipio",
    "Municipio": "municipio",
    "Bien jurídico afectado": "bien_juridico_afectado",
    "Tipo de delito": "tipo_delito",
    "Subtipo de delito": "subtipo_delito",
    "Modalidad": "modalidad",
    "Enero": "enero",
    "Febrero": "febrero",
    "Marzo": "marzo",
    "Abril": "abril",
    "Mayo": "mayo",
    "Junio": "junio",
    "Julio": "julio",
    "Agosto": "agosto",
    "Septiembre": "septiembre",
    "Octubre": "octubre",
    "Noviembre": "noviembre",
    "Diciembre": "diciembre",
}

MONTH_COLS: list[str] = [
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "agosto",
    "septiembre",
    "octubre",
    "noviembre",
    "diciembre",
]
