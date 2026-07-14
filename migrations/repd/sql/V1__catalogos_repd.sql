-- =======================================================================
-- V1: Foreign Data Wrapper + Tablas catalogo REPD
-- =======================================================================

-- FDW para acceder a cvegeo_municipalities (resolucion de municipios INEGI)
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

CREATE FOREIGN TABLE IF NOT EXISTS cvegeo_municipalities (
    id        INTEGER,
    cvegeo    INTEGER,
    cve_ent   INTEGER,
    cve_mun   INTEGER,
    nomgeo    VARCHAR,
    nom_ent   VARCHAR
)
SERVER cvegeo_server
OPTIONS (schema_name 'public', table_name 'cvegeo_municipalities');

-- Catalogos
CREATE TABLE IF NOT EXISTS cat_sexo (
    id          SERIAL PRIMARY KEY,
    nombre      VARCHAR(60) NOT NULL,
    CONSTRAINT uq_cat_sexo_nombre UNIQUE (nombre)
);

CREATE TABLE IF NOT EXISTS cat_nacionalidad (
    id          SERIAL PRIMARY KEY,
    nombre      VARCHAR(100) NOT NULL,
    CONSTRAINT uq_cat_nacionalidad_nombre UNIQUE (nombre)
);

CREATE TABLE IF NOT EXISTS cat_rango_edad (
    id          SERIAL PRIMARY KEY,
    nombre      VARCHAR(50) NOT NULL,
    CONSTRAINT uq_cat_rango_edad_nombre UNIQUE (nombre)
);

CREATE TABLE IF NOT EXISTS cat_estatus (
    id          SERIAL PRIMARY KEY,
    nombre      VARCHAR(100) NOT NULL,
    CONSTRAINT uq_cat_estatus_nombre UNIQUE (nombre)
);

CREATE TABLE IF NOT EXISTS cat_condicion_localizacion (
    id          SERIAL PRIMARY KEY,
    nombre      VARCHAR(60) NOT NULL,
    CONSTRAINT uq_cat_condicion_localizacion_nombre UNIQUE (nombre)
);

CREATE TABLE IF NOT EXISTS cat_clasificacion_localizacion (
    id          SERIAL PRIMARY KEY,
    nombre      VARCHAR(100) NOT NULL,
    CONSTRAINT uq_cat_clasificacion_localizacion_nombre UNIQUE (nombre)
);

CREATE TABLE IF NOT EXISTS cat_tipo_cierre (
    id          SERIAL PRIMARY KEY,
    nombre      VARCHAR(100) NOT NULL,
    CONSTRAINT uq_cat_tipo_cierre_nombre UNIQUE (nombre)
);
