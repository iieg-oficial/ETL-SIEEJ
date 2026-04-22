-- =======================================================================
-- V3: Tabla principal EFIPEM -- finanzas publicas estatales trimestrales
--     Pipeline filtrado a Jalisco (cve_ent = 14).
-- =======================================================================

CREATE TABLE IF NOT EXISTS stg_efipem_finanzas_trimestral (
    id              SERIAL PRIMARY KEY,
    anio            INTEGER  NOT NULL,
    trimestre_id    INTEGER  NOT NULL REFERENCES stg_efipem_cat_trimestre (id),
    cve_ent         CHAR(2)  NOT NULL,
    entidad_id      INTEGER,   -- ID logico hacia cvegeo_states (FDW, sin FK formal)
    tema_id         INTEGER  NOT NULL REFERENCES stg_efipem_cat_tema (id),
    clasificador_id INTEGER  NOT NULL REFERENCES stg_efipem_cat_clasificador (id),
    concepto_id     INTEGER  NOT NULL REFERENCES stg_efipem_cat_concepto (id),
    valor           BIGINT   NOT NULL,
    estatus_id      INTEGER  NOT NULL REFERENCES stg_efipem_cat_estatus (id),
    created_at      TIMESTAMP DEFAULT now(),
    updated_at      TIMESTAMP DEFAULT now(),
    CONSTRAINT uq_efipem_finanzas_trimestral_key UNIQUE (
        anio, trimestre_id, cve_ent, tema_id, clasificador_id, concepto_id
    )
);

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
