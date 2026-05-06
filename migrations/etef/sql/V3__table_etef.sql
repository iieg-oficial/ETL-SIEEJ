CREATE TABLE IF NOT EXISTS stg_etef_datos (
    id              SERIAL          PRIMARY KEY,
    anio            INTEGER         NOT NULL,
    trimestre       VARCHAR(3)      NOT NULL,
    mes             VARCHAR(5)      NOT NULL,
    prod_est        VARCHAR(150),
    cobertura       VARCHAR(50),
    cve_ent         INTEGER         NOT NULL,
    codigo_scian_id INTEGER         NOT NULL REFERENCES stg_etef_cat_codigo_scian(id),
    val_usd         NUMERIC(15, 2),
    estatus_cifra   VARCHAR(20),
    estatus         VARCHAR(30),
    -- SCD2
    row_hash        VARCHAR(64)     NOT NULL DEFAULT '',
    valid_from      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    valid_to        TIMESTAMPTZ,
    is_current      BOOLEAN         NOT NULL DEFAULT TRUE,
    -- Auditoría
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

-- Unicidad solo sobre la versión activa por llave natural (permite historial SCD2)
CREATE UNIQUE INDEX IF NOT EXISTS uq_etef_datos_llave_activa
    ON stg_etef_datos (anio, trimestre, cve_ent, codigo_scian_id)
    WHERE is_current = TRUE;

CREATE INDEX IF NOT EXISTS ix_etef_datos_anio_trimestre
    ON stg_etef_datos (anio, trimestre);

CREATE INDEX IF NOT EXISTS ix_etef_datos_cve_ent
    ON stg_etef_datos (cve_ent);

CREATE INDEX IF NOT EXISTS ix_etef_datos_codigo_scian_id
    ON stg_etef_datos (codigo_scian_id);

CREATE INDEX IF NOT EXISTS ix_etef_datos_row_hash
    ON stg_etef_datos (row_hash);

CREATE INDEX IF NOT EXISTS ix_etef_datos_is_current
    ON stg_etef_datos (is_current)
    WHERE is_current = TRUE;
