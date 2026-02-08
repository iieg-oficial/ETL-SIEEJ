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
    clave_mun = "id"
    fecha = FiscaliaColumns.FECHA_DENUNCIA
    delito = FiscaliaColumns.DELITO
    colonia = FiscaliaColumns.COLONIA
    municipio = FiscaliaColumns.MUNICIPIO
    hora = FiscaliaColumns.HORA
    violencia = FiscaliaColumns.VIOLENCIA
    zona_geografica = FiscaliaColumns.ZONA_GEOGRAFICA
    bien_afectado = FiscaliaColumns.BIEN_AFECTADO

class RenameHistoricalCols(StrEnum):
    clave_mun =  "id"
    fecha = FiscaliaColumns.FECHA_DENUNCIA

    @classmethod
    def rename(cls):
        return {member.name: member.value for member in cls}


class RenameLocalidades(BaseClass, StrEnum):
    CVE_LOC = "id"
    NOM_LOC = "localidad"

    @classmethod
    def rename(cls):
        return {member.name: member.value for member in cls}

@unique
class UpdateCols(BaseClass, StrEnum):
    clave_mun = "id"
    fecha_denuncia = FiscaliaColumns.FECHA_DENUNCIA
    delito = FiscaliaColumns.DELITO
    colonia = FiscaliaColumns.COLONIA
    municipio = FiscaliaColumns.MUNICIPIO
    calle = FiscaliaColumns.CALLE
    cruce = FiscaliaColumns.CRUCE
    localidad = FiscaliaColumns.LOCALIDAD

if __name__ == "__main__":
    print(RenameLocalidades.rename())
    print(RenameLocalidades.get_values())
