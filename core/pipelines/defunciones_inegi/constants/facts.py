"""Contrato del CSV de hechos: renombres, corte de metodología y centinelas."""

from typing import Final

from core.pipelines.defunciones_inegi.attributes import DefuncionesInegiTables as T

PIPELINE_NAME: Final[str] = "defunciones_inegi"

# Clave INEGI de Jalisco, para las vistas acotadas al estado.
ENTIDAD_JALISCO: Final[int] = 14

# Primera edición con el esquema ampliado. 2017-2021 traen 59 columnas;
# de 2022 en adelante, 73/74.
EXTENDED_SCHEMA_YEAR: Final[int] = 2022

# Nemónicos INEGI -> nombre propio. `presunto` (2017-2021) y `tipo_defun`
# (2022+) son la misma variable renombrada por INEGI, no dos columnas.
RENAME_HEADER: Final[dict[str, str]] = {
    "ent_regis": "entidad_registro_id",
    "mun_regis": "municipio_registro_id",
    "ent_resid": "entidad_residencia_id",
    "mun_resid": "municipio_residencia_id",
    "tloc_resid": "tamanio_localidad_residencia",
    "loc_resid": "localidad_residencia",
    "ent_ocurr": "entidad_ocurrencia_id",
    "mun_ocurr": "municipio_ocurrencia_id",
    "tloc_ocurr": "tamanio_localidad_ocurrencia",
    "loc_ocurr": "localidad_ocurrencia",
    "loc_ocur": "localidad_ocurrencia",
    "causa_def": "causa_defuncion",
    "lista_mex": "lista_mexicana",
    "gr_lismex": "grupo_lista_mexicana",
    "lista1": "lista_cie",
    "sexo": "sexo",
    "edad_agru": "edad_agrupada",
    "escolarida": "escolaridad",
    "edo_civil": "estado_civil",
    "cond_act": "condicion_actividad",
    "ocupacion": "ocupacion",
    "nacionalid": "nacionalidad",
    "lengua": "lengua_indigena",
    "derechohab": "derechohabiencia",
    "area_ur": "area_urbana_rural",
    "asist_medi": "asistencia_medica",
    "necropsia": "necropsia",
    "sitio_ocur": "sitio_ocurrencia",
    "lugar_ocur": "lugar_ocurrencia",
    "cond_cert": "certificante",
    "presunto": "presunta_defuncion_violenta",
    "tipo_defun": "presunta_defuncion_violenta",
    "ocurr_trab": "ocurrio_trabajo",
    "vio_fami": "violencia_familiar",
    "par_agre": "parentesco_agresor",
    "embarazo": "condicion_embarazo",
    "rel_emba": "relacion_embarazo",
    "complicaro": "complicaron_embarazo",
    "maternas": "causa_materna",
    "razon_m": "razon_materna",
    "ent_ocules": "entidad_lesion_id",
    "mun_ocules": "municipio_lesion_id",
    "loc_ocules": "localidad_lesion",
    "dis_re_oax": "distrito_registro_oaxaca",
    # Sólo 2022+
    "tloc_regis": "tamanio_localidad_registro",
    "loc_regis": "localidad_registro",
    "cod_adicio": "codigo_adicional",
    "ent_nac": "lugar_nacimiento",
    "nacesp_cve": "pais_nacionalidad",
    "cve_lengua": "lengua",
    "afromex": "afromexicano",
    "conindig": "condicion_indigena",
    "sem_gest": "semanas_gestacion",
    "gramos": "peso_gramos",
    "cirugia": "cirugia",
    "natviole": "accidental_violenta",
    "usonecrops": "uso_necropsia",
    "encefalica": "muerte_encefalica",
    "donador": "donador",
}

# Componentes que se colapsan en una sola fecha.
DATE_PARTS: Final[dict[str, tuple[str, str, str]]] = {
    "fecha_ocurrencia": ("dia_ocurr", "mes_ocurr", "anio_ocur"),
    "fecha_registro": ("dia_regis", "mes_regis", "anio_regis"),
    "fecha_nacimiento": ("dia_nacim", "mes_nacim", "anio_nacim"),
    "fecha_certificacion": ("dia_cert", "mes_cert", "anio_cert"),
}

TIME_PARTS: Final[tuple[str, str]] = ("horas", "minutos")
TIME_COLUMN: Final[str] = "hora_defuncion"

# La edición de la que se toma el año de referencia de cada fila.
EDITION_YEAR_COLUMN: Final[str] = "anio_regis"

# Columna que marca de qué edición vino cada fila/registro de catálogo.
EDITION_COLUMN: Final[str] = "anio_edicion"

DAY_SENTINEL: Final[int] = 99
MONTH_SENTINEL: Final[int] = 99
YEAR_SENTINEL: Final[int] = 9999
HOUR_SENTINEL: Final[int] = 99
MINUTE_SENTINEL: Final[int] = 99

# `edad` codifica unidad + cantidad en cuatro dígitos: 1=horas, 2=días,
# 3=meses, 4=años. Los centinelas dejan la cantidad nula y conservan la unidad.
EDAD_UNIT_DIVISOR: Final[int] = 1000
EDAD_SENTINELS: Final[frozenset[int]] = frozenset({1097, 1098, 2098, 3098, 4998})

NUMERIC_SENTINELS: Final[dict[str, tuple[int, ...]]] = {
    "semanas_gestacion": (88, 99),
    "peso_gramos": (8888, 9999),
}

# `ent_nac` mezcla entidades federativas y países en un solo campo. Las claves
# 888/997/998/999 son recuperables desde `nacionalidad`, así que no se guardan.
LUGAR_NACIMIENTO_COLUMN: Final[str] = "lugar_nacimiento"
ENTIDAD_MAX_CLAVE: Final[int] = 32
PAIS_SENTINELS: Final[frozenset[int]] = frozenset({888, 997, 998, 999})

# Columna de hechos -> catálogo contra el que se resuelve su `_id`.
COLUMN_CATALOG: Final[dict[str, str]] = {
    "sexo": T.CAT_SEXO,
    "edad_agrupada": T.CAT_EDAD_AGRUPADA,
    "escolaridad": T.CAT_ESCOLARIDAD,
    "estado_civil": T.CAT_ESTADO_CIVIL,
    "condicion_actividad": T.CAT_CONDICION_ACTIVIDAD,
    "nacionalidad": T.CAT_NACIONALIDAD,
    "lengua_indigena": T.CAT_LENGUA_INDIGENA,
    "area_urbana_rural": T.CAT_AREA_URBANA_RURAL,
    "asistencia_medica": T.CAT_ASISTENCIA_MEDICA,
    "necropsia": T.CAT_NECROPSIA,
    "sitio_ocurrencia": T.CAT_SITIO_OCURRENCIA,
    "lugar_ocurrencia": T.CAT_LUGAR_OCURRENCIA,
    "certificante": T.CAT_CERTIFICANTE,
    "presunta_defuncion_violenta": T.CAT_PRESUNTA_DEFUNCION_VIOLENTA,
    "ocurrio_trabajo": T.CAT_OCURRIO_TRABAJO,
    "violencia_familiar": T.CAT_VIOLENCIA_FAMILIAR,
    "parentesco_agresor": T.CAT_PARENTESCO_AGRESOR,
    "condicion_embarazo": T.CAT_CONDICION_EMBARAZO,
    "relacion_embarazo": T.CAT_RELACION_EMBARAZO,
    "complicaron_embarazo": T.CAT_COMPLICARON_EMBARAZO,
    "razon_materna": T.CAT_RAZON_MATERNA,
    "lista_cie": T.CAT_LISTA_CIE,
    "lista_mexicana": T.CAT_LISTA_MEXICANA,
    "grupo_lista_mexicana": T.CAT_GRUPO_LISTA_MEXICANA,
    "tamanio_localidad_residencia": T.CAT_TAMANIO_LOCALIDAD,
    "tamanio_localidad_ocurrencia": T.CAT_TAMANIO_LOCALIDAD,
    "tamanio_localidad_registro": T.CAT_TAMANIO_LOCALIDAD,
    "afromexicano": T.CAT_AFROMEXICANO,
    "condicion_indigena": T.CAT_CONDICION_INDIGENA,
    "lengua": T.CAT_LENGUA,
    "cirugia": T.CAT_CIRUGIA,
    "accidental_violenta": T.CAT_ACCIDENTAL_VIOLENTA,
    "uso_necropsia": T.CAT_USO_NECROPSIA,
    "muerte_encefalica": T.CAT_MUERTE_ENCEFALICA,
    "donador": T.CAT_DONADOR,
}

# Se resuelven contra catálogos versionados: la clave sola no basta, hace falta
# la edición.
VERSIONED_COLUMN_CATALOG: Final[dict[str, str]] = {
    "ocupacion": T.CAT_OCUPACION,
    "derechohabiencia": T.CAT_DERECHOHABIENCIA,
    "causa_defuncion": T.CAT_CIE10,
    "causa_materna": T.CAT_CIE10,
    "codigo_adicional": T.CAT_CIE10,
}

# Roles geográficos: (entidad, municipio, localidad). Entidad y municipio se
# conservan como código crudo y se unen contra cvegeo (FDW); la localidad
# resuelve FK a cat_localidad porque cvegeo no llega a ese nivel.
GEO_ROLES: Final[tuple[tuple[str, str, str], ...]] = (
    ("entidad_registro_id", "municipio_registro_id", "localidad_registro"),
    ("entidad_residencia_id", "municipio_residencia_id", "localidad_residencia"),
    ("entidad_ocurrencia_id", "municipio_ocurrencia_id", "localidad_ocurrencia"),
    ("entidad_lesion_id", "municipio_lesion_id", "localidad_lesion"),
)
