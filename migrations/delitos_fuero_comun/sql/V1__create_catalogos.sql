-- =============================================================================
-- V1__create_catalogos.sql  |  Pipeline: delitos_fuero_comun
-- Catalog tables: bien_juridico_afectado, tipo_delito,
--                 subtipo_delito, modalidad.
-- Municipality reference: shared cvegeo_municipalities (FDW → cvegeo DB).
-- =============================================================================

-- ---------------------------------------------------------------------------
-- FDW: expose cvegeo_municipalities from the shared cvegeo database
-- ---------------------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS postgres_fdw;

DROP SERVER IF EXISTS cvegeo_server CASCADE;

CREATE SERVER cvegeo_server
    FOREIGN DATA WRAPPER postgres_fdw
    OPTIONS (
        dbname  '${fdw_dbname}',
        host    '${fdw_host}',
        port    '${fdw_port}'
    );

CREATE USER MAPPING FOR CURRENT_USER
    SERVER cvegeo_server
    OPTIONS (
        user     '${fdw_user}',
        password '${fdw_password}'
    );

CREATE FOREIGN TABLE cvegeo_municipalities (
    id        INTEGER,
    cvegeo    INTEGER,
    cve_ent   INTEGER,
    cve_mun   INTEGER,
    nomgeo    VARCHAR,
    nom_ent   VARCHAR
)
SERVER cvegeo_server
OPTIONS (schema_name 'public', table_name 'cvegeo_municipalities');

-- ---------------------------------------------------------------------------
-- Local catalog tables
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cat_bien_juridico_afectado (
    id                     SERIAL       PRIMARY KEY,
    bien_juridico_afectado VARCHAR(200) NOT NULL,
    CONSTRAINT uq_cat_bien_juridico_afectado UNIQUE (bien_juridico_afectado)
);

CREATE TABLE IF NOT EXISTS cat_tipo_delito (
    id          SERIAL       PRIMARY KEY,
    tipo_delito VARCHAR(200) NOT NULL,
    CONSTRAINT uq_cat_tipo_delito UNIQUE (tipo_delito)
);

-- subtipo → tipo relationship preserved via FK
CREATE TABLE IF NOT EXISTS cat_subtipo_delito (
    id             SERIAL       PRIMARY KEY,
    subtipo_delito VARCHAR(200) NOT NULL,
    tipo_delito_id INTEGER      NOT NULL REFERENCES cat_tipo_delito(id),
    CONSTRAINT uq_cat_subtipo_delito UNIQUE (subtipo_delito)
);

-- modalidad → subtipo relationship; NULL when modalidad == subtipo text
CREATE TABLE IF NOT EXISTS cat_modalidad (
    id                SERIAL       PRIMARY KEY,
    modalidad         VARCHAR(200) NOT NULL,
    subtipo_delito_id INTEGER      REFERENCES cat_subtipo_delito(id),
    CONSTRAINT uq_cat_modalidad UNIQUE (modalidad)
);
