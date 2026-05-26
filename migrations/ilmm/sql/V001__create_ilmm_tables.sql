-- =============================================================================
-- V001__create_ilmm_tables.sql
-- Pipeline: ilmm — Indicadores del Mercado de Trabajo Municipal (INEGI)
-- Tablas: ilmm_estimador (catálogo), ilmm_indicador (catálogo), ilmm (hechos).
-- Estrategia de actualización: solo-inserciones (append-only).
-- Nivel geográfico: municipal — clave_municipio VARCHAR(5) ref. cvegeo_municipalities.
-- =============================================================================

-- ---------------------------------------------------------------------------
-- Catálogo de estimadores (semilla desde est.csv)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ilmm_estimador (
    id          SMALLINT    PRIMARY KEY,
    descripcion VARCHAR(60) NOT NULL
);

INSERT INTO ilmm_estimador (id, descripcion) VALUES
    (1, 'Valor'),
    (2, 'Error estándar'),
    (3, 'Límite inferior de confianza'),
    (4, 'Límite superior de confianza'),
    (5, 'Coeficiente de variación (%)')
ON CONFLICT (id) DO NOTHING;

-- ---------------------------------------------------------------------------
-- Catálogo de indicadores (semilla manual)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ilmm_indicador (
    id        SMALLINT    PRIMARY KEY,
    indicador VARCHAR(40) NOT NULL,
    CONSTRAINT uq_ilmm_indicador UNIQUE (indicador)
);

INSERT INTO ilmm_indicador (id, indicador) VALUES
    (1, 'tasa_desocupacion'),
    (2, 'porcentaje_ocupacion_informal')
ON CONFLICT (id) DO NOTHING;

-- ---------------------------------------------------------------------------
-- Tabla principal de hechos (pivotada por indicador)
-- clave_municipio: clave INEGI 5 dígitos (ej. '01001')
--   → referencia lógica a cvegeo_municipalities (cve_ent||cve_mun);
--     no se declara FK formal porque las foreign tables no admiten referencias.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ilmm (
    id               BIGSERIAL    PRIMARY KEY,
    clave_municipio  VARCHAR(5)   NOT NULL,
    fecha            DATE         NOT NULL,
    indicador_id     SMALLINT     NOT NULL REFERENCES ilmm_indicador(id),
    valor            NUMERIC(12,4),
    error_estandar   NUMERIC(12,4),
    CONSTRAINT uq_ilmm UNIQUE (clave_municipio, fecha, indicador_id)
);

CREATE INDEX IF NOT EXISTS idx_ilmm_municipio ON ilmm (clave_municipio);
CREATE INDEX IF NOT EXISTS idx_ilmm_fecha     ON ilmm (fecha);
CREATE INDEX IF NOT EXISTS idx_ilmm_indicador ON ilmm (indicador_id);
