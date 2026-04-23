-- =======================================================================
-- V2__cvegeo.sql  |  Pipeline: etef
-- Conexión FDW a la BD cvegeo para resolver municipios y entidades.
-- =======================================================================

CREATE EXTENSION IF NOT EXISTS postgres_fdw;

CREATE SERVER IF NOT EXISTS cvegeo_server
    FOREIGN DATA WRAPPER postgres_fdw
    OPTIONS (host 'localhost', port '5432', dbname 'cvegeo');

CREATE USER MAPPING IF NOT EXISTS FOR CURRENT_USER
    SERVER cvegeo_server
    OPTIONS (user 'bi_iieg', password 'changeme');

CREATE FOREIGN TABLE IF NOT EXISTS public.cvegeo_municipalities (
    id      INTEGER,
    cvegeo  INTEGER,
    cve_ent INTEGER,
    cve_mun INTEGER,
    nomgeo  VARCHAR,
    nom_ent VARCHAR
) SERVER cvegeo_server
    OPTIONS (schema_name 'public', table_name 'municipalities');
