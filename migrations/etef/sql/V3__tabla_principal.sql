-- =======================================================================
-- V3__tabla_principal.sql  |  Pipeline: etef
-- Tabla principal de exportaciones trimestrales (Jalisco, CVE_ENT=14)
-- =======================================================================

CREATE TABLE IF NOT EXISTS public.stg_etef_datos (
    id              SERIAL PRIMARY KEY,
    anio            INTEGER NOT NULL,
    trimestre       VARCHAR(2) NOT NULL,
    mes             VARCHAR(5) NOT NULL,
    cve_ent         INTEGER NOT NULL,
    codigo_scian_id INTEGER NOT NULL REFERENCES public.stg_etef_cat_codigo_scian(id),
    val_usd         NUMERIC(15, 2),
    estatus_cifra   VARCHAR(20),
    estatus         VARCHAR(30),
    created_at      TIMESTAMP DEFAULT now(),
    updated_at      TIMESTAMP DEFAULT now(),
    CONSTRAINT uq_etef_datos_llave UNIQUE (anio, trimestre, cve_ent, codigo_scian_id)
);

-- Índices para consultas analíticas
CREATE INDEX IF NOT EXISTS ix_etef_datos_anio_trimestre
    ON public.stg_etef_datos (anio, trimestre);

CREATE INDEX IF NOT EXISTS ix_etef_datos_cve_ent
    ON public.stg_etef_datos (cve_ent);

CREATE INDEX IF NOT EXISTS ix_etef_datos_codigo_scian_id
    ON public.stg_etef_datos (codigo_scian_id);

CREATE INDEX IF NOT EXISTS ix_etef_datos_llave
    ON public.stg_etef_datos (anio, trimestre, cve_ent, codigo_scian_id);
