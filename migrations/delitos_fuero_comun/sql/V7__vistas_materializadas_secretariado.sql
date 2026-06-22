-- =============================================================================
-- V7__vistas_materializadas_secretariado.sql  |  Pipeline: delitos_fuero_comun
-- Vistas materializadas del Secretariado Ejecutivo (SSPC/RNID) para Jalisco.
-- Fuente base: vw_gold_delitos_fuero_comun (V6).
-- Geometrías: cvegeo_municipalities.geom_iieg / geom_inegi (SRID 6368).
-- Todas las MVs se crean WITH NO DATA; el REFRESH inicial ocurre en el DAG.
-- =============================================================================

-- -----------------------------------------------------------------------------
-- PostGIS y extensión de la tabla FDW con columnas de geometría
-- -----------------------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS postgis;

ALTER FOREIGN TABLE cvegeo_municipalities
    ADD COLUMN IF NOT EXISTS geom_iieg geometry(MultiPolygon, 6368),
    ADD COLUMN IF NOT EXISTS geom_inegi geometry(MultiPolygon, 6368);

-- =============================================================================
-- Macro de columnas comunes a las 14 MVs estándar (por delito):
--   fid, geom_iieg, geom_inegi, nombre, fecha, clave_entidad, clave_municipio,
--   bien_juridico, delito, con_arma_de_fuego, con_arma_blanca,
--   con_otro_elemento, no_especificado, con_violencia, sin_violencia,
--   carpetas_investigacion, tasa_carpetas_investigacion
-- El pivot de armas/violencia usa filas nivel_jerarquico = 'modalidad' del gold MV.
-- carpetas_investigacion y tasa usan la fila nivel_jerarquico = 'delito'.
-- Excepción: feminicidio conserva nivel_jerarquico + modalidad sin pivot.
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. vwm_datos_delitos_homicidio_doloso_secretariado
-- -----------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS vwm_datos_delitos_homicidio_doloso_secretariado AS
SELECT
    ROW_NUMBER() OVER (ORDER BY g.cve_municipio, g.fecha_mes)  AS fid,
    m.geom_iieg,
    m.geom_inegi,
    m.nomgeo                                                    AS nombre,
    (g.fecha_mes || '-01')::date                                AS fecha,
    '14'::VARCHAR(2)                                            AS clave_entidad,
    g.cve_municipio                                             AS clave_municipio,
    g.bien_juridico,
    g.delito,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%arma de fuego%'
    )                                                           AS con_arma_de_fuego,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%arma blanca%'
    )                                                           AS con_arma_blanca,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%otro elemento%'
    )                                                           AS con_otro_elemento,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%no especificado%'
    )                                                           AS no_especificado,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%con violencia%'
    )                                                           AS con_violencia,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%sin violencia%'
    )                                                           AS sin_violencia,
    MAX(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'delito'
    )                                                           AS carpetas_investigacion,
    MAX(g.tasa_carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'delito'
    )                                                           AS tasa_carpetas_investigacion
FROM vw_gold_delitos_fuero_comun g
JOIN cvegeo_municipalities m ON m.cvegeo = g.cve_municipio::INTEGER
WHERE g.delito = 'Homicidio doloso'
GROUP BY g.fecha_mes, g.cve_municipio, g.bien_juridico, g.delito,
         m.geom_iieg, m.geom_inegi, m.nomgeo
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS uix_vwm_homicidio_doloso_nk
    ON vwm_datos_delitos_homicidio_doloso_secretariado (clave_municipio, fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_homicidio_doloso_fecha
    ON vwm_datos_delitos_homicidio_doloso_secretariado (fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_homicidio_doloso_mun
    ON vwm_datos_delitos_homicidio_doloso_secretariado (clave_municipio);

-- -----------------------------------------------------------------------------
-- 2. vwm_datos_delitos_feminicidio_secretariado
-- -----------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS vwm_datos_delitos_feminicidio_secretariado AS
SELECT
    ROW_NUMBER() OVER (ORDER BY g.cve_municipio, g.fecha_mes)  AS fid,
    m.geom_iieg,
    m.geom_inegi,
    m.nomgeo                                                    AS nombre,
    (g.fecha_mes || '-01')::date                                AS fecha,
    '14'::VARCHAR(2)                                            AS clave_entidad,
    g.cve_municipio                                             AS clave_municipio,
    g.bien_juridico,
    g.delito,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%arma de fuego%'
    )                                                           AS con_arma_de_fuego,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%arma blanca%'
    )                                                           AS con_arma_blanca,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%otro elemento%'
    )                                                           AS con_otro_elemento,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%no especificado%'
    )                                                           AS no_especificado,
    MAX(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'delito'
    )                                                           AS carpetas_investigacion,
    MAX(g.tasa_carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'delito'
    )                                                           AS tasa_carpetas_investigacion
FROM vw_gold_delitos_fuero_comun g
JOIN cvegeo_municipalities m ON m.cvegeo = g.cve_municipio::INTEGER
WHERE g.delito = 'Feminicidio'
GROUP BY g.fecha_mes, g.cve_municipio, g.bien_juridico, g.delito,
         m.geom_iieg, m.geom_inegi, m.nomgeo
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS uix_vwm_feminicidio_sec_nk
    ON vwm_datos_delitos_feminicidio_secretariado (clave_municipio, fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_feminicidio_sec_fecha
    ON vwm_datos_delitos_feminicidio_secretariado (fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_feminicidio_sec_mun
    ON vwm_datos_delitos_feminicidio_secretariado (clave_municipio);

-- -----------------------------------------------------------------------------
-- 3. vwm_datos_delitos_lesiones_dolosas_secretariado
-- -----------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS vwm_datos_delitos_lesiones_dolosas_secretariado AS
SELECT
    ROW_NUMBER() OVER (ORDER BY g.cve_municipio, g.fecha_mes)  AS fid,
    m.geom_iieg,
    m.geom_inegi,
    m.nomgeo                                                    AS nombre,
    (g.fecha_mes || '-01')::date                                AS fecha,
    '14'::VARCHAR(2)                                            AS clave_entidad,
    g.cve_municipio                                             AS clave_municipio,
    g.bien_juridico,
    g.delito,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%arma de fuego%'
    )                                                           AS con_arma_de_fuego,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%arma blanca%'
    )                                                           AS con_arma_blanca,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%otro elemento%'
    )                                                           AS con_otro_elemento,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%no especificado%'
    )                                                           AS no_especificado,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%con violencia%'
    )                                                           AS con_violencia,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%sin violencia%'
    )                                                           AS sin_violencia,
    MAX(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'delito'
    )                                                           AS carpetas_investigacion,
    MAX(g.tasa_carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'delito'
    )                                                           AS tasa_carpetas_investigacion
FROM vw_gold_delitos_fuero_comun g
JOIN cvegeo_municipalities m ON m.cvegeo = g.cve_municipio::INTEGER
WHERE g.delito = 'Lesiones dolosas'
GROUP BY g.fecha_mes, g.cve_municipio, g.bien_juridico, g.delito,
         m.geom_iieg, m.geom_inegi, m.nomgeo
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS uix_vwm_lesiones_dolosas_nk
    ON vwm_datos_delitos_lesiones_dolosas_secretariado (clave_municipio, fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_lesiones_dolosas_fecha
    ON vwm_datos_delitos_lesiones_dolosas_secretariado (fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_lesiones_dolosas_mun
    ON vwm_datos_delitos_lesiones_dolosas_secretariado (clave_municipio);

-- -----------------------------------------------------------------------------
-- 4. vwm_datos_delitos_violacion_secretariado
-- -----------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS vwm_datos_delitos_violacion_secretariado AS
SELECT
    ROW_NUMBER() OVER (ORDER BY g.cve_municipio, g.fecha_mes)  AS fid,
    m.geom_iieg,
    m.geom_inegi,
    m.nomgeo                                                    AS nombre,
    (g.fecha_mes || '-01')::date                                AS fecha,
    '14'::VARCHAR(2)                                            AS clave_entidad,
    g.cve_municipio                                             AS clave_municipio,
    g.bien_juridico,
    g.delito,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%arma de fuego%'
    )                                                           AS con_arma_de_fuego,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%arma blanca%'
    )                                                           AS con_arma_blanca,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%otro elemento%'
    )                                                           AS con_otro_elemento,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%no especificado%'
    )                                                           AS no_especificado,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%con violencia%'
    )                                                           AS con_violencia,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%sin violencia%'
    )                                                           AS sin_violencia,
    MAX(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'delito'
    )                                                           AS carpetas_investigacion,
    MAX(g.tasa_carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'delito'
    )                                                           AS tasa_carpetas_investigacion
FROM vw_gold_delitos_fuero_comun g
JOIN cvegeo_municipalities m ON m.cvegeo = g.cve_municipio::INTEGER
WHERE g.delito = 'Violación'
GROUP BY g.fecha_mes, g.cve_municipio, g.bien_juridico, g.delito,
         m.geom_iieg, m.geom_inegi, m.nomgeo
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS uix_vwm_violacion_nk
    ON vwm_datos_delitos_violacion_secretariado (clave_municipio, fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_violacion_fecha
    ON vwm_datos_delitos_violacion_secretariado (fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_violacion_mun
    ON vwm_datos_delitos_violacion_secretariado (clave_municipio);

-- -----------------------------------------------------------------------------
-- 5. vwm_datos_delitos_abuso_sexual_secretariado
-- -----------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS vwm_datos_delitos_abuso_sexual_secretariado AS
SELECT
    ROW_NUMBER() OVER (ORDER BY g.cve_municipio, g.fecha_mes)  AS fid,
    m.geom_iieg,
    m.geom_inegi,
    m.nomgeo                                                    AS nombre,
    (g.fecha_mes || '-01')::date                                AS fecha,
    '14'::VARCHAR(2)                                            AS clave_entidad,
    g.cve_municipio                                             AS clave_municipio,
    g.bien_juridico,
    g.delito,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%arma de fuego%'
    )                                                           AS con_arma_de_fuego,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%arma blanca%'
    )                                                           AS con_arma_blanca,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%otro elemento%'
    )                                                           AS con_otro_elemento,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%no especificado%'
    )                                                           AS no_especificado,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%con violencia%'
    )                                                           AS con_violencia,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%sin violencia%'
    )                                                           AS sin_violencia,
    MAX(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'delito'
    )                                                           AS carpetas_investigacion,
    MAX(g.tasa_carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'delito'
    )                                                           AS tasa_carpetas_investigacion
FROM vw_gold_delitos_fuero_comun g
JOIN cvegeo_municipalities m ON m.cvegeo = g.cve_municipio::INTEGER
WHERE g.delito = 'Abuso sexual'
GROUP BY g.fecha_mes, g.cve_municipio, g.bien_juridico, g.delito,
         m.geom_iieg, m.geom_inegi, m.nomgeo
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS uix_vwm_abuso_sexual_nk
    ON vwm_datos_delitos_abuso_sexual_secretariado (clave_municipio, fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_abuso_sexual_fecha
    ON vwm_datos_delitos_abuso_sexual_secretariado (fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_abuso_sexual_mun
    ON vwm_datos_delitos_abuso_sexual_secretariado (clave_municipio);

-- -----------------------------------------------------------------------------
-- 6. vwm_datos_delitos_violencia_familiar_secretariado
-- -----------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS vwm_datos_delitos_violencia_familiar_secretariado AS
SELECT
    ROW_NUMBER() OVER (ORDER BY g.cve_municipio, g.fecha_mes)  AS fid,
    m.geom_iieg,
    m.geom_inegi,
    m.nomgeo                                                    AS nombre,
    (g.fecha_mes || '-01')::date                                AS fecha,
    '14'::VARCHAR(2)                                            AS clave_entidad,
    g.cve_municipio                                             AS clave_municipio,
    g.bien_juridico,
    g.delito,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%arma de fuego%'
    )                                                           AS con_arma_de_fuego,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%arma blanca%'
    )                                                           AS con_arma_blanca,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%otro elemento%'
    )                                                           AS con_otro_elemento,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%no especificado%'
    )                                                           AS no_especificado,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%con violencia%'
    )                                                           AS con_violencia,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%sin violencia%'
    )                                                           AS sin_violencia,
    MAX(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'delito'
    )                                                           AS carpetas_investigacion,
    MAX(g.tasa_carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'delito'
    )                                                           AS tasa_carpetas_investigacion
FROM vw_gold_delitos_fuero_comun g
JOIN cvegeo_municipalities m ON m.cvegeo = g.cve_municipio::INTEGER
WHERE g.delito = 'Violencia familiar'
GROUP BY g.fecha_mes, g.cve_municipio, g.bien_juridico, g.delito,
         m.geom_iieg, m.geom_inegi, m.nomgeo
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS uix_vwm_viol_familiar_nk
    ON vwm_datos_delitos_violencia_familiar_secretariado (clave_municipio, fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_viol_familiar_fecha
    ON vwm_datos_delitos_violencia_familiar_secretariado (fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_viol_familiar_mun
    ON vwm_datos_delitos_violencia_familiar_secretariado (clave_municipio);

-- -----------------------------------------------------------------------------
-- 7. vwm_datos_delitos_violencia_genero_no_familiar_secretariado
--    Delito en gold: 'Violencia de género en todas sus modalidades distinta
--    a la violencia familiar'
-- -----------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS vwm_datos_delitos_violencia_genero_no_familiar_secretariado AS
SELECT
    ROW_NUMBER() OVER (ORDER BY g.cve_municipio, g.fecha_mes)  AS fid,
    m.geom_iieg,
    m.geom_inegi,
    m.nomgeo                                                    AS nombre,
    (g.fecha_mes || '-01')::date                                AS fecha,
    '14'::VARCHAR(2)                                            AS clave_entidad,
    g.cve_municipio                                             AS clave_municipio,
    g.bien_juridico,
    g.delito,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%arma de fuego%'
    )                                                           AS con_arma_de_fuego,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%arma blanca%'
    )                                                           AS con_arma_blanca,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%otro elemento%'
    )                                                           AS con_otro_elemento,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%no especificado%'
    )                                                           AS no_especificado,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%con violencia%'
    )                                                           AS con_violencia,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%sin violencia%'
    )                                                           AS sin_violencia,
    MAX(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'delito'
    )                                                           AS carpetas_investigacion,
    MAX(g.tasa_carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'delito'
    )                                                           AS tasa_carpetas_investigacion
FROM vw_gold_delitos_fuero_comun g
JOIN cvegeo_municipalities m ON m.cvegeo = g.cve_municipio::INTEGER
WHERE g.delito = 'Violencia de género en todas sus modalidades distinta a la violencia familiar'
GROUP BY g.fecha_mes, g.cve_municipio, g.bien_juridico, g.delito,
         m.geom_iieg, m.geom_inegi, m.nomgeo
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS uix_vwm_viol_genero_nf_nk
    ON vwm_datos_delitos_violencia_genero_no_familiar_secretariado (clave_municipio, fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_viol_genero_nf_fecha
    ON vwm_datos_delitos_violencia_genero_no_familiar_secretariado (fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_viol_genero_nf_mun
    ON vwm_datos_delitos_violencia_genero_no_familiar_secretariado (clave_municipio);

-- -----------------------------------------------------------------------------
-- 8. vwm_datos_delitos_robo_coche_cuatro_ruedas_secretariado
-- -----------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS vwm_datos_delitos_robo_coche_cuatro_ruedas_secretariado AS
SELECT
    ROW_NUMBER() OVER (ORDER BY g.cve_municipio, g.fecha_mes)  AS fid,
    m.geom_iieg,
    m.geom_inegi,
    m.nomgeo                                                    AS nombre,
    (g.fecha_mes || '-01')::date                                AS fecha,
    '14'::VARCHAR(2)                                            AS clave_entidad,
    g.cve_municipio                                             AS clave_municipio,
    g.bien_juridico,
    g.delito,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%arma de fuego%'
    )                                                           AS con_arma_de_fuego,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%arma blanca%'
    )                                                           AS con_arma_blanca,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%otro elemento%'
    )                                                           AS con_otro_elemento,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%no especificado%'
    )                                                           AS no_especificado,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%con violencia%'
    )                                                           AS con_violencia,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%sin violencia%'
    )                                                           AS sin_violencia,
    MAX(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'delito'
    )                                                           AS carpetas_investigacion,
    MAX(g.tasa_carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'delito'
    )                                                           AS tasa_carpetas_investigacion
FROM vw_gold_delitos_fuero_comun g
JOIN cvegeo_municipalities m ON m.cvegeo = g.cve_municipio::INTEGER
WHERE g.delito = 'Robo de coche de cuatro ruedas'
GROUP BY g.fecha_mes, g.cve_municipio, g.bien_juridico, g.delito,
         m.geom_iieg, m.geom_inegi, m.nomgeo
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS uix_vwm_robo_coche_4r_nk
    ON vwm_datos_delitos_robo_coche_cuatro_ruedas_secretariado (clave_municipio, fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_robo_coche_4r_fecha
    ON vwm_datos_delitos_robo_coche_cuatro_ruedas_secretariado (fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_robo_coche_4r_mun
    ON vwm_datos_delitos_robo_coche_cuatro_ruedas_secretariado (clave_municipio);

-- -----------------------------------------------------------------------------
-- 9. vwm_datos_delitos_robo_motocicleta_secretariado
-- -----------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS vwm_datos_delitos_robo_motocicleta_secretariado AS
SELECT
    ROW_NUMBER() OVER (ORDER BY g.cve_municipio, g.fecha_mes)  AS fid,
    m.geom_iieg,
    m.geom_inegi,
    m.nomgeo                                                    AS nombre,
    (g.fecha_mes || '-01')::date                                AS fecha,
    '14'::VARCHAR(2)                                            AS clave_entidad,
    g.cve_municipio                                             AS clave_municipio,
    g.bien_juridico,
    g.delito,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%arma de fuego%'
    )                                                           AS con_arma_de_fuego,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%arma blanca%'
    )                                                           AS con_arma_blanca,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%otro elemento%'
    )                                                           AS con_otro_elemento,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%no especificado%'
    )                                                           AS no_especificado,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%con violencia%'
    )                                                           AS con_violencia,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%sin violencia%'
    )                                                           AS sin_violencia,
    MAX(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'delito'
    )                                                           AS carpetas_investigacion,
    MAX(g.tasa_carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'delito'
    )                                                           AS tasa_carpetas_investigacion
FROM vw_gold_delitos_fuero_comun g
JOIN cvegeo_municipalities m ON m.cvegeo = g.cve_municipio::INTEGER
WHERE g.delito = 'Robo de motocicleta'
GROUP BY g.fecha_mes, g.cve_municipio, g.bien_juridico, g.delito,
         m.geom_iieg, m.geom_inegi, m.nomgeo
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS uix_vwm_robo_moto_nk
    ON vwm_datos_delitos_robo_motocicleta_secretariado (clave_municipio, fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_robo_moto_fecha
    ON vwm_datos_delitos_robo_motocicleta_secretariado (fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_robo_moto_mun
    ON vwm_datos_delitos_robo_motocicleta_secretariado (clave_municipio);

-- -----------------------------------------------------------------------------
-- 10. vwm_datos_delitos_robo_autopartes_secretariado
-- -----------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS vwm_datos_delitos_robo_autopartes_secretariado AS
SELECT
    ROW_NUMBER() OVER (ORDER BY g.cve_municipio, g.fecha_mes)  AS fid,
    m.geom_iieg,
    m.geom_inegi,
    m.nomgeo                                                    AS nombre,
    (g.fecha_mes || '-01')::date                                AS fecha,
    '14'::VARCHAR(2)                                            AS clave_entidad,
    g.cve_municipio                                             AS clave_municipio,
    g.bien_juridico,
    g.delito,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%arma de fuego%'
    )                                                           AS con_arma_de_fuego,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%arma blanca%'
    )                                                           AS con_arma_blanca,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%otro elemento%'
    )                                                           AS con_otro_elemento,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%no especificado%'
    )                                                           AS no_especificado,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%con violencia%'
    )                                                           AS con_violencia,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%sin violencia%'
    )                                                           AS sin_violencia,
    MAX(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'delito'
    )                                                           AS carpetas_investigacion,
    MAX(g.tasa_carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'delito'
    )                                                           AS tasa_carpetas_investigacion
FROM vw_gold_delitos_fuero_comun g
JOIN cvegeo_municipalities m ON m.cvegeo = g.cve_municipio::INTEGER
WHERE g.delito = 'Robo de autopartes'
GROUP BY g.fecha_mes, g.cve_municipio, g.bien_juridico, g.delito,
         m.geom_iieg, m.geom_inegi, m.nomgeo
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS uix_vwm_robo_autopartes_nk
    ON vwm_datos_delitos_robo_autopartes_secretariado (clave_municipio, fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_robo_autopartes_fecha
    ON vwm_datos_delitos_robo_autopartes_secretariado (fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_robo_autopartes_mun
    ON vwm_datos_delitos_robo_autopartes_secretariado (clave_municipio);

-- -----------------------------------------------------------------------------
-- 11. vwm_datos_delitos_robo_casa_habitacion_secretariado
-- -----------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS vwm_datos_delitos_robo_casa_habitacion_secretariado AS
SELECT
    ROW_NUMBER() OVER (ORDER BY g.cve_municipio, g.fecha_mes)  AS fid,
    m.geom_iieg,
    m.geom_inegi,
    m.nomgeo                                                    AS nombre,
    (g.fecha_mes || '-01')::date                                AS fecha,
    '14'::VARCHAR(2)                                            AS clave_entidad,
    g.cve_municipio                                             AS clave_municipio,
    g.bien_juridico,
    g.delito,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%arma de fuego%'
    )                                                           AS con_arma_de_fuego,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%arma blanca%'
    )                                                           AS con_arma_blanca,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%otro elemento%'
    )                                                           AS con_otro_elemento,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%no especificado%'
    )                                                           AS no_especificado,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%con violencia%'
    )                                                           AS con_violencia,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%sin violencia%'
    )                                                           AS sin_violencia,
    MAX(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'delito'
    )                                                           AS carpetas_investigacion,
    MAX(g.tasa_carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'delito'
    )                                                           AS tasa_carpetas_investigacion
FROM vw_gold_delitos_fuero_comun g
JOIN cvegeo_municipalities m ON m.cvegeo = g.cve_municipio::INTEGER
WHERE g.delito = 'Robo a casa habitación'
GROUP BY g.fecha_mes, g.cve_municipio, g.bien_juridico, g.delito,
         m.geom_iieg, m.geom_inegi, m.nomgeo
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS uix_vwm_robo_casa_nk
    ON vwm_datos_delitos_robo_casa_habitacion_secretariado (clave_municipio, fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_robo_casa_fecha
    ON vwm_datos_delitos_robo_casa_habitacion_secretariado (fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_robo_casa_mun
    ON vwm_datos_delitos_robo_casa_habitacion_secretariado (clave_municipio);

-- -----------------------------------------------------------------------------
-- 12. vwm_datos_delitos_robo_negocio_secretariado
-- -----------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS vwm_datos_delitos_robo_negocio_secretariado AS
SELECT
    ROW_NUMBER() OVER (ORDER BY g.cve_municipio, g.fecha_mes)  AS fid,
    m.geom_iieg,
    m.geom_inegi,
    m.nomgeo                                                    AS nombre,
    (g.fecha_mes || '-01')::date                                AS fecha,
    '14'::VARCHAR(2)                                            AS clave_entidad,
    g.cve_municipio                                             AS clave_municipio,
    g.bien_juridico,
    g.delito,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%arma de fuego%'
    )                                                           AS con_arma_de_fuego,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%arma blanca%'
    )                                                           AS con_arma_blanca,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%otro elemento%'
    )                                                           AS con_otro_elemento,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%no especificado%'
    )                                                           AS no_especificado,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%con violencia%'
    )                                                           AS con_violencia,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%sin violencia%'
    )                                                           AS sin_violencia,
    MAX(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'delito'
    )                                                           AS carpetas_investigacion,
    MAX(g.tasa_carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'delito'
    )                                                           AS tasa_carpetas_investigacion
FROM vw_gold_delitos_fuero_comun g
JOIN cvegeo_municipalities m ON m.cvegeo = g.cve_municipio::INTEGER
WHERE g.delito = 'Robo a negocio'
GROUP BY g.fecha_mes, g.cve_municipio, g.bien_juridico, g.delito,
         m.geom_iieg, m.geom_inegi, m.nomgeo
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS uix_vwm_robo_negocio_nk
    ON vwm_datos_delitos_robo_negocio_secretariado (clave_municipio, fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_robo_negocio_fecha
    ON vwm_datos_delitos_robo_negocio_secretariado (fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_robo_negocio_mun
    ON vwm_datos_delitos_robo_negocio_secretariado (clave_municipio);

-- -----------------------------------------------------------------------------
-- 13. vwm_datos_delitos_robo_transeunte_via_publica_secretariado
-- -----------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS vwm_datos_delitos_robo_transeunte_via_publica_secretariado AS
SELECT
    ROW_NUMBER() OVER (ORDER BY g.cve_municipio, g.fecha_mes)  AS fid,
    m.geom_iieg,
    m.geom_inegi,
    m.nomgeo                                                    AS nombre,
    (g.fecha_mes || '-01')::date                                AS fecha,
    '14'::VARCHAR(2)                                            AS clave_entidad,
    g.cve_municipio                                             AS clave_municipio,
    g.bien_juridico,
    g.delito,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%arma de fuego%'
    )                                                           AS con_arma_de_fuego,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%arma blanca%'
    )                                                           AS con_arma_blanca,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%otro elemento%'
    )                                                           AS con_otro_elemento,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%no especificado%'
    )                                                           AS no_especificado,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%con violencia%'
    )                                                           AS con_violencia,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%sin violencia%'
    )                                                           AS sin_violencia,
    MAX(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'delito'
    )                                                           AS carpetas_investigacion,
    MAX(g.tasa_carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'delito'
    )                                                           AS tasa_carpetas_investigacion
FROM vw_gold_delitos_fuero_comun g
JOIN cvegeo_municipalities m ON m.cvegeo = g.cve_municipio::INTEGER
WHERE g.delito = 'Robo a transeúnte en vía pública'
GROUP BY g.fecha_mes, g.cve_municipio, g.bien_juridico, g.delito,
         m.geom_iieg, m.geom_inegi, m.nomgeo
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS uix_vwm_robo_transeunte_nk
    ON vwm_datos_delitos_robo_transeunte_via_publica_secretariado (clave_municipio, fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_robo_transeunte_fecha
    ON vwm_datos_delitos_robo_transeunte_via_publica_secretariado (fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_robo_transeunte_mun
    ON vwm_datos_delitos_robo_transeunte_via_publica_secretariado (clave_municipio);

-- -----------------------------------------------------------------------------
-- 14. vwm_datos_delitos_robo_transportista_secretariado
-- -----------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS vwm_datos_delitos_robo_transportista_secretariado AS
SELECT
    ROW_NUMBER() OVER (ORDER BY g.cve_municipio, g.fecha_mes)  AS fid,
    m.geom_iieg,
    m.geom_inegi,
    m.nomgeo                                                    AS nombre,
    (g.fecha_mes || '-01')::date                                AS fecha,
    '14'::VARCHAR(2)                                            AS clave_entidad,
    g.cve_municipio                                             AS clave_municipio,
    g.bien_juridico,
    g.delito,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%arma de fuego%'
    )                                                           AS con_arma_de_fuego,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%arma blanca%'
    )                                                           AS con_arma_blanca,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%otro elemento%'
    )                                                           AS con_otro_elemento,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%no especificado%'
    )                                                           AS no_especificado,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%con violencia%'
    )                                                           AS con_violencia,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%sin violencia%'
    )                                                           AS sin_violencia,
    MAX(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'delito'
    )                                                           AS carpetas_investigacion,
    MAX(g.tasa_carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'delito'
    )                                                           AS tasa_carpetas_investigacion
FROM vw_gold_delitos_fuero_comun g
JOIN cvegeo_municipalities m ON m.cvegeo = g.cve_municipio::INTEGER
WHERE g.delito = 'Robo a transportista'
GROUP BY g.fecha_mes, g.cve_municipio, g.bien_juridico, g.delito,
         m.geom_iieg, m.geom_inegi, m.nomgeo
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS uix_vwm_robo_transportista_nk
    ON vwm_datos_delitos_robo_transportista_secretariado (clave_municipio, fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_robo_transportista_fecha
    ON vwm_datos_delitos_robo_transportista_secretariado (fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_robo_transportista_mun
    ON vwm_datos_delitos_robo_transportista_secretariado (clave_municipio);

-- -----------------------------------------------------------------------------
-- 15. vwm_datos_delitos_robo_institucion_bancaria_secretariado
-- -----------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS vwm_datos_delitos_robo_institucion_bancaria_secretariado AS
SELECT
    ROW_NUMBER() OVER (ORDER BY g.cve_municipio, g.fecha_mes)  AS fid,
    m.geom_iieg,
    m.geom_inegi,
    m.nomgeo                                                    AS nombre,
    (g.fecha_mes || '-01')::date                                AS fecha,
    '14'::VARCHAR(2)                                            AS clave_entidad,
    g.cve_municipio                                             AS clave_municipio,
    g.bien_juridico,
    g.delito,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%arma de fuego%'
    )                                                           AS con_arma_de_fuego,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%arma blanca%'
    )                                                           AS con_arma_blanca,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%otro elemento%'
    )                                                           AS con_otro_elemento,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%no especificado%'
    )                                                           AS no_especificado,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%con violencia%'
    )                                                           AS con_violencia,
    SUM(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'modalidad'
          AND g.modalidad ILIKE '%sin violencia%'
    )                                                           AS sin_violencia,
    MAX(g.carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'delito'
    )                                                           AS carpetas_investigacion,
    MAX(g.tasa_carpetas_investigacion) FILTER (
        WHERE g.nivel_jerarquico = 'delito'
    )                                                           AS tasa_carpetas_investigacion
FROM vw_gold_delitos_fuero_comun g
JOIN cvegeo_municipalities m ON m.cvegeo = g.cve_municipio::INTEGER
WHERE g.delito = 'Robo a institución bancaria'
GROUP BY g.fecha_mes, g.cve_municipio, g.bien_juridico, g.delito,
         m.geom_iieg, m.geom_inegi, m.nomgeo
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS uix_vwm_robo_banco_nk
    ON vwm_datos_delitos_robo_institucion_bancaria_secretariado (clave_municipio, fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_robo_banco_fecha
    ON vwm_datos_delitos_robo_institucion_bancaria_secretariado (fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_robo_banco_mun
    ON vwm_datos_delitos_robo_institucion_bancaria_secretariado (clave_municipio);

-- =============================================================================
-- vwm_feminicidios
-- Feminicidios del Secretariado reubicados en desarrollo social por su uso
-- como indicador de igualdad de género. Conserva nivel_jerarquico + modalidad
-- en lugar del pivot de armas, para permitir desagregación completa.
-- =============================================================================
CREATE MATERIALIZED VIEW IF NOT EXISTS vwm_feminicidios AS
SELECT
    ROW_NUMBER() OVER (
        ORDER BY g.cve_municipio, g.fecha_mes, g.nivel_jerarquico,
                 COALESCE(g.modalidad, '')
    )                                                           AS fid,
    m.geom_iieg,
    m.geom_inegi,
    m.nomgeo                                                    AS nombre,
    (g.fecha_mes || '-01')::date                                AS fecha,
    '14'::VARCHAR(2)                                            AS clave_entidad,
    g.cve_municipio                                             AS clave_municipio,
    g.nivel_jerarquico,
    g.modalidad,
    g.carpetas_investigacion,
    g.tasa_carpetas_investigacion
FROM vw_gold_delitos_fuero_comun g
JOIN cvegeo_municipalities m ON m.cvegeo = g.cve_municipio::INTEGER
WHERE g.delito = 'Feminicidio'
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS uix_vwm_feminicidios_nk
    ON vwm_feminicidios (
        clave_municipio,
        fecha,
        nivel_jerarquico,
        COALESCE(modalidad, '')
    );
CREATE INDEX IF NOT EXISTS ix_vwm_feminicidios_fecha
    ON vwm_feminicidios (fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_feminicidios_mun
    ON vwm_feminicidios (clave_municipio);
