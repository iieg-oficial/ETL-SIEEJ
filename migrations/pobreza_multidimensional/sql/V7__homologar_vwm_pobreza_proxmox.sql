-- =============================================================================
-- V7__homologar_vwm_pobreza_proxmox.sql  |  Pipeline: pobreza_multidimensional
-- Homologa las 16 MVs de pobreza_multidimensional con sus equivalentes en
-- proxmox (desarrollo_social.*):
--   - nombre: se toma de cvegeo_municipalities.nomgeo (catálogo geográfico ya
--     homologado con proxmox) en vez de d.nombre_municipio (dato crudo
--     CONEVAL). Se valido que los 125 nombres de municipio coinciden byte a
--     byte contra proxmox; el dato crudo difiere solo en "Tlaquepaque" (sin
--     "San Pedro"), lo que causaba 3 filas fantasma "solo en pipeline"/"solo
--     en proxmox" (por año) en las 16 vistas al comparar por nombre+fecha.
--     Se castea a varchar(254) para igualar el ancho de proxmox.
--   - clave_entidad: se fija a '14'::character(2) en vez de
--     d.cat_entidad_id::integer. Es un valor constante (las 16 vistas ya
--     filtran WHERE g.cve_ent = 14), así que fijarlo no cambia el dato, solo
--     el tipo, para igualar character(2) de proxmox.
--   - porcentaje / carencias_promedio: se redondean a numeric(12,2) en vez de
--     quedar como double precision. Se validó con datos reales que
--     ROUND(x, 2) reproduce el valor de proxmox de forma exacta (proxmox no
--     recalcula el indicador, solo trunca a 2 decimales el mismo número).
-- Ver comparaciones/comparacion_pobreza_multidimensional.md
-- =============================================================================

DROP MATERIALIZED VIEW IF EXISTS no_pobre_y_no_vulnerable;
DROP MATERIALIZED VIEW IF EXISTS vulnerables_por_ingreso;
DROP MATERIALIZED VIEW IF EXISTS vulnerables_por_carencia_social;
DROP MATERIALIZED VIEW IF EXISTS poblacion_con_tres_o_mas_carencias_sociales;
DROP MATERIALIZED VIEW IF EXISTS poblacion_con_al_menos_una_carencia_social;
DROP MATERIALIZED VIEW IF EXISTS carencia_acceso_alimentacion;
DROP MATERIALIZED VIEW IF EXISTS carencia_servicios_basicos_vivienda;
DROP MATERIALIZED VIEW IF EXISTS carencia_calidad_espacios_vivienda;
DROP MATERIALIZED VIEW IF EXISTS carencia_acceso_seguridad_social;
DROP MATERIALIZED VIEW IF EXISTS carencia_acceso_servicios_salud;
DROP MATERIALIZED VIEW IF EXISTS rezago_educativo;
DROP MATERIALIZED VIEW IF EXISTS poblacion_ingreso_inferior_linea_pobreza_extrema_ingresos;
DROP MATERIALIZED VIEW IF EXISTS poblacion_ingreso_inferior_linea_pobreza_ingresos;
DROP MATERIALIZED VIEW IF EXISTS pobreza_moderada;
DROP MATERIALIZED VIEW IF EXISTS pobreza_extrema;
DROP MATERIALIZED VIEW IF EXISTS pobreza;

-- ---------------------------------------------------------------------------
-- 1. pobreza
-- Personas en situación de pobreza (ingresos + al menos 1 carencia)
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW pobreza AS
SELECT
    ROW_NUMBER() OVER ()::bigint             AS fid,
    g.geom_inegi,
    d.cve_mun                                AS clave_municipio,
    g.geom_iieg,
    (d.anio::text || '-01-01')::date         AS fecha,
    g.nomgeo::varchar(254)                   AS nombre,
    '14'::character(2)                       AS clave_entidad,
    ROUND(d.pobreza_porcentaje::numeric, 2)::numeric(12,2)  AS porcentaje,
    d.pobreza_personas                       AS personas,
    ROUND(d.pobreza_promedio::numeric, 2)::numeric(12,2)    AS carencias_promedio
FROM public.stg_pobreza_multidimensional_datos d
JOIN cvegeo_municipalities g
    ON LPAD(g.cvegeo::text, 5, '0') = d.cve_mun
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX idx_mv_pobreza_fid
    ON pobreza (fid);

-- ---------------------------------------------------------------------------
-- 2. pobreza_extrema
-- Personas en pobreza extrema (ingresos + 3 o más carencias)
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW pobreza_extrema AS
SELECT
    ROW_NUMBER() OVER ()::bigint             AS fid,
    g.geom_inegi,
    d.cve_mun                                AS clave_municipio,
    g.geom_iieg,
    (d.anio::text || '-01-01')::date         AS fecha,
    g.nomgeo::varchar(254)                   AS nombre,
    '14'::character(2)                       AS clave_entidad,
    d.pobreza_ext_personas                   AS personas,
    ROUND(d.pobreza_ext_porcentaje::numeric, 2)::numeric(12,2) AS porcentaje,
    ROUND(d.pobreza_ext_promedio::numeric, 2)::numeric(12,2)   AS carencias_promedio
FROM public.stg_pobreza_multidimensional_datos d
JOIN cvegeo_municipalities g
    ON LPAD(g.cvegeo::text, 5, '0') = d.cve_mun
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX idx_mv_pobreza_extrema_fid
    ON pobreza_extrema (fid);

-- ---------------------------------------------------------------------------
-- 3. pobreza_moderada
-- Personas en pobreza moderada (pobreza no extrema)
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW pobreza_moderada AS
SELECT
    ROW_NUMBER() OVER ()::bigint             AS fid,
    g.geom_inegi,
    d.cve_mun                                AS clave_municipio,
    g.geom_iieg,
    (d.anio::text || '-01-01')::date         AS fecha,
    g.nomgeo::varchar(254)                   AS nombre,
    '14'::character(2)                       AS clave_entidad,
    d.pobreza_mod_personas                   AS personas,
    ROUND(d.pobreza_mod_porcentaje::numeric, 2)::numeric(12,2) AS porcentaje,
    ROUND(d.pobreza_mod_promedio::numeric, 2)::numeric(12,2)   AS carencias_promedio
FROM public.stg_pobreza_multidimensional_datos d
JOIN cvegeo_municipalities g
    ON LPAD(g.cvegeo::text, 5, '0') = d.cve_mun
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX idx_mv_pobreza_moderada_fid
    ON pobreza_moderada (fid);

-- ---------------------------------------------------------------------------
-- 4. poblacion_ingreso_inferior_linea_pobreza_ingresos
-- Personas con ingreso menor a la línea de pobreza por ingresos
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW poblacion_ingreso_inferior_linea_pobreza_ingresos AS
SELECT
    ROW_NUMBER() OVER ()::bigint             AS fid,
    g.geom_inegi,
    g.nomgeo::varchar(254)                   AS nombre,
    (d.anio::text || '-01-01')::date         AS fecha,
    '14'::character(2)                       AS clave_entidad,
    d.cve_mun                                AS clave_municipio,
    g.geom_iieg,
    d.lpi_personas                           AS personas,
    ROUND(d.lpi_porcentaje::numeric, 2)::numeric(12,2) AS porcentaje,
    ROUND(d.lpi_promedio::numeric, 2)::numeric(12,2)   AS carencias_promedio
FROM public.stg_pobreza_multidimensional_datos d
JOIN cvegeo_municipalities g
    ON LPAD(g.cvegeo::text, 5, '0') = d.cve_mun
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX idx_mv_lpi_fid
    ON poblacion_ingreso_inferior_linea_pobreza_ingresos (fid);

-- ---------------------------------------------------------------------------
-- 5. poblacion_ingreso_inferior_linea_pobreza_extrema_ingresos
-- Personas con ingreso menor a la línea de pobreza extrema por ingresos
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW poblacion_ingreso_inferior_linea_pobreza_extrema_ingresos AS
SELECT
    ROW_NUMBER() OVER ()::bigint             AS fid,
    g.geom_iieg,
    g.geom_inegi,
    g.nomgeo::varchar(254)                   AS nombre,
    (d.anio::text || '-01-01')::date         AS fecha,
    '14'::character(2)                       AS clave_entidad,
    d.cve_mun                                AS clave_municipio,
    d.lpei_personas                          AS personas,
    ROUND(d.lpei_porcentaje::numeric, 2)::numeric(12,2) AS porcentaje,
    ROUND(d.lpei_promedio::numeric, 2)::numeric(12,2)   AS carencias_promedio
FROM public.stg_pobreza_multidimensional_datos d
JOIN cvegeo_municipalities g
    ON LPAD(g.cvegeo::text, 5, '0') = d.cve_mun
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX idx_mv_lpei_fid
    ON poblacion_ingreso_inferior_linea_pobreza_extrema_ingresos (fid);

-- ---------------------------------------------------------------------------
-- 6. rezago_educativo
-- Personas con carencia por rezago educativo
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW rezago_educativo AS
SELECT
    ROW_NUMBER() OVER ()::bigint             AS fid,
    g.geom_iieg,
    g.geom_inegi,
    g.nomgeo::varchar(254)                   AS nombre,
    (d.anio::text || '-01-01')::date         AS fecha,
    '14'::character(2)                       AS clave_entidad,
    d.cve_mun                                AS clave_municipio,
    d.rez_edu_personas                       AS personas,
    ROUND(d.rez_edu_porcentaje::numeric, 2)::numeric(12,2) AS porcentaje,
    ROUND(d.rez_edu_promedio::numeric, 2)::numeric(12,2)   AS carencias_promedio
FROM public.stg_pobreza_multidimensional_datos d
JOIN cvegeo_municipalities g
    ON LPAD(g.cvegeo::text, 5, '0') = d.cve_mun
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX idx_mv_rezago_educativo_fid
    ON rezago_educativo (fid);

-- ---------------------------------------------------------------------------
-- 7. carencia_acceso_servicios_salud
-- Personas con carencia por acceso a servicios de salud
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW carencia_acceso_servicios_salud AS
SELECT
    ROW_NUMBER() OVER ()::bigint             AS fid,
    g.geom_iieg,
    g.geom_inegi,
    g.nomgeo::varchar(254)                   AS nombre,
    (d.anio::text || '-01-01')::date         AS fecha,
    '14'::character(2)                       AS clave_entidad,
    d.cve_mun                                AS clave_municipio,
    d.car_salud_personas                     AS personas,
    ROUND(d.car_salud_porcentaje::numeric, 2)::numeric(12,2) AS porcentaje,
    ROUND(d.car_salud_promedio::numeric, 2)::numeric(12,2)   AS carencias_promedio
FROM public.stg_pobreza_multidimensional_datos d
JOIN cvegeo_municipalities g
    ON LPAD(g.cvegeo::text, 5, '0') = d.cve_mun
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX idx_mv_car_salud_fid
    ON carencia_acceso_servicios_salud (fid);

-- ---------------------------------------------------------------------------
-- 8. carencia_acceso_seguridad_social
-- Personas con carencia por acceso a seguridad social
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW carencia_acceso_seguridad_social AS
SELECT
    ROW_NUMBER() OVER ()::bigint             AS fid,
    g.geom_iieg,
    g.geom_inegi,
    g.nomgeo::varchar(254)                   AS nombre,
    (d.anio::text || '-01-01')::date         AS fecha,
    '14'::character(2)                       AS clave_entidad,
    d.cve_mun                                AS clave_municipio,
    d.car_seg_soc_personas                   AS personas,
    ROUND(d.car_seg_soc_porcentaje::numeric, 2)::numeric(12,2) AS porcentaje,
    ROUND(d.car_seg_soc_promedio::numeric, 2)::numeric(12,2)   AS carencias_promedio
FROM public.stg_pobreza_multidimensional_datos d
JOIN cvegeo_municipalities g
    ON LPAD(g.cvegeo::text, 5, '0') = d.cve_mun
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX idx_mv_car_seg_soc_fid
    ON carencia_acceso_seguridad_social (fid);

-- ---------------------------------------------------------------------------
-- 9. carencia_calidad_espacios_vivienda
-- Personas con carencia por calidad y espacios de vivienda
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW carencia_calidad_espacios_vivienda AS
SELECT
    ROW_NUMBER() OVER ()::bigint             AS fid,
    g.geom_iieg,
    g.geom_inegi,
    g.nomgeo::varchar(254)                   AS nombre,
    (d.anio::text || '-01-01')::date         AS fecha,
    '14'::character(2)                       AS clave_entidad,
    d.cve_mun                                AS clave_municipio,
    d.car_viv_personas                       AS personas,
    ROUND(d.car_viv_porcentaje::numeric, 2)::numeric(12,2) AS porcentaje,
    ROUND(d.car_viv_promedio::numeric, 2)::numeric(12,2)   AS carencias_promedio
FROM public.stg_pobreza_multidimensional_datos d
JOIN cvegeo_municipalities g
    ON LPAD(g.cvegeo::text, 5, '0') = d.cve_mun
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX idx_mv_car_viv_fid
    ON carencia_calidad_espacios_vivienda (fid);

-- ---------------------------------------------------------------------------
-- 10. carencia_servicios_basicos_vivienda
-- Personas con carencia por acceso a servicios básicos en vivienda
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW carencia_servicios_basicos_vivienda AS
SELECT
    ROW_NUMBER() OVER ()::bigint             AS fid,
    g.geom_iieg,
    g.geom_inegi,
    g.nomgeo::varchar(254)                   AS nombre,
    (d.anio::text || '-01-01')::date         AS fecha,
    '14'::character(2)                       AS clave_entidad,
    d.cve_mun                                AS clave_municipio,
    d.car_sbv_personas                       AS personas,
    ROUND(d.car_sbv_porcentaje::numeric, 2)::numeric(12,2) AS porcentaje,
    ROUND(d.car_sbv_promedio::numeric, 2)::numeric(12,2)   AS carencias_promedio
FROM public.stg_pobreza_multidimensional_datos d
JOIN cvegeo_municipalities g
    ON LPAD(g.cvegeo::text, 5, '0') = d.cve_mun
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX idx_mv_car_sbv_fid
    ON carencia_servicios_basicos_vivienda (fid);

-- ---------------------------------------------------------------------------
-- 11. carencia_acceso_alimentacion
-- Personas con carencia por acceso a alimentación nutritiva y de calidad
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW carencia_acceso_alimentacion AS
SELECT
    ROW_NUMBER() OVER ()::bigint             AS fid,
    g.geom_iieg,
    g.geom_inegi,
    g.nomgeo::varchar(254)                   AS nombre,
    (d.anio::text || '-01-01')::date         AS fecha,
    '14'::character(2)                       AS clave_entidad,
    d.cve_mun                                AS clave_municipio,
    d.car_ali_personas                       AS personas,
    ROUND(d.car_ali_porcentaje::numeric, 2)::numeric(12,2) AS porcentaje,
    ROUND(d.car_ali_promedio::numeric, 2)::numeric(12,2)   AS carencias_promedio
FROM public.stg_pobreza_multidimensional_datos d
JOIN cvegeo_municipalities g
    ON LPAD(g.cvegeo::text, 5, '0') = d.cve_mun
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX idx_mv_car_ali_fid
    ON carencia_acceso_alimentacion (fid);

-- ---------------------------------------------------------------------------
-- 12. poblacion_con_al_menos_una_carencia_social
-- Personas con al menos una carencia social
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW poblacion_con_al_menos_una_carencia_social AS
SELECT
    ROW_NUMBER() OVER ()::bigint             AS fid,
    g.geom_iieg,
    g.geom_inegi,
    g.nomgeo::varchar(254)                   AS nombre,
    (d.anio::text || '-01-01')::date         AS fecha,
    '14'::character(2)                       AS clave_entidad,
    d.cve_mun                                AS clave_municipio,
    d.al_1_car_personas                      AS personas,
    ROUND(d.al_1_car_porcentaje::numeric, 2)::numeric(12,2) AS porcentaje,
    ROUND(d.al_1_car_promedio::numeric, 2)::numeric(12,2)   AS carencias_promedio
FROM public.stg_pobreza_multidimensional_datos d
JOIN cvegeo_municipalities g
    ON LPAD(g.cvegeo::text, 5, '0') = d.cve_mun
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX idx_mv_al_1_car_fid
    ON poblacion_con_al_menos_una_carencia_social (fid);

-- ---------------------------------------------------------------------------
-- 13. poblacion_con_tres_o_mas_carencias_sociales
-- Personas con tres o más carencias sociales
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW poblacion_con_tres_o_mas_carencias_sociales AS
SELECT
    ROW_NUMBER() OVER ()::bigint             AS fid,
    g.geom_iieg,
    g.geom_inegi,
    g.nomgeo::varchar(254)                   AS nombre,
    (d.anio::text || '-01-01')::date         AS fecha,
    '14'::character(2)                       AS clave_entidad,
    d.cve_mun                                AS clave_municipio,
    d.tres_mas_car_personas                  AS personas,
    ROUND(d.tres_mas_car_porcentaje::numeric, 2)::numeric(12,2) AS porcentaje,
    ROUND(d.tres_mas_car_promedio::numeric, 2)::numeric(12,2)   AS carencias_promedio
FROM public.stg_pobreza_multidimensional_datos d
JOIN cvegeo_municipalities g
    ON LPAD(g.cvegeo::text, 5, '0') = d.cve_mun
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX idx_mv_tres_mas_car_fid
    ON poblacion_con_tres_o_mas_carencias_sociales (fid);

-- ---------------------------------------------------------------------------
-- 14. vulnerables_por_carencia_social
-- Personas vulnerables por carencias (no pobres por ingresos)
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW vulnerables_por_carencia_social AS
SELECT
    ROW_NUMBER() OVER ()::bigint             AS fid,
    g.geom_iieg,
    g.geom_inegi,
    g.nomgeo::varchar(254)                   AS nombre,
    (d.anio::text || '-01-01')::date         AS fecha,
    '14'::character(2)                       AS clave_entidad,
    d.cve_mun                                AS clave_municipio,
    d.vul_carencia_personas                  AS personas,
    ROUND(d.vul_carencia_porcentaje::numeric, 2)::numeric(12,2) AS porcentaje,
    ROUND(d.vul_carencia_promedio::numeric, 2)::numeric(12,2)   AS carencias_promedio
FROM public.stg_pobreza_multidimensional_datos d
JOIN cvegeo_municipalities g
    ON LPAD(g.cvegeo::text, 5, '0') = d.cve_mun
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX idx_mv_vul_carencia_fid
    ON vulnerables_por_carencia_social (fid);

-- ---------------------------------------------------------------------------
-- 15. vulnerables_por_ingreso
-- Personas vulnerables por ingresos (sin carencias)
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW vulnerables_por_ingreso AS
SELECT
    ROW_NUMBER() OVER ()::bigint             AS fid,
    g.geom_iieg,
    g.geom_inegi,
    g.nomgeo::varchar(254)                   AS nombre,
    (d.anio::text || '-01-01')::date         AS fecha,
    '14'::character(2)                       AS clave_entidad,
    d.cve_mun                                AS clave_municipio,
    d.vul_ingreso_personas                   AS personas,
    ROUND(d.vul_ingreso_porcentaje::numeric, 2)::numeric(12,2) AS porcentaje,
    NULL::numeric(12,2)                      AS carencias_promedio
FROM public.stg_pobreza_multidimensional_datos d
JOIN cvegeo_municipalities g
    ON LPAD(g.cvegeo::text, 5, '0') = d.cve_mun
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX idx_mv_vul_ingreso_fid
    ON vulnerables_por_ingreso (fid);

-- ---------------------------------------------------------------------------
-- 16. no_pobre_y_no_vulnerable
-- Personas no pobres y no vulnerables
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW no_pobre_y_no_vulnerable AS
SELECT
    ROW_NUMBER() OVER ()::bigint             AS fid,
    g.geom_iieg,
    g.geom_inegi,
    g.nomgeo::varchar(254)                   AS nombre,
    (d.anio::text || '-01-01')::date         AS fecha,
    '14'::character(2)                       AS clave_entidad,
    d.cve_mun                                AS clave_municipio,
    d.no_pobre_personas                      AS personas,
    ROUND(d.no_pobre_porcentaje::numeric, 2)::numeric(12,2) AS porcentaje,
    NULL::numeric(12,2)                      AS carencias_promedio
FROM public.stg_pobreza_multidimensional_datos d
JOIN cvegeo_municipalities g
    ON LPAD(g.cvegeo::text, 5, '0') = d.cve_mun
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX idx_mv_no_pobre_fid
    ON no_pobre_y_no_vulnerable (fid);

-- =============================================================================
-- Comentarios (se pierden al recrear las MVs vía DROP, se restauran aquí
-- igual que en V6__comments.sql)
-- =============================================================================
COMMENT ON MATERIALIZED VIEW pobreza IS
    'Personas en situación de pobreza (ingresos + al menos 1 carencia). Municipios de Jalisco. Años: 2010, 2015, 2020.';
COMMENT ON COLUMN pobreza.fid IS 'Identificador secuencial de la fila.';
COMMENT ON COLUMN pobreza.geom_inegi IS 'Geometría del municipio (marco geoestadístico INEGI, SRID 6368).';
COMMENT ON COLUMN pobreza.clave_municipio IS 'Clave municipal INEGI de 5 dígitos (EEMMM).';
COMMENT ON COLUMN pobreza.geom_iieg IS 'Geometría del municipio (marco geoestadístico IIEG, SRID 6368).';
COMMENT ON COLUMN pobreza.fecha IS 'Fecha del periodo de medición (1 de enero del año).';
COMMENT ON COLUMN pobreza.nombre IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN pobreza.clave_entidad IS 'FK al catálogo de entidades federativas.';
COMMENT ON COLUMN pobreza.porcentaje IS 'Porcentaje de personas en situación de pobreza.';
COMMENT ON COLUMN pobreza.personas IS 'Número de personas en situación de pobreza.';
COMMENT ON COLUMN pobreza.carencias_promedio IS 'Promedio de carencias de la población en pobreza.';

COMMENT ON MATERIALIZED VIEW pobreza_extrema IS
    'Personas en pobreza extrema (ingresos + 3 o más carencias). Municipios de Jalisco. Años: 2010, 2015, 2020.';
COMMENT ON COLUMN pobreza_extrema.fid IS 'Identificador secuencial de la fila.';
COMMENT ON COLUMN pobreza_extrema.geom_inegi IS 'Geometría del municipio (marco geoestadístico INEGI, SRID 6368).';
COMMENT ON COLUMN pobreza_extrema.clave_municipio IS 'Clave municipal INEGI de 5 dígitos (EEMMM).';
COMMENT ON COLUMN pobreza_extrema.geom_iieg IS 'Geometría del municipio (marco geoestadístico IIEG, SRID 6368).';
COMMENT ON COLUMN pobreza_extrema.fecha IS 'Fecha del periodo de medición (1 de enero del año).';
COMMENT ON COLUMN pobreza_extrema.nombre IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN pobreza_extrema.clave_entidad IS 'FK al catálogo de entidades federativas.';
COMMENT ON COLUMN pobreza_extrema.personas IS 'Número de personas en pobreza extrema.';
COMMENT ON COLUMN pobreza_extrema.porcentaje IS 'Porcentaje de personas en pobreza extrema.';
COMMENT ON COLUMN pobreza_extrema.carencias_promedio IS 'Promedio de carencias de la población en pobreza extrema.';

COMMENT ON MATERIALIZED VIEW pobreza_moderada IS
    'Personas en pobreza moderada (pobreza no extrema). Municipios de Jalisco. Años: 2010, 2015, 2020.';
COMMENT ON COLUMN pobreza_moderada.fid IS 'Identificador secuencial de la fila.';
COMMENT ON COLUMN pobreza_moderada.geom_inegi IS 'Geometría del municipio (marco geoestadístico INEGI, SRID 6368).';
COMMENT ON COLUMN pobreza_moderada.clave_municipio IS 'Clave municipal INEGI de 5 dígitos (EEMMM).';
COMMENT ON COLUMN pobreza_moderada.geom_iieg IS 'Geometría del municipio (marco geoestadístico IIEG, SRID 6368).';
COMMENT ON COLUMN pobreza_moderada.fecha IS 'Fecha del periodo de medición (1 de enero del año).';
COMMENT ON COLUMN pobreza_moderada.nombre IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN pobreza_moderada.clave_entidad IS 'FK al catálogo de entidades federativas.';
COMMENT ON COLUMN pobreza_moderada.personas IS 'Número de personas en pobreza moderada.';
COMMENT ON COLUMN pobreza_moderada.porcentaje IS 'Porcentaje de personas en pobreza moderada.';
COMMENT ON COLUMN pobreza_moderada.carencias_promedio IS 'Promedio de carencias de la población en pobreza moderada.';

COMMENT ON MATERIALIZED VIEW poblacion_ingreso_inferior_linea_pobreza_ingresos IS
    'Personas con ingreso menor a la línea de pobreza por ingresos. Municipios de Jalisco. Años: 2010, 2015, 2020.';
COMMENT ON COLUMN poblacion_ingreso_inferior_linea_pobreza_ingresos.fid IS 'Identificador secuencial de la fila.';
COMMENT ON COLUMN poblacion_ingreso_inferior_linea_pobreza_ingresos.geom_inegi IS 'Geometría del municipio (marco geoestadístico INEGI, SRID 6368).';
COMMENT ON COLUMN poblacion_ingreso_inferior_linea_pobreza_ingresos.nombre IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN poblacion_ingreso_inferior_linea_pobreza_ingresos.fecha IS 'Fecha del periodo de medición (1 de enero del año).';
COMMENT ON COLUMN poblacion_ingreso_inferior_linea_pobreza_ingresos.clave_entidad IS 'FK al catálogo de entidades federativas.';
COMMENT ON COLUMN poblacion_ingreso_inferior_linea_pobreza_ingresos.clave_municipio IS 'Clave municipal INEGI de 5 dígitos (EEMMM).';
COMMENT ON COLUMN poblacion_ingreso_inferior_linea_pobreza_ingresos.geom_iieg IS 'Geometría del municipio (marco geoestadístico IIEG, SRID 6368).';
COMMENT ON COLUMN poblacion_ingreso_inferior_linea_pobreza_ingresos.personas IS 'Número de personas con ingreso inferior a la línea de pobreza por ingresos.';
COMMENT ON COLUMN poblacion_ingreso_inferior_linea_pobreza_ingresos.porcentaje IS 'Porcentaje de personas con ingreso inferior a la línea de pobreza por ingresos.';
COMMENT ON COLUMN poblacion_ingreso_inferior_linea_pobreza_ingresos.carencias_promedio IS 'Promedio de carencias en la población con ingreso inferior a la LPI.';

COMMENT ON MATERIALIZED VIEW poblacion_ingreso_inferior_linea_pobreza_extrema_ingresos IS
    'Personas con ingreso menor a la línea de pobreza extrema por ingresos. Municipios de Jalisco. Años: 2010, 2015, 2020.';
COMMENT ON COLUMN poblacion_ingreso_inferior_linea_pobreza_extrema_ingresos.fid IS 'Identificador secuencial de la fila.';
COMMENT ON COLUMN poblacion_ingreso_inferior_linea_pobreza_extrema_ingresos.geom_iieg IS 'Geometría del municipio (marco geoestadístico IIEG, SRID 6368).';
COMMENT ON COLUMN poblacion_ingreso_inferior_linea_pobreza_extrema_ingresos.geom_inegi IS 'Geometría del municipio (marco geoestadístico INEGI, SRID 6368).';
COMMENT ON COLUMN poblacion_ingreso_inferior_linea_pobreza_extrema_ingresos.nombre IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN poblacion_ingreso_inferior_linea_pobreza_extrema_ingresos.fecha IS 'Fecha del periodo de medición (1 de enero del año).';
COMMENT ON COLUMN poblacion_ingreso_inferior_linea_pobreza_extrema_ingresos.clave_entidad IS 'FK al catálogo de entidades federativas.';
COMMENT ON COLUMN poblacion_ingreso_inferior_linea_pobreza_extrema_ingresos.clave_municipio IS 'Clave municipal INEGI de 5 dígitos (EEMMM).';
COMMENT ON COLUMN poblacion_ingreso_inferior_linea_pobreza_extrema_ingresos.personas IS 'Número de personas con ingreso inferior a la línea de pobreza extrema.';
COMMENT ON COLUMN poblacion_ingreso_inferior_linea_pobreza_extrema_ingresos.porcentaje IS 'Porcentaje de personas con ingreso inferior a la línea de pobreza extrema.';
COMMENT ON COLUMN poblacion_ingreso_inferior_linea_pobreza_extrema_ingresos.carencias_promedio IS 'Promedio de carencias en la población con ingreso inferior a la LPEI.';

COMMENT ON MATERIALIZED VIEW rezago_educativo IS
    'Personas con carencia por rezago educativo. Municipios de Jalisco. Años: 2010, 2015, 2020.';
COMMENT ON COLUMN rezago_educativo.fid IS 'Identificador secuencial de la fila.';
COMMENT ON COLUMN rezago_educativo.geom_iieg IS 'Geometría del municipio (marco geoestadístico IIEG, SRID 6368).';
COMMENT ON COLUMN rezago_educativo.geom_inegi IS 'Geometría del municipio (marco geoestadístico INEGI, SRID 6368).';
COMMENT ON COLUMN rezago_educativo.nombre IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN rezago_educativo.fecha IS 'Fecha del periodo de medición (1 de enero del año).';
COMMENT ON COLUMN rezago_educativo.clave_entidad IS 'FK al catálogo de entidades federativas.';
COMMENT ON COLUMN rezago_educativo.clave_municipio IS 'Clave municipal INEGI de 5 dígitos (EEMMM).';
COMMENT ON COLUMN rezago_educativo.personas IS 'Número de personas con carencia por rezago educativo.';
COMMENT ON COLUMN rezago_educativo.porcentaje IS 'Porcentaje de personas con carencia por rezago educativo.';
COMMENT ON COLUMN rezago_educativo.carencias_promedio IS 'Promedio de carencias en la población con rezago educativo.';

COMMENT ON MATERIALIZED VIEW carencia_acceso_servicios_salud IS
    'Personas con carencia por acceso a servicios de salud. Municipios de Jalisco. Años: 2010, 2015, 2020.';
COMMENT ON COLUMN carencia_acceso_servicios_salud.fid IS 'Identificador secuencial de la fila.';
COMMENT ON COLUMN carencia_acceso_servicios_salud.geom_iieg IS 'Geometría del municipio (marco geoestadístico IIEG, SRID 6368).';
COMMENT ON COLUMN carencia_acceso_servicios_salud.geom_inegi IS 'Geometría del municipio (marco geoestadístico INEGI, SRID 6368).';
COMMENT ON COLUMN carencia_acceso_servicios_salud.nombre IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN carencia_acceso_servicios_salud.fecha IS 'Fecha del periodo de medición (1 de enero del año).';
COMMENT ON COLUMN carencia_acceso_servicios_salud.clave_entidad IS 'FK al catálogo de entidades federativas.';
COMMENT ON COLUMN carencia_acceso_servicios_salud.clave_municipio IS 'Clave municipal INEGI de 5 dígitos (EEMMM).';
COMMENT ON COLUMN carencia_acceso_servicios_salud.personas IS 'Número de personas con carencia por acceso a servicios de salud.';
COMMENT ON COLUMN carencia_acceso_servicios_salud.porcentaje IS 'Porcentaje de personas con carencia por acceso a servicios de salud.';
COMMENT ON COLUMN carencia_acceso_servicios_salud.carencias_promedio IS 'Promedio de carencias en la población con esta carencia.';

COMMENT ON MATERIALIZED VIEW carencia_acceso_seguridad_social IS
    'Personas con carencia por acceso a seguridad social. Municipios de Jalisco. Años: 2010, 2015, 2020.';
COMMENT ON COLUMN carencia_acceso_seguridad_social.fid IS 'Identificador secuencial de la fila.';
COMMENT ON COLUMN carencia_acceso_seguridad_social.geom_iieg IS 'Geometría del municipio (marco geoestadístico IIEG, SRID 6368).';
COMMENT ON COLUMN carencia_acceso_seguridad_social.geom_inegi IS 'Geometría del municipio (marco geoestadístico INEGI, SRID 6368).';
COMMENT ON COLUMN carencia_acceso_seguridad_social.nombre IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN carencia_acceso_seguridad_social.fecha IS 'Fecha del periodo de medición (1 de enero del año).';
COMMENT ON COLUMN carencia_acceso_seguridad_social.clave_entidad IS 'FK al catálogo de entidades federativas.';
COMMENT ON COLUMN carencia_acceso_seguridad_social.clave_municipio IS 'Clave municipal INEGI de 5 dígitos (EEMMM).';
COMMENT ON COLUMN carencia_acceso_seguridad_social.personas IS 'Número de personas con carencia por acceso a seguridad social.';
COMMENT ON COLUMN carencia_acceso_seguridad_social.porcentaje IS 'Porcentaje de personas con carencia por acceso a seguridad social.';
COMMENT ON COLUMN carencia_acceso_seguridad_social.carencias_promedio IS 'Promedio de carencias en la población con esta carencia.';

COMMENT ON MATERIALIZED VIEW carencia_calidad_espacios_vivienda IS
    'Personas con carencia por calidad y espacios de vivienda. Municipios de Jalisco. Años: 2010, 2015, 2020.';
COMMENT ON COLUMN carencia_calidad_espacios_vivienda.fid IS 'Identificador secuencial de la fila.';
COMMENT ON COLUMN carencia_calidad_espacios_vivienda.geom_iieg IS 'Geometría del municipio (marco geoestadístico IIEG, SRID 6368).';
COMMENT ON COLUMN carencia_calidad_espacios_vivienda.geom_inegi IS 'Geometría del municipio (marco geoestadístico INEGI, SRID 6368).';
COMMENT ON COLUMN carencia_calidad_espacios_vivienda.nombre IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN carencia_calidad_espacios_vivienda.fecha IS 'Fecha del periodo de medición (1 de enero del año).';
COMMENT ON COLUMN carencia_calidad_espacios_vivienda.clave_entidad IS 'FK al catálogo de entidades federativas.';
COMMENT ON COLUMN carencia_calidad_espacios_vivienda.clave_municipio IS 'Clave municipal INEGI de 5 dígitos (EEMMM).';
COMMENT ON COLUMN carencia_calidad_espacios_vivienda.personas IS 'Número de personas con carencia por calidad y espacios de vivienda.';
COMMENT ON COLUMN carencia_calidad_espacios_vivienda.porcentaje IS 'Porcentaje de personas con carencia por calidad y espacios de vivienda.';
COMMENT ON COLUMN carencia_calidad_espacios_vivienda.carencias_promedio IS 'Promedio de carencias en la población con esta carencia.';

COMMENT ON MATERIALIZED VIEW carencia_servicios_basicos_vivienda IS
    'Personas con carencia por acceso a servicios básicos en vivienda. Municipios de Jalisco. Años: 2010, 2015, 2020.';
COMMENT ON COLUMN carencia_servicios_basicos_vivienda.fid IS 'Identificador secuencial de la fila.';
COMMENT ON COLUMN carencia_servicios_basicos_vivienda.geom_iieg IS 'Geometría del municipio (marco geoestadístico IIEG, SRID 6368).';
COMMENT ON COLUMN carencia_servicios_basicos_vivienda.geom_inegi IS 'Geometría del municipio (marco geoestadístico INEGI, SRID 6368).';
COMMENT ON COLUMN carencia_servicios_basicos_vivienda.nombre IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN carencia_servicios_basicos_vivienda.fecha IS 'Fecha del periodo de medición (1 de enero del año).';
COMMENT ON COLUMN carencia_servicios_basicos_vivienda.clave_entidad IS 'FK al catálogo de entidades federativas.';
COMMENT ON COLUMN carencia_servicios_basicos_vivienda.clave_municipio IS 'Clave municipal INEGI de 5 dígitos (EEMMM).';
COMMENT ON COLUMN carencia_servicios_basicos_vivienda.personas IS 'Número de personas con carencia por acceso a servicios básicos en vivienda.';
COMMENT ON COLUMN carencia_servicios_basicos_vivienda.porcentaje IS 'Porcentaje de personas con carencia por acceso a servicios básicos en vivienda.';
COMMENT ON COLUMN carencia_servicios_basicos_vivienda.carencias_promedio IS 'Promedio de carencias en la población con esta carencia.';

COMMENT ON MATERIALIZED VIEW carencia_acceso_alimentacion IS
    'Personas con carencia por acceso a alimentación nutritiva y de calidad. Municipios de Jalisco. Años: 2010, 2015, 2020.';
COMMENT ON COLUMN carencia_acceso_alimentacion.fid IS 'Identificador secuencial de la fila.';
COMMENT ON COLUMN carencia_acceso_alimentacion.geom_iieg IS 'Geometría del municipio (marco geoestadístico IIEG, SRID 6368).';
COMMENT ON COLUMN carencia_acceso_alimentacion.geom_inegi IS 'Geometría del municipio (marco geoestadístico INEGI, SRID 6368).';
COMMENT ON COLUMN carencia_acceso_alimentacion.nombre IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN carencia_acceso_alimentacion.fecha IS 'Fecha del periodo de medición (1 de enero del año).';
COMMENT ON COLUMN carencia_acceso_alimentacion.clave_entidad IS 'FK al catálogo de entidades federativas.';
COMMENT ON COLUMN carencia_acceso_alimentacion.clave_municipio IS 'Clave municipal INEGI de 5 dígitos (EEMMM).';
COMMENT ON COLUMN carencia_acceso_alimentacion.personas IS 'Número de personas con carencia por acceso a alimentación nutritiva y de calidad.';
COMMENT ON COLUMN carencia_acceso_alimentacion.porcentaje IS 'Porcentaje de personas con carencia por acceso a alimentación nutritiva y de calidad.';
COMMENT ON COLUMN carencia_acceso_alimentacion.carencias_promedio IS 'Promedio de carencias en la población con esta carencia.';

COMMENT ON MATERIALIZED VIEW poblacion_con_al_menos_una_carencia_social IS
    'Personas con al menos una carencia social. Municipios de Jalisco. Años: 2010, 2015, 2020.';
COMMENT ON COLUMN poblacion_con_al_menos_una_carencia_social.fid IS 'Identificador secuencial de la fila.';
COMMENT ON COLUMN poblacion_con_al_menos_una_carencia_social.geom_iieg IS 'Geometría del municipio (marco geoestadístico IIEG, SRID 6368).';
COMMENT ON COLUMN poblacion_con_al_menos_una_carencia_social.geom_inegi IS 'Geometría del municipio (marco geoestadístico INEGI, SRID 6368).';
COMMENT ON COLUMN poblacion_con_al_menos_una_carencia_social.nombre IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN poblacion_con_al_menos_una_carencia_social.fecha IS 'Fecha del periodo de medición (1 de enero del año).';
COMMENT ON COLUMN poblacion_con_al_menos_una_carencia_social.clave_entidad IS 'FK al catálogo de entidades federativas.';
COMMENT ON COLUMN poblacion_con_al_menos_una_carencia_social.clave_municipio IS 'Clave municipal INEGI de 5 dígitos (EEMMM).';
COMMENT ON COLUMN poblacion_con_al_menos_una_carencia_social.personas IS 'Número de personas con al menos una carencia social.';
COMMENT ON COLUMN poblacion_con_al_menos_una_carencia_social.porcentaje IS 'Porcentaje de personas con al menos una carencia social.';
COMMENT ON COLUMN poblacion_con_al_menos_una_carencia_social.carencias_promedio IS 'Promedio de carencias en la población con al menos una carencia social.';

COMMENT ON MATERIALIZED VIEW poblacion_con_tres_o_mas_carencias_sociales IS
    'Personas con tres o más carencias sociales. Municipios de Jalisco. Años: 2010, 2015, 2020.';
COMMENT ON COLUMN poblacion_con_tres_o_mas_carencias_sociales.fid IS 'Identificador secuencial de la fila.';
COMMENT ON COLUMN poblacion_con_tres_o_mas_carencias_sociales.geom_iieg IS 'Geometría del municipio (marco geoestadístico IIEG, SRID 6368).';
COMMENT ON COLUMN poblacion_con_tres_o_mas_carencias_sociales.geom_inegi IS 'Geometría del municipio (marco geoestadístico INEGI, SRID 6368).';
COMMENT ON COLUMN poblacion_con_tres_o_mas_carencias_sociales.nombre IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN poblacion_con_tres_o_mas_carencias_sociales.fecha IS 'Fecha del periodo de medición (1 de enero del año).';
COMMENT ON COLUMN poblacion_con_tres_o_mas_carencias_sociales.clave_entidad IS 'FK al catálogo de entidades federativas.';
COMMENT ON COLUMN poblacion_con_tres_o_mas_carencias_sociales.clave_municipio IS 'Clave municipal INEGI de 5 dígitos (EEMMM).';
COMMENT ON COLUMN poblacion_con_tres_o_mas_carencias_sociales.personas IS 'Número de personas con tres o más carencias sociales.';
COMMENT ON COLUMN poblacion_con_tres_o_mas_carencias_sociales.porcentaje IS 'Porcentaje de personas con tres o más carencias sociales.';
COMMENT ON COLUMN poblacion_con_tres_o_mas_carencias_sociales.carencias_promedio IS 'Promedio de carencias en la población con tres o más carencias sociales.';

COMMENT ON MATERIALIZED VIEW vulnerables_por_carencia_social IS
    'Personas vulnerables por carencias (no pobres por ingresos). Municipios de Jalisco. Años: 2010, 2015, 2020.';
COMMENT ON COLUMN vulnerables_por_carencia_social.fid IS 'Identificador secuencial de la fila.';
COMMENT ON COLUMN vulnerables_por_carencia_social.geom_iieg IS 'Geometría del municipio (marco geoestadístico IIEG, SRID 6368).';
COMMENT ON COLUMN vulnerables_por_carencia_social.geom_inegi IS 'Geometría del municipio (marco geoestadístico INEGI, SRID 6368).';
COMMENT ON COLUMN vulnerables_por_carencia_social.nombre IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN vulnerables_por_carencia_social.fecha IS 'Fecha del periodo de medición (1 de enero del año).';
COMMENT ON COLUMN vulnerables_por_carencia_social.clave_entidad IS 'FK al catálogo de entidades federativas.';
COMMENT ON COLUMN vulnerables_por_carencia_social.clave_municipio IS 'Clave municipal INEGI de 5 dígitos (EEMMM).';
COMMENT ON COLUMN vulnerables_por_carencia_social.personas IS 'Número de personas vulnerables por carencia social.';
COMMENT ON COLUMN vulnerables_por_carencia_social.porcentaje IS 'Porcentaje de personas vulnerables por carencia social.';
COMMENT ON COLUMN vulnerables_por_carencia_social.carencias_promedio IS 'Promedio de carencias en la población vulnerable por carencia social.';

COMMENT ON MATERIALIZED VIEW vulnerables_por_ingreso IS
    'Personas vulnerables por ingresos (sin carencias). Municipios de Jalisco. Años: 2010, 2015, 2020.';
COMMENT ON COLUMN vulnerables_por_ingreso.fid IS 'Identificador secuencial de la fila.';
COMMENT ON COLUMN vulnerables_por_ingreso.geom_iieg IS 'Geometría del municipio (marco geoestadístico IIEG, SRID 6368).';
COMMENT ON COLUMN vulnerables_por_ingreso.geom_inegi IS 'Geometría del municipio (marco geoestadístico INEGI, SRID 6368).';
COMMENT ON COLUMN vulnerables_por_ingreso.nombre IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN vulnerables_por_ingreso.fecha IS 'Fecha del periodo de medición (1 de enero del año).';
COMMENT ON COLUMN vulnerables_por_ingreso.clave_entidad IS 'FK al catálogo de entidades federativas.';
COMMENT ON COLUMN vulnerables_por_ingreso.clave_municipio IS 'Clave municipal INEGI de 5 dígitos (EEMMM).';
COMMENT ON COLUMN vulnerables_por_ingreso.personas IS 'Número de personas vulnerables por ingresos.';
COMMENT ON COLUMN vulnerables_por_ingreso.porcentaje IS 'Porcentaje de personas vulnerables por ingresos.';
COMMENT ON COLUMN vulnerables_por_ingreso.carencias_promedio IS 'No disponible en la fuente CONEVAL para este indicador (siempre NULL).';

COMMENT ON MATERIALIZED VIEW no_pobre_y_no_vulnerable IS
    'Personas no pobres y no vulnerables. Municipios de Jalisco. Años: 2010, 2015, 2020.';
COMMENT ON COLUMN no_pobre_y_no_vulnerable.fid IS 'Identificador secuencial de la fila.';
COMMENT ON COLUMN no_pobre_y_no_vulnerable.geom_iieg IS 'Geometría del municipio (marco geoestadístico IIEG, SRID 6368).';
COMMENT ON COLUMN no_pobre_y_no_vulnerable.geom_inegi IS 'Geometría del municipio (marco geoestadístico INEGI, SRID 6368).';
COMMENT ON COLUMN no_pobre_y_no_vulnerable.nombre IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN no_pobre_y_no_vulnerable.fecha IS 'Fecha del periodo de medición (1 de enero del año).';
COMMENT ON COLUMN no_pobre_y_no_vulnerable.clave_entidad IS 'FK al catálogo de entidades federativas.';
COMMENT ON COLUMN no_pobre_y_no_vulnerable.clave_municipio IS 'Clave municipal INEGI de 5 dígitos (EEMMM).';
COMMENT ON COLUMN no_pobre_y_no_vulnerable.personas IS 'Número de personas no pobres y no vulnerables.';
COMMENT ON COLUMN no_pobre_y_no_vulnerable.porcentaje IS 'Porcentaje de personas no pobres y no vulnerables.';
COMMENT ON COLUMN no_pobre_y_no_vulnerable.carencias_promedio IS 'No disponible en la fuente CONEVAL para este indicador (siempre NULL).';
