-- ============================================================
-- V2__table_asg_imss.sql
-- Pipeline: asg_imss
-- Description: Main data table for ASG-IMSS Jalisco pipeline
-- Coverage: Jalisco only (cve_entidad = 14)
-- Update strategy: append-only; record_hash ensures idempotency
-- ============================================================

CREATE TABLE IF NOT EXISTS public.stg_asg_imss_datos (
    id                  SERIAL          PRIMARY KEY,

    -- Dimensions
    cve_delegacion      INTEGER         NOT NULL,
    cve_subdelegacion   INTEGER         NOT NULL,
    cve_entidad         INTEGER         NOT NULL,
    -- IMSS-proprietary municipality code (not INEGI clave geoestadistica)
    cve_municipio       VARCHAR(10)     NOT NULL,
    sector_economico_1  INTEGER,
    sector_economico_2  INTEGER,
    sector_economico_4  INTEGER,
    tamanio_patron      VARCHAR(5),
    sexo                INTEGER         NOT NULL,
    rango_edad          VARCHAR(5)      NOT NULL,
    rango_salarial      VARCHAR(5),
    rango_uma           VARCHAR(5),
    fecha_corte         DATE            NOT NULL,

    -- Metrics — counts
    asegurados          INTEGER         NOT NULL DEFAULT 0,
    no_trabajadores     INTEGER         NOT NULL DEFAULT 0,
    ta                  INTEGER         NOT NULL DEFAULT 0,
    teu                 INTEGER         NOT NULL DEFAULT 0,
    tec                 INTEGER         NOT NULL DEFAULT 0,
    tpu                 INTEGER         NOT NULL DEFAULT 0,
    tpc                 INTEGER         NOT NULL DEFAULT 0,
    ta_sal              INTEGER         NOT NULL DEFAULT 0,
    teu_sal             INTEGER         NOT NULL DEFAULT 0,
    tec_sal             INTEGER         NOT NULL DEFAULT 0,
    tpu_sal             INTEGER         NOT NULL DEFAULT 0,
    tpc_sal             INTEGER         NOT NULL DEFAULT 0,

    -- Metrics — payroll mass
    masa_sal_ta         NUMERIC(16, 2)  NOT NULL DEFAULT 0,
    masa_sal_teu        NUMERIC(16, 2)  NOT NULL DEFAULT 0,
    masa_sal_tec        NUMERIC(16, 2)  NOT NULL DEFAULT 0,
    masa_sal_tpu        NUMERIC(16, 2)  NOT NULL DEFAULT 0,
    masa_sal_tpc        NUMERIC(16, 2)  NOT NULL DEFAULT 0,

    -- Audit
    record_hash         VARCHAR(64)     NOT NULL,
    created_at          TIMESTAMPTZ     DEFAULT NOW(),

    CONSTRAINT uq_asg_imss_datos_record_hash UNIQUE (record_hash)
);

CREATE UNIQUE INDEX IF NOT EXISTS ix_asg_imss_datos_record_hash
    ON public.stg_asg_imss_datos (record_hash);

CREATE INDEX IF NOT EXISTS ix_asg_imss_datos_fecha_corte
    ON public.stg_asg_imss_datos (fecha_corte);
