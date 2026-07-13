from enum import Enum


class BaseClass(Enum):
    def __init__(self, id, attribute):
        self.id = id
        self.attribute = attribute

    @classmethod
    def to_records(cls, attr_name: str) -> list[dict]:
        return [{"id": c.id, attr_name: c.attribute} for c in cls]


class Sector(BaseClass):
    no_aplica = (0, "No aplica")
    primario = (1, "Primario")
    secundario = (2, "Secundario")
    terciario = (3, "Terciario")
    no_especificado = (4, "No especificado")


class Ocupacion(BaseClass):
    no_aplica = (0, "No aplica")
    profesionales_tecnicos_arte = (1, "Profesionales, técnicos y trabajadores del arte")
    trabajadores_educacion = (2, "Trabajadores de la educación")
    funcionarios_directivos = (3, "Funcionarios y directivos")
    oficinistas = (4, "Oficinistas")
    industriales_artesanos_ayudantes = (5, "Trabajadores industriales, artesanos y ayudantes")
    comerciantes = (6, "Comerciantes")
    operadores_transporte = (7, "Operadores de transporte")
    servicios_personales = (8, "Trabajadores en servicios personales")
    proteccion_vigilancia = (9, "Trabajadores en protección y vigilancia")
    agropecuarios = (10, "Trabajadores agropecuarios")
    no_especificado = (11, "No especificado")


class SituacionTrabajo(BaseClass):
    no_aplica = (0, "No aplica")
    subordinados_remunerados = (1, "Trabajadores subordinados y remunerados")
    empleadores = (2, "Empleadores")
    cuenta_propia = (3, "Trabajadores por cuenta propia")
    sin_pago = (4, "Trabajadores sin pago")
    no_especificado = (5, "No especificado")
