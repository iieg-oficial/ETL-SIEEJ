from enum import StrEnum, unique, auto

from core.pipelines.fiscalia.attributes import FiscaliaColumns

class BaseClass:
    @classmethod
    def to_dict(cls):
        return {member.name: member.value for member in cls}

    @classmethod
    def get_keys(cls):
        return [member.name for member in cls]

    @classmethod
    def get_values(cls):
        return [member.value for member in cls]


@unique
class HistoricalCols(BaseClass, StrEnum):
    fecha = FiscaliaColumns.FECHA_DENUNCIA
    delito = FiscaliaColumns.DELITO
    colonia = FiscaliaColumns.COLONIA
    municipio = FiscaliaColumns.MUNICIPIO
    clave_mun = "id"
    hora = FiscaliaColumns.HORA
    violencia = FiscaliaColumns.ES_VIOLENCIA
    zona_geografica = FiscaliaColumns.ZONA_GEOGRAFICA
    bien_afectado = FiscaliaColumns.BIEN_AFECTADO

#TODO: Crear el mapping de UpdateCols con los cols de csv




if __name__ == "__main__":
    print(HistoricalCols.to_dict())
