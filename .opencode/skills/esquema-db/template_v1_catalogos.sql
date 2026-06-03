-- V1__{flujo}__catalogos.sql
-- Tablas catálogo del pipeline {flujo}.
-- Una tabla por cada columna identificada con es_catalogo: true en reporte_eda.json.

CREATE TABLE IF NOT EXISTS cat_estado_tramite (
    id   SMALLINT     PRIMARY KEY,
    estado_tramite VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS cat_tipo_solicitante (
    id              SMALLINT     PRIMARY KEY,
    tipo_solicitante VARCHAR(150) NOT NULL UNIQUE
);
