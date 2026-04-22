from enum import Enum, auto


class BaseClass(Enum):
    def __init__(self, id, attribute):
        self.id = id
        self.attribute = attribute

    @classmethod
    def to_records(cls, attr_name):
        return [{"id": c.id, attr_name: c.attribute} for c in cls]


class TiposEstablecimiento(BaseClass):
    de_apoyo = (auto(), "De apoyo")
    de_asistencia_social = (auto(), "De asistencia social")
    de_consulta_externa = (auto(), "De consulta externa")
    de_hospitalizacion = (auto(), "De hospitalización")


class EstratoUnidad(BaseClass):
    urbano = (auto(), "Urbano")
    rural = (auto(), "Rural")


class EstatusEstablecimiento(BaseClass):
    en_operacion = (auto(), "En operación")
    en_proceso_construccion = (auto(), "En proceso de construcción")
    pendiente = (auto(), "Pendiente de entrar en operación")
    fuera_operacion = (auto(), "Fuera de operación")


class Movimientos(BaseClass):
    alta = (auto(), "Alta")
    modificacion = (auto(), "Modificación")
    baja = (auto(), "Baja")


class NivelAtencion(BaseClass):
    primer_nivel = (auto(), "Primer nivel")
    segundo_nivel = (auto(), "Segundo nivel")
    tercer_nivel = (auto(), "Tercer nivel")
    no_aplica = (auto(), "No aplica")
