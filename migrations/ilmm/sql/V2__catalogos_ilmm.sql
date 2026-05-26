-- ---------------------------------------------------------------------------
-- Catálogo de estimadores (semilla desde est.csv)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cat_ilmm_estimador (
    id          SMALLINT    PRIMARY KEY,
    descripcion VARCHAR(60) NOT NULL
);

INSERT INTO cat_ilmm_estimador (id, descripcion) VALUES
    (1, 'Valor'),
    (2, 'Error estándar'),
    (3, 'Límite inferior de confianza'),
    (4, 'Límite superior de confianza'),
    (5, 'Coeficiente de variación (%)')
ON CONFLICT (id) DO NOTHING;

-- ---------------------------------------------------------------------------
-- Catálogo de indicadores (semilla manual)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cat_ilmm_indicador (
    id        SMALLINT    PRIMARY KEY,
    indicador VARCHAR(40) NOT NULL,
    CONSTRAINT uq_cat_ilmm_indicador UNIQUE (indicador)
);

INSERT INTO cat_ilmm_indicador (id, indicador) VALUES
    (1, 'tasa_desocupacion'),
    (2, 'porcentaje_ocupacion_informal')
ON CONFLICT (id) DO NOTHING;
