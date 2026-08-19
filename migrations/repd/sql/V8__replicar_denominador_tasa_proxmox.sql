-- =============================================================================
-- V8__replicar_denominador_tasa_proxmox.sql  |  Pipeline: repd
-- Decision: priorizar paridad exacta con proxmox sobre la correccion
-- demografica del dato. tasa_hombres/tasa_mujeres pasan a dividir entre
-- poblacion TOTAL del municipio (pob_total_all), igual que la tabla legacy
-- de proxmox (personas_desaparecidas_tabla), en vez de dividir entre la
-- poblacion CONAPO especifica de cada sexo como hacia V5/V7.
--
-- Validado: recalculando localmente con este mismo denominador se obtiene
-- match exacto (0 diferencias, 3508 filas) contra tasa_hombres/tasa_mujeres
-- de proxmox. Ver comparaciones/comparacion_repd_local_proxmox.md seccion 4.3.
--
-- tasa_total NO cambia (ya dividia entre pob_total_all en V5/V7).
-- Nota: esto reintroduce a proposito el bug de denominador de proxmox en
-- las vistas locales -- decision explicita para que ambas instancias
-- queden identicas, no un error de calculo.
-- =============================================================================

DROP MATERIALIZED VIEW IF EXISTS personas_localizadas_mujeres;
DROP MATERIALIZED VIEW IF EXISTS personas_localizadas_hombres;
DROP MATERIALIZED VIEW IF EXISTS personas_localizadas;
DROP MATERIALIZED VIEW IF EXISTS personas_desaparecidas_mujeres;
DROP MATERIALIZED VIEW IF EXISTS personas_desaparecidas_hombres;
DROP MATERIALIZED VIEW IF EXISTS personas_desaparecidas;

-- -----------------------------------------------------------------------------
-- 1. personas_desaparecidas
-- -----------------------------------------------------------------------------
CREATE MATERIALIZED VIEW personas_desaparecidas AS
WITH agg AS (
    SELECT
        DATE_TRUNC('month', c.fecha_desaparicion)::date       AS fecha,
        LPAD(g.cvegeo::text, 5, '0')                          AS clave_municipio,
        COUNT(*)                                              AS total,
        COUNT(*) FILTER (WHERE sx.nombre = 'HOMBRE')          AS total_hombres,
        COUNT(*) FILTER (WHERE sx.nombre = 'MUJER')           AS total_mujeres
    FROM stg_repd_casos c
    JOIN cat_estatus e            ON c.estatus_id = e.id AND e.nombre = 'PERSONA DESAPARECIDA'
    LEFT JOIN cat_sexo sx         ON c.sexo_id = sx.id
    JOIN cvegeo_municipalities g  ON c.municipio_desaparicion_id = g.id
    WHERE c.fecha_desaparicion IS NOT NULL
      AND g.cve_ent = 14
    GROUP BY 1, 2
),
pob AS (
    SELECT municipio_id, anio, SUM(pob_total) AS pob_total_all
    FROM conapo_poblacion
    GROUP BY 1, 2
),
grid AS (
    SELECT
        m.geom_iieg,
        m.geom_inegi,
        m.nomgeo,
        m.cvegeo,
        f.fecha
    FROM cvegeo_municipalities m
    CROSS JOIN (
        SELECT DISTINCT DATE_TRUNC('month', fecha_desaparicion)::date AS fecha
        FROM stg_repd_casos
        WHERE fecha_desaparicion IS NOT NULL
    ) f
    WHERE m.cve_ent = 14
)
SELECT
    ROW_NUMBER() OVER ()::bigint                              AS fid,
    grid.geom_iieg,
    grid.geom_inegi,
    grid.nomgeo::varchar(254)                                 AS nombre,
    grid.fecha,
    '14'::character(2)                                        AS clave_entidad,
    LPAD(grid.cvegeo::text, 5, '0')::character(5)             AS clave_municipio,
    COALESCE(a.total, 0)::integer                             AS total,
    COALESCE(a.total_hombres, 0)::integer                     AS total_hombres,
    COALESCE(a.total_mujeres, 0)::integer                     AS total_mujeres,
    CASE WHEN p.pob_total_all > 0
        THEN ROUND((COALESCE(a.total, 0)::numeric / p.pob_total_all) * 100000, 2)
        ELSE NULL
    END::numeric(12,2)                                        AS tasa_total,
    CASE WHEN p.pob_total_all > 0
        THEN ROUND((COALESCE(a.total_hombres, 0)::numeric / p.pob_total_all) * 100000, 2)
        ELSE NULL
    END::numeric(12,2)                                        AS tasa_hombres,
    CASE WHEN p.pob_total_all > 0
        THEN ROUND((COALESCE(a.total_mujeres, 0)::numeric / p.pob_total_all) * 100000, 2)
        ELSE NULL
    END::numeric(12,2)                                        AS tasa_mujeres
FROM grid
LEFT JOIN agg a ON a.clave_municipio = LPAD(grid.cvegeo::text, 5, '0') AND a.fecha = grid.fecha
LEFT JOIN pob p  ON p.municipio_id = grid.cvegeo AND p.anio = EXTRACT(YEAR FROM grid.fecha)::int
WITH NO DATA;

CREATE UNIQUE INDEX uix_personas_desaparecidas_nk ON personas_desaparecidas (clave_municipio, fecha);
CREATE INDEX ix_personas_desaparecidas_fecha ON personas_desaparecidas (fecha);
CREATE INDEX ix_personas_desaparecidas_mun ON personas_desaparecidas (clave_municipio);

-- -----------------------------------------------------------------------------
-- 2. personas_desaparecidas_hombres
-- -----------------------------------------------------------------------------
CREATE MATERIALIZED VIEW personas_desaparecidas_hombres AS
WITH agg AS (
    SELECT
        DATE_TRUNC('month', c.fecha_desaparicion)::date       AS fecha,
        LPAD(g.cvegeo::text, 5, '0')                          AS clave_municipio,
        COUNT(*)                                              AS total_hombres
    FROM stg_repd_casos c
    JOIN cat_estatus e            ON c.estatus_id = e.id AND e.nombre = 'PERSONA DESAPARECIDA'
    JOIN cat_sexo sx              ON c.sexo_id = sx.id AND sx.nombre = 'HOMBRE'
    JOIN cvegeo_municipalities g  ON c.municipio_desaparicion_id = g.id
    WHERE c.fecha_desaparicion IS NOT NULL
      AND g.cve_ent = 14
    GROUP BY 1, 2
),
pob AS (
    SELECT municipio_id, anio, SUM(pob_total) AS pob_total_all
    FROM conapo_poblacion
    GROUP BY 1, 2
),
grid AS (
    SELECT m.geom_iieg, m.geom_inegi, m.nomgeo, m.cvegeo, f.fecha
    FROM cvegeo_municipalities m
    CROSS JOIN (
        SELECT DISTINCT DATE_TRUNC('month', fecha_desaparicion)::date AS fecha
        FROM stg_repd_casos
        WHERE fecha_desaparicion IS NOT NULL
    ) f
    WHERE m.cve_ent = 14
)
SELECT
    ROW_NUMBER() OVER ()::bigint                              AS fid,
    grid.geom_iieg,
    grid.geom_inegi,
    grid.nomgeo::varchar(254)                                 AS nombre,
    grid.fecha,
    '14'::character(2)                                        AS clave_entidad,
    LPAD(grid.cvegeo::text, 5, '0')::character(5)             AS clave_municipio,
    COALESCE(a.total_hombres, 0)::integer                     AS total_hombres,
    CASE WHEN p.pob_total_all > 0
        THEN ROUND((COALESCE(a.total_hombres, 0)::numeric / p.pob_total_all) * 100000, 2)
        ELSE NULL
    END::numeric(12,2)                                        AS tasa_hombres
FROM grid
LEFT JOIN agg a ON a.clave_municipio = LPAD(grid.cvegeo::text, 5, '0') AND a.fecha = grid.fecha
LEFT JOIN pob p  ON p.municipio_id = grid.cvegeo AND p.anio = EXTRACT(YEAR FROM grid.fecha)::int
WITH NO DATA;

CREATE UNIQUE INDEX uix_personas_desaparecidas_hombres_nk ON personas_desaparecidas_hombres (clave_municipio, fecha);
CREATE INDEX ix_personas_desaparecidas_hombres_fecha ON personas_desaparecidas_hombres (fecha);
CREATE INDEX ix_personas_desaparecidas_hombres_mun ON personas_desaparecidas_hombres (clave_municipio);

-- -----------------------------------------------------------------------------
-- 3. personas_desaparecidas_mujeres
-- -----------------------------------------------------------------------------
CREATE MATERIALIZED VIEW personas_desaparecidas_mujeres AS
WITH agg AS (
    SELECT
        DATE_TRUNC('month', c.fecha_desaparicion)::date       AS fecha,
        LPAD(g.cvegeo::text, 5, '0')                          AS clave_municipio,
        COUNT(*)                                              AS total_mujeres
    FROM stg_repd_casos c
    JOIN cat_estatus e            ON c.estatus_id = e.id AND e.nombre = 'PERSONA DESAPARECIDA'
    JOIN cat_sexo sx              ON c.sexo_id = sx.id AND sx.nombre = 'MUJER'
    JOIN cvegeo_municipalities g  ON c.municipio_desaparicion_id = g.id
    WHERE c.fecha_desaparicion IS NOT NULL
      AND g.cve_ent = 14
    GROUP BY 1, 2
),
pob AS (
    SELECT municipio_id, anio, SUM(pob_total) AS pob_total_all
    FROM conapo_poblacion
    GROUP BY 1, 2
),
grid AS (
    SELECT m.geom_iieg, m.geom_inegi, m.nomgeo, m.cvegeo, f.fecha
    FROM cvegeo_municipalities m
    CROSS JOIN (
        SELECT DISTINCT DATE_TRUNC('month', fecha_desaparicion)::date AS fecha
        FROM stg_repd_casos
        WHERE fecha_desaparicion IS NOT NULL
    ) f
    WHERE m.cve_ent = 14
)
SELECT
    ROW_NUMBER() OVER ()::bigint                              AS fid,
    grid.geom_iieg,
    grid.geom_inegi,
    grid.nomgeo::varchar(254)                                 AS nombre,
    grid.fecha,
    '14'::character(2)                                        AS clave_entidad,
    LPAD(grid.cvegeo::text, 5, '0')::character(5)             AS clave_municipio,
    COALESCE(a.total_mujeres, 0)::integer                     AS total_mujeres,
    CASE WHEN p.pob_total_all > 0
        THEN ROUND((COALESCE(a.total_mujeres, 0)::numeric / p.pob_total_all) * 100000, 2)
        ELSE NULL
    END::numeric(12,2)                                        AS tasa_mujeres
FROM grid
LEFT JOIN agg a ON a.clave_municipio = LPAD(grid.cvegeo::text, 5, '0') AND a.fecha = grid.fecha
LEFT JOIN pob p  ON p.municipio_id = grid.cvegeo AND p.anio = EXTRACT(YEAR FROM grid.fecha)::int
WITH NO DATA;

CREATE UNIQUE INDEX uix_personas_desaparecidas_mujeres_nk ON personas_desaparecidas_mujeres (clave_municipio, fecha);
CREATE INDEX ix_personas_desaparecidas_mujeres_fecha ON personas_desaparecidas_mujeres (fecha);
CREATE INDEX ix_personas_desaparecidas_mujeres_mun ON personas_desaparecidas_mujeres (clave_municipio);

-- -----------------------------------------------------------------------------
-- 4. personas_localizadas
-- -----------------------------------------------------------------------------
CREATE MATERIALIZED VIEW personas_localizadas AS
WITH agg AS (
    SELECT
        DATE_TRUNC('month', c.fecha_desaparicion)::date                          AS fecha,
        LPAD(g.cvegeo::text, 5, '0')                                             AS clave_municipio,
        COUNT(*)                                                                  AS total,
        COUNT(*) FILTER (WHERE sx.nombre = 'HOMBRE')                             AS total_hombres,
        COUNT(*) FILTER (WHERE sx.nombre = 'MUJER')                              AS total_mujeres,
        COUNT(*) FILTER (WHERE cl.nombre = 'CON VIDA')                           AS con_vida,
        COUNT(*) FILTER (WHERE cl.nombre = 'SIN VIDA')                           AS sin_vida,
        COUNT(*) FILTER (WHERE cl.nombre = 'CON VIDA' AND sx.nombre = 'HOMBRE')  AS hombres_con_vida,
        COUNT(*) FILTER (WHERE cl.nombre = 'SIN VIDA' AND sx.nombre = 'HOMBRE')  AS hombres_sin_vida,
        COUNT(*) FILTER (WHERE cl.nombre = 'CON VIDA' AND sx.nombre = 'MUJER')   AS mujeres_con_vida,
        COUNT(*) FILTER (WHERE cl.nombre = 'SIN VIDA' AND sx.nombre = 'MUJER')   AS mujeres_sin_vida
    FROM stg_repd_casos c
    JOIN cat_estatus e                        ON c.estatus_id = e.id AND e.nombre = 'PERSONA LOCALIZADA'
    LEFT JOIN cat_sexo sx                      ON c.sexo_id = sx.id
    LEFT JOIN cat_condicion_localizacion cl    ON c.condicion_localizacion_id = cl.id
    JOIN cvegeo_municipalities g               ON c.municipio_desaparicion_id = g.id
    WHERE c.fecha_desaparicion IS NOT NULL
      AND g.cve_ent = 14
    GROUP BY 1, 2
),
pob AS (
    SELECT municipio_id, anio, SUM(pob_total) AS pob_total_all
    FROM conapo_poblacion
    GROUP BY 1, 2
),
grid AS (
    SELECT m.geom_iieg, m.geom_inegi, m.nomgeo, m.cvegeo, f.fecha
    FROM cvegeo_municipalities m
    CROSS JOIN (
        SELECT DISTINCT DATE_TRUNC('month', fecha_desaparicion)::date AS fecha
        FROM stg_repd_casos
        WHERE fecha_desaparicion IS NOT NULL
    ) f
    WHERE m.cve_ent = 14
)
SELECT
    ROW_NUMBER() OVER ()::bigint                              AS fid,
    grid.geom_iieg,
    grid.geom_inegi,
    grid.nomgeo::varchar(254)                                 AS nombre,
    grid.fecha,
    '14'::character(2)                                        AS clave_entidad,
    LPAD(grid.cvegeo::text, 5, '0')::character(5)             AS clave_municipio,
    COALESCE(a.total, 0)::integer                             AS total,
    COALESCE(a.total_hombres, 0)::integer                     AS total_hombres,
    COALESCE(a.total_mujeres, 0)::integer                     AS total_mujeres,
    COALESCE(a.con_vida, 0)::bigint                           AS con_vida,
    COALESCE(a.sin_vida, 0)::bigint                           AS sin_vida,
    COALESCE(a.hombres_con_vida, 0)::bigint                   AS hombres_con_vida,
    COALESCE(a.hombres_sin_vida, 0)::bigint                   AS hombres_sin_vida,
    COALESCE(a.mujeres_con_vida, 0)::bigint                   AS mujeres_con_vida,
    COALESCE(a.mujeres_sin_vida, 0)::bigint                   AS mujeres_sin_vida,
    CASE WHEN p.pob_total_all > 0
        THEN ROUND((COALESCE(a.total, 0)::numeric / p.pob_total_all) * 100000, 2)
        ELSE NULL
    END::numeric(12,2)                                        AS tasa_total,
    CASE WHEN p.pob_total_all > 0
        THEN ROUND((COALESCE(a.total_hombres, 0)::numeric / p.pob_total_all) * 100000, 2)
        ELSE NULL
    END::numeric(12,2)                                        AS tasa_hombres,
    CASE WHEN p.pob_total_all > 0
        THEN ROUND((COALESCE(a.total_mujeres, 0)::numeric / p.pob_total_all) * 100000, 2)
        ELSE NULL
    END::numeric(12,2)                                        AS tasa_mujeres
FROM grid
LEFT JOIN agg a ON a.clave_municipio = LPAD(grid.cvegeo::text, 5, '0') AND a.fecha = grid.fecha
LEFT JOIN pob p  ON p.municipio_id = grid.cvegeo AND p.anio = EXTRACT(YEAR FROM grid.fecha)::int
WITH NO DATA;

CREATE UNIQUE INDEX uix_personas_localizadas_nk ON personas_localizadas (clave_municipio, fecha);
CREATE INDEX ix_personas_localizadas_fecha ON personas_localizadas (fecha);
CREATE INDEX ix_personas_localizadas_mun ON personas_localizadas (clave_municipio);

-- -----------------------------------------------------------------------------
-- 5. personas_localizadas_hombres
-- -----------------------------------------------------------------------------
CREATE MATERIALIZED VIEW personas_localizadas_hombres AS
WITH agg AS (
    SELECT
        DATE_TRUNC('month', c.fecha_desaparicion)::date                          AS fecha,
        LPAD(g.cvegeo::text, 5, '0')                                             AS clave_municipio,
        COUNT(*)                                                                  AS total_hombres,
        COUNT(*) FILTER (WHERE cl.nombre = 'CON VIDA')                           AS hombres_con_vida,
        COUNT(*) FILTER (WHERE cl.nombre = 'SIN VIDA')                           AS hombres_sin_vida
    FROM stg_repd_casos c
    JOIN cat_estatus e                        ON c.estatus_id = e.id AND e.nombre = 'PERSONA LOCALIZADA'
    JOIN cat_sexo sx                           ON c.sexo_id = sx.id AND sx.nombre = 'HOMBRE'
    LEFT JOIN cat_condicion_localizacion cl    ON c.condicion_localizacion_id = cl.id
    JOIN cvegeo_municipalities g               ON c.municipio_desaparicion_id = g.id
    WHERE c.fecha_desaparicion IS NOT NULL
      AND g.cve_ent = 14
    GROUP BY 1, 2
),
pob AS (
    SELECT municipio_id, anio, SUM(pob_total) AS pob_total_all
    FROM conapo_poblacion
    GROUP BY 1, 2
),
grid AS (
    SELECT m.geom_iieg, m.geom_inegi, m.nomgeo, m.cvegeo, f.fecha
    FROM cvegeo_municipalities m
    CROSS JOIN (
        SELECT DISTINCT DATE_TRUNC('month', fecha_desaparicion)::date AS fecha
        FROM stg_repd_casos
        WHERE fecha_desaparicion IS NOT NULL
    ) f
    WHERE m.cve_ent = 14
)
SELECT
    ROW_NUMBER() OVER ()::bigint                              AS fid,
    grid.geom_iieg,
    grid.geom_inegi,
    grid.nomgeo::varchar(254)                                 AS nombre,
    grid.fecha,
    '14'::character(2)                                        AS clave_entidad,
    LPAD(grid.cvegeo::text, 5, '0')::character(5)             AS clave_municipio,
    COALESCE(a.total_hombres, 0)::integer                     AS total_hombres,
    COALESCE(a.hombres_con_vida, 0)::bigint                   AS hombres_con_vida,
    COALESCE(a.hombres_sin_vida, 0)::bigint                   AS hombres_sin_vida,
    CASE WHEN p.pob_total_all > 0
        THEN ROUND((COALESCE(a.total_hombres, 0)::numeric / p.pob_total_all) * 100000, 2)
        ELSE NULL
    END::numeric(12,2)                                        AS tasa_hombres
FROM grid
LEFT JOIN agg a ON a.clave_municipio = LPAD(grid.cvegeo::text, 5, '0') AND a.fecha = grid.fecha
LEFT JOIN pob p  ON p.municipio_id = grid.cvegeo AND p.anio = EXTRACT(YEAR FROM grid.fecha)::int
WITH NO DATA;

CREATE UNIQUE INDEX uix_personas_localizadas_hombres_nk ON personas_localizadas_hombres (clave_municipio, fecha);
CREATE INDEX ix_personas_localizadas_hombres_fecha ON personas_localizadas_hombres (fecha);
CREATE INDEX ix_personas_localizadas_hombres_mun ON personas_localizadas_hombres (clave_municipio);

-- -----------------------------------------------------------------------------
-- 6. personas_localizadas_mujeres
-- -----------------------------------------------------------------------------
CREATE MATERIALIZED VIEW personas_localizadas_mujeres AS
WITH agg AS (
    SELECT
        DATE_TRUNC('month', c.fecha_desaparicion)::date                          AS fecha,
        LPAD(g.cvegeo::text, 5, '0')                                             AS clave_municipio,
        COUNT(*)                                                                  AS total_mujeres,
        COUNT(*) FILTER (WHERE cl.nombre = 'CON VIDA')                           AS mujeres_con_vida,
        COUNT(*) FILTER (WHERE cl.nombre = 'SIN VIDA')                           AS mujeres_sin_vida
    FROM stg_repd_casos c
    JOIN cat_estatus e                        ON c.estatus_id = e.id AND e.nombre = 'PERSONA LOCALIZADA'
    JOIN cat_sexo sx                           ON c.sexo_id = sx.id AND sx.nombre = 'MUJER'
    LEFT JOIN cat_condicion_localizacion cl    ON c.condicion_localizacion_id = cl.id
    JOIN cvegeo_municipalities g               ON c.municipio_desaparicion_id = g.id
    WHERE c.fecha_desaparicion IS NOT NULL
      AND g.cve_ent = 14
    GROUP BY 1, 2
),
pob AS (
    SELECT municipio_id, anio, SUM(pob_total) AS pob_total_all
    FROM conapo_poblacion
    GROUP BY 1, 2
),
grid AS (
    SELECT m.geom_iieg, m.geom_inegi, m.nomgeo, m.cvegeo, f.fecha
    FROM cvegeo_municipalities m
    CROSS JOIN (
        SELECT DISTINCT DATE_TRUNC('month', fecha_desaparicion)::date AS fecha
        FROM stg_repd_casos
        WHERE fecha_desaparicion IS NOT NULL
    ) f
    WHERE m.cve_ent = 14
)
SELECT
    ROW_NUMBER() OVER ()::bigint                              AS fid,
    grid.geom_iieg,
    grid.geom_inegi,
    grid.nomgeo::varchar(254)                                 AS nombre,
    grid.fecha,
    '14'::character(2)                                        AS clave_entidad,
    LPAD(grid.cvegeo::text, 5, '0')::character(5)             AS clave_municipio,
    COALESCE(a.total_mujeres, 0)::integer                     AS total_mujeres,
    COALESCE(a.mujeres_con_vida, 0)::bigint                   AS mujeres_con_vida,
    COALESCE(a.mujeres_sin_vida, 0)::bigint                   AS mujeres_sin_vida,
    CASE WHEN p.pob_total_all > 0
        THEN ROUND((COALESCE(a.total_mujeres, 0)::numeric / p.pob_total_all) * 100000, 2)
        ELSE NULL
    END::numeric(12,2)                                        AS tasa_mujeres
FROM grid
LEFT JOIN agg a ON a.clave_municipio = LPAD(grid.cvegeo::text, 5, '0') AND a.fecha = grid.fecha
LEFT JOIN pob p  ON p.municipio_id = grid.cvegeo AND p.anio = EXTRACT(YEAR FROM grid.fecha)::int
WITH NO DATA;

CREATE UNIQUE INDEX uix_personas_localizadas_mujeres_nk ON personas_localizadas_mujeres (clave_municipio, fecha);
CREATE INDEX ix_personas_localizadas_mujeres_fecha ON personas_localizadas_mujeres (fecha);
CREATE INDEX ix_personas_localizadas_mujeres_mun ON personas_localizadas_mujeres (clave_municipio);
