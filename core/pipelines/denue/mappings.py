from typing import Any, List, Dict

RANGOS_PERSONAL: List[Dict[str, Any]] = [
    {"id": 1, "descripcion": "0 a 5 personas"},
    {"id": 2, "descripcion": "6 a 10 personas"},
    {"id": 3, "descripcion": "11 a 30 personas"},
    {"id": 4, "descripcion": "31 a 50 personas"},
    {"id": 5, "descripcion": "51 a 100 personas"},
    {"id": 6, "descripcion": "101 a 250 personas"},
    {"id": 7, "descripcion": "251 y más personas"},
]

TIPOS_ESTABLECIMIENTOS: List[Dict[str, Any]] = [
    {"id": 1, "descripcion": "Fijo"},
    {"id": 2, "descripcion": "Semifijo"},
]

RANGO_PERSONAL_MAP: Dict[str, int] = {
    "0 a 5": 1,
    "6 a 10": 2,
    "11 a 30": 3,
    "31 a 50": 4,
    "51 a 100": 5,
    "101 a 250": 6,
    "251 y más": 7,
}

TIPO_ESTABLECIMIENTO_MAP: Dict[str, int] = {
    "Fijo": 1,
    "Semifijo": 2,
}
