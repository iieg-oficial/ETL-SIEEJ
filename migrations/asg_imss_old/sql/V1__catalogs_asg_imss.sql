-- ============================================================
-- V1__catalogs_asg_imss.sql
-- Pipeline: asg_imss
-- Description: Catalog tables for ASG-IMSS Jalisco pipeline
-- ============================================================

CREATE TABLE IF NOT EXISTS public.stg_asg_imss_cat_delegacion (
    id              SERIAL        PRIMARY KEY,
    cve_delegacion  INTEGER       NOT NULL,
    descripcion     VARCHAR(100)  NOT NULL,
    CONSTRAINT uq_asg_imss_cat_delegacion_cve UNIQUE (cve_delegacion)
);

CREATE TABLE IF NOT EXISTS public.stg_asg_imss_cat_subdelegacion (
    id                 SERIAL        PRIMARY KEY,
    cve_delegacion     INTEGER       NOT NULL,
    cve_subdelegacion  INTEGER       NOT NULL,
    descripcion        VARCHAR(100)  NOT NULL,
    CONSTRAINT uq_asg_imss_cat_subdelegacion_cve UNIQUE (cve_delegacion, cve_subdelegacion)
);

-- NOTE: cve_municipio uses IMSS-proprietary codes, not INEGI clave geoestadistica.
-- A mapping to cvegeo is pending.
CREATE TABLE IF NOT EXISTS public.stg_asg_imss_cat_entidad_municipio (
    id              SERIAL        PRIMARY KEY,
    cve_municipio   VARCHAR(10)   NOT NULL,
    cve_delegacion  INTEGER       NOT NULL,
    cve_entidad     INTEGER       NOT NULL,
    desc_entidad    VARCHAR(100)  NOT NULL,
    desc_municipio  VARCHAR(200)  NOT NULL,
    CONSTRAINT uq_asg_imss_cat_entidad_municipio_cve UNIQUE (cve_municipio)
);

CREATE TABLE IF NOT EXISTS public.stg_asg_imss_cat_sector_1 (
    id           SERIAL        PRIMARY KEY,
    cve_sector_1 INTEGER       NOT NULL,
    descripcion  VARCHAR(300)  NOT NULL,
    CONSTRAINT uq_asg_imss_cat_sector_1_cve UNIQUE (cve_sector_1)
);

CREATE TABLE IF NOT EXISTS public.stg_asg_imss_cat_sector_2 (
    id                 SERIAL        PRIMARY KEY,
    cve_sector_1       INTEGER       NOT NULL,
    cve_sector_2       INTEGER       NOT NULL,
    cve_sector_2_2pos  INTEGER       NOT NULL,
    descripcion        VARCHAR(500)  NOT NULL,
    CONSTRAINT uq_asg_imss_cat_sector_2_cve UNIQUE (cve_sector_1, cve_sector_2)
);

CREATE TABLE IF NOT EXISTS public.stg_asg_imss_cat_sector_4 (
    id                 SERIAL        PRIMARY KEY,
    cve_sector_2       INTEGER       NOT NULL,
    cve_sector_4       INTEGER       NOT NULL,
    cve_sector_4_4pos  VARCHAR(10)   NOT NULL,
    descripcion        VARCHAR(500)  NOT NULL,
    CONSTRAINT uq_asg_imss_cat_sector_4_cve UNIQUE (cve_sector_2, cve_sector_4)
);

CREATE TABLE IF NOT EXISTS public.stg_asg_imss_cat_tamanio_patron (
    id           SERIAL       PRIMARY KEY,
    cve          VARCHAR(5)   NOT NULL,
    descripcion  VARCHAR(100) NOT NULL,
    CONSTRAINT uq_asg_imss_cat_tamanio_patron_cve UNIQUE (cve)
);

CREATE TABLE IF NOT EXISTS public.stg_asg_imss_cat_sexo (
    id           SERIAL       PRIMARY KEY,
    cve          INTEGER      NOT NULL,
    descripcion  VARCHAR(50)  NOT NULL,
    CONSTRAINT uq_asg_imss_cat_sexo_cve UNIQUE (cve)
);

CREATE TABLE IF NOT EXISTS public.stg_asg_imss_cat_rango_edad (
    id           SERIAL        PRIMARY KEY,
    cve          VARCHAR(5)    NOT NULL,
    descripcion  VARCHAR(200)  NOT NULL,
    CONSTRAINT uq_asg_imss_cat_rango_edad_cve UNIQUE (cve)
);

CREATE TABLE IF NOT EXISTS public.stg_asg_imss_cat_rango_salarial (
    id           SERIAL        PRIMARY KEY,
    cve          VARCHAR(5)    NOT NULL,
    descripcion  VARCHAR(200)  NOT NULL,
    CONSTRAINT uq_asg_imss_cat_rango_salarial_cve UNIQUE (cve)
);

CREATE TABLE IF NOT EXISTS public.stg_asg_imss_cat_rango_uma (
    id           SERIAL        PRIMARY KEY,
    cve          VARCHAR(5)    NOT NULL,
    descripcion  VARCHAR(200)  NOT NULL,
    CONSTRAINT uq_asg_imss_cat_rango_uma_cve UNIQUE (cve)
);
