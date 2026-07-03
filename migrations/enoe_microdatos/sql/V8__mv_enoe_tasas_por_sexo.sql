-- Recrear mv_enoe_tasas y mv_enoe_tasas_jalisco con poblaciones y tasas por sexo
DROP MATERIALIZED VIEW IF EXISTS mv_enoe_tasas;
DROP MATERIALIZED VIEW IF EXISTS mv_enoe_tasas_jalisco;

-- ─── mv_enoe_tasas (municipio × trimestre) ───────────────────────────────────

CREATE MATERIALIZED VIEW mv_enoe_tasas AS
WITH base AS (
    SELECT *
    FROM stg_enoe_microdatos
    WHERE r_def = 0
      AND c_res IN (1, 3)
      AND eda BETWEEN 15 AND 98
),
agg AS (
    SELECT
        anio,
        trimestre,
        entidad_id,
        municipio_id,
        -- Poblaciones totales
        SUM(fac)                                                                          AS p15ymas,
        SUM(CASE WHEN clase1 = 1                                    THEN fac ELSE 0 END)  AS pea,
        SUM(CASE WHEN clase2 = 2                                    THEN fac ELSE 0 END)  AS pd,
        SUM(CASE WHEN clase2 = 1                                    THEN fac ELSE 0 END)  AS po,
        SUM(CASE WHEN clase2 = 1 AND ambito1 <> 1                   THEN fac ELSE 0 END)  AS pona,
        -- Numeradores totales
        SUM(CASE WHEN clase2 = 1 AND dur9c    = 2                   THEN fac ELSE 0 END)  AS o_menos_15hrs,
        SUM(CASE WHEN clase2 = 1 AND tpg_p8a  = 1                   THEN fac ELSE 0 END)  AS pobot,
        SUM(CASE WHEN clase2 = 1 AND remune2c = 1                   THEN fac ELSE 0 END)  AS pasa,
        SUM(CASE WHEN clase2 = 1 AND sub_o    = 1                   THEN fac ELSE 0 END)  AS psub_o,
        SUM(CASE WHEN clase2 = 1 AND tcco    IN (1, 2, 3)           THEN fac ELSE 0 END)  AS pcco,
        SUM(CASE WHEN clase2 = 1 AND tue2     = 5                   THEN fac ELSE 0 END)  AS posi,
        SUM(CASE WHEN clase2 = 1 AND emp_ppal = 1                   THEN fac ELSE 0 END)  AS poi,
        SUM(CASE WHEN clase2 = 1 AND emp_ppal = 1 AND ambito1 <> 1  THEN fac ELSE 0 END)  AS poina,
        -- Poblaciones por sexo (h = hombres sex=1, m = mujeres sex=2)
        SUM(CASE WHEN sex = 1                                       THEN fac ELSE 0 END)  AS p15ymas_h,
        SUM(CASE WHEN sex = 2                                       THEN fac ELSE 0 END)  AS p15ymas_m,
        SUM(CASE WHEN clase1 = 1 AND sex = 1                        THEN fac ELSE 0 END)  AS pea_h,
        SUM(CASE WHEN clase1 = 1 AND sex = 2                        THEN fac ELSE 0 END)  AS pea_m,
        SUM(CASE WHEN clase2 = 2 AND sex = 1                        THEN fac ELSE 0 END)  AS pd_h,
        SUM(CASE WHEN clase2 = 2 AND sex = 2                        THEN fac ELSE 0 END)  AS pd_m,
        SUM(CASE WHEN clase2 = 1 AND sex = 1                        THEN fac ELSE 0 END)  AS po_h,
        SUM(CASE WHEN clase2 = 1 AND sex = 2                        THEN fac ELSE 0 END)  AS po_m,
        SUM(CASE WHEN clase2 = 1 AND ambito1 <> 1 AND sex = 1       THEN fac ELSE 0 END)  AS pona_h,
        SUM(CASE WHEN clase2 = 1 AND ambito1 <> 1 AND sex = 2       THEN fac ELSE 0 END)  AS pona_m,
        -- Numeradores por sexo
        SUM(CASE WHEN clase2 = 1 AND dur9c    = 2  AND sex = 1      THEN fac ELSE 0 END)  AS o_menos_15hrs_h,
        SUM(CASE WHEN clase2 = 1 AND dur9c    = 2  AND sex = 2      THEN fac ELSE 0 END)  AS o_menos_15hrs_m,
        SUM(CASE WHEN clase2 = 1 AND tpg_p8a  = 1  AND sex = 1      THEN fac ELSE 0 END)  AS pobot_h,
        SUM(CASE WHEN clase2 = 1 AND tpg_p8a  = 1  AND sex = 2      THEN fac ELSE 0 END)  AS pobot_m,
        SUM(CASE WHEN clase2 = 1 AND remune2c = 1  AND sex = 1      THEN fac ELSE 0 END)  AS pasa_h,
        SUM(CASE WHEN clase2 = 1 AND remune2c = 1  AND sex = 2      THEN fac ELSE 0 END)  AS pasa_m,
        SUM(CASE WHEN clase2 = 1 AND sub_o    = 1  AND sex = 1      THEN fac ELSE 0 END)  AS psub_o_h,
        SUM(CASE WHEN clase2 = 1 AND sub_o    = 1  AND sex = 2      THEN fac ELSE 0 END)  AS psub_o_m,
        SUM(CASE WHEN clase2 = 1 AND tcco IN (1,2,3) AND sex = 1    THEN fac ELSE 0 END)  AS pcco_h,
        SUM(CASE WHEN clase2 = 1 AND tcco IN (1,2,3) AND sex = 2    THEN fac ELSE 0 END)  AS pcco_m,
        SUM(CASE WHEN clase2 = 1 AND tue2     = 5  AND sex = 1      THEN fac ELSE 0 END)  AS posi_h,
        SUM(CASE WHEN clase2 = 1 AND tue2     = 5  AND sex = 2      THEN fac ELSE 0 END)  AS posi_m,
        SUM(CASE WHEN clase2 = 1 AND emp_ppal = 1  AND sex = 1      THEN fac ELSE 0 END)  AS poi_h,
        SUM(CASE WHEN clase2 = 1 AND emp_ppal = 1  AND sex = 2      THEN fac ELSE 0 END)  AS poi_m,
        SUM(CASE WHEN clase2 = 1 AND emp_ppal = 1 AND ambito1 <> 1 AND sex = 1 THEN fac ELSE 0 END) AS poina_h,
        SUM(CASE WHEN clase2 = 1 AND emp_ppal = 1 AND ambito1 <> 1 AND sex = 2 THEN fac ELSE 0 END) AS poina_m
    FROM base
    GROUP BY anio, trimestre, entidad_id, municipio_id
)
SELECT
    a.anio,
    a.trimestre,
    a.municipio_id,
    m.nomgeo                                                                    AS municipio,
    -- Poblaciones totales
    a.p15ymas, a.pea, a.pd, a.po, a.pona,
    -- Tasas totales
    ROUND((a.pea::numeric                          / NULLIF(a.p15ymas, 0)) * 100, 2) AS tp,
    ROUND((a.pd::numeric                           / NULLIF(a.pea,     0)) * 100, 2) AS td,
    ROUND(((a.pd + a.o_menos_15hrs)::numeric       / NULLIF(a.pea,     0)) * 100, 2) AS topd,
    ROUND(((a.pd + a.pobot)::numeric               / NULLIF(a.pea,     0)) * 100, 2) AS tprg,
    ROUND((a.pasa::numeric                         / NULLIF(a.po,      0)) * 100, 2) AS tta,
    ROUND((a.psub_o::numeric                       / NULLIF(a.po,      0)) * 100, 2) AS tsub,
    ROUND((a.pcco::numeric                         / NULLIF(a.po,      0)) * 100, 2) AS tcco,
    ROUND((a.posi::numeric                         / NULLIF(a.po,      0)) * 100, 2) AS tosi1,
    ROUND((a.poi::numeric                          / NULLIF(a.po,      0)) * 100, 2) AS til1,
    ROUND((a.posi::numeric                         / NULLIF(a.pona,    0)) * 100, 2) AS tosi2,
    ROUND((a.poina::numeric                        / NULLIF(a.pona,    0)) * 100, 2) AS til2,
    -- Poblaciones por sexo
    a.p15ymas_h, a.p15ymas_m,
    a.pea_h,     a.pea_m,
    a.pd_h,      a.pd_m,
    a.po_h,      a.po_m,
    a.pona_h,    a.pona_m,
    -- Tasas por sexo
    ROUND((a.pea_h::numeric                              / NULLIF(a.p15ymas_h, 0)) * 100, 2) AS tp_h,
    ROUND((a.pea_m::numeric                              / NULLIF(a.p15ymas_m, 0)) * 100, 2) AS tp_m,
    ROUND((a.pd_h::numeric                               / NULLIF(a.pea_h,     0)) * 100, 2) AS td_h,
    ROUND((a.pd_m::numeric                               / NULLIF(a.pea_m,     0)) * 100, 2) AS td_m,
    ROUND(((a.pd_h + a.o_menos_15hrs_h)::numeric         / NULLIF(a.pea_h,     0)) * 100, 2) AS topd_h,
    ROUND(((a.pd_m + a.o_menos_15hrs_m)::numeric         / NULLIF(a.pea_m,     0)) * 100, 2) AS topd_m,
    ROUND(((a.pd_h + a.pobot_h)::numeric                 / NULLIF(a.pea_h,     0)) * 100, 2) AS tprg_h,
    ROUND(((a.pd_m + a.pobot_m)::numeric                 / NULLIF(a.pea_m,     0)) * 100, 2) AS tprg_m,
    ROUND((a.pasa_h::numeric                             / NULLIF(a.po_h,      0)) * 100, 2) AS tta_h,
    ROUND((a.pasa_m::numeric                             / NULLIF(a.po_m,      0)) * 100, 2) AS tta_m,
    ROUND((a.psub_o_h::numeric                           / NULLIF(a.po_h,      0)) * 100, 2) AS tsub_h,
    ROUND((a.psub_o_m::numeric                           / NULLIF(a.po_m,      0)) * 100, 2) AS tsub_m,
    ROUND((a.pcco_h::numeric                             / NULLIF(a.po_h,      0)) * 100, 2) AS tcco_h,
    ROUND((a.pcco_m::numeric                             / NULLIF(a.po_m,      0)) * 100, 2) AS tcco_m,
    ROUND((a.posi_h::numeric                             / NULLIF(a.po_h,      0)) * 100, 2) AS tosi1_h,
    ROUND((a.posi_m::numeric                             / NULLIF(a.po_m,      0)) * 100, 2) AS tosi1_m,
    ROUND((a.poi_h::numeric                              / NULLIF(a.po_h,      0)) * 100, 2) AS til1_h,
    ROUND((a.poi_m::numeric                              / NULLIF(a.po_m,      0)) * 100, 2) AS til1_m,
    ROUND((a.posi_h::numeric                             / NULLIF(a.pona_h,    0)) * 100, 2) AS tosi2_h,
    ROUND((a.posi_m::numeric                             / NULLIF(a.pona_m,    0)) * 100, 2) AS tosi2_m,
    ROUND((a.poina_h::numeric                            / NULLIF(a.pona_h,    0)) * 100, 2) AS til2_h,
    ROUND((a.poina_m::numeric                            / NULLIF(a.pona_m,    0)) * 100, 2) AS til2_m
FROM agg a
LEFT JOIN cvegeo_municipalities m
       ON m.cve_ent = a.entidad_id AND m.cve_mun = a.municipio_id
ORDER BY a.anio, a.trimestre, a.municipio_id;

CREATE UNIQUE INDEX uix_mv_enoe_tasas
    ON mv_enoe_tasas (anio, trimestre, municipio_id);

-- ─── mv_enoe_tasas_jalisco (trimestre nivel estado) ──────────────────────────

CREATE MATERIALIZED VIEW mv_enoe_tasas_jalisco AS
WITH base AS (
    SELECT *
    FROM stg_enoe_microdatos
    WHERE r_def = 0
      AND c_res IN (1, 3)
      AND eda BETWEEN 15 AND 98
),
agg AS (
    SELECT
        anio,
        trimestre,
        -- Poblaciones totales
        SUM(fac)                                                                          AS p15ymas,
        SUM(CASE WHEN clase1 = 1                                    THEN fac ELSE 0 END)  AS pea,
        SUM(CASE WHEN clase2 = 2                                    THEN fac ELSE 0 END)  AS pd,
        SUM(CASE WHEN clase2 = 1                                    THEN fac ELSE 0 END)  AS po,
        SUM(CASE WHEN clase2 = 1 AND ambito1 <> 1                   THEN fac ELSE 0 END)  AS pona,
        -- Numeradores totales
        SUM(CASE WHEN clase2 = 1 AND dur9c    = 2                   THEN fac ELSE 0 END)  AS o_menos_15hrs,
        SUM(CASE WHEN clase2 = 1 AND tpg_p8a  = 1                   THEN fac ELSE 0 END)  AS pobot,
        SUM(CASE WHEN clase2 = 1 AND remune2c = 1                   THEN fac ELSE 0 END)  AS pasa,
        SUM(CASE WHEN clase2 = 1 AND sub_o    = 1                   THEN fac ELSE 0 END)  AS psub_o,
        SUM(CASE WHEN clase2 = 1 AND tcco    IN (1, 2, 3)           THEN fac ELSE 0 END)  AS pcco,
        SUM(CASE WHEN clase2 = 1 AND tue2     = 5                   THEN fac ELSE 0 END)  AS posi,
        SUM(CASE WHEN clase2 = 1 AND emp_ppal = 1                   THEN fac ELSE 0 END)  AS poi,
        SUM(CASE WHEN clase2 = 1 AND emp_ppal = 1 AND ambito1 <> 1  THEN fac ELSE 0 END)  AS poina,
        -- Poblaciones por sexo
        SUM(CASE WHEN sex = 1                                       THEN fac ELSE 0 END)  AS p15ymas_h,
        SUM(CASE WHEN sex = 2                                       THEN fac ELSE 0 END)  AS p15ymas_m,
        SUM(CASE WHEN clase1 = 1 AND sex = 1                        THEN fac ELSE 0 END)  AS pea_h,
        SUM(CASE WHEN clase1 = 1 AND sex = 2                        THEN fac ELSE 0 END)  AS pea_m,
        SUM(CASE WHEN clase2 = 2 AND sex = 1                        THEN fac ELSE 0 END)  AS pd_h,
        SUM(CASE WHEN clase2 = 2 AND sex = 2                        THEN fac ELSE 0 END)  AS pd_m,
        SUM(CASE WHEN clase2 = 1 AND sex = 1                        THEN fac ELSE 0 END)  AS po_h,
        SUM(CASE WHEN clase2 = 1 AND sex = 2                        THEN fac ELSE 0 END)  AS po_m,
        SUM(CASE WHEN clase2 = 1 AND ambito1 <> 1 AND sex = 1       THEN fac ELSE 0 END)  AS pona_h,
        SUM(CASE WHEN clase2 = 1 AND ambito1 <> 1 AND sex = 2       THEN fac ELSE 0 END)  AS pona_m,
        -- Numeradores por sexo
        SUM(CASE WHEN clase2 = 1 AND dur9c    = 2  AND sex = 1      THEN fac ELSE 0 END)  AS o_menos_15hrs_h,
        SUM(CASE WHEN clase2 = 1 AND dur9c    = 2  AND sex = 2      THEN fac ELSE 0 END)  AS o_menos_15hrs_m,
        SUM(CASE WHEN clase2 = 1 AND tpg_p8a  = 1  AND sex = 1      THEN fac ELSE 0 END)  AS pobot_h,
        SUM(CASE WHEN clase2 = 1 AND tpg_p8a  = 1  AND sex = 2      THEN fac ELSE 0 END)  AS pobot_m,
        SUM(CASE WHEN clase2 = 1 AND remune2c = 1  AND sex = 1      THEN fac ELSE 0 END)  AS pasa_h,
        SUM(CASE WHEN clase2 = 1 AND remune2c = 1  AND sex = 2      THEN fac ELSE 0 END)  AS pasa_m,
        SUM(CASE WHEN clase2 = 1 AND sub_o    = 1  AND sex = 1      THEN fac ELSE 0 END)  AS psub_o_h,
        SUM(CASE WHEN clase2 = 1 AND sub_o    = 1  AND sex = 2      THEN fac ELSE 0 END)  AS psub_o_m,
        SUM(CASE WHEN clase2 = 1 AND tcco IN (1,2,3) AND sex = 1    THEN fac ELSE 0 END)  AS pcco_h,
        SUM(CASE WHEN clase2 = 1 AND tcco IN (1,2,3) AND sex = 2    THEN fac ELSE 0 END)  AS pcco_m,
        SUM(CASE WHEN clase2 = 1 AND tue2     = 5  AND sex = 1      THEN fac ELSE 0 END)  AS posi_h,
        SUM(CASE WHEN clase2 = 1 AND tue2     = 5  AND sex = 2      THEN fac ELSE 0 END)  AS posi_m,
        SUM(CASE WHEN clase2 = 1 AND emp_ppal = 1  AND sex = 1      THEN fac ELSE 0 END)  AS poi_h,
        SUM(CASE WHEN clase2 = 1 AND emp_ppal = 1  AND sex = 2      THEN fac ELSE 0 END)  AS poi_m,
        SUM(CASE WHEN clase2 = 1 AND emp_ppal = 1 AND ambito1 <> 1 AND sex = 1 THEN fac ELSE 0 END) AS poina_h,
        SUM(CASE WHEN clase2 = 1 AND emp_ppal = 1 AND ambito1 <> 1 AND sex = 2 THEN fac ELSE 0 END) AS poina_m
    FROM base
    GROUP BY anio, trimestre
)
SELECT
    anio,
    trimestre,
    -- Poblaciones totales
    p15ymas, pea, pd, po, pona,
    -- Tasas totales
    ROUND((pea::numeric                          / NULLIF(p15ymas, 0)) * 100, 2) AS tp,
    ROUND((pd::numeric                           / NULLIF(pea,     0)) * 100, 2) AS td,
    ROUND(((pd + o_menos_15hrs)::numeric         / NULLIF(pea,     0)) * 100, 2) AS topd,
    ROUND(((pd + pobot)::numeric                 / NULLIF(pea,     0)) * 100, 2) AS tprg,
    ROUND((pasa::numeric                         / NULLIF(po,      0)) * 100, 2) AS tta,
    ROUND((psub_o::numeric                       / NULLIF(po,      0)) * 100, 2) AS tsub,
    ROUND((pcco::numeric                         / NULLIF(po,      0)) * 100, 2) AS tcco,
    ROUND((posi::numeric                         / NULLIF(po,      0)) * 100, 2) AS tosi1,
    ROUND((poi::numeric                          / NULLIF(po,      0)) * 100, 2) AS til1,
    ROUND((posi::numeric                         / NULLIF(pona,    0)) * 100, 2) AS tosi2,
    ROUND((poina::numeric                        / NULLIF(pona,    0)) * 100, 2) AS til2,
    -- Poblaciones por sexo
    p15ymas_h, p15ymas_m,
    pea_h,     pea_m,
    pd_h,      pd_m,
    po_h,      po_m,
    pona_h,    pona_m,
    -- Tasas por sexo
    ROUND((pea_h::numeric                        / NULLIF(p15ymas_h, 0)) * 100, 2) AS tp_h,
    ROUND((pea_m::numeric                        / NULLIF(p15ymas_m, 0)) * 100, 2) AS tp_m,
    ROUND((pd_h::numeric                         / NULLIF(pea_h,     0)) * 100, 2) AS td_h,
    ROUND((pd_m::numeric                         / NULLIF(pea_m,     0)) * 100, 2) AS td_m,
    ROUND(((pd_h + o_menos_15hrs_h)::numeric     / NULLIF(pea_h,     0)) * 100, 2) AS topd_h,
    ROUND(((pd_m + o_menos_15hrs_m)::numeric     / NULLIF(pea_m,     0)) * 100, 2) AS topd_m,
    ROUND(((pd_h + pobot_h)::numeric             / NULLIF(pea_h,     0)) * 100, 2) AS tprg_h,
    ROUND(((pd_m + pobot_m)::numeric             / NULLIF(pea_m,     0)) * 100, 2) AS tprg_m,
    ROUND((pasa_h::numeric                       / NULLIF(po_h,      0)) * 100, 2) AS tta_h,
    ROUND((pasa_m::numeric                       / NULLIF(po_m,      0)) * 100, 2) AS tta_m,
    ROUND((psub_o_h::numeric                     / NULLIF(po_h,      0)) * 100, 2) AS tsub_h,
    ROUND((psub_o_m::numeric                     / NULLIF(po_m,      0)) * 100, 2) AS tsub_m,
    ROUND((pcco_h::numeric                       / NULLIF(po_h,      0)) * 100, 2) AS tcco_h,
    ROUND((pcco_m::numeric                       / NULLIF(po_m,      0)) * 100, 2) AS tcco_m,
    ROUND((posi_h::numeric                       / NULLIF(po_h,      0)) * 100, 2) AS tosi1_h,
    ROUND((posi_m::numeric                       / NULLIF(po_m,      0)) * 100, 2) AS tosi1_m,
    ROUND((poi_h::numeric                        / NULLIF(po_h,      0)) * 100, 2) AS til1_h,
    ROUND((poi_m::numeric                        / NULLIF(po_m,      0)) * 100, 2) AS til1_m,
    ROUND((posi_h::numeric                       / NULLIF(pona_h,    0)) * 100, 2) AS tosi2_h,
    ROUND((posi_m::numeric                       / NULLIF(pona_m,    0)) * 100, 2) AS tosi2_m,
    ROUND((poina_h::numeric                      / NULLIF(pona_h,    0)) * 100, 2) AS til2_h,
    ROUND((poina_m::numeric                      / NULLIF(pona_m,    0)) * 100, 2) AS til2_m
FROM agg
ORDER BY anio, trimestre;

CREATE UNIQUE INDEX uix_mv_enoe_tasas_jalisco
    ON mv_enoe_tasas_jalisco (anio, trimestre);
