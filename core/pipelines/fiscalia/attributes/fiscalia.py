from enum import  StrEnum, auto

class FiscaliaTables(StrEnum):
    def __getattribute__(self, name):
        return super().__getattribute__(name)

    ZONAS_GEOGRAFICAS = auto()

    COLONIAS = auto()
    CALLES = auto()
    CRUCES = auto()
    SEMANA = auto()
    VIOLENCIA = auto()
    DELITOS = auto()
    BIEN_AFECTADO = auto()
    CASOS = auto()

class FiscaliaColumns(StrEnum):
    ZONA_GEOGRAFICA = auto()
    MUNICIPIO = auto()

    COLONIA = auto()
    CALLE = auto()
    CRUCE = auto()

    FECHA_DENUNCIA = auto()
    DIA = auto()
    VIOLENCIA = auto()
    DELITO = auto()
    BIEN_AFECTADO = auto()
    HORA = auto()
    LONGITUD = auto()
    LATITUD = auto()
    COMISION = auto()
    VICTIMAS = auto()
    FECHA_ACTUALIZACION = auto()

    @classmethod
    def values(cls):
        return [c.value for c in cls]

    def __getattribute__(self, name):
        return super().__getattribute__(name)

