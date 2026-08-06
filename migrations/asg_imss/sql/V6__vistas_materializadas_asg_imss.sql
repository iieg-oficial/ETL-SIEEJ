-- ========================================================================
-- V6: Vistas materializadas ASG IMSS para consumo GIS (iieg_gis)
-- ========================================================================
-- 4 vistas materializadas con geometrias municipales:
--   * trabajadores_asegurados
--   * trabajadores_asegurados_hombres
--   * trabajadores_asegurados_mujeres
--   * brecha_salarial
-- Fuente: vw_asg_imss (que ya resuelve cvegeo por nombre).
-- Fecha base: mensual (DATE_TRUNC('month', fecha_corte)).
-- Filtro geografico: Jalisco (cve_ent = 14).
-- Metrica de empleo: ta (puestos de trabajo afiliados al IMSS).
-- ========================================================================

-- ---------------------------------------------------------------------------
-- 1. trabajadores_asegurados
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS trabajadores_asegurados AS
WITH agg AS (
    SELECT
        DATE_TRUNC('month', v.fecha_corte)::date AS fecha,
        v.cvegeo                                AS cvegeo,
        SUM(v.ta)                               AS total,
        SUM(v.ta) FILTER (WHERE v.sexo = '2')   AS total_mujeres,
        SUM(v.ta) FILTER (WHERE v.sexo = '1')   AS total_hombres,
        SUM(v.ta) FILTER (WHERE v.sexo = '3')   AS total_no_binario
    FROM vw_asg_imss v
    WHERE v.cvegeo IS NOT NULL
    GROUP BY 1, 2
)
SELECT
    ROW_NUMBER() OVER ()::bigint               AS fid,
    g.geom_iieg,
    g.geom_inegi,
    g.nomgeo::varchar(254)                     AS nombre,
    a.fecha,
    '14'::char(2)                              AS clave_entidad,
    LPAD(g.cvegeo::text, 5, '0')::varchar(5)   AS clave_municipio,
    a.total                                    AS total,
    a.total_mujeres                            AS total_mujeres,
    a.total_hombres                            AS total_hombres,
    a.total_no_binario                         AS total_no_binario,
    CASE WHEN a.total > 0
        THEN ROUND((a.total_mujeres::numeric / a.total) * 100, 2)
        ELSE NULL
    END                                        AS porcentaje_mujeres,
    CASE WHEN a.total > 0
        THEN ROUND((a.total_hombres::numeric / a.total) * 100, 2)
        ELSE NULL
    END                                        AS porcentaje_hombres
FROM agg a
JOIN cvegeo_municipalities g ON a.cvegeo = g.cvegeo
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS ix_trabajadores_asegurados_fid
    ON trabajadores_asegurados (fid);

-- ---------------------------------------------------------------------------
-- 2. trabajadores_asegurados_hombres
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS trabajadores_asegurados_hombres AS
WITH agg AS (
    SELECT
        DATE_TRUNC('month', v.fecha_corte)::date AS fecha,
        v.cvegeo                                AS cvegeo,
        SUM(v.ta) FILTER (WHERE v.sexo = '1')   AS total_hombres
    FROM vw_asg_imss v
    WHERE v.cvegeo IS NOT NULL
    GROUP BY 1, 2
)
SELECT
    ROW_NUMBER() OVER ()::bigint               AS fid,
    g.geom_iieg,
    g.geom_inegi,
    g.nomgeo::varchar(254)                     AS nombre,
    a.fecha,
    '14'::char(2)                              AS clave_entidad,
    LPAD(g.cvegeo::text, 5, '0')::varchar(5)   AS clave_municipio,
    a.total_hombres                            AS total_hombres,
    CASE WHEN a.total_hombres > 0
        THEN 100.00
        ELSE NULL
    END                                        AS porcentaje_hombres
FROM agg a
JOIN cvegeo_municipalities g ON a.cvegeo = g.cvegeo
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS ix_trabajadores_asegurados_hombres_fid
    ON trabajadores_asegurados_hombres (fid);

-- ---------------------------------------------------------------------------
-- 3. trabajadores_asegurados_mujeres
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS trabajadores_asegurados_mujeres AS
WITH agg AS (
    SELECT
        DATE_TRUNC('month', v.fecha_corte)::date AS fecha,
        v.cvegeo                                AS cvegeo,
        SUM(v.ta) FILTER (WHERE v.sexo = '2')   AS total_mujeres
    FROM vw_asg_imss v
    WHERE v.cvegeo IS NOT NULL
    GROUP BY 1, 2
)
SELECT
    ROW_NUMBER() OVER ()::bigint               AS fid,
    g.geom_iieg,
    g.geom_inegi,
    g.nomgeo::varchar(254)                     AS nombre,
    a.fecha,
    '14'::char(2)                              AS clave_entidad,
    LPAD(g.cvegeo::text, 5, '0')::varchar(5)   AS clave_municipio,
    a.total_mujeres                            AS total_mujeres,
    CASE WHEN a.total_mujeres > 0
        THEN 100.00
        ELSE NULL
    END                                        AS porcentaje_mujeres
FROM agg a
JOIN cvegeo_municipalities g ON a.cvegeo = g.cvegeo
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS ix_trabajadores_asegurados_mujeres_fid
    ON trabajadores_asegurados_mujeres (fid);

-- ---------------------------------------------------------------------------
-- 4. brecha_salarial
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS brecha_salarial AS
WITH salarios AS (
    SELECT
        DATE_TRUNC('month', v.fecha_corte)::date AS fecha,
        v.cvegeo                                     AS cvegeo,
        MAX(v.fecha_corte)                           AS fecha_corte,
        SUM(v.masa_sal_ta) FILTER (WHERE v.sexo = '2') AS masa_sal_mujeres,
        SUM(v.masa_sal_ta) FILTER (WHERE v.sexo = '1') AS masa_sal_hombres,
        SUM(v.ta_sal) FILTER (WHERE v.sexo = '2')      AS ta_sal_mujeres,
        SUM(v.ta_sal) FILTER (WHERE v.sexo = '1')      AS ta_sal_hombres
    FROM vw_asg_imss v
    WHERE v.cvegeo IS NOT NULL
    GROUP BY 1, 2
),
daily AS (
    SELECT
        s.*,
        CASE WHEN s.ta_sal_mujeres > 0
            THEN ROUND((s.masa_sal_mujeres / (s.ta_sal_mujeres * EXTRACT(DAY FROM s.fecha_corte)))::numeric, 2)
            ELSE NULL
        END AS salario_promedio_diario_mujeres,
        CASE WHEN s.ta_sal_hombres > 0
            THEN ROUND((s.masa_sal_hombres / (s.ta_sal_hombres * EXTRACT(DAY FROM s.fecha_corte)))::numeric, 2)
            ELSE NULL
        END AS salario_promedio_diario_hombres
    FROM salarios s
)
SELECT
    ROW_NUMBER() OVER ()::bigint               AS fid,
    g.geom_iieg,
    g.geom_inegi,
    g.nomgeo::varchar(254)                     AS nombre,
    d.fecha,
    '14'::char(2)                              AS clave_entidad,
    LPAD(g.cvegeo::text, 5, '0')::varchar(5)   AS clave_municipio,
    CASE WHEN d.salario_promedio_diario_hombres > 0
        THEN ROUND(((d.salario_promedio_diario_hombres - d.salario_promedio_diario_mujeres)
                    / d.salario_promedio_diario_hombres) * 100, 2)
        ELSE NULL
    END                                        AS brecha_salarial,
    d.salario_promedio_diario_mujeres,
    d.salario_promedio_diario_hombres
FROM daily d
JOIN cvegeo_municipalities g ON d.cvegeo = g.cvegeo
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS ix_brecha_salarial_fid
    ON brecha_salarial (fid);
