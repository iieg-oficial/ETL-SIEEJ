-- =============================================================================
-- V2__create_stg_2015_2025.sql  |  Pipeline: delitos_fuero_comun
-- Historical staging table 2015-2025 (bootstrap only).
-- Expected rows: ~2,562,994  |  Years: 2015-2025  |  Level: municipal
-- NK: (anio, cvegeo, bien_juridico_afectado_id, tipo_delito_id,
--      subtipo_delito_id, modalidad_id)
-- =============================================================================

CREATE TABLE IF NOT EXISTS stg_delitos_fuero_comun_2015_2025 (
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

    CONSTRAINT uq_stg_delitos_2015_2025_nk UNIQUE (
        anio,
        cvegeo,
        bien_juridico_afectado_id,
        tipo_delito_id,
        subtipo_delito_id,
        modalidad_id
    )
);

CREATE INDEX IF NOT EXISTS ix_stg_delitos_2015_2025_anio
    ON stg_delitos_fuero_comun_2015_2025 (anio);

CREATE INDEX IF NOT EXISTS ix_stg_delitos_2015_2025_cvegeo
    ON stg_delitos_fuero_comun_2015_2025 (cvegeo);

CREATE INDEX IF NOT EXISTS ix_stg_delitos_2015_2025_tipo
    ON stg_delitos_fuero_comun_2015_2025 (tipo_delito_id, subtipo_delito_id);
