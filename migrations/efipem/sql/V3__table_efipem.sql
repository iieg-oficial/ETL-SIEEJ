CREATE TABLE IF NOT EXISTS stg_efipem_finanzas_trimestral (
    id              SERIAL      PRIMARY KEY,
    anio            INTEGER     NOT NULL,
    trimestre_id    INTEGER     NOT NULL REFERENCES stg_efipem_cat_trimestre (id),
    cve_ent         INTEGER     NOT NULL,
    tema_id         INTEGER     NOT NULL REFERENCES stg_efipem_cat_tema (id),
    clasificador_id INTEGER     NOT NULL REFERENCES stg_efipem_cat_clasificador (id),
    concepto_id     INTEGER     NOT NULL REFERENCES stg_efipem_cat_concepto (id),
    valor           BIGINT      NOT NULL,
    estatus_id      INTEGER     NOT NULL REFERENCES stg_efipem_cat_estatus (id),
    -- SCD2
    row_hash        VARCHAR(64) NOT NULL DEFAULT '',
    valid_from      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    valid_to        TIMESTAMPTZ,
    is_current      BOOLEAN     NOT NULL DEFAULT TRUE,
    -- Auditoría
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Unicidad solo sobre la versión activa por llave natural (permite historial SCD2)
CREATE UNIQUE INDEX IF NOT EXISTS uq_efipem_finanzas_trimestral_llave_activa
    ON stg_efipem_finanzas_trimestral (anio, trimestre_id, cve_ent, tema_id, clasificador_id, concepto_id)
    WHERE is_current = TRUE;

CREATE INDEX IF NOT EXISTS ix_efipem_finanzas_trimestral_anio_trim
    ON stg_efipem_finanzas_trimestral (anio, trimestre_id);

CREATE INDEX IF NOT EXISTS ix_efipem_finanzas_trimestral_cve_ent
    ON stg_efipem_finanzas_trimestral (cve_ent);

CREATE INDEX IF NOT EXISTS ix_efipem_finanzas_trimestral_tema
    ON stg_efipem_finanzas_trimestral (tema_id);

CREATE INDEX IF NOT EXISTS ix_efipem_finanzas_trimestral_clasificador
    ON stg_efipem_finanzas_trimestral (clasificador_id);

CREATE INDEX IF NOT EXISTS ix_efipem_finanzas_trimestral_concepto
    ON stg_efipem_finanzas_trimestral (concepto_id);

CREATE INDEX IF NOT EXISTS ix_efipem_finanzas_trimestral_row_hash
    ON stg_efipem_finanzas_trimestral (row_hash);

CREATE INDEX IF NOT EXISTS ix_efipem_finanzas_trimestral_is_current
    ON stg_efipem_finanzas_trimestral (is_current)
    WHERE is_current = TRUE;
