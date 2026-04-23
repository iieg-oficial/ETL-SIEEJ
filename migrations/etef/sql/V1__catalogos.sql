-- =======================================================================
-- V1__catalogos.sql  |  Pipeline: etef
-- Tablas catálogo para códigos SCIAN
-- =======================================================================

CREATE TABLE IF NOT EXISTS public.stg_etef_cat_codigo_scian (
    id          SERIAL PRIMARY KEY,
    codigo      VARCHAR(3) NOT NULL,
    descripcion VARCHAR(255),
    version     VARCHAR(10),
    CONSTRAINT uq_etef_cat_codigo_scian_codigo UNIQUE (codigo)
);

-- Índice para búsquedas rápidas
CREATE INDEX IF NOT EXISTS ix_etef_cat_codigo_scian_codigo
    ON public.stg_etef_cat_codigo_scian (codigo);
