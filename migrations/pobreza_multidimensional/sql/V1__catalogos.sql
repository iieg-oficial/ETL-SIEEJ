-- =======================================================================
-- V1__catalogos.sql  |  Pipeline: pobreza_multidimensional
-- Tablas catálogo alimentadas desde los CSV de ENIGH.
-- =======================================================================

CREATE TABLE IF NOT EXISTS public.stg_pobreza_multidimensional_cat_entidad (
    id      SERIAL PRIMARY KEY,
    codigo  INTEGER NOT NULL,
    nombre  TEXT    NOT NULL,
    CONSTRAINT uq_pm_cat_entidad_codigo UNIQUE (codigo)
);

CREATE TABLE IF NOT EXISTS public.stg_pobreza_multidimensional_cat_parentesco (
    id      SERIAL PRIMARY KEY,
    codigo  INTEGER NOT NULL,
    nombre  TEXT    NOT NULL,
    CONSTRAINT uq_pm_cat_parentesco_codigo UNIQUE (codigo)
);
