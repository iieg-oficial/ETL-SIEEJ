-- =======================================================================
-- V1: Foreign Data Wrapper hacia la BD cvegeo
--     Expone cvegeo_states (nivel entidad) para resolver la entidad
--     federativa a la que corresponde cada registro de EFIPEM.
-- =======================================================================

CREATE EXTENSION IF NOT EXISTS postgres_fdw;

CREATE SERVER IF NOT EXISTS cvegeo_server
FOREIGN DATA WRAPPER postgres_fdw
OPTIONS (
    dbname '${fdw_dbname}',
    host '${fdw_host}',
    port '${fdw_port}'
);

CREATE USER MAPPING IF NOT EXISTS FOR CURRENT_USER
SERVER cvegeo_server
OPTIONS (
    user '${fdw_user}',
    password '${fdw_password}'
);

CREATE FOREIGN TABLE IF NOT EXISTS cvegeo_states (
    id       INTEGER,
    cve_ent  INTEGER,
    nom_ent  VARCHAR
)
SERVER cvegeo_server
OPTIONS (schema_name 'public', table_name 'cvegeo_states');
