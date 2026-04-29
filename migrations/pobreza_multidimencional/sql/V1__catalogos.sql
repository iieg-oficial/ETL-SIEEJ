-- =======================================================================
-- V1__catalogos.sql  |  Pipeline: pobreza_multidimencional
-- Catálogo de entidades federativas CONEVAL.
-- =======================================================================

CREATE TABLE IF NOT EXISTS public.stg_pobreza_multidimencional_cat_entidad (
    id      SERIAL PRIMARY KEY,
    cve_ent VARCHAR(2)  NOT NULL,
    nombre_entidad  VARCHAR(100) NOT NULL,
    CONSTRAINT uq_pobreza_multidimencional_cat_entidad_cve UNIQUE (cve_ent)
);
