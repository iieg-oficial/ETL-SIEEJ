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
    id INTEGER,
    cve_ent INTEGER,
    nom_ent VARCHAR
)
SERVER cvegeo_server
OPTIONS (schema_name 'public', table_name 'cvegeo_states');

CREATE FOREIGN TABLE IF NOT EXISTS cvegeo_municipalities (
    id INTEGER,
    cvegeo  INTEGER,
    cve_ent INTEGER,
    cve_mun INTEGER,
    nomgeo  VARCHAR,
    nom_ent VARCHAR
)
SERVER cvegeo_server
OPTIONS (schema_name 'public', table_name 'cvegeo_municipalities');

COMMENT ON FOREIGN TABLE cvegeo_states IS
    'Catálogo de entidades federativas del Marco Geoestadístico (INEGI), expuesto vía postgres_fdw desde la base cvegeo.';
COMMENT ON COLUMN cvegeo_states.cve_ent IS
    'Clave de la entidad federativa (1 a 32) según el Catálogo Único de Claves de Áreas Geoestadísticas del INEGI.';
COMMENT ON COLUMN cvegeo_states.nom_ent IS
    'Nombre oficial de la entidad federativa.';

COMMENT ON FOREIGN TABLE cvegeo_municipalities IS
    'Catálogo de municipios del Marco Geoestadístico (INEGI), expuesto vía postgres_fdw desde la base cvegeo.';
COMMENT ON COLUMN cvegeo_municipalities.cvegeo IS
    'Clave geoestadística del municipio (cve_ent * 1000 + cve_mun).';
COMMENT ON COLUMN cvegeo_municipalities.nomgeo IS
    'Nombre oficial del municipio.';
