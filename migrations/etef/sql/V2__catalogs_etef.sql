CREATE TABLE IF NOT EXISTS stg_etef_cat_codigo_scian (
    id          SERIAL      PRIMARY KEY,
    codigo      VARCHAR(10) NOT NULL UNIQUE,
    descripcion VARCHAR(255)
);

CREATE INDEX IF NOT EXISTS ix_etef_cat_codigo_scian_codigo
    ON stg_etef_cat_codigo_scian (codigo);
