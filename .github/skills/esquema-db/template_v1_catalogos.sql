-- =============================================================================
-- V1__{flujo}__catalogos.sql
-- Tablas catálogo del pipeline {flujo}.
-- Una tabla por cada columna identificada con es_catalogo: true en reporte_eda.json.
-- Convención: prefijo cat_, nombre en snake_case, en español, sin tildes.
-- =============================================================================

-- Ejemplo: catálogo de estado del trámite
CREATE TABLE IF NOT EXISTS cat_estado_tramite (
    id   SMALLINT     PRIMARY KEY,
    -- Columna descriptiva con el valor legible del catálogo
    estado_tramite VARCHAR(100) NOT NULL UNIQUE
);

-- Ejemplo: catálogo de tipo de solicitante
CREATE TABLE IF NOT EXISTS cat_tipo_solicitante (
    id              SMALLINT     PRIMARY KEY,
    tipo_solicitante VARCHAR(150) NOT NULL UNIQUE
);

-- Repetir un bloque CREATE TABLE por cada catálogo identificado en el reporte EDA.
-- Usar SMALLINT para ids de catálogos con < 32,767 valores.
-- Usar INTEGER para catálogos con cardinalidad mayor.
