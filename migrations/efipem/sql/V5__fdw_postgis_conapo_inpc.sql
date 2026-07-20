-- =======================================================================
-- V5: PostGIS + FDW cvegeo_municipalities (geometrías) + FDW CONAPO + FDW INPC
-- =======================================================================

CREATE EXTENSION IF NOT EXISTS postgis;

-- Foreign table de cvegeo_municipalities con geometrías (SRID 6368)
CREATE FOREIGN TABLE IF NOT EXISTS cvegeo_municipalities (
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

-- FDW para acceder al INPC (indice nacional de precios al consumidor)
CREATE SERVER IF NOT EXISTS inpc_server
FOREIGN DATA WRAPPER postgres_fdw
OPTIONS (
    dbname 'inpc',
    host '${inpc_host}',
    port '${inpc_port}'
);

CREATE USER MAPPING IF NOT EXISTS FOR CURRENT_USER
SERVER inpc_server
OPTIONS (
    user '${inpc_user}',
    password '${inpc_password}'
);

CREATE FOREIGN TABLE IF NOT EXISTS inpc_nacional (
    id              INTEGER,
    fecha           DATE,
    objeto_gasto_id INTEGER,
    indice_de_precios DOUBLE PRECISION,
    fecha_actualizacion DATE
)
SERVER inpc_server
OPTIONS (schema_name 'public', table_name 'inpc_nacional');

CREATE FOREIGN TABLE IF NOT EXISTS inpc_objetos_gasto (
    id            INTEGER,
    objeto_gasto  VARCHAR
)
SERVER inpc_server
OPTIONS (schema_name 'public', table_name 'objetos_gasto');
