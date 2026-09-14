from enum import StrEnum, auto


class NacimientosDgisTables(StrEnum):
    # Agregado por edad de la madre: una fila por año, municipio y edad.
    STG_NACIMIENTOS_EDAD_MADRE = auto()

    # Microdato: una fila por certificado de nacimiento.
    STG_NACIMIENTOS_CERTIFICADOS = auto()

    # Catálogos de dominio cerrado publicados por SINAC.
    CAT_SI_NO = auto()
    CAT_SEXO = auto()
    CAT_ESTADO_CONYUGAL = auto()
    CAT_ESCOLARIDAD = auto()
    CAT_AFILIACION = auto()
    CAT_OCUPACION_HABITUAL = auto()
    CAT_LUGAR_NACIMIENTO = auto()
    CAT_PRODUCTO_EMBARAZO = auto()
    CAT_RESOLUCION_EMBARAZO = auto()
    CAT_ENTIDAD = auto()
    CAT_MUNICIPIO = auto()
    CAT_LOCALIDAD = auto()
    CAT_DIAGNOSTICO = auto()
    CAT_ESTABLECIMIENTO_SALUD = auto()

    @classmethod
    def catalogs(cls) -> list["NacimientosDgisTables"]:
        return [table for table in cls if table.startswith("cat_")]
