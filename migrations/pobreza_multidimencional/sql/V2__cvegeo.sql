-- =======================================================================
-- V2__cvegeo.sql  |  Pipeline: pobreza_multidimencional
-- Foreign Data Wrapper hacia la BD cvegeo del IIEG.
-- =======================================================================

CREATE EXTENSION IF NOT EXISTS postgres_fdw;

CREATE SERVER IF NOT EXISTS cvegeo_server
    FOREIGN DATA WRAPPER postgres_fdw
    OPTIONS (
        dbname '${fdw_dbname}',
        host   '${fdw_host}',
        port   '${fdw_port}'
    );

CREATE USER MAPPING IF NOT EXISTS FOR CURRENT_USER
    SERVER cvegeo_server
    OPTIONS (
        user     '${fdw_user}',
        password '${fdw_password}'
    );

CREATE FOREIGN TABLE IF NOT EXISTS public.cvegeo_municipalities (
    id      INTEGER,
    cvegeo  INTEGER,
    cve_ent INTEGER,
    cve_mun INTEGER,
    nomgeo  VARCHAR,
    nom_ent VARCHAR
)
SERVER cvegeo_server
OPTIONS (schema_name 'public', table_name 'cvegeo_municipalities');
