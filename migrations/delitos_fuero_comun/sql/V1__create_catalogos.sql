-- =============================================================================
-- V1__create_catalogos.sql  |  Pipeline: delitos_fuero_comun
-- Catalog tables: municipio, bien_juridico_afectado, tipo_delito,
--                 subtipo_delito, modalidad.
-- =============================================================================

-- Municipality catalog (natural key cve_municipio 5-digit INEGI code)
CREATE TABLE IF NOT EXISTS cat_municipio (
    id            SERIAL       PRIMARY KEY,
    cve_municipio VARCHAR(5)   NOT NULL,
    clave_ent     VARCHAR(2)   NOT NULL,
    entidad       VARCHAR(200) NOT NULL,
    municipio     VARCHAR(200) NOT NULL,
    CONSTRAINT uq_cat_municipio_cve UNIQUE (cve_municipio)
);

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
