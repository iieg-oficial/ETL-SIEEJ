from enum import StrEnum, unique

from core.pipelines.fiscalia.attributes.fiscalia import FiscaliaColumns

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

@unique
class UpdateCols(BaseClass, StrEnum):
    fecha_denuncia = FiscaliaColumns.FECHA_DENUNCIA
    delito = FiscaliaColumns.DELITO
    colonia = FiscaliaColumns.COLONIA
    municipio = FiscaliaColumns.MUNICIPIO
    clave_mun = "id"
    calle = FiscaliaColumns.CALLE
    cruce = FiscaliaColumns.CRUCE
    localidad = FiscaliaColumns.LOCALIDAD

