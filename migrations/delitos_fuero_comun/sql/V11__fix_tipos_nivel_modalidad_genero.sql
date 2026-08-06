-- =============================================================================
-- V11__fix_tipos_nivel_modalidad_genero.sql  |  Pipeline: delitos_fuero_comun
-- V10 dejo nivel_jerarquico y modalidad sin acotar (character varying) en el
-- grupo genero (abuso_sexual, violacion, violencia_familiar,
-- violencia_genero_no_familiar) y en vwm_feminicidios. proxmox los tiene como
-- varchar(30) y varchar(100) respectivamente. ALTER MATERIALIZED VIEW no
-- soporta ALTER COLUMN ... TYPE, así que hay que recrearlas.
-- =============================================================================

DROP MATERIALIZED VIEW IF EXISTS vwm_feminicidios;
DROP MATERIALIZED VIEW IF EXISTS vwm_datos_delitos_violencia_genero_no_familiar_secretariado;
DROP MATERIALIZED VIEW IF EXISTS vwm_datos_delitos_violencia_familiar_secretariado;
DROP MATERIALIZED VIEW IF EXISTS vwm_datos_delitos_abuso_sexual_secretariado;
DROP MATERIALIZED VIEW IF EXISTS vwm_datos_delitos_violacion_secretariado;

-- -----------------------------------------------------------------------------
-- vwm_datos_delitos_violacion_secretariado
-- -----------------------------------------------------------------------------
CREATE MATERIALIZED VIEW vwm_datos_delitos_violacion_secretariado AS
WITH datos AS (
    SELECT
        g.cve_municipio,
        g.fecha_mes,
        g.nivel_jerarquico::VARCHAR(30)   AS nivel_jerarquico,
        g.bien_juridico::VARCHAR(100)     AS bien_juridico,
        g.delito::VARCHAR(120)            AS delito,
        g.modalidad::VARCHAR(100)         AS modalidad,
        g.carpetas_investigacion::integer AS carpetas_investigacion,
        g.tasa_carpetas_investigacion::numeric(12, 2) AS tasa_carpetas_investigacion
    FROM vw_gold_delitos_fuero_comun g
    WHERE g.delito = 'Violación' AND g.nivel_jerarquico = 'delito'
),
base AS (
    SELECT
        LPAD(m.cvegeo::text, 5, '0')::VARCHAR(5) AS clave_municipio,
        m.nomgeo,
        m.geom_iieg,
        m.geom_inegi,
        f.fecha_mes
    FROM cvegeo_municipalities m
    CROSS JOIN (SELECT DISTINCT fecha_mes FROM vw_gold_delitos_fuero_comun) f
    WHERE m.cve_ent = 14
)
SELECT
    base.geom_iieg,
    base.geom_inegi,
    base.nomgeo::VARCHAR(254)                     AS nombre,
    (base.fecha_mes || '-01')::date                AS fecha,
    '14'::CHARACTER(2)                             AS clave_entidad,
    base.clave_municipio,
    datos.nivel_jerarquico,
    datos.bien_juridico,
    datos.delito,
    datos.modalidad,
    datos.carpetas_investigacion,
    datos.tasa_carpetas_investigacion
FROM base
LEFT JOIN datos ON base.clave_municipio = datos.cve_municipio AND base.fecha_mes = datos.fecha_mes
WITH NO DATA;

CREATE UNIQUE INDEX uix_vwm_violacion_nk ON vwm_datos_delitos_violacion_secretariado (clave_municipio, fecha);
CREATE INDEX ix_vwm_violacion_fecha ON vwm_datos_delitos_violacion_secretariado (fecha);
CREATE INDEX ix_vwm_violacion_mun ON vwm_datos_delitos_violacion_secretariado (clave_municipio);

-- -----------------------------------------------------------------------------
-- vwm_datos_delitos_abuso_sexual_secretariado
-- -----------------------------------------------------------------------------
CREATE MATERIALIZED VIEW vwm_datos_delitos_abuso_sexual_secretariado AS
WITH datos AS (
    SELECT
        g.cve_municipio,
        g.fecha_mes,
        g.nivel_jerarquico::VARCHAR(30)   AS nivel_jerarquico,
        g.bien_juridico::VARCHAR(100)     AS bien_juridico,
        g.delito::VARCHAR(120)            AS delito,
        g.modalidad::VARCHAR(100)         AS modalidad,
        g.carpetas_investigacion::integer AS carpetas_investigacion,
        g.tasa_carpetas_investigacion::numeric(12, 2) AS tasa_carpetas_investigacion
    FROM vw_gold_delitos_fuero_comun g
    WHERE g.delito = 'Abuso sexual' AND g.nivel_jerarquico = 'delito'
),
base AS (
    SELECT
        LPAD(m.cvegeo::text, 5, '0')::VARCHAR(5) AS clave_municipio,
        m.nomgeo,
        m.geom_iieg,
        m.geom_inegi,
        f.fecha_mes
    FROM cvegeo_municipalities m
    CROSS JOIN (SELECT DISTINCT fecha_mes FROM vw_gold_delitos_fuero_comun) f
    WHERE m.cve_ent = 14
)
SELECT
    base.geom_iieg,
    base.geom_inegi,
    base.nomgeo::VARCHAR(254)                     AS nombre,
    (base.fecha_mes || '-01')::date                AS fecha,
    '14'::CHARACTER(2)                             AS clave_entidad,
    base.clave_municipio,
    datos.nivel_jerarquico,
    datos.bien_juridico,
    datos.delito,
    datos.modalidad,
    datos.carpetas_investigacion,
    datos.tasa_carpetas_investigacion
FROM base
LEFT JOIN datos ON base.clave_municipio = datos.cve_municipio AND base.fecha_mes = datos.fecha_mes
WITH NO DATA;

CREATE UNIQUE INDEX uix_vwm_abuso_sexual_nk ON vwm_datos_delitos_abuso_sexual_secretariado (clave_municipio, fecha);
CREATE INDEX ix_vwm_abuso_sexual_fecha ON vwm_datos_delitos_abuso_sexual_secretariado (fecha);
CREATE INDEX ix_vwm_abuso_sexual_mun ON vwm_datos_delitos_abuso_sexual_secretariado (clave_municipio);

-- -----------------------------------------------------------------------------
-- vwm_datos_delitos_violencia_familiar_secretariado
-- -----------------------------------------------------------------------------
CREATE MATERIALIZED VIEW vwm_datos_delitos_violencia_familiar_secretariado AS
WITH datos AS (
    SELECT
        g.cve_municipio,
        g.fecha_mes,
        g.nivel_jerarquico::VARCHAR(30)   AS nivel_jerarquico,
        g.bien_juridico::VARCHAR(100)     AS bien_juridico,
        g.delito::VARCHAR(120)            AS delito,
        g.modalidad::VARCHAR(100)         AS modalidad,
        g.carpetas_investigacion::integer AS carpetas_investigacion,
        g.tasa_carpetas_investigacion::numeric(12, 2) AS tasa_carpetas_investigacion
    FROM vw_gold_delitos_fuero_comun g
    WHERE g.delito = 'Violencia familiar' AND g.nivel_jerarquico = 'delito'
),
base AS (
    SELECT
        LPAD(m.cvegeo::text, 5, '0')::VARCHAR(5) AS clave_municipio,
        m.nomgeo,
        m.geom_iieg,
        m.geom_inegi,
        f.fecha_mes
    FROM cvegeo_municipalities m
    CROSS JOIN (SELECT DISTINCT fecha_mes FROM vw_gold_delitos_fuero_comun) f
    WHERE m.cve_ent = 14
)
SELECT
    base.geom_iieg,
    base.geom_inegi,
    base.nomgeo::VARCHAR(254)                     AS nombre,
    (base.fecha_mes || '-01')::date                AS fecha,
    '14'::CHARACTER(2)                             AS clave_entidad,
    base.clave_municipio,
    datos.nivel_jerarquico,
    datos.bien_juridico,
    datos.delito,
    datos.modalidad,
    datos.carpetas_investigacion,
    datos.tasa_carpetas_investigacion
FROM base
LEFT JOIN datos ON base.clave_municipio = datos.cve_municipio AND base.fecha_mes = datos.fecha_mes
WITH NO DATA;

CREATE UNIQUE INDEX uix_vwm_viol_familiar_nk ON vwm_datos_delitos_violencia_familiar_secretariado (clave_municipio, fecha);
CREATE INDEX ix_vwm_viol_familiar_fecha ON vwm_datos_delitos_violencia_familiar_secretariado (fecha);
CREATE INDEX ix_vwm_viol_familiar_mun ON vwm_datos_delitos_violencia_familiar_secretariado (clave_municipio);

-- -----------------------------------------------------------------------------
-- vwm_datos_delitos_violencia_genero_no_familiar_secretariado
-- -----------------------------------------------------------------------------
CREATE MATERIALIZED VIEW vwm_datos_delitos_violencia_genero_no_familiar_secretariado AS
WITH datos AS (
    SELECT
        g.cve_municipio,
        g.fecha_mes,
        g.nivel_jerarquico::VARCHAR(30)   AS nivel_jerarquico,
        g.bien_juridico::VARCHAR(100)     AS bien_juridico,
        g.delito::VARCHAR(120)            AS delito,
        g.modalidad::VARCHAR(100)         AS modalidad,
        g.carpetas_investigacion::integer AS carpetas_investigacion,
        g.tasa_carpetas_investigacion::numeric(12, 2) AS tasa_carpetas_investigacion
    FROM vw_gold_delitos_fuero_comun g
    WHERE g.delito = 'Violencia de género en todas sus modalidades distinta a la violencia familiar'
      AND g.nivel_jerarquico = 'delito'
),
base AS (
    SELECT
        LPAD(m.cvegeo::text, 5, '0')::VARCHAR(5) AS clave_municipio,
        m.nomgeo,
        m.geom_iieg,
        m.geom_inegi,
        f.fecha_mes
    FROM cvegeo_municipalities m
    CROSS JOIN (SELECT DISTINCT fecha_mes FROM vw_gold_delitos_fuero_comun) f
    WHERE m.cve_ent = 14
)
SELECT
    base.geom_iieg,
    base.geom_inegi,
    base.nomgeo::VARCHAR(254)                     AS nombre,
    (base.fecha_mes || '-01')::date                AS fecha,
    '14'::CHARACTER(2)                             AS clave_entidad,
    base.clave_municipio,
    datos.nivel_jerarquico,
    datos.bien_juridico,
    datos.delito,
    datos.modalidad,
    datos.carpetas_investigacion,
    datos.tasa_carpetas_investigacion
FROM base
LEFT JOIN datos ON base.clave_municipio = datos.cve_municipio AND base.fecha_mes = datos.fecha_mes
WITH NO DATA;

CREATE UNIQUE INDEX uix_vwm_viol_genero_nf_nk ON vwm_datos_delitos_violencia_genero_no_familiar_secretariado (clave_municipio, fecha);
CREATE INDEX ix_vwm_viol_genero_nf_fecha ON vwm_datos_delitos_violencia_genero_no_familiar_secretariado (fecha);
CREATE INDEX ix_vwm_viol_genero_nf_mun ON vwm_datos_delitos_violencia_genero_no_familiar_secretariado (clave_municipio);

-- -----------------------------------------------------------------------------
-- vwm_feminicidios
-- -----------------------------------------------------------------------------
CREATE MATERIALIZED VIEW vwm_feminicidios AS
WITH datos AS (
    SELECT
        g.cve_municipio,
        g.fecha_mes,
        g.nivel_jerarquico::VARCHAR(30)   AS nivel_jerarquico,
        g.modalidad::VARCHAR(100)         AS modalidad,
        g.carpetas_investigacion::integer AS carpetas_investigacion,
        g.tasa_carpetas_investigacion::numeric(12, 2) AS tasa_carpetas_investigacion
    FROM vw_gold_delitos_fuero_comun g
    WHERE g.delito = 'Feminicidio' AND g.nivel_jerarquico = 'delito'
),
base AS (
    SELECT
        LPAD(m.cvegeo::text, 5, '0')::VARCHAR(5) AS clave_municipio,
        m.nomgeo,
        m.geom_iieg,
        m.geom_inegi,
        f.fecha_mes
    FROM cvegeo_municipalities m
    CROSS JOIN (SELECT DISTINCT fecha_mes FROM vw_gold_delitos_fuero_comun) f
    WHERE m.cve_ent = 14
)
SELECT
    base.geom_iieg,
    base.geom_inegi,
    base.nomgeo::VARCHAR(254)                     AS nombre,
    (base.fecha_mes || '-01')::date                AS fecha,
    '14'::CHARACTER(2)                             AS clave_entidad,
    base.clave_municipio,
    datos.nivel_jerarquico,
    datos.modalidad,
    datos.carpetas_investigacion,
    datos.tasa_carpetas_investigacion
FROM base
LEFT JOIN datos ON base.clave_municipio = datos.cve_municipio AND base.fecha_mes = datos.fecha_mes
WITH NO DATA;

CREATE UNIQUE INDEX uix_vwm_feminicidios_nk ON vwm_feminicidios (clave_municipio, fecha);
CREATE INDEX ix_vwm_feminicidios_fecha ON vwm_feminicidios (fecha);
CREATE INDEX ix_vwm_feminicidios_mun ON vwm_feminicidios (clave_municipio);
