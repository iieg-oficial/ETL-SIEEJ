import re
from typing import Literal

NACIONAL_MEMBER_PATTERN = re.compile(r"enec_absoluto_nacional_2018_(\d{4})\.csv$")
ENTIDAD_MEMBER_PATTERN = re.compile(r"enec_absoluto_entidad_2018_(\d{4})\.csv$")
NACIONAL_DESCRIPTION = "enec_absoluto_nacional"
ENTIDAD_DESCRIPTION = "enec_absoluto_entidad"

SOURCE_ENCODING: str = "utf-8"

# Firma de un archivo ZIP. INEGI responde 200 con HTML cuando la ruta no existe,
# así que el status code no sirve para detectar una URL inválida.
ZIP_MAGIC: Literal[b"PK"] = b"PK"

# El encabezado de la fuente trae "J000A " CON UN ESPACIO AL FINAL. Sin este
# strip el rename falla en silencio y la columna se pierde.
STRIP_HEADERS: bool = True

# Clave geoestadística que la fuente usa para el agregado nacional dentro del
# conjunto por entidad. Esas filas se excluyen de stg_enec_entidad porque son
# byte-idénticas a las de stg_enec_nacional con código de actividad 23.
CVEGEO_NACIONAL: str = "00"

# Clave que la fuente usa para la obra ejecutada fuera del país. No es una
# entidad federativa y no cruza contra cvegeo_states, pero SÍ forma parte del
# total nacional: excluirla descuadra el valor de producción.
CVEGEO_EXTRANJERO: int = 33

# Las 44 medidas, comunes a los dos conjuntos. Se omite O110B a propósito: es
# byte-idéntica a O110A, la repite como encabezado del desglose por sector.
MEASURE_RENAME: dict[str, str] = {
    # Personal ocupado — número de personas (G210A en número de días)
    "G210A": "dias_trabajados",
    "H001A": "per_ocu_tot",
    "H000A": "per_ocu_dependiente",
    "H171A": "per_ocu_obreros",
    "H200A": "per_ocu_administrativos",
    "H300A": "per_ocu_no_remunerados",
    "I100A": "per_ocu_subcontratado",
    # Horas trabajadas — miles de horas
    "H001D": "horas_tot",
    "H000D": "horas_dependiente",
    "H171D": "horas_obreros",
    "H200D": "horas_administrativos",
    "H300D": "horas_no_remunerados",
    "I000D": "horas_subcontratado",
    # Remuneraciones — miles de pesos corrientes
    "J000A": "remuneraciones_tot",
    "J117A": "salarios_obreros",
    "J200A": "sueldos_administrativos",
    "J030A": "prestaciones",
    # Remuneraciones medias — pesos corrientes
    "A171A": "remuneracion_media_persona",
    "A171B": "remuneracion_media_hora",
    "A171C": "remuneracion_media_salarios",
    "J171A": "salario_medio_obreros",
    "J200B": "sueldo_medio_administrativos",
    # Gastos — miles de pesos corrientes
    "K000A": "gastos_tot",
    "K321A": "gasto_materiales_contratista",
    "K322A": "gasto_materiales_subcontratista",
    "K610A": "gasto_suministro_personal",
    "K720A": "gasto_subcontratistas",
    "K999A": "gastos_otros",
    "K321B": "consumo_materiales_contratista",
    "K322B": "consumo_materiales_subcontratista",
    # Ingresos — miles de pesos corrientes
    "M000A": "ingresos_tot",
    "M321A": "ingresos_contratista",
    "M322A": "ingresos_subcontratista",
    "M323A": "ingresos_administracion",
    "M999A": "ingresos_otros",
    # Valor de producción — miles de pesos corrientes
    "O110A": "valor_produccion",
    "O110A_1": "valor_produccion_edificacion",
    "O110A_2": "valor_produccion_agua_riego",
    "O110A_3": "valor_produccion_electricidad",
    "O110A_4": "valor_produccion_transporte",
    "O110A_5": "valor_produccion_petroleo",
    "O110A_6": "valor_produccion_otras",
    "O110B_1": "valor_produccion_publico",
    "O110B_2": "valor_produccion_privado",
}

NACIONAL_RENAME: dict[str, str] = {
    "CODIGO_ACTIVIDAD": "codigo_actividad",
    "DESCRIPCION_ACTIVIDAD": "descripcion_actividad",
    "ANIO": "anio",
    "MES": "mes",
    "ESTATUS": "estatus",
    **MEASURE_RENAME,
}

ENTIDAD_RENAME: dict[str, str] = {
    "CVEGEO": "entidad_id",
    "ANIO": "anio",
    "MES": "mes",
    "ESTATUS": "estatus",
    **MEASURE_RENAME,
}

NULL_VALUES: list[str] = [
    "null",
    "nan",
    "-",
    "--",
    "---",
    "*",
    "s/d",
    "sin dato",
]

# Conteos de personas y montos: enteros en la fuente, sin excepción.
INT_COLS: list[str] = [
    "per_ocu_tot",
    "per_ocu_dependiente",
    "per_ocu_obreros",
    "per_ocu_administrativos",
    "per_ocu_no_remunerados",
    "per_ocu_subcontratado",
    "remuneraciones_tot",
    "salarios_obreros",
    "sueldos_administrativos",
    "prestaciones",
    "gastos_tot",
    "gasto_materiales_contratista",
    "gasto_materiales_subcontratista",
    "gasto_suministro_personal",
    "gasto_subcontratistas",
    "gastos_otros",
    "consumo_materiales_contratista",
    "consumo_materiales_subcontratista",
    "ingresos_tot",
    "ingresos_contratista",
    "ingresos_subcontratista",
    "ingresos_administracion",
    "ingresos_otros",
    "valor_produccion",
    "valor_produccion_edificacion",
    "valor_produccion_agua_riego",
    "valor_produccion_electricidad",
    "valor_produccion_transporte",
    "valor_produccion_petroleo",
    "valor_produccion_otras",
    "valor_produccion_publico",
    "valor_produccion_privado",
]

# Días, horas y promedios: decimales en la fuente.
FLOAT_COLS: list[str] = [
    "dias_trabajados",
    "horas_tot",
    "horas_dependiente",
    "horas_obreros",
    "horas_administrativos",
    "horas_no_remunerados",
    "horas_subcontratado",
    "remuneracion_media_persona",
    "remuneracion_media_hora",
    "remuneracion_media_salarios",
    "salario_medio_obreros",
    "sueldo_medio_administrativos",
]

NACIONAL_CONFLICT_KEYS: list[str] = ["fecha", "codigo_actividad"]
ENTIDAD_CONFLICT_KEYS: list[str] = ["fecha", "entidad_id"]
