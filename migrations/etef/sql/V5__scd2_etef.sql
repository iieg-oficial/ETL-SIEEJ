-- =======================================================================
-- V5__scd2_etef.sql  |  Pipeline: etef
-- Agrega soporte SCD2 con row_hash a stg_etef_datos
-- Decisiones aprobadas por DEA:
--   - Llave natural: (anio, trimestre, cve_ent, codigo_scian_id)
--   - Unicidad parcial: solo la versión activa (is_current = TRUE)
--   - Columnas mutables hasheadas: val_usd, estatus_cifra, estatus
-- =======================================================================

-- 1. Eliminar restricción de unicidad plana (reemplazada por índice parcial)
ALTER TABLE public.stg_etef_datos
    DROP CONSTRAINT IF EXISTS uq_etef_datos_llave;

-- 2. Agregar columnas faltantes del CSV
ALTER TABLE public.stg_etef_datos
    ADD COLUMN IF NOT EXISTS prod_est  VARCHAR(150),
    ADD COLUMN IF NOT EXISTS cobertura VARCHAR(50);

-- 3. Agregar columnas SCD2
ALTER TABLE public.stg_etef_datos
    ADD COLUMN IF NOT EXISTS row_hash   VARCHAR(64)  NOT NULL DEFAULT '',
    ADD COLUMN IF NOT EXISTS valid_from TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    ADD COLUMN IF NOT EXISTS valid_to   TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS is_current BOOLEAN      NOT NULL DEFAULT TRUE;

-- 4. Índice parcial de unicidad: garantiza una sola versión activa por llave natural
CREATE UNIQUE INDEX IF NOT EXISTS uq_etef_datos_llave_activa
    ON public.stg_etef_datos (anio, trimestre, cve_ent, codigo_scian_id)
    WHERE is_current = TRUE;

-- 5. Índices auxiliares para consultas SCD2
CREATE INDEX IF NOT EXISTS ix_etef_datos_is_current
    ON public.stg_etef_datos (is_current);

CREATE INDEX IF NOT EXISTS ix_etef_datos_row_hash
    ON public.stg_etef_datos (row_hash);
