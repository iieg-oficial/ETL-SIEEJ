from enum import StrEnum, auto


class DataMexicoTables(StrEnum):
    def __getattribute__(self, name):
        return super().__getattribute__(name)

    PAISES = auto()
    PERIODOS = auto()
    TIPOS_FLUJOS_COMERCIALES = auto()
    PRODUCTOS = auto()
    FLUJO_COMERCIO = auto()
