from enum import Enum, auto


class BaseClass(Enum):
    def __init__(self, id, attribute):
        self.id = id
        self.attribute = attribute

    @classmethod
    def to_records(cls, attr_name):
        return [{"id": c.id, attr_name: c.attribute} for c in cls]

class Turnos(BaseClass):
    MATUTINO = (auto(), "Matutino")
    VESPERTINO = (auto(), "Vespertino")
    CONTINUO = (auto(), "Continuo")
    DISCONTINUO = (auto(), "Discontinuo")
    NOCTURNO = (auto(), "Nocturno")

class TipoEducativo(BaseClass):
    BASICA = (auto(), "Básica")
    ESPECIAL = (auto(), "Especial")
    MEDIA_SUPERIOR = (auto(), "Media superior")
    INICIAL = (auto(), "Inicial")
    SUPERIOR = (auto(), "Superior")
    CAPACITACION = (auto(), "Capacitación")


class NivelEducativo(BaseClass):
    INICIAL = (auto(), "Inicial")
    INICIAL_GENERAL = (auto(), "Inicial General")
    PREESCOLAR = (auto(), "Preescolar")
    CAM = (auto(), "Centro de atención múltiple")
    PRIMARIA = (auto(), "Primaria")
    SECUNDARIA = (auto(), "Secundaria")
    BACHILLERATO = (auto(), "Bachillerato")
    FORMACION_PARA_EL_TRABAJO = (auto(), "Formación para el trabajo")
    LICENCIATURA = (auto(), "Licenciatura")

class ServicioEducativo(BaseClass):
    LACTANTE_Y_MATERNAL = (auto(), "Lactante y maternal")
    INICIAL_NO_ESCOLARIZADA = (auto(), "Inicial no escolarizada")
    INICIAL_INDIGENA = (auto(), "Inicial indígena")
    GENERAL = (auto(), "General")
    INDIGENA = (auto(), "Indígena")
    COMUNITARIO = (auto(), "Comunitario")
    USAER = (auto(), "Unidad de servicios de apoyo a la educación regular")
    TECNICA = (auto(), "Técnica")
    TELESECUNDARIA = (auto(), "Telesecundaria")
    FORMACION_PARA_EL_TRABAJO = (auto(), "Formación para el trabajo")
    PROFESIONAL_TECNICO_BACHILLER = (auto(), "Profesional técnico bachiller")
    BACHILLERATO_GENERAL = (auto(), "Bachillerato general")
    TECNOLOGICO = (auto(), "Tecnológico")
    LICENCIATURA_UNIVERSITARIA_Y_TECNOLOGICA = (auto(), "Licenciatura universitaria y tecnológica")

class NombreControl(BaseClass):
    PUBLICO = (auto(), "Público")
    PRIVADO = (auto(), "Privado")

class TipoSostenimiento(BaseClass):
    FEDERAL_TRANSFERIDO = (auto(), "Federal transferido")
    FEDERAL = (auto(), "Federal")
    ESTATAL = (auto(), "Estatal")
    PRIVADO = (auto(), "Privado")
    AUTONOMO = (auto(), "Autónomo")
    SUBSIDIO = (auto(), "Subsidio")

if __name__ == "__main__":
    # print(TipoEducativo.to_records("tipo_educativo"))
    print(ServicioEducativo.to_records("servicio_educativo"))

