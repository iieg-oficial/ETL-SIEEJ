from core.pipelines.fiscalia.mappings.tables import BienesAfectados
from core.pipelines.fiscalia.attributes.delitos import (
      ElPatrimonio,
      IntregridadCorporal,
      IntegridadSexual,
      LaFamilia
)
def map_bienes_to_delitos():
        return {
            **{delito: BienesAfectados.el_patrimonio.id for delito in ElPatrimonio.values()},
            **{delito: BienesAfectados.integrad_corporal.id for delito in IntregridadCorporal.values()},
            **{delito: BienesAfectados.integrad_sexual.id for delito in IntegridadSexual.values()},
            **{delito: BienesAfectados.la_familia.id for delito in LaFamilia.values()},
            **{delito: BienesAfectados.el_patrimonio.id for delito in ElPatrimonio.values()}
        }
