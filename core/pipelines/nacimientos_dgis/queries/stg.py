from core.pipelines.nacimientos_dgis.attributes import NacimientosDgisTables as T

COPY_STG = f"""
COPY {T.STG_NACIMIENTOS} (
    anio, cve_geo, edad_madre,
    tot_nac, nac_padre_conocido,
    nac_padre_18_mas, nac_padre_25_mas,
    fecha_actualizacion
) FROM STDIN WITH (FORMAT csv, HEADER false)
"""

TRUNCATE_STG = f"TRUNCATE {T.STG_NACIMIENTOS} RESTART IDENTITY"
