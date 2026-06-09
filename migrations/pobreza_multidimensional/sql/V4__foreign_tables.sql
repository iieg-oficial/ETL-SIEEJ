-- =======================================================================
-- V4__foreign_tables.sql  |  Pipeline: pobreza_multidimensional
-- Tablas foráneas para geometrías municipales (cvegeo FDW).
-- =======================================================================

CREATE EXTENSION IF NOT EXISTS postgres_fdw;
CREATE EXTENSION IF NOT EXISTS postgis;

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

CREATE FOREIGN TABLE IF NOT EXISTS cvegeo_municipalities (
    id      INTEGER,
    cvegeo  INTEGER,
    cve_ent INTEGER,
    cve_mun INTEGER,
    nomgeo  VARCHAR,
    nom_ent VARCHAR,
    geometry geometry
)
SERVER cvegeo_server
OPTIONS (schema_name 'public', table_name 'cvegeo_municipalities');
