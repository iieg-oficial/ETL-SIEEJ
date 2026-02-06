from core.pipelines.fiscalia.mappings.schemas import BienesAfectados
def map_bienes_to_delitos():
        return {
            **{delito: BienesAfectados.el_patrimonio.id for delito in ElPatrimonio.values()},
            **{delito: BienesAfectados.integrad_corporal.id for delito in IntregridadCorporal.values()},
            **{delito: BienesAfectados.la_familia.id for delito in LaFamilia.values()},
            **{delito: BienesAfectados.el_patrimonio.id for delito in ElPatrimonio.values()}
        }
