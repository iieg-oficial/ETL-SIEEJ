from enum import Enum, auto


class BaseClass(Enum):
    def __init__(self, id, attribute):
        self.id = id
        self.attribute = attribute

    @classmethod
    def to_records(cls, attr_name):
        return [{"id": c.id, attr_name: c.attribute} for c in cls]


class ObjetoGasto(BaseClass):
    indice_general = (auto(), "Índice general")
    alimentos_bebidas_y_tabaco = (auto(), "Alimentos, bebidas y tabaco")
    ropa_calzado_y_accesorios = (auto(), "Ropa, calzado y accesorios")
    vivienda = (auto(), "Vivienda")
    muebles_aparatos_y_accesorios_domesticos = (auto(), "Muebles, aparatos y accesorios domésticos")
    salud_y_cuidado_personal = (auto(), "Salud y cuidado personal")
    transporte = (auto(), "Transporte")
    educacion_y_esparcimiento = (auto(), "Educación y esparcimiento")
    otros_servicios = (auto(), "Otros servicios")
