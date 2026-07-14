-- =======================================================================
-- V4: PostGIS + geometry en FDW cvegeo + FDW a CONAPO
-- =======================================================================

CREATE EXTENSION IF NOT EXISTS postgis;

-- Recrear foreign table de cvegeo con columnas geom_iieg y geom_inegi (SRID 6368)
-- La vista vw_repd depende de la foreign table, se recrea despues
DROP FOREIGN TABLE IF EXISTS cvegeo_municipalities CASCADE;
CREATE FOREIGN TABLE cvegeo_municipalities (
    id          INTEGER,
    cvegeo      INTEGER,
    cve_ent     INTEGER,
    cve_mun     INTEGER,
    nomgeo      VARCHAR,
    nom_ent     VARCHAR,
    geom_iieg   geometry(MultiPolygon, 6368),
    geom_inegi  geometry(MultiPolygon, 6368),
    region      VARCHAR,
    area_km2_iieg   DOUBLE PRECISION,
    area_km2_inegi  DOUBLE PRECISION,
    area_ha_iieg    DOUBLE PRECISION,
    area_ha_inegi   DOUBLE PRECISION
)
SERVER cvegeo_server
OPTIONS (schema_name 'public', table_name 'cvegeo_municipalities');

-- Recrear la vista analitica V3 que dependia de la foreign table
CREATE OR REPLACE VIEW vw_repd AS
SELECT
    c.id,
    c.feb,
    s.nombre                        AS sexo,
    n.nombre                        AS nacionalidad,
    ar.nombre                       AS rango_edad,
    c.fecha_reporte,
    c.fecha_desaparicion,
    c.estado_desaparicion,
    md.nomgeo                       AS municipio_desaparicion,
    st.nombre                       AS estatus,
    c.fecha_localizacion,
    lc.nombre                       AS condicion_localizacion,
    lcl.nombre                      AS clasificacion_localizacion,
    c.estado_localizacion,
    ml.nomgeo                       AS municipio_localizacion,
    c.fecha_cierre,
    ct.nombre                       AS tipo_cierre,
    c.feb_vinculado,
    c.tiene_carpeta_investigacion,
    c.version_actual,
    c.fecha_creacion,
    c.fecha_actualizacion
FROM stg_repd_casos c
LEFT JOIN cat_sexo s                            ON c.sexo_id = s.id
LEFT JOIN cat_nacionalidad n                    ON c.nacionalidad_id = n.id
LEFT JOIN cat_rango_edad ar                     ON c.rango_edad_id = ar.id
LEFT JOIN cat_estatus st                        ON c.estatus_id = st.id
LEFT JOIN cat_condicion_localizacion lc         ON c.condicion_localizacion_id = lc.id
LEFT JOIN cat_clasificacion_localizacion lcl    ON c.clasificacion_localizacion_id = lcl.id
LEFT JOIN cat_tipo_cierre ct                    ON c.tipo_cierre_id = ct.id
LEFT JOIN cvegeo_municipalities md              ON c.municipio_desaparicion_id = md.id
LEFT JOIN cvegeo_municipalities ml              ON c.municipio_localizacion_id = ml.id;

-- FDW para acceder a CONAPO (poblacion municipal por sexo y anio)
CREATE SERVER IF NOT EXISTS conapo_server
FOREIGN DATA WRAPPER postgres_fdw
OPTIONS (
    dbname 'conapo',
    host '${fdw_host}',
    port '${fdw_port}'
);

CREATE USER MAPPING IF NOT EXISTS FOR CURRENT_USER
SERVER conapo_server
OPTIONS (
    user '${fdw_user}',
    password '${fdw_password}'
);

CREATE FOREIGN TABLE IF NOT EXISTS conapo_poblacion (
    municipio_id  INTEGER,
    sexo_id       INTEGER,
    anio          INTEGER,
    pob_total     INTEGER
)
SERVER conapo_server
OPTIONS (schema_name 'public', table_name 'stg_poblacion_mitad_anio');
