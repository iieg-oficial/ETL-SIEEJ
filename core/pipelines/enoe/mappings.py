from enum import Enum, auto


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
    sector_informal = (1, "Sector informal")
    fuera_sector_informal = (2, "Fuera del sector informal")


class TipoLocalidad(BaseClass):
    mayor_100k = (1, "Localidades mayores de 100 000 habitantes")
    entre_15k_99k = (2, "Localidades de 15 000 a 99 999 habitantes")
    entre_2500_14k = (3, "Localidades de 2 500 a 14 999 habitantes")
    menor_2500 = (4, "Localidades menores de 2 500 habitantes")


class EstadoCivil(BaseClass):
    union_libre = (1, "Vive con su pareja en unión libre")
    separado = (2, "Está separado(a)")
    divorciado = (3, "Está divorciado(a)")
    viudo = (4, "Está viudo(a)")
    casado = (5, "Está casado(a)")
    soltero = (6, "Está soltero(a)")
    no_sabe = (9, "No sabe")


class NivelEducativo(BaseClass):
    ninguno = (0, "Ninguno")
    preescolar = (1, "Preescolar")
    primaria = (2, "Primaria")
    secundaria = (3, "Secundaria")
    preparatoria_bachillerato = (4, "Preparatoria o bachillerato")
    normal = (5, "Normal")
    carrera_tecnica = (6, "Carrera técnica")
    profesional = (7, "Profesional")
    maestria = (8, "Maestría")
    doctorado = (9, "Doctorado")
    no_sabe = (99, "No sabe")
