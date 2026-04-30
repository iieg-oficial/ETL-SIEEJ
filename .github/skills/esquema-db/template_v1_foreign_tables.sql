-- =============================================================================
-- V1__foreign_tables.sql
-- Tablas foráneas (FDW) para acceder a cvegeo_municipalities y cvegeo_states.
-- Usar SOLO si el pipeline tiene nivel geográfico municipal o estatal.
-- Flyway sustituye ${var} con los valores definidos en flyway.conf.
-- =============================================================================

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

-- Tabla de estados (incluir si el pipeline maneja nivel estatal)
CREATE FOREIGN TABLE IF NOT EXISTS cvegeo_states (
    id      INTEGER,
    cve_ent INTEGER,
    nom_ent VARCHAR
)
SERVER cvegeo_server
OPTIONS (schema_name 'public', table_name 'cvegeo_states');

-- Tabla de municipios (incluir si el pipeline maneja nivel municipal)
CREATE FOREIGN TABLE IF NOT EXISTS cvegeo_municipalities (
    id      INTEGER,
    cvegeo  INTEGER,
    cve_ent INTEGER,
    cve_mun INTEGER,
    nomgeo  VARCHAR,
    nom_ent VARCHAR
)
SERVER cvegeo_server
OPTIONS (schema_name 'public', table_name 'cvegeo_municipalities');

-- Eliminar las CREATE FOREIGN TABLE que no apliquen al nivel geográfico del pipeline.
