from enum import StrEnum


class PendientesProducts(StrEnum):
    MODELO_ELEVACION_ACONDICIONADO = "modelo_elevacion_acondicionado"
    GRADOS = "pendiente_grados"
    PORCENTAJE = "pendiente_porcentaje"


class PendientesTables(StrEnum):
    FUENTES_LIMITES_MUNICIPALES = "fuentes_limites_municipales"
    ESTADISTICAS_PENDIENTE_MUNICIPALES = "estadisticas_pendiente_municipales"
