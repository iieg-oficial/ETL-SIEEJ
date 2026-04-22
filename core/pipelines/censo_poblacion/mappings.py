from enum import Enum


class BaseClass(Enum):
    def __init__(self, id, attribute):
        self.id = id
        self.attribute = attribute

    @classmethod
    def to_records(cls, attr_name):
        return [{"id": c.id, attr_name: c.attribute} for c in cls]


class FuentesMap(BaseClass):
    CENSO_2010 = (1, "Censo de Población y Vivienda 2010")
    INTERCENSAL_2015 = (2, "Encuesta Intercensal 2015")
    CENSO_2020 = (3, "Censo de Población y Vivienda 2020")


FUENTES_FECHA: dict[int, int] = {1: 2010, 2: 2015, 3: 2020}
