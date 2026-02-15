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
    fecha_denuncia = FiscaliaColumns.FECHA_DENUNCIA
    delito = FiscaliaColumns.DELITO
    hora = FiscaliaColumns.HORA
    colonia = FiscaliaColumns.COLONIA
    municipio = FiscaliaColumns.MUNICIPIO
    longitud = FiscaliaColumns.LONGITUD
    latitud = FiscaliaColumns.LATITUD

class RenameHistoricalCols(StrEnum):
    x = FiscaliaColumns.LONGITUD
    y = FiscaliaColumns.LATITUD

    @classmethod
    def rename(cls):
        return {member.name: member.value for member in cls}


@unique
class UpdateCols(BaseClass, StrEnum):
    fecha_denuncia = FiscaliaColumns.FECHA_DENUNCIA
    delito = FiscaliaColumns.DELITO
    hora = FiscaliaColumns.HORA
    violencia = FiscaliaColumns.VIOLENCIA
    colonia = FiscaliaColumns.COLONIA
    municipio = FiscaliaColumns.MUNICIPIO
    calle = FiscaliaColumns.CALLE
    cruce = FiscaliaColumns.CRUCE

    longitud = FiscaliaColumns.LONGITUD
    latitud = FiscaliaColumns.LATITUD

class RenameUpdateCols(StrEnum):
    x = FiscaliaColumns.LONGITUD
    y = FiscaliaColumns.LATITUD

    @classmethod
    def rename(cls):
        return {member.name: member.value for member in cls}
