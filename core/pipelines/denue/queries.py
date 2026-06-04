from core.pipelines.denue.attributes import DenueTables as T

TMP_TABLE_DDL = """
DROP TABLE IF EXISTS tmp_raw;
CREATE TEMP TABLE tmp_raw (
    clee TEXT,
    id INTEGER,
    nombre_establecimiento TEXT,
    razon_social TEXT,
    latitud FLOAT,
    longitud FLOAT,
    fecha_alta DATE,
    nombre_asentamiento TEXT,
    ageb TEXT,
    codigo_actividad TEXT,
    entidad_id INTEGER,
    cve_mun INTEGER,
    localidad_id INTEGER,
    fecha_actualizacion DATE,
    rango_personal_id INTEGER,
    tipo_establecimiento_id INTEGER
)
"""

SECTOR_RANGO_CASE = """
CASE
    WHEN LEFT(r.codigo_actividad, 2) IN ('31','32','33') THEN '31-33'
    WHEN LEFT(r.codigo_actividad, 2) IN ('48','49') THEN '48-49'
    ELSE LEFT(r.codigo_actividad, 2)
END
"""

INSERT_FROM_RAW = f"""
INSERT INTO {T.STG_EST_JAL} (
    id, actualizacion_id, clee, nombre_establecimiento, razon_social,
    latitud, longitud, fecha_alta, nombre_asentamiento, ageb,
    localidad_id, sector_id, subsector_id, rama_id, subrama_id,
    clase_actividad_id, rango_personal_id, tipo_establecimiento_id
)
SELECT
    r.id,
    ca.id,
    r.clee,
    r.nombre_establecimiento,
    r.razon_social,
    r.latitud,
    r.longitud,
    r.fecha_alta,
    r.nombre_asentamiento,
    r.ageb,
    cl.id,
    cs.id,
    csub.id,
    cr.id,
    csr.id,
    cca.id,
    r.rango_personal_id,
    r.tipo_establecimiento_id
FROM tmp_raw r
LEFT JOIN {T.CAT_ACTUALIZACIONES} ca ON ca.fecha_actualizacion = r.fecha_actualizacion
LEFT JOIN {T.CAT_LOCALIDADES} cl ON cl.cve_geo_id = (
    r.entidad_id * 10000000 + r.cve_mun * 10000 + r.localidad_id
)
LEFT JOIN {T.CAT_SECTORES} cs ON cs.codigo = {SECTOR_RANGO_CASE}
LEFT JOIN {T.CAT_SUBSECTORES} csub ON csub.codigo = LEFT(r.codigo_actividad, 3)
LEFT JOIN {T.CAT_RAMAS} cr ON cr.codigo = LEFT(r.codigo_actividad, 4)
LEFT JOIN {T.CAT_SUBRAMAS} csr ON csr.codigo = LEFT(r.codigo_actividad, 5)
LEFT JOIN {T.CAT_CLASES_ACTIVIDAD} cca ON cca.codigo = r.codigo_actividad
ON CONFLICT (id, actualizacion_id) DO UPDATE SET
    clee = EXCLUDED.clee,
    nombre_establecimiento = EXCLUDED.nombre_establecimiento,
    razon_social = EXCLUDED.razon_social,
    latitud = EXCLUDED.latitud,
    longitud = EXCLUDED.longitud,
    fecha_alta = EXCLUDED.fecha_alta,
    nombre_asentamiento = EXCLUDED.nombre_asentamiento,
    ageb = EXCLUDED.ageb,
    localidad_id = EXCLUDED.localidad_id,
    sector_id = EXCLUDED.sector_id,
    subsector_id = EXCLUDED.subsector_id,
    rama_id = EXCLUDED.rama_id,
    subrama_id = EXCLUDED.subrama_id,
    clase_actividad_id = EXCLUDED.clase_actividad_id,
    rango_personal_id = EXCLUDED.rango_personal_id,
    tipo_establecimiento_id = EXCLUDED.tipo_establecimiento_id
"""
