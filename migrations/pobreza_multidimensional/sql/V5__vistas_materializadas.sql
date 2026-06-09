-- =======================================================================
-- V5__vistas_materializadas.sql  |  Pipeline: pobreza_multidimensional
-- Vistas materializadas por indicador de pobreza — Jalisco (cve_ent = 14).
-- Fuente: stg_pobreza_multidimensional_datos  |  Años: 2010, 2015, 2020
-- =======================================================================

-- ---------------------------------------------------------------------------
-- 1. pobreza
-- Personas en situación de pobreza (ingresos + al menos 1 carencia)
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS pobreza AS
SELECT
    ROW_NUMBER() OVER ()::bigint             AS fid,
    g.geometry                               AS geom_inegi,
    d.cve_mun                                AS clave_municipio,
    g.geometry                               AS geom_iieg,
    (d.anio::text || '-01-01')::date         AS fecha,
    d.nombre_municipio                       AS nombre,
    d.cat_entidad_id                         AS clave_entidad,
    d.pobreza_porcentaje                     AS pobreza,
    d.pobreza_personas                       AS personas,
    d.pobreza_promedio                       AS carencias_promedio
FROM public.stg_pobreza_multidimensional_datos d
JOIN cvegeo_municipalities g
    ON LPAD(g.cvegeo::text, 5, '0') = d.cve_mun
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_pobreza_fid
    ON pobreza (fid);

-- ---------------------------------------------------------------------------
-- 2. pobreza_extrema
-- Personas en pobreza extrema (ingresos + 3 o más carencias)
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS pobreza_extrema AS
SELECT
    ROW_NUMBER() OVER ()::bigint             AS fid,
    g.geometry                               AS geom_inegi,
    d.cve_mun                                AS clave_municipio,
    g.geometry                               AS geom_iieg,
    (d.anio::text || '-01-01')::date         AS fecha,
    d.nombre_municipio                       AS nombre,
    d.cat_entidad_id                         AS clave_entidad,
    d.pobreza_ext_personas                   AS personas,
    d.pobreza_ext_porcentaje                 AS porcentaje,
    d.pobreza_ext_promedio                   AS carencias_promedio
FROM public.stg_pobreza_multidimensional_datos d
JOIN cvegeo_municipalities g
    ON LPAD(g.cvegeo::text, 5, '0') = d.cve_mun
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_pobreza_extrema_fid
    ON pobreza_extrema (fid);

-- ---------------------------------------------------------------------------
-- 3. pobreza_moderada
-- Personas en pobreza moderada (pobreza no extrema)
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS pobreza_moderada AS
SELECT
    ROW_NUMBER() OVER ()::bigint             AS fid,
    g.geometry                               AS geom_inegi,
    d.cve_mun                                AS clave_municipio,
    g.geometry                               AS geom_iieg,
    (d.anio::text || '-01-01')::date         AS fecha,
    d.nombre_municipio                       AS nombre,
    d.cat_entidad_id                         AS clave_entidad,
    d.pobreza_mod_personas                   AS personas,
    d.pobreza_mod_porcentaje                 AS porcentaje,
    d.pobreza_mod_promedio                   AS carencias_promedio
FROM public.stg_pobreza_multidimensional_datos d
JOIN cvegeo_municipalities g
    ON LPAD(g.cvegeo::text, 5, '0') = d.cve_mun
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_pobreza_moderada_fid
    ON pobreza_moderada (fid);

-- ---------------------------------------------------------------------------
-- 4. poblacion_ingreso_inferior_linea_pobreza_ingresos
-- Personas con ingreso menor a la línea de pobreza por ingresos
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS poblacion_ingreso_inferior_linea_pobreza_ingresos AS
SELECT
    ROW_NUMBER() OVER ()::bigint             AS fid,
    g.geometry                               AS geom_inegi,
    d.nombre_municipio                       AS nombre,
    (d.anio::text || '-01-01')::date         AS fecha,
    d.cat_entidad_id                         AS clave_entidad,
    d.cve_mun                                AS clave_municipio,
    g.geometry                               AS geom_iieg,
    d.lpi_personas                           AS personas,
    d.lpi_porcentaje                         AS porcentaje,
    d.lpi_promedio                           AS carencias_promedio
FROM public.stg_pobreza_multidimensional_datos d
JOIN cvegeo_municipalities g
    ON LPAD(g.cvegeo::text, 5, '0') = d.cve_mun
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_lpi_fid
    ON poblacion_ingreso_inferior_linea_pobreza_ingresos (fid);

-- ---------------------------------------------------------------------------
-- 5. poblacion_ingreso_inferior_linea_pobreza_extrema_ingresos
-- Personas con ingreso menor a la línea de pobreza extrema por ingresos
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS poblacion_ingreso_inferior_linea_pobreza_extrema_ingresos AS
SELECT
    ROW_NUMBER() OVER ()::bigint             AS fid,
    g.geometry                               AS geom_iieg,
    g.geometry                               AS geom_inegi,
    d.nombre_municipio                       AS nombre,
    (d.anio::text || '-01-01')::date         AS fecha,
    d.cat_entidad_id                         AS clave_entidad,
    d.cve_mun                                AS clave_municipio,
    d.lpei_personas                          AS personas,
    d.lpei_porcentaje                        AS porcentaje,
    d.lpei_promedio                          AS carencias_promedio
FROM public.stg_pobreza_multidimensional_datos d
JOIN cvegeo_municipalities g
    ON LPAD(g.cvegeo::text, 5, '0') = d.cve_mun
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_lpei_fid
    ON poblacion_ingreso_inferior_linea_pobreza_extrema_ingresos (fid);

-- ---------------------------------------------------------------------------
-- 6. rezago_educativo
-- Personas con carencia por rezago educativo
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS rezago_educativo AS
SELECT
    ROW_NUMBER() OVER ()::bigint             AS fid,
    g.geometry                               AS geom_iieg,
    g.geometry                               AS geom_inegi,
    d.nombre_municipio                       AS nombre,
    (d.anio::text || '-01-01')::date         AS fecha,
    d.cat_entidad_id                         AS clave_entidad,
    d.cve_mun                                AS clave_municipio,
    d.rez_edu_personas                       AS personas,
    d.rez_edu_porcentaje                     AS porcentaje,
    d.rez_edu_promedio                       AS carencias_promedio
FROM public.stg_pobreza_multidimensional_datos d
JOIN cvegeo_municipalities g
    ON LPAD(g.cvegeo::text, 5, '0') = d.cve_mun
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_rezago_educativo_fid
    ON rezago_educativo (fid);

-- ---------------------------------------------------------------------------
-- 7. carencia_acceso_servicios_salud
-- Personas con carencia por acceso a servicios de salud
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS carencia_acceso_servicios_salud AS
SELECT
    ROW_NUMBER() OVER ()::bigint             AS fid,
    g.geometry                               AS geom_iieg,
    g.geometry                               AS geom_inegi,
    d.nombre_municipio                       AS nombre,
    (d.anio::text || '-01-01')::date         AS fecha,
    d.cat_entidad_id                         AS clave_entidad,
    d.cve_mun                                AS clave_municipio,
    d.car_salud_personas                     AS personas,
    d.car_salud_porcentaje                   AS porcentaje,
    d.car_salud_promedio                     AS carencias_promedio
FROM public.stg_pobreza_multidimensional_datos d
JOIN cvegeo_municipalities g
    ON LPAD(g.cvegeo::text, 5, '0') = d.cve_mun
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_car_salud_fid
    ON carencia_acceso_servicios_salud (fid);

-- ---------------------------------------------------------------------------
-- 8. carencia_acceso_seguridad_social
-- Personas con carencia por acceso a seguridad social
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS carencia_acceso_seguridad_social AS
SELECT
    ROW_NUMBER() OVER ()::bigint             AS fid,
    g.geometry                               AS geom_iieg,
    g.geometry                               AS geom_inegi,
    d.nombre_municipio                       AS nombre,
    (d.anio::text || '-01-01')::date         AS fecha,
    d.cat_entidad_id                         AS clave_entidad,
    d.cve_mun                                AS clave_municipio,
    d.car_seg_soc_personas                   AS personas,
    d.car_seg_soc_porcentaje                 AS porcentaje,
    d.car_seg_soc_promedio                   AS carencias_promedio
FROM public.stg_pobreza_multidimensional_datos d
JOIN cvegeo_municipalities g
    ON LPAD(g.cvegeo::text, 5, '0') = d.cve_mun
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_car_seg_soc_fid
    ON carencia_acceso_seguridad_social (fid);

-- ---------------------------------------------------------------------------
-- 9. carencia_calidad_espacios_vivienda
-- Personas con carencia por calidad y espacios de vivienda
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS carencia_calidad_espacios_vivienda AS
SELECT
    ROW_NUMBER() OVER ()::bigint             AS fid,
    g.geometry                               AS geom_iieg,
    g.geometry                               AS geom_inegi,
    d.nombre_municipio                       AS nombre,
    (d.anio::text || '-01-01')::date         AS fecha,
    d.cat_entidad_id                         AS clave_entidad,
    d.cve_mun                                AS clave_municipio,
    d.car_viv_personas                       AS personas,
    d.car_viv_porcentaje                     AS porcentaje,
    d.car_viv_promedio                       AS carencias_promedio
FROM public.stg_pobreza_multidimensional_datos d
JOIN cvegeo_municipalities g
    ON LPAD(g.cvegeo::text, 5, '0') = d.cve_mun
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_car_viv_fid
    ON carencia_calidad_espacios_vivienda (fid);

-- ---------------------------------------------------------------------------
-- 10. carencia_servicios_basicos_vivienda
-- Personas con carencia por acceso a servicios básicos en vivienda
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS carencia_servicios_basicos_vivienda AS
SELECT
    ROW_NUMBER() OVER ()::bigint             AS fid,
    g.geometry                               AS geom_iieg,
    g.geometry                               AS geom_inegi,
    d.nombre_municipio                       AS nombre,
    (d.anio::text || '-01-01')::date         AS fecha,
    d.cat_entidad_id                         AS clave_entidad,
    d.cve_mun                                AS clave_municipio,
    d.car_sbv_personas                       AS personas,
    d.car_sbv_porcentaje                     AS porcentaje,
    d.car_sbv_promedio                       AS carencias_promedio
FROM public.stg_pobreza_multidimensional_datos d
JOIN cvegeo_municipalities g
    ON LPAD(g.cvegeo::text, 5, '0') = d.cve_mun
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_car_sbv_fid
    ON carencia_servicios_basicos_vivienda (fid);

-- ---------------------------------------------------------------------------
-- 11. carencia_acceso_alimentacion
-- Personas con carencia por acceso a alimentación nutritiva y de calidad
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS carencia_acceso_alimentacion AS
SELECT
    ROW_NUMBER() OVER ()::bigint             AS fid,
    g.geometry                               AS geom_iieg,
    g.geometry                               AS geom_inegi,
    d.nombre_municipio                       AS nombre,
    (d.anio::text || '-01-01')::date         AS fecha,
    d.cat_entidad_id                         AS clave_entidad,
    d.cve_mun                                AS clave_municipio,
    d.car_ali_personas                       AS personas,
    d.car_ali_porcentaje                     AS porcentaje,
    d.car_ali_promedio                       AS carencias_promedio
FROM public.stg_pobreza_multidimensional_datos d
JOIN cvegeo_municipalities g
    ON LPAD(g.cvegeo::text, 5, '0') = d.cve_mun
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_car_ali_fid
    ON carencia_acceso_alimentacion (fid);

-- ---------------------------------------------------------------------------
-- 12. poblacion_con_al_menos_una_carencia_social
-- Personas con al menos una carencia social
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS poblacion_con_al_menos_una_carencia_social AS
SELECT
    ROW_NUMBER() OVER ()::bigint             AS fid,
    g.geometry                               AS geom_iieg,
    g.geometry                               AS geom_inegi,
    d.nombre_municipio                       AS nombre,
    (d.anio::text || '-01-01')::date         AS fecha,
    d.cat_entidad_id                         AS clave_entidad,
    d.cve_mun                                AS clave_municipio,
    d.al_1_car_personas                      AS personas,
    d.al_1_car_porcentaje                    AS porcentaje,
    d.al_1_car_promedio                      AS carencias_promedio
FROM public.stg_pobreza_multidimensional_datos d
JOIN cvegeo_municipalities g
    ON LPAD(g.cvegeo::text, 5, '0') = d.cve_mun
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_al_1_car_fid
    ON poblacion_con_al_menos_una_carencia_social (fid);

-- ---------------------------------------------------------------------------
-- 13. poblacion_con_tres_o_mas_carencias_sociales
-- Personas con tres o más carencias sociales
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS poblacion_con_tres_o_mas_carencias_sociales AS
SELECT
    ROW_NUMBER() OVER ()::bigint             AS fid,
    g.geometry                               AS geom_iieg,
    g.geometry                               AS geom_inegi,
    d.nombre_municipio                       AS nombre,
    (d.anio::text || '-01-01')::date         AS fecha,
    d.cat_entidad_id                         AS clave_entidad,
    d.cve_mun                                AS clave_municipio,
    d.tres_mas_car_personas                  AS personas,
    d.tres_mas_car_porcentaje                AS porcentaje,
    d.tres_mas_car_promedio                  AS carencias_promedio
FROM public.stg_pobreza_multidimensional_datos d
JOIN cvegeo_municipalities g
    ON LPAD(g.cvegeo::text, 5, '0') = d.cve_mun
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_tres_mas_car_fid
    ON poblacion_con_tres_o_mas_carencias_sociales (fid);

-- ---------------------------------------------------------------------------
-- 14. vulnerables_por_carencia_social
-- Personas vulnerables por carencias (no pobres por ingresos)
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS vulnerables_por_carencia_social AS
SELECT
    ROW_NUMBER() OVER ()::bigint             AS fid,
    g.geometry                               AS geom_iieg,
    g.geometry                               AS geom_inegi,
    d.nombre_municipio                       AS nombre,
    (d.anio::text || '-01-01')::date         AS fecha,
    d.cat_entidad_id                         AS clave_entidad,
    d.cve_mun                                AS clave_municipio,
    d.vul_carencia_personas                  AS personas,
    d.vul_carencia_porcentaje                AS porcentaje,
    d.vul_carencia_promedio                  AS carencias_promedio
FROM public.stg_pobreza_multidimensional_datos d
JOIN cvegeo_municipalities g
    ON LPAD(g.cvegeo::text, 5, '0') = d.cve_mun
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_vul_carencia_fid
    ON vulnerables_por_carencia_social (fid);

-- ---------------------------------------------------------------------------
-- 15. vulnerables_por_ingreso
-- Personas vulnerables por ingresos (sin carencias)
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS vulnerables_por_ingreso AS
SELECT
    ROW_NUMBER() OVER ()::bigint             AS fid,
    g.geometry                               AS geom_iieg,
    g.geometry                               AS geom_inegi,
    d.nombre_municipio                       AS nombre,
    (d.anio::text || '-01-01')::date         AS fecha,
    d.cat_entidad_id                         AS clave_entidad,
    d.cve_mun                                AS clave_municipio,
    d.vul_ingreso_personas                   AS personas,
    d.vul_ingreso_porcentaje                 AS porcentaje,
    NULL::FLOAT                              AS carencias_promedio
FROM public.stg_pobreza_multidimensional_datos d
JOIN cvegeo_municipalities g
    ON LPAD(g.cvegeo::text, 5, '0') = d.cve_mun
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_vul_ingreso_fid
    ON vulnerables_por_ingreso (fid);

-- ---------------------------------------------------------------------------
-- 16. no_pobre_y_no_vulnerable
-- Personas no pobres y no vulnerables
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS no_pobre_y_no_vulnerable AS
SELECT
    ROW_NUMBER() OVER ()::bigint             AS fid,
    g.geometry                               AS geom_iieg,
    g.geometry                               AS geom_inegi,
    d.nombre_municipio                       AS nombre,
    (d.anio::text || '-01-01')::date         AS fecha,
    d.cat_entidad_id                         AS clave_entidad,
    d.cve_mun                                AS clave_municipio,
    d.no_pobre_personas                      AS personas,
    d.no_pobre_porcentaje                    AS porcentaje,
    NULL::FLOAT                              AS carencias_promedio
FROM public.stg_pobreza_multidimensional_datos d
JOIN cvegeo_municipalities g
    ON LPAD(g.cvegeo::text, 5, '0') = d.cve_mun
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_no_pobre_fid
    ON no_pobre_y_no_vulnerable (fid);
