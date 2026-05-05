-- =============================================================================
-- V3__{flujo}__tabla_principal.sql
-- Tabla principal de staging del pipeline {flujo}.
-- Convención: prefijo stg_, nombre en snake_case, en español, sin tildes.
-- =============================================================================

CREATE TABLE IF NOT EXISTS stg_{flujo} (
    id              SERIAL          PRIMARY KEY,

    -- Claves foráneas a tablas catálogo (una por catálogo generado en V1)
    id_estado_tramite   SMALLINT    NOT NULL REFERENCES cat_estado_tramite(id),
    id_tipo_solicitante SMALLINT    NOT NULL REFERENCES cat_tipo_solicitante(id),

    -- Columnas geográficas (si aplica)
    -- cve_ent  VARCHAR(2),   -- referencia a cve_geo
    -- cve_mun  VARCHAR(5),   -- referencia a cve_geo

    -- Columnas de datos principales (un ejemplo por tipo)
    descripcion     VARCHAR(500),
    valor_numerico  NUMERIC(12, 2),
    fecha_registro  DATE            NOT NULL,

    -- -------------------------------------------------------------------------
    -- Campos SCD — incluir SOLO si tipo_update es "scd"
    -- -------------------------------------------------------------------------
    -- hash_registro   VARCHAR(64),          -- SHA-256 de columnas monitoreadas
    -- valid_from      TIMESTAMP   NOT NULL DEFAULT NOW(),
    -- valid_to        TIMESTAMP,            -- NULL = registro vigente
    -- is_current      BOOLEAN     NOT NULL DEFAULT TRUE,
    -- -------------------------------------------------------------------------

    -- Timestamps de auditoría
    created_at      TIMESTAMP       NOT NULL DEFAULT NOW()
);

-- Índices recomendados (ajustar según las consultas más frecuentes)
CREATE INDEX IF NOT EXISTS idx_stg_{flujo}_fecha ON stg_{flujo}(fecha_registro);
-- CREATE INDEX IF NOT EXISTS idx_stg_{flujo}_geo ON stg_{flujo}(cve_ent, cve_mun);
-- CREATE INDEX IF NOT EXISTS idx_stg_{flujo}_current ON stg_{flujo}(is_current) WHERE is_current = TRUE;
