from enum import Enum

from core.utils import normalize_text


class BaseClass(Enum):
    @classmethod
    def values(cls):
        return [c.value for c in cls]

    @classmethod
    def norm_values(cls):
        return [normalize_text(c.value) for c in cls]


class IntregridadCorporal(BaseClass):
    homicidio_doloso = "Homicidio doloso"
    lesiones_dolosas = "Lesiones dolosas"
    feminicidio = "Feminicidio"


class IntegridadSexual(BaseClass):
    violacion = "Violación"
    abuso_sexual_infantil = "Abuso sexual infantil"


class LaFamilia(BaseClass):
    violencia_familiar = "Violencia familiar"
    violencia_vicaria = "Violencia vicaria"


class ElPatrimonio(BaseClass):
    robo_carga_pesada = "Robo a carga pesada"
    robo_vehiculos_particulares = "Robo a vehículos particulares"
    robo_habitacion = "Robo casa habitación"
    robo_motocicletas = "Robo de motocicleta"
    robo_negocio = "Robo a negocio"
    robo_persona = "Robo a persona"
    robo_int_vehiculos = "Robo a int de vehículos"
    robo_autopartes = "Robo de autopartes"
    robo_cuentahabitantes = "Robo a cuentahabientes"
    robo_bancos = "Robo a bancos"
