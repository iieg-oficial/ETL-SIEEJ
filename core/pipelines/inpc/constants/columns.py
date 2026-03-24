from typing import Final, Dict, List


RENAME_HEADER: List[str] = [
    "fecha",
    "indice_general",
    "alimentos_bebidas_y_tabaco",
    "ropa_calzado_y_accesorios",
    "vivienda",
    "muebles_aparatos_y_accesorios_domesticos",
    "salud_y_cuidado_personal",
    "transporte",
    "educacion_y_esparcimiento",
    "otros_servicios",
]

CITY_NUMERICAL_COLS: List[str] = [
    "indice_general",
    "alimentos_bebidas_y_tabaco",
    "ropa_calzado_y_accesorios",
    "vivienda",
    "muebles_aparatos_y_accesorios_domesticos",
    "salud_y_cuidado_personal",
    "transporte",
    "educacion_y_esparcimiento",
    "otros_servicios",
]

NULL_VALUES: List[str] = ["N/E"]

REPLACE_MONTHS: Final[Dict[str, str]] = {
    "Ene": "01",
    "Feb": "02",
    "Mar": "03",
    "Abr": "04",
    "May": "05",
    "Jun": "06",
    "Jul": "07",
    "Ago": "08",
    "Sep": "09",
    "Oct": "10",
    "Nov": "11",
    "Dic": "12",
}
