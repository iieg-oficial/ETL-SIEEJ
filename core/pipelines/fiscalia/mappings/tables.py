from enum import Enum, auto

from core.pipelines.fiscalia.attributes.delitos import (
    IntregridadCorporal,
    IntegridadSexual,
    LaFamilia,
    ElPatrimonio
)
class BaseClass(Enum):
    def __init__(self, id, attrtibute):
        self.id = id
        self.attrtibute = attrtibute
    @classmethod
    def to_records(cls, _attr_name):
        return [
            {'id': c.id, _attr_name: c.attrtibute}
            for c in cls
        ]

class ZonasGeograficas(BaseClass):
    AMG = (auto(), "AMG")
    Interior = (auto(), "Interior")
class BienesAfectados(BaseClass):
    integrad_corporal = (auto(), "La vida y la integridad corporal")
    integrad_sexual = (auto(), "La vida y la integridad sexual")
    la_familia  = (auto(), "La familia")
    el_patrimonio = (auto(), "El patrimonio")
    otros_bienes_afectados = (auto(), "Otros bienes afectados")

class Delitos(BaseClass):
    homicidio_doloso = (auto(), IntregridadCorporal.homicidio_doloso.value)
    lesiones_dolosas = (auto(), IntregridadCorporal.lesiones_dolosas.value)
    feminicidio = (auto(), IntregridadCorporal.feminicidio.value)
    violacion = (auto(), IntegridadSexual.violacion.value)
    abuso_sexual_infantil = (auto(), IntegridadSexual.abuso_sexual_infantil.value)
    violencia_familiar  = (auto(), LaFamilia.violencia_familiar.value)
    robo_carga_pesada =  (auto(), ElPatrimonio.robo_carga_pesada.value)
    robo_vehiculos_particulares = (auto(), ElPatrimonio.robo_vehiculos_particulares.value)
    robo_habitacion = (auto(), ElPatrimonio.robo_habitacion.value)
    robo_motocicletas = (auto(), ElPatrimonio.robo_motocicletas.value)
    robo_negocio = (auto(), ElPatrimonio.robo_negocio.value)
    robo_persona = (auto(), ElPatrimonio.robo_persona.value)
    robo_int_vehiculos = (auto(), ElPatrimonio.robo_int_vehiculos.value)
    robo_autopartes = (auto(), ElPatrimonio.robo_autopartes.value)
    robo_cuentahabitantes = (auto(), ElPatrimonio.robo_cuentahabitantes.value)
    robo_bancos = (auto(), ElPatrimonio.robo_bancos.value)

class EsViolencia(BaseClass):
    con_violencia = (auto(), "Con violencia")
    sin_violencia = (auto(), "Sin violencia")
