-- =======================================================================
-- V5: Vistas materializadas REPD para consumo GIS (iieg_gis)
-- =======================================================================
-- 6 vistas materializadas con geometrias municipales y tasas CONAPO.
-- Status: 2 = PERSONA DESAPARECIDA, 3 = PERSONA LOCALIZADA
-- Fecha base: disappearance_date truncado a mes (YYYY-MM-01)
-- Tasa: (conteo / pob_total CONAPO) * 100000
-- =======================================================================

-- ---------------------------------------------------------------------------
-- 1. personas_desaparecidas
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS personas_desaparecidas AS
WITH agg AS (
    SELECT
        DATE_TRUNC('month', c.disappearance_date)::date AS fecha,
        c.disappearance_municipality_id                  AS mun_id,
        COUNT(*)                                         AS total,
        COUNT(*) FILTER (WHERE c.sex_id = 1)             AS total_hombres,
        COUNT(*) FILTER (WHERE c.sex_id = 2)             AS total_mujeres
    FROM stg_repd_case_current c
    WHERE c.status_id = 2
      AND c.disappearance_date IS NOT NULL
      AND c.disappearance_municipality_id IS NOT NULL
    GROUP BY 1, 2
),
pob AS (
    SELECT
        municipio_id,
        anio,
        SUM(pob_total)                                   AS pob_total_all,
        SUM(pob_total) FILTER (WHERE sexo_id = 1)       AS pob_total_hombres,
        SUM(pob_total) FILTER (WHERE sexo_id = 2)       AS pob_total_mujeres
    FROM conapo_poblacion
    GROUP BY 1, 2
)
SELECT
    ROW_NUMBER() OVER ()::bigint                          AS fid,
    g.geom_iieg,
    g.geom_inegi,
    g.nomgeo::varchar(254)                               AS nombre,
    a.fecha,
    '14'::char(2)                                        AS clave_entidad,
    LPAD(g.cvegeo::text, 5, '0')::varchar(5)             AS clave_municipio,
    a.total,
    a.total_hombres,
    a.total_mujeres,
    CASE WHEN p.pob_total_all IS NOT NULL AND p.pob_total_all > 0
        THEN ROUND((a.total::numeric / p.pob_total_all) * 100000, 2)
        ELSE NULL
    END                                                  AS tasa_total,
    CASE WHEN p.pob_total_hombres IS NOT NULL AND p.pob_total_hombres > 0
        THEN ROUND((a.total_hombres::numeric / p.pob_total_hombres) * 100000, 2)
        ELSE NULL
    END                                                  AS tasa_hombres,
    CASE WHEN p.pob_total_mujeres IS NOT NULL AND p.pob_total_mujeres > 0
        THEN ROUND((a.total_mujeres::numeric / p.pob_total_mujeres) * 100000, 2)
        ELSE NULL
    END                                                  AS tasa_mujeres
FROM agg a
JOIN cvegeo_municipalities g ON a.mun_id = g.id
LEFT JOIN pob p
    ON p.municipio_id = g.cvegeo
   AND p.anio = EXTRACT(YEAR FROM a.fecha)::int
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS ix_personas_desaparecidas_fid
    ON personas_desaparecidas (fid);

-- ---------------------------------------------------------------------------
-- 2. personas_desaparecidas_hombres
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS personas_desaparecidas_hombres AS
WITH agg AS (
    SELECT
        DATE_TRUNC('month', c.disappearance_date)::date AS fecha,
        c.disappearance_municipality_id                  AS mun_id,
        COUNT(*)                                         AS total_hombres
    FROM stg_repd_case_current c
    WHERE c.status_id = 2
      AND c.sex_id = 1
      AND c.disappearance_date IS NOT NULL
      AND c.disappearance_municipality_id IS NOT NULL
    GROUP BY 1, 2
),
pob AS (
    SELECT
        municipio_id,
        anio,
        SUM(pob_total) AS pob_total_hombres
    FROM conapo_poblacion
    WHERE sexo_id = 1
    GROUP BY 1, 2
)
SELECT
    ROW_NUMBER() OVER ()::bigint                          AS fid,
    g.geom_iieg,
    g.geom_inegi,
    g.nomgeo::varchar(254)                               AS nombre,
    a.fecha,
    '14'::char(2)                                        AS clave_entidad,
    LPAD(g.cvegeo::text, 5, '0')::varchar(5)             AS clave_municipio,
    a.total_hombres,
    CASE WHEN p.pob_total_hombres IS NOT NULL AND p.pob_total_hombres > 0
        THEN ROUND((a.total_hombres::numeric / p.pob_total_hombres) * 100000, 2)
        ELSE NULL
    END                                                  AS tasa_hombres
FROM agg a
JOIN cvegeo_municipalities g ON a.mun_id = g.id
LEFT JOIN pob p
    ON p.municipio_id = g.cvegeo
   AND p.anio = EXTRACT(YEAR FROM a.fecha)::int
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS ix_personas_desaparecidas_hombres_fid
    ON personas_desaparecidas_hombres (fid);

-- ---------------------------------------------------------------------------
-- 3. personas_desaparecidas_mujeres
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS personas_desaparecidas_mujeres AS
WITH agg AS (
    SELECT
        DATE_TRUNC('month', c.disappearance_date)::date AS fecha,
        c.disappearance_municipality_id                  AS mun_id,
        COUNT(*)                                         AS total_mujeres
    FROM stg_repd_case_current c
    WHERE c.status_id = 2
      AND c.sex_id = 2
      AND c.disappearance_date IS NOT NULL
      AND c.disappearance_municipality_id IS NOT NULL
    GROUP BY 1, 2
),
pob AS (
    SELECT
        municipio_id,
        anio,
        SUM(pob_total) AS pob_total_mujeres
    FROM conapo_poblacion
    WHERE sexo_id = 2
    GROUP BY 1, 2
)
SELECT
    ROW_NUMBER() OVER ()::bigint                          AS fid,
    g.geom_iieg,
    g.geom_inegi,
    g.nomgeo::varchar(254)                               AS nombre,
    a.fecha,
    '14'::char(2)                                        AS clave_entidad,
    LPAD(g.cvegeo::text, 5, '0')::varchar(5)             AS clave_municipio,
    a.total_mujeres,
    CASE WHEN p.pob_total_mujeres IS NOT NULL AND p.pob_total_mujeres > 0
        THEN ROUND((a.total_mujeres::numeric / p.pob_total_mujeres) * 100000, 2)
        ELSE NULL
    END                                                  AS tasa_mujeres
FROM agg a
JOIN cvegeo_municipalities g ON a.mun_id = g.id
LEFT JOIN pob p
    ON p.municipio_id = g.cvegeo
   AND p.anio = EXTRACT(YEAR FROM a.fecha)::int
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS ix_personas_desaparecidas_mujeres_fid
    ON personas_desaparecidas_mujeres (fid);

-- ---------------------------------------------------------------------------
-- 4. personas_localizadas
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS personas_localizadas AS
WITH agg AS (
    SELECT
        DATE_TRUNC('month', c.disappearance_date)::date AS fecha,
        c.disappearance_municipality_id                  AS mun_id,
        COUNT(*)                                         AS total,
        COUNT(*) FILTER (WHERE c.sex_id = 1)             AS total_hombres,
        COUNT(*) FILTER (WHERE c.sex_id = 2)             AS total_mujeres
    FROM stg_repd_case_current c
    WHERE c.status_id = 3
      AND c.disappearance_date IS NOT NULL
      AND c.disappearance_municipality_id IS NOT NULL
    GROUP BY 1, 2
),
pob AS (
    SELECT
        municipio_id,
        anio,
        SUM(pob_total)                                   AS pob_total_all,
        SUM(pob_total) FILTER (WHERE sexo_id = 1)       AS pob_total_hombres,
        SUM(pob_total) FILTER (WHERE sexo_id = 2)       AS pob_total_mujeres
    FROM conapo_poblacion
    GROUP BY 1, 2
)
SELECT
    ROW_NUMBER() OVER ()::bigint                          AS fid,
    g.geom_iieg,
    g.geom_inegi,
    g.nomgeo::varchar(254)                               AS nombre,
    a.fecha,
    '14'::char(2)                                        AS clave_entidad,
    LPAD(g.cvegeo::text, 5, '0')::varchar(5)             AS clave_municipio,
    a.total,
    a.total_hombres,
    a.total_mujeres,
    CASE WHEN p.pob_total_all IS NOT NULL AND p.pob_total_all > 0
        THEN ROUND((a.total::numeric / p.pob_total_all) * 100000, 2)
        ELSE NULL
    END                                                  AS tasa_total,
    CASE WHEN p.pob_total_hombres IS NOT NULL AND p.pob_total_hombres > 0
        THEN ROUND((a.total_hombres::numeric / p.pob_total_hombres) * 100000, 2)
        ELSE NULL
    END                                                  AS tasa_hombres,
    CASE WHEN p.pob_total_mujeres IS NOT NULL AND p.pob_total_mujeres > 0
        THEN ROUND((a.total_mujeres::numeric / p.pob_total_mujeres) * 100000, 2)
        ELSE NULL
    END                                                  AS tasa_mujeres
FROM agg a
JOIN cvegeo_municipalities g ON a.mun_id = g.id
LEFT JOIN pob p
    ON p.municipio_id = g.cvegeo
   AND p.anio = EXTRACT(YEAR FROM a.fecha)::int
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS ix_personas_localizadas_fid
    ON personas_localizadas (fid);

-- ---------------------------------------------------------------------------
-- 5. personas_localizadas_hombres
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS personas_localizadas_hombres AS
WITH agg AS (
    SELECT
        DATE_TRUNC('month', c.disappearance_date)::date AS fecha,
        c.disappearance_municipality_id                  AS mun_id,
        COUNT(*)                                         AS total_hombres
    FROM stg_repd_case_current c
    WHERE c.status_id = 3
      AND c.sex_id = 1
      AND c.disappearance_date IS NOT NULL
      AND c.disappearance_municipality_id IS NOT NULL
    GROUP BY 1, 2
),
pob AS (
    SELECT
        municipio_id,
        anio,
        SUM(pob_total) AS pob_total_hombres
    FROM conapo_poblacion
    WHERE sexo_id = 1
    GROUP BY 1, 2
)
SELECT
    ROW_NUMBER() OVER ()::bigint                          AS fid,
    g.geom_iieg,
    g.geom_inegi,
    g.nomgeo::varchar(254)                               AS nombre,
    a.fecha,
    '14'::char(2)                                        AS clave_entidad,
    LPAD(g.cvegeo::text, 5, '0')::varchar(5)             AS clave_municipio,
    a.total_hombres,
    CASE WHEN p.pob_total_hombres IS NOT NULL AND p.pob_total_hombres > 0
        THEN ROUND((a.total_hombres::numeric / p.pob_total_hombres) * 100000, 2)
        ELSE NULL
    END                                                  AS tasa_hombres
FROM agg a
JOIN cvegeo_municipalities g ON a.mun_id = g.id
LEFT JOIN pob p
    ON p.municipio_id = g.cvegeo
   AND p.anio = EXTRACT(YEAR FROM a.fecha)::int
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS ix_personas_localizadas_hombres_fid
    ON personas_localizadas_hombres (fid);

-- ---------------------------------------------------------------------------
-- 6. personas_localizadas_mujeres
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS personas_localizadas_mujeres AS
WITH agg AS (
    SELECT
        DATE_TRUNC('month', c.disappearance_date)::date AS fecha,
        c.disappearance_municipality_id                  AS mun_id,
        COUNT(*)                                         AS total_mujeres
    FROM stg_repd_case_current c
    WHERE c.status_id = 3
      AND c.sex_id = 2
      AND c.disappearance_date IS NOT NULL
      AND c.disappearance_municipality_id IS NOT NULL
    GROUP BY 1, 2
),
pob AS (
    SELECT
        municipio_id,
        anio,
        SUM(pob_total) AS pob_total_mujeres
    FROM conapo_poblacion
    WHERE sexo_id = 2
    GROUP BY 1, 2
)
SELECT
    ROW_NUMBER() OVER ()::bigint                          AS fid,
    g.geom_iieg,
    g.geom_inegi,
    g.nomgeo::varchar(254)                               AS nombre,
    a.fecha,
    '14'::char(2)                                        AS clave_entidad,
    LPAD(g.cvegeo::text, 5, '0')::varchar(5)             AS clave_municipio,
    a.total_mujeres,
    CASE WHEN p.pob_total_mujeres IS NOT NULL AND p.pob_total_mujeres > 0
        THEN ROUND((a.total_mujeres::numeric / p.pob_total_mujeres) * 100000, 2)
        ELSE NULL
    END                                                  AS tasa_mujeres
FROM agg a
JOIN cvegeo_municipalities g ON a.mun_id = g.id
LEFT JOIN pob p
    ON p.municipio_id = g.cvegeo
   AND p.anio = EXTRACT(YEAR FROM a.fecha)::int
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS ix_personas_localizadas_mujeres_fid
    ON personas_localizadas_mujeres (fid);
