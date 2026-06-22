-- =======================================================================
-- V1: Foreign Data Wrappers (cvegeo + conapo) + Tablas catalogo REPD
-- =======================================================================

CREATE EXTENSION IF NOT EXISTS postgres_fdw;
CREATE EXTENSION IF NOT EXISTS postgis;

-- FDW para acceder a cvegeo_municipalities (geometrias + resolucion de municipios)
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

CREATE FOREIGN TABLE IF NOT EXISTS cvegeo_municipalities (
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

-- Catalogos
CREATE TABLE IF NOT EXISTS stg_repd_cat_sex (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(60) NOT NULL,
    CONSTRAINT uq_repd_cat_sex_name UNIQUE (name)
);

CREATE TABLE IF NOT EXISTS stg_repd_cat_nationality (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    CONSTRAINT uq_repd_cat_nationality_name UNIQUE (name)
);

CREATE TABLE IF NOT EXISTS stg_repd_cat_age_range (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(50) NOT NULL,
    CONSTRAINT uq_repd_cat_age_range_name UNIQUE (name)
);

CREATE TABLE IF NOT EXISTS stg_repd_cat_status (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    CONSTRAINT uq_repd_cat_status_name UNIQUE (name)
);

CREATE TABLE IF NOT EXISTS stg_repd_cat_location_condition (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(60) NOT NULL,
    CONSTRAINT uq_repd_cat_location_condition_name UNIQUE (name)
);

CREATE TABLE IF NOT EXISTS stg_repd_cat_location_classification (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    CONSTRAINT uq_repd_cat_location_classification_name UNIQUE (name)
);

CREATE TABLE IF NOT EXISTS stg_repd_cat_closure_type (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    CONSTRAINT uq_repd_cat_closure_type_name UNIQUE (name)
);
