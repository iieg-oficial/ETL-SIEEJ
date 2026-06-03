-- ---------------------------------------------------------------------------
-- Tabla principal de hechos (una fila por municipio × fecha × estimador)
-- clave_municipio: clave INEGI 5 dígitos (ej. '01001')
--   → referencia lógica a cvegeo_municipalities (cve_ent||cve_mun);
--     no se declara FK formal porque las foreign tables no admiten referencias.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS stg_ilmm (
    id               BIGSERIAL    PRIMARY KEY,
    clave_municipio  VARCHAR(5)   NOT NULL,
    fecha            DATE         NOT NULL,
    estimador_id     SMALLINT     NOT NULL REFERENCES cat_ilmm_estimador(id),
    pob_econo_activa NUMERIC(12,4),
    ocupados         NUMERIC(12,4),
    informales       NUMERIC(12,4),
    CONSTRAINT uq_stg_ilmm UNIQUE (clave_municipio, fecha, estimador_id)
);

CREATE INDEX IF NOT EXISTS idx_stg_ilmm_municipio  ON stg_ilmm (clave_municipio);
CREATE INDEX IF NOT EXISTS idx_stg_ilmm_fecha      ON stg_ilmm (fecha);
CREATE INDEX IF NOT EXISTS idx_stg_ilmm_estimador  ON stg_ilmm (estimador_id);
