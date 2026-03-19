from typing import NamedTuple, Dict, Final


class EntityInfo(NamedTuple):
    entity: str
    code: str


INPC_ENTITIES: Dict[int, EntityInfo] = {
    1: EntityInfo("Aguascalientes", "894950"),
    2: EntityInfo("Baja California", "895380"),
    3: EntityInfo("Baja California Sur", "895810"),
    4: EntityInfo("Campeche", "896240"),
    5: EntityInfo("Coahuila", "896670"),
    6: EntityInfo("Colima", "897100"),
    7: EntityInfo("Chiapas", "897530"),
    8: EntityInfo("Chihuahua", "897960"),
    9: EntityInfo("CDMX", "898390"),
    10: EntityInfo("Durango", "898820"),
    11: EntityInfo("Guanajuato", "899250"),
    12: EntityInfo("Guerrero", "899680"),
    13: EntityInfo("Hidalgo", "900110"),
    14: EntityInfo("Jalisco", "900540"),
    15: EntityInfo("Estado de México", "900970"),
    16: EntityInfo("Michoacán", "901400"),
    17: EntityInfo("Morelos", "901830"),
    18: EntityInfo("Nayarit", "902260"),
    19: EntityInfo("Nuevo León", "902690"),
    20: EntityInfo("Oaxaca", "903120"),
    21: EntityInfo("Puebla", "903550"),
    22: EntityInfo("Querétaro", "903980"),
    23: EntityInfo("Quintana Roo", "904410"),
    24: EntityInfo("San Luis Potosí", "904840"),
    25: EntityInfo("Sinaloa", "905270"),
    26: EntityInfo("Sonora", "905700"),
    27: EntityInfo("Tabasco", "906130"),
    28: EntityInfo("Tamaulipas", "906560"),
    29: EntityInfo("Tlaxcala", "906990"),
    30: EntityInfo("Veracruz", "907420"),
    31: EntityInfo("Yucatán", "907850"),
    32: EntityInfo("Zacatecas", "908280"),
}

INPC_NACIONAL: Final[str] = "865541"

ENTITY_NAME_ALIASES: Dict[str, str] = {
    "CDMX": "Ciudad de México",
    "Coahuila": "Coahuila de Zaragoza",
    "Estado de México": "México",
    "Michoacán": "Michoacán de Ocampo",
    "Veracruz": "Veracruz de Ignacio de la Llave",
}
