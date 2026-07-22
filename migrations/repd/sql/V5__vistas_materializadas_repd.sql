-- =======================================================================
-- V5: Vistas materializadas REPD para consumo GIS (iieg_gis)
-- =======================================================================
-- 6 vistas materializadas con geometrias municipales y tasas CONAPO.
-- El estatus y el sexo del REPD se resuelven por NOMBRE (JOIN a catalogos),
-- no por id, para no depender del orden de insercion de los catalogos.
-- Nombres de estatus: 'PERSONA DESAPARECIDA', 'PERSONA LOCALIZADA'.
-- Nombres de sexo REPD: 'HOMBRE', 'MUJER'.
-- CONAPO usa ids fijos (1 = HOMBRES, 2 = MUJERES) en conapo_poblacion.
-- Fecha base: fecha_desaparicion truncada a mes (YYYY-MM-01).
-- Tasa: (conteo / pob_total CONAPO) * 100000.
-- =======================================================================

-- ---------------------------------------------------------------------------
-- 1. personas_desaparecidas
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS personas_desaparecidas AS
WITH agg AS (
    SELECT
        DATE_TRUNC('month', c.fecha_desaparicion)::date AS fecha,
        c.municipio_desaparicion_id                      AS mun_id,
        COUNT(*)                                         AS total,
        COUNT(*) FILTER (WHERE sx.nombre = 'HOMBRE')     AS total_hombres,
        COUNT(*) FILTER (WHERE sx.nombre = 'MUJER')      AS total_mujeres
    FROM stg_repd_casos c
    JOIN cat_estatus e    ON c.estatus_id = e.id AND e.nombre = 'PERSONA DESAPARECIDA'
    LEFT JOIN cat_sexo sx ON c.sexo_id = sx.id
    WHERE c.fecha_desaparicion IS NOT NULL
      AND c.municipio_desaparicion_id IS NOT NULL
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
        DATE_TRUNC('month', c.fecha_desaparicion)::date AS fecha,
        c.municipio_desaparicion_id                      AS mun_id,
        COUNT(*)                                         AS total_hombres
    FROM stg_repd_casos c
    JOIN cat_estatus e ON c.estatus_id = e.id AND e.nombre = 'PERSONA DESAPARECIDA'
    JOIN cat_sexo sx   ON c.sexo_id = sx.id AND sx.nombre = 'HOMBRE'
    WHERE c.fecha_desaparicion IS NOT NULL
      AND c.municipio_desaparicion_id IS NOT NULL
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
        DATE_TRUNC('month', c.fecha_desaparicion)::date AS fecha,
        c.municipio_desaparicion_id                      AS mun_id,
        COUNT(*)                                         AS total_mujeres
    FROM stg_repd_casos c
    JOIN cat_estatus e ON c.estatus_id = e.id AND e.nombre = 'PERSONA DESAPARECIDA'
    JOIN cat_sexo sx   ON c.sexo_id = sx.id AND sx.nombre = 'MUJER'
    WHERE c.fecha_desaparicion IS NOT NULL
      AND c.municipio_desaparicion_id IS NOT NULL
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
        DATE_TRUNC('month', c.fecha_desaparicion)::date AS fecha,
        c.municipio_desaparicion_id                      AS mun_id,
        COUNT(*)                                         AS total,
        COUNT(*) FILTER (WHERE sx.nombre = 'HOMBRE')     AS total_hombres,
        COUNT(*) FILTER (WHERE sx.nombre = 'MUJER')      AS total_mujeres
    FROM stg_repd_casos c
    JOIN cat_estatus e    ON c.estatus_id = e.id AND e.nombre = 'PERSONA LOCALIZADA'
    LEFT JOIN cat_sexo sx ON c.sexo_id = sx.id
    WHERE c.fecha_desaparicion IS NOT NULL
      AND c.municipio_desaparicion_id IS NOT NULL
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
        DATE_TRUNC('month', c.fecha_desaparicion)::date AS fecha,
        c.municipio_desaparicion_id                      AS mun_id,
        COUNT(*)                                         AS total_hombres
    FROM stg_repd_casos c
    JOIN cat_estatus e ON c.estatus_id = e.id AND e.nombre = 'PERSONA LOCALIZADA'
    JOIN cat_sexo sx   ON c.sexo_id = sx.id AND sx.nombre = 'HOMBRE'
    WHERE c.fecha_desaparicion IS NOT NULL
      AND c.municipio_desaparicion_id IS NOT NULL
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
        DATE_TRUNC('month', c.fecha_desaparicion)::date AS fecha,
        c.municipio_desaparicion_id                      AS mun_id,
        COUNT(*)                                         AS total_mujeres
    FROM stg_repd_casos c
    JOIN cat_estatus e ON c.estatus_id = e.id AND e.nombre = 'PERSONA LOCALIZADA'
    JOIN cat_sexo sx   ON c.sexo_id = sx.id AND sx.nombre = 'MUJER'
    WHERE c.fecha_desaparicion IS NOT NULL
      AND c.municipio_desaparicion_id IS NOT NULL
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
