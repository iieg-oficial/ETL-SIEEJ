from enum import Enum, auto


class BaseClass(Enum):
    def __init__(self, id, attribute):
        self.id = id
        self.attribute = attribute

    @classmethod
    def to_records(cls, attr_name):
        return [{"id": c.id, attr_name: c.attribute} for c in cls]


class GradosMarginacion(BaseClass):
    muy_bajo = (auto(), "Muy bajo")
    bajo = (auto(), "Bajo")
    medio = (auto(), "Medio")
    alto = (auto(), "Alto")
    muy_alto = (auto(), "Muy alto")
