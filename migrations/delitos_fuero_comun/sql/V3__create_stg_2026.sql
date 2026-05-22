-- =============================================================================
-- V3__create_stg_2026.sql  |  Pipeline: delitos_fuero_comun
-- Current-year staging table 2026 (bootstrap + monthly update).
-- Expected rows: ~286,140  |  Year: 2026  |  Level: municipal
-- NK: (anio, cvegeo, bien_juridico_afectado_id, tipo_delito_id,
--      subtipo_delito_id, modalidad_id)
-- =============================================================================

CREATE TABLE IF NOT EXISTS stg_delitos_fuero_comun_2026 (
    id                        SERIAL       PRIMARY KEY,

    -- Temporal key
    anio                      SMALLINT     NOT NULL,

    -- Geographic identifier — logical FK to cvegeo_municipalities.cvegeo
    cvegeo                    INTEGER      NOT NULL,

    -- Catalog FKs
    bien_juridico_afectado_id INTEGER      NOT NULL
        REFERENCES cat_bien_juridico_afectado(id),
    tipo_delito_id            INTEGER      NOT NULL
        REFERENCES cat_tipo_delito(id),
    subtipo_delito_id         INTEGER      NOT NULL
        REFERENCES cat_subtipo_delito(id),
    modalidad_id              INTEGER      NOT NULL
        REFERENCES cat_modalidad(id),

    -- Monthly counts (NULL = month not yet published)
    enero      INTEGER,
    febrero    INTEGER,
    marzo      INTEGER,
    abril      INTEGER,
    mayo       INTEGER,
    junio      INTEGER,
    julio      INTEGER,
    agosto     INTEGER,
    septiembre INTEGER,
    octubre    INTEGER,
    noviembre  INTEGER,
    diciembre  INTEGER,

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_stg_delitos_2026_nk UNIQUE (
        anio,
        cvegeo,
        bien_juridico_afectado_id,
        tipo_delito_id,
        subtipo_delito_id,
        modalidad_id
    )
);

CREATE INDEX IF NOT EXISTS ix_stg_delitos_2026_anio
    ON stg_delitos_fuero_comun_2026 (anio);

CREATE INDEX IF NOT EXISTS ix_stg_delitos_2026_cvegeo
    ON stg_delitos_fuero_comun_2026 (cvegeo);

CREATE INDEX IF NOT EXISTS ix_stg_delitos_2026_tipo
    ON stg_delitos_fuero_comun_2026 (tipo_delito_id, subtipo_delito_id);
