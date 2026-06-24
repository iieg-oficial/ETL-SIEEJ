-- =======================================================================
-- V4: PostGIS + geometry en FDW cvegeo + FDW a CONAPO
-- =======================================================================

CREATE EXTENSION IF NOT EXISTS postgis;

-- Recrear foreign table de cvegeo con columna geometry
-- La vista stg_repd_case_current_vw depende de la foreign table, se recrea despues
DROP FOREIGN TABLE IF EXISTS cvegeo_municipalities CASCADE;
CREATE FOREIGN TABLE cvegeo_municipalities (
    id        INTEGER,
    cvegeo    INTEGER,
    cve_ent   INTEGER,
    cve_mun   INTEGER,
    nomgeo    VARCHAR,
    nom_ent   VARCHAR,
    geometry  geometry(MultiPolygon, 6372)
)
SERVER cvegeo_server
OPTIONS (schema_name 'public', table_name 'cvegeo_municipalities');

-- Recrear la vista analitica V3 que dependia de la foreign table
CREATE OR REPLACE VIEW stg_repd_case_current_vw AS
SELECT
    c.id,
    c.feb,
    s.name                          AS sex,
    n.name                          AS nationality,
    ar.name                         AS age_range,
    c.report_date,
    c.disappearance_date,
    c.disappearance_state_name,
    md.nomgeo                       AS disappearance_municipality,
    st.name                         AS status,
    c.location_date,
    lc.name                         AS location_condition,
    lcl.name                        AS location_classification,
    c.location_state_name,
    ml.nomgeo                       AS location_municipality,
    c.closure_date,
    ct.name                         AS closure_type,
    c.linked_feb,
    c.has_investigation_folder,
    c.current_version,
    c.created_at,
    c.updated_at
FROM stg_repd_case_current c
LEFT JOIN stg_repd_cat_sex s                        ON c.sex_id = s.id
LEFT JOIN stg_repd_cat_nationality n                ON c.nationality_id = n.id
LEFT JOIN stg_repd_cat_age_range ar                 ON c.age_range_id = ar.id
LEFT JOIN stg_repd_cat_status st                    ON c.status_id = st.id
LEFT JOIN stg_repd_cat_location_condition lc        ON c.location_condition_id = lc.id
LEFT JOIN stg_repd_cat_location_classification lcl  ON c.location_classification_id = lcl.id
LEFT JOIN stg_repd_cat_closure_type ct              ON c.closure_type_id = ct.id
LEFT JOIN cvegeo_municipalities md                  ON c.disappearance_municipality_id = md.id
LEFT JOIN cvegeo_municipalities ml                  ON c.location_municipality_id = ml.id;

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
