from enum import StrEnum, auto

class AMG(StrEnum):
    GUADALAJARA = auto()
    ZAPOPAN = auto()
    SAN_PEDRO_TLAQUEPAQUE = auto()
    TONALA = auto()
    TLAJOMULCO_DE_ZUNIGA = auto()
    EL_SALTO =  auto()
    IXTLAHUACAN_DE_LOS_MEMBRILLOS = auto()
    JUANACATLAN = auto()
    ZAPOTLANEJO = auto()
    ACATLAN_DE_JUAREZ = auto()

    @classmethod
    def values(cls):
        return [c.value for c in cls]
