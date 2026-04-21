-- ============================================================
-- V1__tablas_iniciales.sql
-- Pipeline: asg_imss
-- Descripción: Tablas catálogo y tabla principal de datos ASG-IMSS Jalisco
-- ============================================================

-- ---------------------------------------------------------------------------
-- Catálogos
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.stg_asg_imss_cat_delegacion (
    id              SERIAL PRIMARY KEY,
    cve_delegacion  INTEGER       NOT NULL,
    descripcion     VARCHAR(100)  NOT NULL,
    CONSTRAINT uq_asg_imss_cat_delegacion_cve UNIQUE (cve_delegacion)
);

CREATE TABLE IF NOT EXISTS public.stg_asg_imss_cat_subdelegacion (
    id                 SERIAL PRIMARY KEY,
    cve_delegacion     INTEGER       NOT NULL,
    cve_subdelegacion  INTEGER       NOT NULL,
    descripcion        VARCHAR(100)  NOT NULL,
    CONSTRAINT uq_asg_imss_cat_subdelegacion_cve UNIQUE (cve_delegacion, cve_subdelegacion)
);

CREATE TABLE IF NOT EXISTS public.stg_asg_imss_cat_entidad_municipio (
    id              SERIAL PRIMARY KEY,
    cve_municipio   VARCHAR(10)   NOT NULL,
    cve_delegacion  INTEGER       NOT NULL,
    cve_entidad     INTEGER       NOT NULL,
    desc_entidad    VARCHAR(100)  NOT NULL,
    desc_municipio  VARCHAR(200)  NOT NULL,
    CONSTRAINT uq_asg_imss_cat_entidad_municipio_cve UNIQUE (cve_municipio)
);

CREATE TABLE IF NOT EXISTS public.stg_asg_imss_cat_sector_1 (
    id           SERIAL PRIMARY KEY,
    cve_sector_1 INTEGER       NOT NULL,
    descripcion  VARCHAR(300)  NOT NULL,
    CONSTRAINT uq_asg_imss_cat_sector_1_cve UNIQUE (cve_sector_1)
);

CREATE TABLE IF NOT EXISTS public.stg_asg_imss_cat_sector_2 (
    id                 SERIAL PRIMARY KEY,
    cve_sector_1       INTEGER       NOT NULL,
    cve_sector_2       INTEGER       NOT NULL,
    cve_sector_2_2pos  INTEGER       NOT NULL,
    descripcion        VARCHAR(500)  NOT NULL,
    CONSTRAINT uq_asg_imss_cat_sector_2_cve UNIQUE (cve_sector_1, cve_sector_2)
);

CREATE TABLE IF NOT EXISTS public.stg_asg_imss_cat_sector_4 (
    id                  SERIAL PRIMARY KEY,
    cve_sector_2        INTEGER       NOT NULL,
    cve_sector_4        INTEGER       NOT NULL,
    cve_sector_4_4pos   VARCHAR(10)   NOT NULL,
    descripcion         VARCHAR(500)  NOT NULL,
    CONSTRAINT uq_asg_imss_cat_sector_4_cve UNIQUE (cve_sector_2, cve_sector_4)
);

CREATE TABLE IF NOT EXISTS public.stg_asg_imss_cat_tamanio_patron (
    id           SERIAL PRIMARY KEY,
    cve          VARCHAR(5)    NOT NULL,
    descripcion  VARCHAR(100)  NOT NULL,
    CONSTRAINT uq_asg_imss_cat_tamanio_patron_cve UNIQUE (cve)
);

CREATE TABLE IF NOT EXISTS public.stg_asg_imss_cat_sexo (
    id           SERIAL PRIMARY KEY,
    cve          INTEGER      NOT NULL,
    descripcion  VARCHAR(50)  NOT NULL,
    CONSTRAINT uq_asg_imss_cat_sexo_cve UNIQUE (cve)
);

CREATE TABLE IF NOT EXISTS public.stg_asg_imss_cat_rango_edad (
    id           SERIAL PRIMARY KEY,
    cve          VARCHAR(5)    NOT NULL,
    descripcion  VARCHAR(200)  NOT NULL,
    CONSTRAINT uq_asg_imss_cat_rango_edad_cve UNIQUE (cve)
);

CREATE TABLE IF NOT EXISTS public.stg_asg_imss_cat_rango_salarial (
    id           SERIAL PRIMARY KEY,
    cve          VARCHAR(5)    NOT NULL,
    descripcion  VARCHAR(200)  NOT NULL,
    CONSTRAINT uq_asg_imss_cat_rango_salarial_cve UNIQUE (cve)
);

CREATE TABLE IF NOT EXISTS public.stg_asg_imss_cat_rango_uma (
    id           SERIAL PRIMARY KEY,
    cve          VARCHAR(5)    NOT NULL,
    descripcion  VARCHAR(200)  NOT NULL,
    CONSTRAINT uq_asg_imss_cat_rango_uma_cve UNIQUE (cve)
);

-- ---------------------------------------------------------------------------
-- Tabla principal de datos
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.stg_asg_imss_datos (
    id                  SERIAL PRIMARY KEY,

    -- Dimensiones
    cve_delegacion      INTEGER       NOT NULL,
    cve_subdelegacion   INTEGER       NOT NULL,
    cve_entidad         INTEGER       NOT NULL,
    cve_municipio       VARCHAR(10)   NOT NULL,
    sector_economico_1  INTEGER,
    sector_economico_2  INTEGER,
    sector_economico_4  INTEGER,
    tamanio_patron      VARCHAR(5),
    sexo                INTEGER       NOT NULL,
    rango_edad          VARCHAR(5)    NOT NULL,
    rango_salarial      VARCHAR(5),
    rango_uma           VARCHAR(5),
    fecha_corte         DATE          NOT NULL,

    -- Métricas — conteos
    asegurados          INTEGER       NOT NULL DEFAULT 0,
    no_trabajadores     INTEGER       NOT NULL DEFAULT 0,
    ta                  INTEGER       NOT NULL DEFAULT 0,
    teu                 INTEGER       NOT NULL DEFAULT 0,
    tec                 INTEGER       NOT NULL DEFAULT 0,
    tpu                 INTEGER       NOT NULL DEFAULT 0,
    tpc                 INTEGER       NOT NULL DEFAULT 0,
    ta_sal              INTEGER       NOT NULL DEFAULT 0,
    teu_sal             INTEGER       NOT NULL DEFAULT 0,
    tec_sal             INTEGER       NOT NULL DEFAULT 0,
    tpu_sal             INTEGER       NOT NULL DEFAULT 0,
    tpc_sal             INTEGER       NOT NULL DEFAULT 0,

    -- Métricas — masa salarial
    masa_sal_ta         NUMERIC(16,2) NOT NULL DEFAULT 0,
    masa_sal_teu        NUMERIC(16,2) NOT NULL DEFAULT 0,
    masa_sal_tec        NUMERIC(16,2) NOT NULL DEFAULT 0,
    masa_sal_tpu        NUMERIC(16,2) NOT NULL DEFAULT 0,
    masa_sal_tpc        NUMERIC(16,2) NOT NULL DEFAULT 0,

    -- Auditoría
    record_hash         VARCHAR(64)   NOT NULL,
    created_at          TIMESTAMP     DEFAULT NOW(),

    CONSTRAINT uq_asg_imss_datos_record_hash UNIQUE (record_hash)
);

CREATE UNIQUE INDEX IF NOT EXISTS ix_asg_imss_datos_record_hash
    ON public.stg_asg_imss_datos (record_hash);

CREATE INDEX IF NOT EXISTS ix_asg_imss_datos_fecha_corte
    ON public.stg_asg_imss_datos (fecha_corte);
