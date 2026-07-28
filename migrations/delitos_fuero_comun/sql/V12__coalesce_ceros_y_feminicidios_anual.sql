-- =============================================================================
-- V12__coalesce_ceros_y_feminicidios_anual.sql  |  Pipeline: delitos_fuero_comun
-- Dos correcciones encontradas al comparar datos contra proxmox:
--
-- 1. vw_gold_delitos_fuero_comun descarta filas con conteo = 0, así que el
--    grid completo de V10 deja NULL donde proxmox escribe 0 explícito (su
--    tabla origen sí materializa ceros para cada municipio/mes/delito). Se
--    envuelve carpetas_investigacion, tasa_carpetas_investigacion y las
--    columnas pivote en COALESCE(..., 0). bien_juridico/delito también se
--    completan con un CTE "meta" (constantes por delito, no dependen de si
--    hubo incidentes) para que no queden NULL en meses sin dato.
--
-- 2. vwm_feminicidios en proxmox (desarrollo_social.feminicidios) es un
--    indicador ANUAL (fecha = 1 de enero de cada año, 2015-2025), no mensual
--    como el resto de las vistas del Secretariado. Se rediseña con grid
--    municipio x año (años cerrados, anteriores al año en curso) y se
--    recalcula la tasa con población CONAPO anual en vez de sumar tasas
--    mensuales.
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
-- GRUPO ARMA
-- =============================================================================

CREATE MATERIALIZED VIEW vwm_datos_delitos_homicidio_doloso_secretariado AS
WITH meta AS (
    SELECT DISTINCT bien_juridico, delito FROM vw_gold_delitos_fuero_comun WHERE delito = 'Homicidio doloso' LIMIT 1
),
datos AS (
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
    COALESCE(datos.bien_juridico, meta.bien_juridico) AS bien_juridico,
    COALESCE(datos.delito, meta.delito)               AS delito,
    COALESCE(datos.con_arma_de_fuego, 0)              AS con_arma_de_fuego,
    COALESCE(datos.con_arma_blanca, 0)                AS con_arma_blanca,
    COALESCE(datos.con_otro_elemento, 0)              AS con_otro_elemento,
    COALESCE(datos.no_especificado, 0)                AS no_especificado,
    COALESCE(datos.carpetas_investigacion, 0)         AS carpetas_investigacion,
    COALESCE(datos.tasa_carpetas_investigacion, 0)    AS tasa_carpetas_investigacion
FROM base
CROSS JOIN meta
LEFT JOIN datos ON base.clave_municipio = datos.cve_municipio AND base.fecha_mes = datos.fecha_mes
WITH NO DATA;

CREATE UNIQUE INDEX uix_vwm_homicidio_doloso_nk ON vwm_datos_delitos_homicidio_doloso_secretariado (clave_municipio, fecha);
CREATE INDEX ix_vwm_homicidio_doloso_fecha ON vwm_datos_delitos_homicidio_doloso_secretariado (fecha);
CREATE INDEX ix_vwm_homicidio_doloso_mun ON vwm_datos_delitos_homicidio_doloso_secretariado (clave_municipio);

CREATE MATERIALIZED VIEW vwm_datos_delitos_feminicidio_secretariado AS
WITH meta AS (
    SELECT DISTINCT bien_juridico, delito FROM vw_gold_delitos_fuero_comun WHERE delito = 'Feminicidio' LIMIT 1
),
datos AS (
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
    COALESCE(datos.bien_juridico, meta.bien_juridico) AS bien_juridico,
    COALESCE(datos.delito, meta.delito)               AS delito,
    COALESCE(datos.con_arma_de_fuego, 0)              AS con_arma_de_fuego,
    COALESCE(datos.con_arma_blanca, 0)                AS con_arma_blanca,
    COALESCE(datos.con_otro_elemento, 0)              AS con_otro_elemento,
    COALESCE(datos.no_especificado, 0)                AS no_especificado,
    COALESCE(datos.carpetas_investigacion, 0)         AS carpetas_investigacion,
    COALESCE(datos.tasa_carpetas_investigacion, 0)    AS tasa_carpetas_investigacion
FROM base
CROSS JOIN meta
LEFT JOIN datos ON base.clave_municipio = datos.cve_municipio AND base.fecha_mes = datos.fecha_mes
WITH NO DATA;

CREATE UNIQUE INDEX uix_vwm_feminicidio_sec_nk ON vwm_datos_delitos_feminicidio_secretariado (clave_municipio, fecha);
CREATE INDEX ix_vwm_feminicidio_sec_fecha ON vwm_datos_delitos_feminicidio_secretariado (fecha);
CREATE INDEX ix_vwm_feminicidio_sec_mun ON vwm_datos_delitos_feminicidio_secretariado (clave_municipio);

CREATE MATERIALIZED VIEW vwm_datos_delitos_lesiones_dolosas_secretariado AS
WITH meta AS (
    SELECT DISTINCT bien_juridico, delito FROM vw_gold_delitos_fuero_comun WHERE delito = 'Lesiones dolosas' LIMIT 1
),
datos AS (
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
    COALESCE(datos.bien_juridico, meta.bien_juridico) AS bien_juridico,
    COALESCE(datos.delito, meta.delito)               AS delito,
    COALESCE(datos.con_arma_de_fuego, 0)              AS con_arma_de_fuego,
    COALESCE(datos.con_arma_blanca, 0)                AS con_arma_blanca,
    COALESCE(datos.con_otro_elemento, 0)              AS con_otro_elemento,
    COALESCE(datos.no_especificado, 0)                AS no_especificado,
    COALESCE(datos.carpetas_investigacion, 0)         AS carpetas_investigacion,
    COALESCE(datos.tasa_carpetas_investigacion, 0)    AS tasa_carpetas_investigacion
FROM base
CROSS JOIN meta
LEFT JOIN datos ON base.clave_municipio = datos.cve_municipio AND base.fecha_mes = datos.fecha_mes
WITH NO DATA;

CREATE UNIQUE INDEX uix_vwm_lesiones_dolosas_nk ON vwm_datos_delitos_lesiones_dolosas_secretariado (clave_municipio, fecha);
CREATE INDEX ix_vwm_lesiones_dolosas_fecha ON vwm_datos_delitos_lesiones_dolosas_secretariado (fecha);
CREATE INDEX ix_vwm_lesiones_dolosas_mun ON vwm_datos_delitos_lesiones_dolosas_secretariado (clave_municipio);

-- =============================================================================
-- GRUPO GÉNERO
-- =============================================================================

CREATE MATERIALIZED VIEW vwm_datos_delitos_violacion_secretariado AS
WITH meta AS (
    SELECT DISTINCT bien_juridico::VARCHAR(100) AS bien_juridico, delito::VARCHAR(120) AS delito
    FROM vw_gold_delitos_fuero_comun WHERE delito = 'Violación' LIMIT 1
),
datos AS (
    SELECT
        g.cve_municipio,
        g.fecha_mes,
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
    'delito'::VARCHAR(30)                             AS nivel_jerarquico,
    COALESCE(datos.bien_juridico, meta.bien_juridico) AS bien_juridico,
    COALESCE(datos.delito, meta.delito)               AS delito,
    datos.modalidad,
    COALESCE(datos.carpetas_investigacion, 0)         AS carpetas_investigacion,
    COALESCE(datos.tasa_carpetas_investigacion, 0)    AS tasa_carpetas_investigacion
FROM base
CROSS JOIN meta
LEFT JOIN datos ON base.clave_municipio = datos.cve_municipio AND base.fecha_mes = datos.fecha_mes
WITH NO DATA;

CREATE UNIQUE INDEX uix_vwm_violacion_nk ON vwm_datos_delitos_violacion_secretariado (clave_municipio, fecha);
CREATE INDEX ix_vwm_violacion_fecha ON vwm_datos_delitos_violacion_secretariado (fecha);
CREATE INDEX ix_vwm_violacion_mun ON vwm_datos_delitos_violacion_secretariado (clave_municipio);

CREATE MATERIALIZED VIEW vwm_datos_delitos_abuso_sexual_secretariado AS
WITH meta AS (
    SELECT DISTINCT bien_juridico::VARCHAR(100) AS bien_juridico, delito::VARCHAR(120) AS delito
    FROM vw_gold_delitos_fuero_comun WHERE delito = 'Abuso sexual' LIMIT 1
),
datos AS (
    SELECT
        g.cve_municipio,
        g.fecha_mes,
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
    'delito'::VARCHAR(30)                             AS nivel_jerarquico,
    COALESCE(datos.bien_juridico, meta.bien_juridico) AS bien_juridico,
    COALESCE(datos.delito, meta.delito)               AS delito,
    datos.modalidad,
    COALESCE(datos.carpetas_investigacion, 0)         AS carpetas_investigacion,
    COALESCE(datos.tasa_carpetas_investigacion, 0)    AS tasa_carpetas_investigacion
FROM base
CROSS JOIN meta
LEFT JOIN datos ON base.clave_municipio = datos.cve_municipio AND base.fecha_mes = datos.fecha_mes
WITH NO DATA;

CREATE UNIQUE INDEX uix_vwm_abuso_sexual_nk ON vwm_datos_delitos_abuso_sexual_secretariado (clave_municipio, fecha);
CREATE INDEX ix_vwm_abuso_sexual_fecha ON vwm_datos_delitos_abuso_sexual_secretariado (fecha);
CREATE INDEX ix_vwm_abuso_sexual_mun ON vwm_datos_delitos_abuso_sexual_secretariado (clave_municipio);

CREATE MATERIALIZED VIEW vwm_datos_delitos_violencia_familiar_secretariado AS
WITH meta AS (
    SELECT DISTINCT bien_juridico::VARCHAR(100) AS bien_juridico, delito::VARCHAR(120) AS delito
    FROM vw_gold_delitos_fuero_comun WHERE delito = 'Violencia familiar' LIMIT 1
),
datos AS (
    SELECT
        g.cve_municipio,
        g.fecha_mes,
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
    'delito'::VARCHAR(30)                             AS nivel_jerarquico,
    COALESCE(datos.bien_juridico, meta.bien_juridico) AS bien_juridico,
    COALESCE(datos.delito, meta.delito)               AS delito,
    datos.modalidad,
    COALESCE(datos.carpetas_investigacion, 0)         AS carpetas_investigacion,
    COALESCE(datos.tasa_carpetas_investigacion, 0)    AS tasa_carpetas_investigacion
FROM base
CROSS JOIN meta
LEFT JOIN datos ON base.clave_municipio = datos.cve_municipio AND base.fecha_mes = datos.fecha_mes
WITH NO DATA;

CREATE UNIQUE INDEX uix_vwm_viol_familiar_nk ON vwm_datos_delitos_violencia_familiar_secretariado (clave_municipio, fecha);
CREATE INDEX ix_vwm_viol_familiar_fecha ON vwm_datos_delitos_violencia_familiar_secretariado (fecha);
CREATE INDEX ix_vwm_viol_familiar_mun ON vwm_datos_delitos_violencia_familiar_secretariado (clave_municipio);

-- -----------------------------------------------------------------------------
-- vwm_datos_delitos_violencia_genero_no_familiar_secretariado
-- Jalisco no tiene ninguna fila en gold para este delito (0 carpetas en todo
-- 2015-2026), así que "meta" no puede salir de vw_gold_delitos_fuero_comun
-- como en las demás vistas: se deriva directo del catálogo + staging (que sí
-- tiene 1,375 filas Jalisco con conteo 0, ver investigación en el plan).
-- -----------------------------------------------------------------------------
CREATE MATERIALIZED VIEW vwm_datos_delitos_violencia_genero_no_familiar_secretariado AS
WITH meta AS (
    SELECT DISTINCT
        bja.bien_juridico_afectado::VARCHAR(100) AS bien_juridico,
        td.tipo_delito::VARCHAR(120)             AS delito
    FROM stg_delitos_fuero_comun_2015_2025 s
    JOIN cat_bien_juridico_afectado bja ON s.bien_juridico_afectado_id = bja.id
    JOIN cat_tipo_delito td ON s.tipo_delito_id = td.id
    WHERE td.tipo_delito ILIKE '%violencia de g_nero%distinta%'
    LIMIT 1
),
datos AS (
    SELECT
        g.cve_municipio,
        g.fecha_mes,
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
    'delito'::VARCHAR(30)                             AS nivel_jerarquico,
    COALESCE(datos.bien_juridico, meta.bien_juridico) AS bien_juridico,
    COALESCE(datos.delito, meta.delito)               AS delito,
    datos.modalidad,
    COALESCE(datos.carpetas_investigacion, 0)         AS carpetas_investigacion,
    COALESCE(datos.tasa_carpetas_investigacion, 0)    AS tasa_carpetas_investigacion
FROM base
CROSS JOIN meta
LEFT JOIN datos ON base.clave_municipio = datos.cve_municipio AND base.fecha_mes = datos.fecha_mes
WITH NO DATA;

CREATE UNIQUE INDEX uix_vwm_viol_genero_nf_nk ON vwm_datos_delitos_violencia_genero_no_familiar_secretariado (clave_municipio, fecha);
CREATE INDEX ix_vwm_viol_genero_nf_fecha ON vwm_datos_delitos_violencia_genero_no_familiar_secretariado (fecha);
CREATE INDEX ix_vwm_viol_genero_nf_mun ON vwm_datos_delitos_violencia_genero_no_familiar_secretariado (clave_municipio);

-- =============================================================================
-- GRUPO VIOLENCIA
-- =============================================================================

CREATE MATERIALIZED VIEW vwm_datos_delitos_robo_coche_cuatro_ruedas_secretariado AS
WITH meta AS (
    SELECT DISTINCT bien_juridico, delito FROM vw_gold_delitos_fuero_comun WHERE delito = 'Robo de coche de cuatro ruedas' LIMIT 1
),
datos AS (
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
    COALESCE(datos.bien_juridico, meta.bien_juridico) AS bien_juridico,
    COALESCE(datos.delito, meta.delito)               AS delito,
    COALESCE(datos.con_violencia, 0)                  AS con_violencia,
    COALESCE(datos.sin_violencia, 0)                  AS sin_violencia,
    COALESCE(datos.carpetas_investigacion, 0)         AS carpetas_investigacion,
    COALESCE(datos.tasa_carpetas_investigacion, 0)    AS tasa_carpetas_investigacion
FROM base
CROSS JOIN meta
LEFT JOIN datos ON base.clave_municipio = datos.cve_municipio AND base.fecha_mes = datos.fecha_mes
WITH NO DATA;

CREATE UNIQUE INDEX uix_vwm_robo_coche_4r_nk ON vwm_datos_delitos_robo_coche_cuatro_ruedas_secretariado (clave_municipio, fecha);
CREATE INDEX ix_vwm_robo_coche_4r_fecha ON vwm_datos_delitos_robo_coche_cuatro_ruedas_secretariado (fecha);
CREATE INDEX ix_vwm_robo_coche_4r_mun ON vwm_datos_delitos_robo_coche_cuatro_ruedas_secretariado (clave_municipio);

CREATE MATERIALIZED VIEW vwm_datos_delitos_robo_motocicleta_secretariado AS
WITH meta AS (
    SELECT DISTINCT bien_juridico, delito FROM vw_gold_delitos_fuero_comun WHERE delito = 'Robo de motocicleta' LIMIT 1
),
datos AS (
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
    COALESCE(datos.bien_juridico, meta.bien_juridico) AS bien_juridico,
    COALESCE(datos.delito, meta.delito)               AS delito,
    COALESCE(datos.con_violencia, 0)                  AS con_violencia,
    COALESCE(datos.sin_violencia, 0)                  AS sin_violencia,
    COALESCE(datos.carpetas_investigacion, 0)         AS carpetas_investigacion,
    COALESCE(datos.tasa_carpetas_investigacion, 0)    AS tasa_carpetas_investigacion
FROM base
CROSS JOIN meta
LEFT JOIN datos ON base.clave_municipio = datos.cve_municipio AND base.fecha_mes = datos.fecha_mes
WITH NO DATA;

CREATE UNIQUE INDEX uix_vwm_robo_moto_nk ON vwm_datos_delitos_robo_motocicleta_secretariado (clave_municipio, fecha);
CREATE INDEX ix_vwm_robo_moto_fecha ON vwm_datos_delitos_robo_motocicleta_secretariado (fecha);
CREATE INDEX ix_vwm_robo_moto_mun ON vwm_datos_delitos_robo_motocicleta_secretariado (clave_municipio);

CREATE MATERIALIZED VIEW vwm_datos_delitos_robo_autopartes_secretariado AS
WITH meta AS (
    SELECT DISTINCT bien_juridico, delito FROM vw_gold_delitos_fuero_comun WHERE delito = 'Robo de autopartes' LIMIT 1
),
datos AS (
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
    COALESCE(datos.bien_juridico, meta.bien_juridico) AS bien_juridico,
    COALESCE(datos.delito, meta.delito)               AS delito,
    COALESCE(datos.con_violencia, 0)                  AS con_violencia,
    COALESCE(datos.sin_violencia, 0)                  AS sin_violencia,
    COALESCE(datos.carpetas_investigacion, 0)         AS carpetas_investigacion,
    COALESCE(datos.tasa_carpetas_investigacion, 0)    AS tasa_carpetas_investigacion
FROM base
CROSS JOIN meta
LEFT JOIN datos ON base.clave_municipio = datos.cve_municipio AND base.fecha_mes = datos.fecha_mes
WITH NO DATA;

CREATE UNIQUE INDEX uix_vwm_robo_autopartes_nk ON vwm_datos_delitos_robo_autopartes_secretariado (clave_municipio, fecha);
CREATE INDEX ix_vwm_robo_autopartes_fecha ON vwm_datos_delitos_robo_autopartes_secretariado (fecha);
CREATE INDEX ix_vwm_robo_autopartes_mun ON vwm_datos_delitos_robo_autopartes_secretariado (clave_municipio);

CREATE MATERIALIZED VIEW vwm_datos_delitos_robo_casa_habitacion_secretariado AS
WITH meta AS (
    SELECT DISTINCT bien_juridico, delito FROM vw_gold_delitos_fuero_comun WHERE delito = 'Robo a casa habitación' LIMIT 1
),
datos AS (
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
    COALESCE(datos.bien_juridico, meta.bien_juridico) AS bien_juridico,
    COALESCE(datos.delito, meta.delito)               AS delito,
    COALESCE(datos.con_violencia, 0)                  AS con_violencia,
    COALESCE(datos.sin_violencia, 0)                  AS sin_violencia,
    COALESCE(datos.carpetas_investigacion, 0)         AS carpetas_investigacion,
    COALESCE(datos.tasa_carpetas_investigacion, 0)    AS tasa_carpetas_investigacion
FROM base
CROSS JOIN meta
LEFT JOIN datos ON base.clave_municipio = datos.cve_municipio AND base.fecha_mes = datos.fecha_mes
WITH NO DATA;

CREATE UNIQUE INDEX uix_vwm_robo_casa_nk ON vwm_datos_delitos_robo_casa_habitacion_secretariado (clave_municipio, fecha);
CREATE INDEX ix_vwm_robo_casa_fecha ON vwm_datos_delitos_robo_casa_habitacion_secretariado (fecha);
CREATE INDEX ix_vwm_robo_casa_mun ON vwm_datos_delitos_robo_casa_habitacion_secretariado (clave_municipio);

CREATE MATERIALIZED VIEW vwm_datos_delitos_robo_negocio_secretariado AS
WITH meta AS (
    SELECT DISTINCT bien_juridico, delito FROM vw_gold_delitos_fuero_comun WHERE delito = 'Robo a negocio' LIMIT 1
),
datos AS (
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
    COALESCE(datos.bien_juridico, meta.bien_juridico) AS bien_juridico,
    COALESCE(datos.delito, meta.delito)               AS delito,
    COALESCE(datos.con_violencia, 0)                  AS con_violencia,
    COALESCE(datos.sin_violencia, 0)                  AS sin_violencia,
    COALESCE(datos.carpetas_investigacion, 0)         AS carpetas_investigacion,
    COALESCE(datos.tasa_carpetas_investigacion, 0)    AS tasa_carpetas_investigacion
FROM base
CROSS JOIN meta
LEFT JOIN datos ON base.clave_municipio = datos.cve_municipio AND base.fecha_mes = datos.fecha_mes
WITH NO DATA;

CREATE UNIQUE INDEX uix_vwm_robo_negocio_nk ON vwm_datos_delitos_robo_negocio_secretariado (clave_municipio, fecha);
CREATE INDEX ix_vwm_robo_negocio_fecha ON vwm_datos_delitos_robo_negocio_secretariado (fecha);
CREATE INDEX ix_vwm_robo_negocio_mun ON vwm_datos_delitos_robo_negocio_secretariado (clave_municipio);

CREATE MATERIALIZED VIEW vwm_datos_delitos_robo_transeunte_via_publica_secretariado AS
WITH meta AS (
    SELECT DISTINCT bien_juridico, delito FROM vw_gold_delitos_fuero_comun WHERE delito = 'Robo a transeúnte en vía pública' LIMIT 1
),
datos AS (
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
    COALESCE(datos.bien_juridico, meta.bien_juridico) AS bien_juridico,
    COALESCE(datos.delito, meta.delito)               AS delito,
    COALESCE(datos.con_violencia, 0)                  AS con_violencia,
    COALESCE(datos.sin_violencia, 0)                  AS sin_violencia,
    COALESCE(datos.carpetas_investigacion, 0)         AS carpetas_investigacion,
    COALESCE(datos.tasa_carpetas_investigacion, 0)    AS tasa_carpetas_investigacion
FROM base
CROSS JOIN meta
LEFT JOIN datos ON base.clave_municipio = datos.cve_municipio AND base.fecha_mes = datos.fecha_mes
WITH NO DATA;

CREATE UNIQUE INDEX uix_vwm_robo_transeunte_nk ON vwm_datos_delitos_robo_transeunte_via_publica_secretariado (clave_municipio, fecha);
CREATE INDEX ix_vwm_robo_transeunte_fecha ON vwm_datos_delitos_robo_transeunte_via_publica_secretariado (fecha);
CREATE INDEX ix_vwm_robo_transeunte_mun ON vwm_datos_delitos_robo_transeunte_via_publica_secretariado (clave_municipio);

CREATE MATERIALIZED VIEW vwm_datos_delitos_robo_transportista_secretariado AS
WITH meta AS (
    SELECT DISTINCT bien_juridico, delito FROM vw_gold_delitos_fuero_comun WHERE delito = 'Robo a transportista' LIMIT 1
),
datos AS (
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
    COALESCE(datos.bien_juridico, meta.bien_juridico) AS bien_juridico,
    COALESCE(datos.delito, meta.delito)               AS delito,
    COALESCE(datos.con_violencia, 0)                  AS con_violencia,
    COALESCE(datos.sin_violencia, 0)                  AS sin_violencia,
    COALESCE(datos.carpetas_investigacion, 0)         AS carpetas_investigacion,
    COALESCE(datos.tasa_carpetas_investigacion, 0)    AS tasa_carpetas_investigacion
FROM base
CROSS JOIN meta
LEFT JOIN datos ON base.clave_municipio = datos.cve_municipio AND base.fecha_mes = datos.fecha_mes
WITH NO DATA;

CREATE UNIQUE INDEX uix_vwm_robo_transportista_nk ON vwm_datos_delitos_robo_transportista_secretariado (clave_municipio, fecha);
CREATE INDEX ix_vwm_robo_transportista_fecha ON vwm_datos_delitos_robo_transportista_secretariado (fecha);
CREATE INDEX ix_vwm_robo_transportista_mun ON vwm_datos_delitos_robo_transportista_secretariado (clave_municipio);

CREATE MATERIALIZED VIEW vwm_datos_delitos_robo_institucion_bancaria_secretariado AS
WITH meta AS (
    SELECT DISTINCT bien_juridico, delito FROM vw_gold_delitos_fuero_comun WHERE delito = 'Robo a institución bancaria' LIMIT 1
),
datos AS (
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
    COALESCE(datos.bien_juridico, meta.bien_juridico) AS bien_juridico,
    COALESCE(datos.delito, meta.delito)               AS delito,
    COALESCE(datos.con_violencia, 0)                  AS con_violencia,
    COALESCE(datos.sin_violencia, 0)                  AS sin_violencia,
    COALESCE(datos.carpetas_investigacion, 0)         AS carpetas_investigacion,
    COALESCE(datos.tasa_carpetas_investigacion, 0)    AS tasa_carpetas_investigacion
FROM base
CROSS JOIN meta
LEFT JOIN datos ON base.clave_municipio = datos.cve_municipio AND base.fecha_mes = datos.fecha_mes
WITH NO DATA;

CREATE UNIQUE INDEX uix_vwm_robo_banco_nk ON vwm_datos_delitos_robo_institucion_bancaria_secretariado (clave_municipio, fecha);
CREATE INDEX ix_vwm_robo_banco_fecha ON vwm_datos_delitos_robo_institucion_bancaria_secretariado (fecha);
CREATE INDEX ix_vwm_robo_banco_mun ON vwm_datos_delitos_robo_institucion_bancaria_secretariado (clave_municipio);

-- =============================================================================
-- vwm_feminicidios: rediseño a grano anual (municipio x año cerrado),
-- tasa recalculada con población CONAPO anual.
-- =============================================================================
CREATE MATERIALIZED VIEW vwm_feminicidios AS
WITH datos AS (
    SELECT
        g.cve_municipio,
        g.fecha_anio,
        SUM(g.carpetas_investigacion)::integer AS carpetas_investigacion
    FROM vw_gold_delitos_fuero_comun g
    WHERE g.delito = 'Feminicidio' AND g.nivel_jerarquico = 'delito'
    GROUP BY g.cve_municipio, g.fecha_anio
),
base AS (
    SELECT
        LPAD(m.cvegeo::text, 5, '0')::VARCHAR(5) AS clave_municipio,
        m.nomgeo,
        m.geom_iieg,
        m.geom_inegi,
        f.fecha_anio
    FROM cvegeo_municipalities m
    CROSS JOIN (
        SELECT DISTINCT fecha_anio
        FROM vw_gold_delitos_fuero_comun
        WHERE fecha_anio < EXTRACT(YEAR FROM CURRENT_DATE)
    ) f
    WHERE m.cve_ent = 14
)
SELECT
    base.geom_iieg,
    base.geom_inegi,
    base.nomgeo::VARCHAR(254)                    AS nombre,
    make_date(base.fecha_anio::int, 1, 1)         AS fecha,
    '14'::CHARACTER(2)                            AS clave_entidad,
    base.clave_municipio,
    'delito'::VARCHAR(30)                         AS nivel_jerarquico,
    NULL::VARCHAR(100)                            AS modalidad,
    COALESCE(datos.carpetas_investigacion, 0)     AS carpetas_investigacion,
    CASE
        WHEN p.pob_mit_mun IS NULL OR p.pob_mit_mun = 0 THEN NULL
        ELSE ROUND(100000.0 * COALESCE(datos.carpetas_investigacion, 0) / p.pob_mit_mun, 2)
    END::numeric(12, 2)                           AS tasa_carpetas_investigacion
FROM base
LEFT JOIN datos ON base.clave_municipio = datos.cve_municipio AND base.fecha_anio = datos.fecha_anio
LEFT JOIN conapo_indicadores_demograficos p
    ON  p.municipio_id = base.clave_municipio::integer
    AND p.anio         = base.fecha_anio::int
WITH NO DATA;

CREATE UNIQUE INDEX uix_vwm_feminicidios_nk ON vwm_feminicidios (clave_municipio, fecha);
CREATE INDEX ix_vwm_feminicidios_fecha ON vwm_feminicidios (fecha);
CREATE INDEX ix_vwm_feminicidios_mun ON vwm_feminicidios (clave_municipio);
