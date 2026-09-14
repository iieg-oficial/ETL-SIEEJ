from core.pipelines.nacimientos_dgis.attributes import NacimientosDgisTables as T
from core.pipelines.nacimientos_dgis.schemas import StgNacimientosCertificados

CERTIFICADO_COLUMNS = ",\n    ".join(
    column for column in StgNacimientosCertificados.columns() if column != StgNacimientosCertificados.id.key
)

COPY_STG = f"""
COPY {T.STG_NACIMIENTOS_EDAD_MADRE} (
    anio, cve_geo, edad_madre,
    tot_nac, nac_padre_conocido,
    nac_padre_18_mas, nac_padre_25_mas,
    fecha_actualizacion
) FROM STDIN WITH (FORMAT csv, HEADER false)
"""

TRUNCATE_STG = f"TRUNCATE {T.STG_NACIMIENTOS_EDAD_MADRE} RESTART IDENTITY"

COPY_CERTIFICADOS = f"""
COPY {T.STG_NACIMIENTOS_CERTIFICADOS} (
    {CERTIFICADO_COLUMNS}
) FROM STDIN WITH (FORMAT csv, HEADER false)
"""

TRUNCATE_CERTIFICADOS = f"TRUNCATE {T.STG_NACIMIENTOS_CERTIFICADOS} RESTART IDENTITY"
