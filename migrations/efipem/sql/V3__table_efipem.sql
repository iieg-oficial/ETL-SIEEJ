CREATE TABLE IF NOT EXISTS stg_efipem (
    id              SERIAL      PRIMARY KEY,
    anio            INTEGER     NOT NULL,
    cvegeo          CHAR(5)     NOT NULL,
    cve_ent         SMALLINT    NOT NULL,
    cve_mun         SMALLINT    NOT NULL,
    tema_id         INTEGER     NOT NULL REFERENCES cat_tema (id),
    clasificador_id INTEGER     NOT NULL REFERENCES cat_clasificador (id),
    concepto_id     INTEGER     NOT NULL REFERENCES cat_concepto (id),
    valor           BIGINT      NOT NULL,
    estatus_id      INTEGER     NOT NULL REFERENCES cat_estatus (id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_stg_efipem_llave
        UNIQUE (anio, cvegeo, tema_id, clasificador_id, concepto_id)
);

CREATE INDEX IF NOT EXISTS ix_stg_efipem_anio
    ON stg_efipem (anio);

CREATE INDEX IF NOT EXISTS ix_stg_efipem_cvegeo
    ON stg_efipem (cvegeo);

CREATE INDEX IF NOT EXISTS ix_stg_efipem_cve_ent
    ON stg_efipem (cve_ent);

CREATE INDEX IF NOT EXISTS ix_stg_efipem_tema
    ON stg_efipem (tema_id);

CREATE INDEX IF NOT EXISTS ix_stg_efipem_clasificador
    ON stg_efipem (clasificador_id);

CREATE INDEX IF NOT EXISTS ix_stg_efipem_concepto
    ON stg_efipem (concepto_id);
