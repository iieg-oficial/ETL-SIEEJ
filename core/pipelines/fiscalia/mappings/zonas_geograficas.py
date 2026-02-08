from core.pipelines.fiscalia.attributes.amg import AMG
from core.pipelines.fiscalia.mappings.schemas import ZonasGeograficas
from core.pipelines.fiscalia.helpers.normalize import normalize_text

def map_municipios_to_zonas_geo(df):
    municipios = df["municipio"].dropna().unique()
    zg = {}
    for mun in municipios:
        if normalize_text(mun) in AMG.values():
            zg[mun] = ZonasGeograficas.AMG.id
        else:
            zg[mun] = ZonasGeograficas.Interior.id
    return zg
