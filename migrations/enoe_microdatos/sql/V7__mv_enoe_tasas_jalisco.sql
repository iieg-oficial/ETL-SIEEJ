CREATE MATERIALIZED VIEW IF NOT EXISTS mv_enoe_tasas_jalisco AS
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
        SUM(fac)                                                                       AS p15ymas,
        SUM(CASE WHEN clase1 = 1                                   THEN fac ELSE 0 END) AS pea,
        SUM(CASE WHEN clase2 = 2                                   THEN fac ELSE 0 END) AS pd,
        SUM(CASE WHEN clase2 = 1                                   THEN fac ELSE 0 END) AS po,
        SUM(CASE WHEN clase2 = 1 AND ambito1 <> 1                  THEN fac ELSE 0 END) AS pona,
        SUM(CASE WHEN clase2 = 1 AND dur9c    = 2                  THEN fac ELSE 0 END) AS o_menos_15hrs,
        SUM(CASE WHEN clase2 = 1 AND tpg_p8a  = 1                  THEN fac ELSE 0 END) AS pobot,
        SUM(CASE WHEN clase2 = 1 AND remune2c = 1                  THEN fac ELSE 0 END) AS pasa,
        SUM(CASE WHEN clase2 = 1 AND sub_o    = 1                  THEN fac ELSE 0 END) AS psub_o,
        SUM(CASE WHEN clase2 = 1 AND tcco    IN (1, 2, 3)          THEN fac ELSE 0 END) AS pcco,
        SUM(CASE WHEN clase2 = 1 AND tue2     = 5                  THEN fac ELSE 0 END) AS posi,
        SUM(CASE WHEN clase2 = 1 AND emp_ppal = 1                  THEN fac ELSE 0 END) AS poi,
        SUM(CASE WHEN clase2 = 1 AND emp_ppal = 1 AND ambito1 <> 1 THEN fac ELSE 0 END) AS poina
    FROM base
    GROUP BY anio, trimestre
)
SELECT
    anio,
    trimestre,
    p15ymas,
    pea,
    pd,
    po,
    pona,
    ROUND((pea::numeric    / NULLIF(p15ymas, 0)) * 100, 2) AS tp,
    ROUND((pd::numeric     / NULLIF(pea,     0)) * 100, 2) AS td,
    ROUND(((pd + o_menos_15hrs)::numeric / NULLIF(pea, 0)) * 100, 2) AS topd,
    ROUND(((pd + pobot)::numeric         / NULLIF(pea, 0)) * 100, 2) AS tprg,
    ROUND((pasa::numeric   / NULLIF(po,    0)) * 100, 2) AS tta,
    ROUND((psub_o::numeric / NULLIF(po,    0)) * 100, 2) AS tsub,
    ROUND((pcco::numeric   / NULLIF(po,    0)) * 100, 2) AS tcco,
    ROUND((posi::numeric   / NULLIF(po,    0)) * 100, 2) AS tosi1,
    ROUND((poi::numeric    / NULLIF(po,    0)) * 100, 2) AS til1,
    ROUND((posi::numeric   / NULLIF(pona,  0)) * 100, 2) AS tosi2,
    ROUND((poina::numeric  / NULLIF(pona,  0)) * 100, 2) AS til2
FROM agg
ORDER BY anio, trimestre;

CREATE UNIQUE INDEX IF NOT EXISTS uix_mv_enoe_tasas_jalisco
    ON mv_enoe_tasas_jalisco (anio, trimestre);
