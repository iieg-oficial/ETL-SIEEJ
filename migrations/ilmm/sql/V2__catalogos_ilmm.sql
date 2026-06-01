-- ---------------------------------------------------------------------------
-- Catálogo de estimadores
-- Estructura creada aquí; la semilla se carga desde catalogos/est.csv vía ETL.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cat_ilmm_estimador (
    id          SMALLINT    PRIMARY KEY,
    descripcion VARCHAR(60) NOT NULL
);
