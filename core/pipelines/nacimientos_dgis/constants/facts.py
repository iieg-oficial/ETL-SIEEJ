"""Renombres, centinelas y resolución contra catálogo de los campos del certificado."""

from typing import Final

from core.pipelines.nacimientos_dgis.attributes import NacimientosDgisTables as T

# Centinelas de edad, de la madre y del padre. Cuál se usa depende de la
# edición, no del campo: 2020 deja el dato vacío, 2021-2023 escribe 99 y
# 2024-2025 escribe 999. Por eso van los tres juntos y no uno por año.
#
# El 0 no está documentado en `Descriptores_SINAC_2020.xlsx` y aparece 22
# veces en 2022; no es una edad, porque en la fuente no existe ninguna edad
# de 1 a 11 años. El 99 tampoco: las edades 91 a 98 no existen y el 99 sale
# 4,171 veces en 2022, un pico imposible para un padre de 99 años.
EDAD_SENTINELS: Final[frozenset[int]] = frozenset({0, 99, 888, 999})

JALISCO_CVE_ENTIDAD: Final[int] = 14

# Nemónicos de SINAC a nombres propios. Las claves que se resuelven contra un
# catálogo conservan aquí el nombre del código; el `_id` lo pone el transform.
RENAME_HEADER: Final[dict[str, str]] = {
    "SECONSIDERAINDIGENA": "se_considera_indigena",
    "HABLALENGUAINDIGENA": "habla_lengua_indigena",
    "ATENCIONPRENATAL": "atencion_prenatal",
    "SOBREVIVIOPARTO": "sobrevivio_parto",
    "INTERRUMPIOESTUDIOS": "interrumpio_estudios",
    "TRABAJAACTUALMENTE": "trabaja_actualmente",
    "ESTADOCONYUGAL": "estado_conyugal",
    "AFILIACION": "afiliacion",
    "ESCOLARIDAD": "escolaridad",
    "CLAVEOCUPACIONHABITUAL": "ocupacion_habitual",
    "SEXO": "sexo",
    "PRODUCTOEMBARAZO": "producto_embarazo",
    "LUGARNACIMIENTO": "lugar_nacimiento",
    "RESOLUCIONEMBARAZO": "resolucion_embarazo",
    "CODIGOCIEANOMALIA1": "diagnostico_1",
    "CODIGOCIEANOMALIA2": "diagnostico_2",
    "CLUES": "establecimiento_salud",
    "NUMEROEMBARAZOS": "numero_embarazos",
    "TOTALCONSULTAS": "total_consultas",
    "EDADGESTACIONAL": "edad_gestacional",
    "TALLA": "talla",
    "PESO": "peso",
    "ORDENPRODUCTO": "orden_producto",
    "TOTALPRODUCTOS": "total_productos",
    "HORANACIMIENTO": "hora_nacimiento",
    "TIEMPOTRASLADO": "tiempo_traslado",
    "EDAD": "edad_madre",
    "EDADPADRE": "edad_padre",
}

# ---------------------------------------------------------------------------
# Campos SI/NO
# ---------------------------------------------------------------------------
# El catálogo SI_NO de SINAC no es binario: 0=NO ESPECIFICADO, 1=SI, 2=NO,
# 8=NO APLICA, 9=SE IGNORA, y en los datos aparecen cuatro de los cinco.
# Un `boolean` colapsaría "no aplica", "se ignora" y "no especificado" en el
# mismo NULL, y esa diferencia no se recupera después.
SI_NO_COLUMNS: Final[tuple[str, ...]] = (
    "se_considera_indigena",
    "habla_lengua_indigena",
    "atencion_prenatal",
    "sobrevivio_parto",
    "interrumpio_estudios",
    "trabaja_actualmente",
)

# ---------------------------------------------------------------------------
# Centinelas numéricos
# ---------------------------------------------------------------------------
NUMERIC_SENTINELS: Final[dict[str, tuple[int, ...]]] = {
    "numero_embarazos": (99,),
    "total_consultas": (99,),
    "edad_gestacional": (99,),
    "talla": (99,),
    "peso": (9999,),
}

# Columnas enteras que pandas trae como float porque la fuente tiene nulos.
# Sin castear, el COPY manda "23.0" a un smallint y la carga revienta.
INTEGER_COLUMNS: Final[tuple[str, ...]] = (
    "edad_madre",
    "edad_padre",
    "orden_producto",
    "total_productos",
)

TIME_SENTINEL: Final[str] = "99:99"
TIME_COLUMNS: Final[tuple[str, ...]] = ("hora_nacimiento",)
INTERVAL_COLUMNS: Final[tuple[str, ...]] = ("tiempo_traslado",)

# "NINGUNA APARENTE": no es una anomalía, es la ausencia de anomalía.
DIAGNOSTICO_NINGUNA: Final[str] = "0000"

# ---------------------------------------------------------------------------
# Resolución contra catálogo
# ---------------------------------------------------------------------------
# Columna del hecho -> tabla de catálogo contra la que se resuelve su clave.
COLUMN_CATALOG: Final[dict[str, str]] = {
    **{column: T.CAT_SI_NO for column in SI_NO_COLUMNS},
    "estado_conyugal": T.CAT_ESTADO_CONYUGAL,
    "afiliacion": T.CAT_AFILIACION,
    "escolaridad": T.CAT_ESCOLARIDAD,
    "ocupacion_habitual": T.CAT_OCUPACION_HABITUAL,
    "sexo": T.CAT_SEXO,
    "producto_embarazo": T.CAT_PRODUCTO_EMBARAZO,
    "lugar_nacimiento": T.CAT_LUGAR_NACIMIENTO,
    "resolucion_embarazo": T.CAT_RESOLUCION_EMBARAZO,
    "entidad_parto": T.CAT_ENTIDAD,
    "municipio_parto": T.CAT_MUNICIPIO,
    "localidad_parto": T.CAT_LOCALIDAD,
    "localidad_residencia": T.CAT_LOCALIDAD,
    "diagnostico_1": T.CAT_DIAGNOSTICO,
    "diagnostico_2": T.CAT_DIAGNOSTICO,
    "establecimiento_salud": T.CAT_ESTABLECIMIENTO_SALUD,
}

# Catálogos cuya clave es alfanumérica; el resto son enteros.
TEXT_KEY_TABLES: Final[frozenset[str]] = frozenset({T.CAT_DIAGNOSTICO, T.CAT_ESTABLECIMIENTO_SALUD})

# ---------------------------------------------------------------------------
# Claves geográficas compuestas
# ---------------------------------------------------------------------------
# Municipio y localidad no son únicos por sí solos: SINAC los publica por
# entidad. Se componen igual que el `cve_geo` que ya usaba el pipeline.
MUNICIPIO_FACTOR: Final[int] = 1_000
LOCALIDAD_ENTIDAD_FACTOR: Final[int] = 10_000_000
LOCALIDAD_MUNICIPIO_FACTOR: Final[int] = 10_000

# columna destino -> (entidad, municipio, localidad | None)
COMPOSITE_GEO: Final[dict[str, tuple[str, str, str | None]]] = {
    "municipio_parto": ("ENTIDADFEDERATIVAPARTO", "MUNICIPIOPARTO", None),
    "localidad_parto": ("ENTIDADFEDERATIVAPARTO", "MUNICIPIOPARTO", "LOCALIDADPARTO"),
    "localidad_residencia": ("ENTIDADRESIDENCIA", "MUNICIPIORESIDENCIA", "LOCALIDADRESIDENCIA"),
}

ENTIDAD_SOURCE: Final[dict[str, str]] = {"entidad_parto": "ENTIDADFEDERATIVAPARTO"}

COPY_COLS: Final[list[str]] = [
    "anio",
    "cve_geo",
    "edad_madre",
    "tot_nac",
    "nac_padre_conocido",
    "nac_padre_18_mas",
    "nac_padre_25_mas",
    "fecha_actualizacion",
]
