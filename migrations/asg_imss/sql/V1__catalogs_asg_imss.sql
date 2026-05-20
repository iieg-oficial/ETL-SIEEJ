-- =======================================================================
-- V1: Catálogos del pipeline asg_imss (IMSS — Asegurados, Salarios y
-- Trabajadores Eventuales).
--
-- Reglas de modelado:
--   * Todos los catálogos son: id SERIAL PK, clave (SK) con UNIQUE,
--     descripcion TEXT NOT NULL.
--   * El literal "NA" es un VALOR VÁLIDO de catálogo (no nulo) salvo en
--     los catálogos de sector (cat_sector_1/2/4) donde NO existe.
--   * Catálogos auto-poblables: el load puede insertar claves nuevas con
--     descripcion = 'SIN DESCRIPCION'.
--   * Catálogos de IMSS NO comparten formato con CVEGEO/INEGI, por lo que
--     no se referencian las tablas FDW de cve_geo aquí.
-- =======================================================================

-- -----------------------------------------------------------------------
-- Delegación y Subdelegación (jerarquía 1:N)
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cat_delegacion (
    id          SERIAL      PRIMARY KEY,
    clave       VARCHAR(3)  NOT NULL,
    descripcion TEXT        NOT NULL,
    CONSTRAINT uq_cat_delegacion_clave UNIQUE (clave)
);

CREATE TABLE IF NOT EXISTS cat_subdelegacion (
    id             SERIAL      PRIMARY KEY,
    clave          VARCHAR(3)  NOT NULL,
    descripcion    TEXT        NOT NULL,
    delegacion_id  INTEGER     NOT NULL REFERENCES cat_delegacion (id),
    CONSTRAINT uq_cat_subdelegacion_deleg_clave UNIQUE (delegacion_id, clave)
);

CREATE INDEX IF NOT EXISTS ix_cat_subdelegacion_delegacion
    ON cat_subdelegacion (delegacion_id);

-- -----------------------------------------------------------------------
-- Entidad y Municipio IMSS (jerarquía 1:N) — catálogo propio del IMSS,
-- NO compatible con INEGI / cvegeo.
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cat_entidad (
    id          SERIAL      PRIMARY KEY,
    clave       CHAR(2)     NOT NULL,
    descripcion TEXT        NOT NULL,
    CONSTRAINT uq_cat_entidad_clave UNIQUE (clave)
);

CREATE TABLE IF NOT EXISTS cat_municipio (
    id          SERIAL      PRIMARY KEY,
    clave       VARCHAR(4)  NOT NULL,
    descripcion TEXT        NOT NULL,
    entidad_id  INTEGER     NOT NULL REFERENCES cat_entidad (id),
    CONSTRAINT uq_cat_municipio_entidad_clave UNIQUE (entidad_id, clave)
);

CREATE INDEX IF NOT EXISTS ix_cat_municipio_entidad
    ON cat_municipio (entidad_id);

-- -----------------------------------------------------------------------
-- Sectores económicos (jerarquía 1:N → 1:N).
-- Longitudes fijas: sector_1=1, sector_2=2, sector_4=4.
-- El padding/normalización lo realiza la etapa de transform.
-- 'NA' NO es valor válido en sectores; los sectores SÍ admiten NULL en
-- la tabla de hechos (FK nullable en stg_asg_imss).
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cat_sector_1 (
    id          SERIAL      PRIMARY KEY,
    clave       CHAR(1)     NOT NULL,
    descripcion TEXT        NOT NULL,
    CONSTRAINT uq_cat_sector_1_clave UNIQUE (clave)
);

CREATE TABLE IF NOT EXISTS cat_sector_2 (
    id           SERIAL      PRIMARY KEY,
    clave        CHAR(2)     NOT NULL,
    descripcion  TEXT        NOT NULL,
    sector_1_id  INTEGER     NOT NULL REFERENCES cat_sector_1 (id),
    CONSTRAINT uq_cat_sector_2_clave UNIQUE (clave)
);

CREATE INDEX IF NOT EXISTS ix_cat_sector_2_sector_1
    ON cat_sector_2 (sector_1_id);

CREATE TABLE IF NOT EXISTS cat_sector_4 (
    id           SERIAL      PRIMARY KEY,
    clave        CHAR(4)     NOT NULL,
    descripcion  TEXT        NOT NULL,
    sector_2_id  INTEGER     NOT NULL REFERENCES cat_sector_2 (id),
    CONSTRAINT uq_cat_sector_4_clave UNIQUE (clave)
);

CREATE INDEX IF NOT EXISTS ix_cat_sector_4_sector_2
    ON cat_sector_4 (sector_2_id);

-- -----------------------------------------------------------------------
-- Catálogos simples
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cat_tamano_registro_patronal (
    id          SERIAL      PRIMARY KEY,
    clave       VARCHAR(2)  NOT NULL,
    descripcion TEXT        NOT NULL,
    CONSTRAINT uq_cat_tamano_registro_patronal_clave UNIQUE (clave)
);

CREATE TABLE IF NOT EXISTS cat_sexo (
    id          SERIAL      PRIMARY KEY,
    clave       VARCHAR(2)  NOT NULL,
    descripcion TEXT        NOT NULL,
    CONSTRAINT uq_cat_sexo_clave UNIQUE (clave)
);

CREATE TABLE IF NOT EXISTS cat_rango_edad (
    id          SERIAL      PRIMARY KEY,
    clave       VARCHAR(3)  NOT NULL,
    descripcion TEXT        NOT NULL,
    CONSTRAINT uq_cat_rango_edad_clave UNIQUE (clave)
);

CREATE TABLE IF NOT EXISTS cat_rango_salario (
    id          SERIAL      PRIMARY KEY,
    clave       VARCHAR(3)  NOT NULL,
    descripcion TEXT        NOT NULL,
    CONSTRAINT uq_cat_rango_salario_clave UNIQUE (clave)
);

CREATE TABLE IF NOT EXISTS cat_rango_uma (
    id          SERIAL      PRIMARY KEY,
    clave       VARCHAR(3)  NOT NULL,
    descripcion TEXT        NOT NULL,
    CONSTRAINT uq_cat_rango_uma_clave UNIQUE (clave)
);
