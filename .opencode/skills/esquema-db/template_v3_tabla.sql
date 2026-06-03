-- V3__{flujo}__tabla_principal.sql
-- Tabla principal de staging del pipeline {flujo}.

CREATE TABLE IF NOT EXISTS stg_{flujo} (
    id              SERIAL          PRIMARY KEY,

    -- Claves foráneas a tablas catálogo
    id_estado_tramite   SMALLINT    NOT NULL REFERENCES cat_estado_tramite(id),
    id_tipo_solicitante SMALLINT    NOT NULL REFERENCES cat_tipo_solicitante(id),

    -- Columnas de datos principales
    descripcion     VARCHAR(500),
    valor_numerico  NUMERIC(12, 2),
    fecha_registro  DATE            NOT NULL,

    -- Campos SCD — incluir SOLO si tipo_update es "scd"
    -- hash_registro   VARCHAR(64),
    -- valid_from      TIMESTAMP   NOT NULL DEFAULT NOW(),
    -- valid_to        TIMESTAMP,
    -- is_current      BOOLEAN     NOT NULL DEFAULT TRUE,

    -- Timestamps de auditoría
    created_at      TIMESTAMP       NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_stg_{flujo}_fecha ON stg_{flujo}(fecha_registro);
