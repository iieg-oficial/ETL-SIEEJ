-- =======================================================================
-- V2: Tablas catalogo EFIPEM
-- =======================================================================

CREATE TABLE IF NOT EXISTS stg_efipem_cat_trimestre (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(10) NOT NULL,
    CONSTRAINT uq_efipem_cat_trimestre_name UNIQUE (name)
);

CREATE TABLE IF NOT EXISTS stg_efipem_cat_tema (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    CONSTRAINT uq_efipem_cat_tema_name UNIQUE (name)
);

CREATE TABLE IF NOT EXISTS stg_efipem_cat_clasificador (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    CONSTRAINT uq_efipem_cat_clasificador_name UNIQUE (name)
);

-- Descripcion del clasificador (concepto financiero).
-- Un mismo nombre de concepto puede existir en distintos clasificadores,
-- por eso la llave natural es (clasificador_id, name).
CREATE TABLE IF NOT EXISTS stg_efipem_cat_concepto (
    id              SERIAL PRIMARY KEY,
    clasificador_id INTEGER NOT NULL REFERENCES stg_efipem_cat_clasificador (id),
    name            VARCHAR(255) NOT NULL,
    CONSTRAINT uq_efipem_cat_concepto_clasif_name UNIQUE (clasificador_id, name)
);

CREATE INDEX IF NOT EXISTS ix_efipem_cat_concepto_clasificador
    ON stg_efipem_cat_concepto (clasificador_id);

CREATE TABLE IF NOT EXISTS stg_efipem_cat_estatus (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    CONSTRAINT uq_efipem_cat_estatus_name UNIQUE (name)
);
