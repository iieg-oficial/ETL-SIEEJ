-- =======================================================================
-- V2: Tablas catalogo EFIPEM
-- =======================================================================

CREATE TABLE IF NOT EXISTS cat_tema (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    CONSTRAINT uq_cat_tema_name UNIQUE (name)
);

CREATE TABLE IF NOT EXISTS cat_clasificador (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    CONSTRAINT uq_cat_clasificador_name UNIQUE (name)
);

-- Descripcion del clasificador (concepto financiero).
-- Un mismo nombre de concepto puede existir en distintos clasificadores,
-- por eso la llave natural es (clasificador_id, name).
CREATE TABLE IF NOT EXISTS cat_concepto (
    id              SERIAL PRIMARY KEY,
    clasificador_id INTEGER NOT NULL REFERENCES cat_clasificador (id),
    name            VARCHAR(255) NOT NULL,
    CONSTRAINT uq_cat_concepto_clasif_name UNIQUE (clasificador_id, name)
);

CREATE INDEX IF NOT EXISTS ix_cat_concepto_clasificador
    ON cat_concepto (clasificador_id);

CREATE TABLE IF NOT EXISTS cat_estatus (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    CONSTRAINT uq_cat_estatus_name UNIQUE (name)
);
