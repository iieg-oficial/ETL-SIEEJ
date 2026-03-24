from typing import List, Dict

CUBE: str = "economy_foreign_trade_mun"
MEASURES: str = "Trade Value"
LOCALE: str = "es"

TITLE_COLS: List[str] = ["nombre_pais"]
CAPITALIZE_COLS: List[str] = ["flujo", "descripcion"]

RENAME_PAISES: Dict[str, str] = {
    "Country ID": "codigo_pais",
    "Country": "nombre_pais",
}

RENAME_FLUJOS: Dict[str, str] = {
    "Flow ID": "id",
    "Flow": "flujo",
}

RENAME_PRODUCTOS: Dict[str, str] = {
    "HS6 ID": "id",
    "HS6": "descripcion",
}

RENAME_PERIODOS: Dict[str, str] = {
    "Quarter ID": "id",
    "Quarter": "etiqueta_trimestre",
}

RENAME_COMERCIO: Dict[str, str] = {
    "Country ID": "codigo_pais",
    "State ID": "entidad_id",
    "Quarter ID": "periodo_id",
    "Flow ID": "tipo_flujo_id",
    "HS6 ID": "producto_id",
    "Trade Value": "valor_comercio",
}
