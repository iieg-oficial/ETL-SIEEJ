-- Criterio general INEGI: entrevista completa, residente habitual o nuevo, 15-98 años
-- Ponderador: fac (FAC_TRI) — siempre sumar, nunca contar registros
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_enoe_tasas AS
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
        -- Poblaciones base (SUM de FAC_TRI)
        SUM(fac)                                                                    AS p15ymas,
        SUM(CASE WHEN clase1 = 1                                  THEN fac ELSE 0 END) AS pea,
        SUM(CASE WHEN clase2 = 2                                  THEN fac ELSE 0 END) AS pd,
        SUM(CASE WHEN clase2 = 1                                  THEN fac ELSE 0 END) AS po,
        SUM(CASE WHEN clase2 = 1 AND ambito1 <> 1                 THEN fac ELSE 0 END) AS pona,
        -- Numeradores por tasa
        SUM(CASE WHEN clase2 = 1 AND dur9c   = 2                  THEN fac ELSE 0 END) AS o_menos_15hrs,
        SUM(CASE WHEN clase2 = 1 AND tpg_p8a = 1                  THEN fac ELSE 0 END) AS pobot,
        SUM(CASE WHEN clase2 = 1 AND remune2c = 1                 THEN fac ELSE 0 END) AS pasa,
        SUM(CASE WHEN clase2 = 1 AND sub_o   = 1                  THEN fac ELSE 0 END) AS psub_o,
        SUM(CASE WHEN clase2 = 1 AND tcco   IN (1, 2, 3)          THEN fac ELSE 0 END) AS pcco,
        SUM(CASE WHEN clase2 = 1 AND tue2    = 5                  THEN fac ELSE 0 END) AS posi,
        SUM(CASE WHEN clase2 = 1 AND emp_ppal = 1                 THEN fac ELSE 0 END) AS poi,
        SUM(CASE WHEN clase2 = 1 AND emp_ppal = 1 AND ambito1 <> 1 THEN fac ELSE 0 END) AS poina
    FROM base
    GROUP BY anio, trimestre, entidad_id, municipio_id
)
SELECT
    a.anio,
    a.trimestre,
    a.municipio_id,
    m.nomgeo                                                    AS municipio,
    -- Poblaciones base
    a.p15ymas,
    a.pea,
    a.pd,
    a.po,
    a.pona,
    -- I. Tasa de Participación: PEA / P15yMAS
    ROUND((a.pea::numeric    / NULLIF(a.p15ymas, 0)) * 100, 2) AS tp,
    -- II. Tasa de Desocupación: PD / PEA
    ROUND((a.pd::numeric     / NULLIF(a.pea,     0)) * 100, 2) AS td,
    -- III. Tasa de Ocupación Parcial y Desocupación: (PD + O<15hrs) / PEA
    ROUND(((a.pd + a.o_menos_15hrs)::numeric / NULLIF(a.pea, 0)) * 100, 2) AS topd,
    -- IV. Tasa de Presión General: (PD + POBOT) / PEA
    ROUND(((a.pd + a.pobot)::numeric         / NULLIF(a.pea, 0)) * 100, 2) AS tprg,
    -- V. Tasa de Trabajo Asalariado: PASA / PO
    ROUND((a.pasa::numeric   / NULLIF(a.po,    0)) * 100, 2) AS tta,
    -- VI. Tasa de Subocupación: PSUB_O / PO
    ROUND((a.psub_o::numeric / NULLIF(a.po,    0)) * 100, 2) AS tsub,
    -- VII. Tasa de Condiciones Críticas de Ocupación: PCCO / PO
    ROUND((a.pcco::numeric   / NULLIF(a.po,    0)) * 100, 2) AS tcco,
    -- VIII. Tasa de Ocupación en el Sector Informal 1: POSI / PO
    ROUND((a.posi::numeric   / NULLIF(a.po,    0)) * 100, 2) AS tosi1,
    -- IX. Tasa de Informalidad Laboral 1: POI / PO
    ROUND((a.poi::numeric    / NULLIF(a.po,    0)) * 100, 2) AS til1,
    -- X. Tasa de Ocupación en el Sector Informal 2: POSI / PONA
    ROUND((a.posi::numeric   / NULLIF(a.pona,  0)) * 100, 2) AS tosi2,
    -- XI. Tasa de Informalidad Laboral 2: POINA / PONA
    ROUND((a.poina::numeric  / NULLIF(a.pona,  0)) * 100, 2) AS til2
FROM agg a
LEFT JOIN cvegeo_municipalities m
       ON m.cve_ent = a.entidad_id AND m.cve_mun = a.municipio_id
ORDER BY a.anio, a.trimestre, a.municipio_id;

CREATE UNIQUE INDEX IF NOT EXISTS uix_mv_enoe_tasas
    ON mv_enoe_tasas (anio, trimestre, municipio_id);
