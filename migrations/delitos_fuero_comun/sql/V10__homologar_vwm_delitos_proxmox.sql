-- =============================================================================
-- V10__homologar_vwm_delitos_proxmox.sql  |  Pipeline: delitos_fuero_comun
-- Homologa las 16 MVs del Secretariado con sus equivalentes en proxmox:
--   - Se quita fid (proxmox no la tiene).
--   - Se ajustan tipos: clave_entidad character(2), clave_municipio varchar(5),
--     carpetas_investigacion integer, nombre varchar(254); en el grupo género +
--     vwm_feminicidios además tasa_carpetas_investigacion numeric(12,2) y
--     bien_juridico/delito varchar(100)/varchar(120).
--   - Se reemplaza la plantilla única de 6 columnas pivote por 3 plantillas,
--     igual que proxmox:
--       * grupo arma (feminicidio, homicidio_doloso, lesiones_dolosas):
--         con_arma_de_fuego / con_arma_blanca / con_otro_elemento / no_especificado
--       * grupo violencia (los 8 robo_*): con_violencia / sin_violencia
--       * grupo género (abuso_sexual, violacion, violencia_familiar,
--         violencia_genero_no_familiar) y vwm_feminicidios: sin pivote,
--         columnas crudas nivel_jerarquico + modalidad de la fila
--         nivel_jerarquico='delito'.
--   - Se agrega grid completo (cvegeo_municipalities Jalisco x fechas) vía
--     CROSS JOIN + LEFT JOIN, igual que proxmox, en vez de solo filas con dato.
--     El eje de fechas usa TODO vw_gold_delitos_fuero_comun (no solo el delito
--     de cada vista): así vistas con datos 0 en Jalisco (p. ej.
--     violencia_genero_no_familiar) igual generan el grid completo en vez de
--     quedar vacías, igual que en proxmox.
-- Ver comparaciones/comparacion_delitos_fuero_comun_local_proxmox.md
-- =============================================================================

DROP MATERIALIZED VIEW IF EXISTS vwm_feminicidios;
DROP MATERIALIZED VIEW IF EXISTS vwm_datos_delitos_robo_institucion_bancaria_secretariado;
DROP MATERIALIZED VIEW IF EXISTS vwm_datos_delitos_robo_transportista_secretariado;
DROP MATERIALIZED VIEW IF EXISTS vwm_datos_delitos_robo_transeunte_via_publica_secretariado;
DROP MATERIALIZED VIEW IF EXISTS vwm_datos_delitos_robo_negocio_secretariado;
DROP MATERIALIZED VIEW IF EXISTS vwm_datos_delitos_robo_casa_habitacion_secretariado;
DROP MATERIALIZED VIEW IF EXISTS vwm_datos_delitos_robo_autopartes_secretariado;
DROP MATERIALIZED VIEW IF EXISTS vwm_datos_delitos_robo_motocicleta_secretariado;
DROP MATERIALIZED VIEW IF EXISTS vwm_datos_delitos_robo_coche_cuatro_ruedas_secretariado;
DROP MATERIALIZED VIEW IF EXISTS vwm_datos_delitos_violencia_genero_no_familiar_secretariado;
DROP MATERIALIZED VIEW IF EXISTS vwm_datos_delitos_violencia_familiar_secretariado;
DROP MATERIALIZED VIEW IF EXISTS vwm_datos_delitos_abuso_sexual_secretariado;
DROP MATERIALIZED VIEW IF EXISTS vwm_datos_delitos_violacion_secretariado;
DROP MATERIALIZED VIEW IF EXISTS vwm_datos_delitos_lesiones_dolosas_secretariado;
DROP MATERIALIZED VIEW IF EXISTS vwm_datos_delitos_feminicidio_secretariado;
DROP MATERIALIZED VIEW IF EXISTS vwm_datos_delitos_homicidio_doloso_secretariado;

-- =============================================================================
-- GRUPO ARMA: con_arma_de_fuego / con_arma_blanca / con_otro_elemento / no_especificado
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. vwm_datos_delitos_homicidio_doloso_secretariado
-- -----------------------------------------------------------------------------
CREATE MATERIALIZED VIEW vwm_datos_delitos_homicidio_doloso_secretariado AS
WITH datos AS (
    SELECT
        g.cve_municipio,
        g.fecha_mes,
        MAX(g.bien_juridico)::text                                                                                         AS bien_juridico,
        MAX(g.delito)::text                                                                                                 AS delito,
        SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%arma de fuego%')   AS con_arma_de_fuego,
        SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%arma blanca%')     AS con_arma_blanca,
        SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%otro elemento%')   AS con_otro_elemento,
        SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%no especificado%') AS no_especificado,
        MAX(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'delito')::integer                                    AS carpetas_investigacion,
        MAX(g.tasa_carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'delito')                                        AS tasa_carpetas_investigacion
    FROM vw_gold_delitos_fuero_comun g
    WHERE g.delito = 'Homicidio doloso'
    GROUP BY g.cve_municipio, g.fecha_mes
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
    datos.bien_juridico,
    datos.delito,
    datos.con_arma_de_fuego,
    datos.con_arma_blanca,
    datos.con_otro_elemento,
    datos.no_especificado,
    datos.carpetas_investigacion,
    datos.tasa_carpetas_investigacion
FROM base
LEFT JOIN datos ON base.clave_municipio = datos.cve_municipio AND base.fecha_mes = datos.fecha_mes
WITH NO DATA;

CREATE UNIQUE INDEX uix_vwm_homicidio_doloso_nk ON vwm_datos_delitos_homicidio_doloso_secretariado (clave_municipio, fecha);
CREATE INDEX ix_vwm_homicidio_doloso_fecha ON vwm_datos_delitos_homicidio_doloso_secretariado (fecha);
CREATE INDEX ix_vwm_homicidio_doloso_mun ON vwm_datos_delitos_homicidio_doloso_secretariado (clave_municipio);

-- -----------------------------------------------------------------------------
-- 2. vwm_datos_delitos_feminicidio_secretariado
-- -----------------------------------------------------------------------------
CREATE MATERIALIZED VIEW vwm_datos_delitos_feminicidio_secretariado AS
WITH datos AS (
    SELECT
        g.cve_municipio,
        g.fecha_mes,
        MAX(g.bien_juridico)::text                                                                                         AS bien_juridico,
        MAX(g.delito)::text                                                                                                 AS delito,
        SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%arma de fuego%')   AS con_arma_de_fuego,
        SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%arma blanca%')     AS con_arma_blanca,
        SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%otro elemento%')   AS con_otro_elemento,
        SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%no especificado%') AS no_especificado,
        MAX(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'delito')::integer                                    AS carpetas_investigacion,
        MAX(g.tasa_carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'delito')                                        AS tasa_carpetas_investigacion
    FROM vw_gold_delitos_fuero_comun g
    WHERE g.delito = 'Feminicidio'
    GROUP BY g.cve_municipio, g.fecha_mes
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
    datos.bien_juridico,
    datos.delito,
    datos.con_arma_de_fuego,
    datos.con_arma_blanca,
    datos.con_otro_elemento,
    datos.no_especificado,
    datos.carpetas_investigacion,
    datos.tasa_carpetas_investigacion
FROM base
LEFT JOIN datos ON base.clave_municipio = datos.cve_municipio AND base.fecha_mes = datos.fecha_mes
WITH NO DATA;

CREATE UNIQUE INDEX uix_vwm_feminicidio_sec_nk ON vwm_datos_delitos_feminicidio_secretariado (clave_municipio, fecha);
CREATE INDEX ix_vwm_feminicidio_sec_fecha ON vwm_datos_delitos_feminicidio_secretariado (fecha);
CREATE INDEX ix_vwm_feminicidio_sec_mun ON vwm_datos_delitos_feminicidio_secretariado (clave_municipio);

-- -----------------------------------------------------------------------------
-- 3. vwm_datos_delitos_lesiones_dolosas_secretariado
-- -----------------------------------------------------------------------------
CREATE MATERIALIZED VIEW vwm_datos_delitos_lesiones_dolosas_secretariado AS
WITH datos AS (
    SELECT
        g.cve_municipio,
        g.fecha_mes,
        MAX(g.bien_juridico)::text                                                                                         AS bien_juridico,
        MAX(g.delito)::text                                                                                                 AS delito,
        SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%arma de fuego%')   AS con_arma_de_fuego,
        SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%arma blanca%')     AS con_arma_blanca,
        SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%otro elemento%')   AS con_otro_elemento,
        SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%no especificado%') AS no_especificado,
        MAX(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'delito')::integer                                    AS carpetas_investigacion,
        MAX(g.tasa_carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'delito')                                        AS tasa_carpetas_investigacion
    FROM vw_gold_delitos_fuero_comun g
    WHERE g.delito = 'Lesiones dolosas'
    GROUP BY g.cve_municipio, g.fecha_mes
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
    datos.bien_juridico,
    datos.delito,
    datos.con_arma_de_fuego,
    datos.con_arma_blanca,
    datos.con_otro_elemento,
    datos.no_especificado,
    datos.carpetas_investigacion,
    datos.tasa_carpetas_investigacion
FROM base
LEFT JOIN datos ON base.clave_municipio = datos.cve_municipio AND base.fecha_mes = datos.fecha_mes
WITH NO DATA;

CREATE UNIQUE INDEX uix_vwm_lesiones_dolosas_nk ON vwm_datos_delitos_lesiones_dolosas_secretariado (clave_municipio, fecha);
CREATE INDEX ix_vwm_lesiones_dolosas_fecha ON vwm_datos_delitos_lesiones_dolosas_secretariado (fecha);
CREATE INDEX ix_vwm_lesiones_dolosas_mun ON vwm_datos_delitos_lesiones_dolosas_secretariado (clave_municipio);

-- =============================================================================
-- GRUPO GÉNERO: sin pivote, columnas crudas nivel_jerarquico + modalidad
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 4. vwm_datos_delitos_violacion_secretariado
-- -----------------------------------------------------------------------------
CREATE MATERIALIZED VIEW vwm_datos_delitos_violacion_secretariado AS
WITH datos AS (
    SELECT
        g.cve_municipio,
        g.fecha_mes,
        g.nivel_jerarquico,
        g.bien_juridico::VARCHAR(100)     AS bien_juridico,
        g.delito::VARCHAR(120)            AS delito,
        g.modalidad,
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
-- 5. vwm_datos_delitos_abuso_sexual_secretariado
-- -----------------------------------------------------------------------------
CREATE MATERIALIZED VIEW vwm_datos_delitos_abuso_sexual_secretariado AS
WITH datos AS (
    SELECT
        g.cve_municipio,
        g.fecha_mes,
        g.nivel_jerarquico,
        g.bien_juridico::VARCHAR(100)     AS bien_juridico,
        g.delito::VARCHAR(120)            AS delito,
        g.modalidad,
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
-- 6. vwm_datos_delitos_violencia_familiar_secretariado
-- -----------------------------------------------------------------------------
CREATE MATERIALIZED VIEW vwm_datos_delitos_violencia_familiar_secretariado AS
WITH datos AS (
    SELECT
        g.cve_municipio,
        g.fecha_mes,
        g.nivel_jerarquico,
        g.bien_juridico::VARCHAR(100)     AS bien_juridico,
        g.delito::VARCHAR(120)            AS delito,
        g.modalidad,
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
-- 7. vwm_datos_delitos_violencia_genero_no_familiar_secretariado
--    Jalisco no registra carpetas para este tipo_delito en todo 2015-2026
--    (verificado contra staging); el grid completo genera igual todas las
--    combinaciones municipio x fecha con columnas de dato en NULL.
-- -----------------------------------------------------------------------------
CREATE MATERIALIZED VIEW vwm_datos_delitos_violencia_genero_no_familiar_secretariado AS
WITH datos AS (
    SELECT
        g.cve_municipio,
        g.fecha_mes,
        g.nivel_jerarquico,
        g.bien_juridico::VARCHAR(100)     AS bien_juridico,
        g.delito::VARCHAR(120)            AS delito,
        g.modalidad,
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

-- =============================================================================
-- GRUPO VIOLENCIA: con_violencia / sin_violencia
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 8. vwm_datos_delitos_robo_coche_cuatro_ruedas_secretariado
-- -----------------------------------------------------------------------------
CREATE MATERIALIZED VIEW vwm_datos_delitos_robo_coche_cuatro_ruedas_secretariado AS
WITH datos AS (
    SELECT
        g.cve_municipio,
        g.fecha_mes,
        MAX(g.bien_juridico)::text                                                                                       AS bien_juridico,
        MAX(g.delito)::text                                                                                               AS delito,
        SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%con violencia%') AS con_violencia,
        SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%sin violencia%') AS sin_violencia,
        MAX(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'delito')::integer                                  AS carpetas_investigacion,
        MAX(g.tasa_carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'delito')                                      AS tasa_carpetas_investigacion
    FROM vw_gold_delitos_fuero_comun g
    WHERE g.delito = 'Robo de coche de cuatro ruedas'
    GROUP BY g.cve_municipio, g.fecha_mes
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
    datos.bien_juridico,
    datos.delito,
    datos.con_violencia,
    datos.sin_violencia,
    datos.carpetas_investigacion,
    datos.tasa_carpetas_investigacion
FROM base
LEFT JOIN datos ON base.clave_municipio = datos.cve_municipio AND base.fecha_mes = datos.fecha_mes
WITH NO DATA;

CREATE UNIQUE INDEX uix_vwm_robo_coche_4r_nk ON vwm_datos_delitos_robo_coche_cuatro_ruedas_secretariado (clave_municipio, fecha);
CREATE INDEX ix_vwm_robo_coche_4r_fecha ON vwm_datos_delitos_robo_coche_cuatro_ruedas_secretariado (fecha);
CREATE INDEX ix_vwm_robo_coche_4r_mun ON vwm_datos_delitos_robo_coche_cuatro_ruedas_secretariado (clave_municipio);

-- -----------------------------------------------------------------------------
-- 9. vwm_datos_delitos_robo_motocicleta_secretariado
-- -----------------------------------------------------------------------------
CREATE MATERIALIZED VIEW vwm_datos_delitos_robo_motocicleta_secretariado AS
WITH datos AS (
    SELECT
        g.cve_municipio,
        g.fecha_mes,
        MAX(g.bien_juridico)::text                                                                                       AS bien_juridico,
        MAX(g.delito)::text                                                                                               AS delito,
        SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%con violencia%') AS con_violencia,
        SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%sin violencia%') AS sin_violencia,
        MAX(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'delito')::integer                                  AS carpetas_investigacion,
        MAX(g.tasa_carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'delito')                                      AS tasa_carpetas_investigacion
    FROM vw_gold_delitos_fuero_comun g
    WHERE g.delito = 'Robo de motocicleta'
    GROUP BY g.cve_municipio, g.fecha_mes
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
    datos.bien_juridico,
    datos.delito,
    datos.con_violencia,
    datos.sin_violencia,
    datos.carpetas_investigacion,
    datos.tasa_carpetas_investigacion
FROM base
LEFT JOIN datos ON base.clave_municipio = datos.cve_municipio AND base.fecha_mes = datos.fecha_mes
WITH NO DATA;

CREATE UNIQUE INDEX uix_vwm_robo_moto_nk ON vwm_datos_delitos_robo_motocicleta_secretariado (clave_municipio, fecha);
CREATE INDEX ix_vwm_robo_moto_fecha ON vwm_datos_delitos_robo_motocicleta_secretariado (fecha);
CREATE INDEX ix_vwm_robo_moto_mun ON vwm_datos_delitos_robo_motocicleta_secretariado (clave_municipio);

-- -----------------------------------------------------------------------------
-- 10. vwm_datos_delitos_robo_autopartes_secretariado
-- -----------------------------------------------------------------------------
CREATE MATERIALIZED VIEW vwm_datos_delitos_robo_autopartes_secretariado AS
WITH datos AS (
    SELECT
        g.cve_municipio,
        g.fecha_mes,
        MAX(g.bien_juridico)::text                                                                                       AS bien_juridico,
        MAX(g.delito)::text                                                                                               AS delito,
        SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%con violencia%') AS con_violencia,
        SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%sin violencia%') AS sin_violencia,
        MAX(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'delito')::integer                                  AS carpetas_investigacion,
        MAX(g.tasa_carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'delito')                                      AS tasa_carpetas_investigacion
    FROM vw_gold_delitos_fuero_comun g
    WHERE g.delito = 'Robo de autopartes'
    GROUP BY g.cve_municipio, g.fecha_mes
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
    datos.bien_juridico,
    datos.delito,
    datos.con_violencia,
    datos.sin_violencia,
    datos.carpetas_investigacion,
    datos.tasa_carpetas_investigacion
FROM base
LEFT JOIN datos ON base.clave_municipio = datos.cve_municipio AND base.fecha_mes = datos.fecha_mes
WITH NO DATA;

CREATE UNIQUE INDEX uix_vwm_robo_autopartes_nk ON vwm_datos_delitos_robo_autopartes_secretariado (clave_municipio, fecha);
CREATE INDEX ix_vwm_robo_autopartes_fecha ON vwm_datos_delitos_robo_autopartes_secretariado (fecha);
CREATE INDEX ix_vwm_robo_autopartes_mun ON vwm_datos_delitos_robo_autopartes_secretariado (clave_municipio);

-- -----------------------------------------------------------------------------
-- 11. vwm_datos_delitos_robo_casa_habitacion_secretariado
-- -----------------------------------------------------------------------------
CREATE MATERIALIZED VIEW vwm_datos_delitos_robo_casa_habitacion_secretariado AS
WITH datos AS (
    SELECT
        g.cve_municipio,
        g.fecha_mes,
        MAX(g.bien_juridico)::text                                                                                       AS bien_juridico,
        MAX(g.delito)::text                                                                                               AS delito,
        SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%con violencia%') AS con_violencia,
        SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%sin violencia%') AS sin_violencia,
        MAX(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'delito')::integer                                  AS carpetas_investigacion,
        MAX(g.tasa_carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'delito')                                      AS tasa_carpetas_investigacion
    FROM vw_gold_delitos_fuero_comun g
    WHERE g.delito = 'Robo a casa habitación'
    GROUP BY g.cve_municipio, g.fecha_mes
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
    datos.bien_juridico,
    datos.delito,
    datos.con_violencia,
    datos.sin_violencia,
    datos.carpetas_investigacion,
    datos.tasa_carpetas_investigacion
FROM base
LEFT JOIN datos ON base.clave_municipio = datos.cve_municipio AND base.fecha_mes = datos.fecha_mes
WITH NO DATA;

CREATE UNIQUE INDEX uix_vwm_robo_casa_nk ON vwm_datos_delitos_robo_casa_habitacion_secretariado (clave_municipio, fecha);
CREATE INDEX ix_vwm_robo_casa_fecha ON vwm_datos_delitos_robo_casa_habitacion_secretariado (fecha);
CREATE INDEX ix_vwm_robo_casa_mun ON vwm_datos_delitos_robo_casa_habitacion_secretariado (clave_municipio);

-- -----------------------------------------------------------------------------
-- 12. vwm_datos_delitos_robo_negocio_secretariado
-- -----------------------------------------------------------------------------
CREATE MATERIALIZED VIEW vwm_datos_delitos_robo_negocio_secretariado AS
WITH datos AS (
    SELECT
        g.cve_municipio,
        g.fecha_mes,
        MAX(g.bien_juridico)::text                                                                                       AS bien_juridico,
        MAX(g.delito)::text                                                                                               AS delito,
        SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%con violencia%') AS con_violencia,
        SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%sin violencia%') AS sin_violencia,
        MAX(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'delito')::integer                                  AS carpetas_investigacion,
        MAX(g.tasa_carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'delito')                                      AS tasa_carpetas_investigacion
    FROM vw_gold_delitos_fuero_comun g
    WHERE g.delito = 'Robo a negocio'
    GROUP BY g.cve_municipio, g.fecha_mes
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
    datos.bien_juridico,
    datos.delito,
    datos.con_violencia,
    datos.sin_violencia,
    datos.carpetas_investigacion,
    datos.tasa_carpetas_investigacion
FROM base
LEFT JOIN datos ON base.clave_municipio = datos.cve_municipio AND base.fecha_mes = datos.fecha_mes
WITH NO DATA;

CREATE UNIQUE INDEX uix_vwm_robo_negocio_nk ON vwm_datos_delitos_robo_negocio_secretariado (clave_municipio, fecha);
CREATE INDEX ix_vwm_robo_negocio_fecha ON vwm_datos_delitos_robo_negocio_secretariado (fecha);
CREATE INDEX ix_vwm_robo_negocio_mun ON vwm_datos_delitos_robo_negocio_secretariado (clave_municipio);

-- -----------------------------------------------------------------------------
-- 13. vwm_datos_delitos_robo_transeunte_via_publica_secretariado
-- -----------------------------------------------------------------------------
CREATE MATERIALIZED VIEW vwm_datos_delitos_robo_transeunte_via_publica_secretariado AS
WITH datos AS (
    SELECT
        g.cve_municipio,
        g.fecha_mes,
        MAX(g.bien_juridico)::text                                                                                       AS bien_juridico,
        MAX(g.delito)::text                                                                                               AS delito,
        SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%con violencia%') AS con_violencia,
        SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%sin violencia%') AS sin_violencia,
        MAX(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'delito')::integer                                  AS carpetas_investigacion,
        MAX(g.tasa_carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'delito')                                      AS tasa_carpetas_investigacion
    FROM vw_gold_delitos_fuero_comun g
    WHERE g.delito = 'Robo a transeúnte en vía pública'
    GROUP BY g.cve_municipio, g.fecha_mes
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
    datos.bien_juridico,
    datos.delito,
    datos.con_violencia,
    datos.sin_violencia,
    datos.carpetas_investigacion,
    datos.tasa_carpetas_investigacion
FROM base
LEFT JOIN datos ON base.clave_municipio = datos.cve_municipio AND base.fecha_mes = datos.fecha_mes
WITH NO DATA;

CREATE UNIQUE INDEX uix_vwm_robo_transeunte_nk ON vwm_datos_delitos_robo_transeunte_via_publica_secretariado (clave_municipio, fecha);
CREATE INDEX ix_vwm_robo_transeunte_fecha ON vwm_datos_delitos_robo_transeunte_via_publica_secretariado (fecha);
CREATE INDEX ix_vwm_robo_transeunte_mun ON vwm_datos_delitos_robo_transeunte_via_publica_secretariado (clave_municipio);

-- -----------------------------------------------------------------------------
-- 14. vwm_datos_delitos_robo_transportista_secretariado
-- -----------------------------------------------------------------------------
CREATE MATERIALIZED VIEW vwm_datos_delitos_robo_transportista_secretariado AS
WITH datos AS (
    SELECT
        g.cve_municipio,
        g.fecha_mes,
        MAX(g.bien_juridico)::text                                                                                       AS bien_juridico,
        MAX(g.delito)::text                                                                                               AS delito,
        SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%con violencia%') AS con_violencia,
        SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%sin violencia%') AS sin_violencia,
        MAX(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'delito')::integer                                  AS carpetas_investigacion,
        MAX(g.tasa_carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'delito')                                      AS tasa_carpetas_investigacion
    FROM vw_gold_delitos_fuero_comun g
    WHERE g.delito = 'Robo a transportista'
    GROUP BY g.cve_municipio, g.fecha_mes
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
    datos.bien_juridico,
    datos.delito,
    datos.con_violencia,
    datos.sin_violencia,
    datos.carpetas_investigacion,
    datos.tasa_carpetas_investigacion
FROM base
LEFT JOIN datos ON base.clave_municipio = datos.cve_municipio AND base.fecha_mes = datos.fecha_mes
WITH NO DATA;

CREATE UNIQUE INDEX uix_vwm_robo_transportista_nk ON vwm_datos_delitos_robo_transportista_secretariado (clave_municipio, fecha);
CREATE INDEX ix_vwm_robo_transportista_fecha ON vwm_datos_delitos_robo_transportista_secretariado (fecha);
CREATE INDEX ix_vwm_robo_transportista_mun ON vwm_datos_delitos_robo_transportista_secretariado (clave_municipio);

-- -----------------------------------------------------------------------------
-- 15. vwm_datos_delitos_robo_institucion_bancaria_secretariado
-- -----------------------------------------------------------------------------
CREATE MATERIALIZED VIEW vwm_datos_delitos_robo_institucion_bancaria_secretariado AS
WITH datos AS (
    SELECT
        g.cve_municipio,
        g.fecha_mes,
        MAX(g.bien_juridico)::text                                                                                       AS bien_juridico,
        MAX(g.delito)::text                                                                                               AS delito,
        SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%con violencia%') AS con_violencia,
        SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%sin violencia%') AS sin_violencia,
        MAX(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'delito')::integer                                  AS carpetas_investigacion,
        MAX(g.tasa_carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'delito')                                      AS tasa_carpetas_investigacion
    FROM vw_gold_delitos_fuero_comun g
    WHERE g.delito = 'Robo a institución bancaria'
    GROUP BY g.cve_municipio, g.fecha_mes
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
    datos.bien_juridico,
    datos.delito,
    datos.con_violencia,
    datos.sin_violencia,
    datos.carpetas_investigacion,
    datos.tasa_carpetas_investigacion
FROM base
LEFT JOIN datos ON base.clave_municipio = datos.cve_municipio AND base.fecha_mes = datos.fecha_mes
WITH NO DATA;

CREATE UNIQUE INDEX uix_vwm_robo_banco_nk ON vwm_datos_delitos_robo_institucion_bancaria_secretariado (clave_municipio, fecha);
CREATE INDEX ix_vwm_robo_banco_fecha ON vwm_datos_delitos_robo_institucion_bancaria_secretariado (fecha);
CREATE INDEX ix_vwm_robo_banco_mun ON vwm_datos_delitos_robo_institucion_bancaria_secretariado (clave_municipio);

-- =============================================================================
-- 16. vwm_feminicidios (desarrollo_social en proxmox)
--     Grupo género sin bien_juridico/delito, igual que su equivalente proxmox.
-- =============================================================================
CREATE MATERIALIZED VIEW vwm_feminicidios AS
WITH datos AS (
    SELECT
        g.cve_municipio,
        g.fecha_mes,
        g.nivel_jerarquico,
        g.modalidad,
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
