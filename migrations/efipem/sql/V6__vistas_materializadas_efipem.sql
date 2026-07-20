-- =======================================================================
-- V6: Vistas materializadas EFIPEM para consumo GIS (iieg_gis)
-- =======================================================================
-- 11 vistas materializadas con geometrias municipales.
-- Tema: 1=Egresos, 2=Ingresos
-- Clasificador: 1=Capitulo, 5=Tema
-- Fecha base: anual (anio -> YYYY-01-01)
-- Precios reales: deflactados con INPC base 2023=100 (indice_general)
-- Per capita: deflactado / pob_total CONAPO del anio correspondiente
-- Ingresos propios = Impuestos + Productos + Aprovechamientos
-- =======================================================================

-- ---------------------------------------------------------------------------
-- Helper CTE reutilizable para anios disponibles
-- ---------------------------------------------------------------------------
-- Las MVs se construyen con CROSS JOIN de municipios x anios con datos
-- y LEFT JOIN de los conceptos para que todos los municipios tengan filas.

-- ---------------------------------------------------------------------------
-- 1. ingresos_totales
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS ingresos_totales AS
SELECT
    ROW_NUMBER() OVER ()::bigint                  AS fid,
    g.geom_iieg,
    g.geom_inegi,
    g.nomgeo::varchar(254)                        AS nombre,
    make_date(f.anio, 1, 1)                       AS fecha,
    '14'::char(2)                                 AS clave_entidad,
    LPAD(g.cvegeo::text, 5, '0')::varchar(5)     AS clave_municipio,
    f.valor
FROM stg_efipem f
JOIN cat_tema tm        ON f.tema_id = tm.id     AND tm.name = 'Ingresos'
JOIN cat_clasificador cl ON f.clasificador_id = cl.id AND cl.name = 'Tema'
JOIN cat_concepto cp     ON f.concepto_id = cp.id AND cp.name = 'Total de ingresos'
JOIN cvegeo_municipalities g ON f.cvegeo = LPAD(g.cvegeo::text, 5, '0')
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS ix_ingresos_totales_fid ON ingresos_totales (fid);

-- ---------------------------------------------------------------------------
-- 2. ingresos_totales_reales_precios_2023
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS ingresos_totales_reales_precios_2023 AS
WITH idx_2023 AS (
    SELECT AVG(indice_de_precios) AS indice
    FROM inpc_nacional
    WHERE objeto_gasto_id = 1
      AND EXTRACT(YEAR FROM fecha) = 2023
),
idx_anual AS (
    SELECT EXTRACT(YEAR FROM fecha)::int AS anio, AVG(indice_de_precios) AS indice
    FROM inpc_nacional
    WHERE objeto_gasto_id = 1
    GROUP BY 1
)
SELECT
    ROW_NUMBER() OVER ()::bigint                  AS fid,
    g.geom_iieg,
    g.geom_inegi,
    g.nomgeo::varchar(254)                        AS nombre,
    make_date(f.anio, 1, 1)                       AS fecha,
    '14'::char(2)                                 AS clave_entidad,
    LPAD(g.cvegeo::text, 5, '0')::varchar(5)     AS clave_municipio,
    CASE WHEN ia.indice IS NOT NULL AND ia.indice > 0
        THEN ROUND((f.valor::numeric * (i2023.indice / ia.indice))::numeric, 2)
        ELSE NULL
    END                                           AS valor
FROM stg_efipem f
JOIN cat_tema tm        ON f.tema_id = tm.id     AND tm.name = 'Ingresos'
JOIN cat_clasificador cl ON f.clasificador_id = cl.id AND cl.name = 'Tema'
JOIN cat_concepto cp     ON f.concepto_id = cp.id AND cp.name = 'Total de ingresos'
JOIN cvegeo_municipalities g ON f.cvegeo = LPAD(g.cvegeo::text, 5, '0')
CROSS JOIN idx_2023 i2023
LEFT JOIN idx_anual ia ON ia.anio = f.anio
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS ix_ingresos_totales_reales_precios_2023_fid
    ON ingresos_totales_reales_precios_2023 (fid);

-- ---------------------------------------------------------------------------
-- 3. ingresos_totales_reales_per_capita_precios_2023
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS ingresos_totales_reales_per_capita_precios_2023 AS
WITH idx_2023 AS (
    SELECT AVG(indice_de_precios) AS indice
    FROM inpc_nacional
    WHERE objeto_gasto_id = 1
      AND EXTRACT(YEAR FROM fecha) = 2023
),
idx_anual AS (
    SELECT EXTRACT(YEAR FROM fecha)::int AS anio, AVG(indice_de_precios) AS indice
    FROM inpc_nacional
    WHERE objeto_gasto_id = 1
    GROUP BY 1
),
pob AS (
    SELECT municipio_id, anio, SUM(pob_total) AS pob_total
    FROM conapo_poblacion
    GROUP BY 1, 2
)
SELECT
    ROW_NUMBER() OVER ()::bigint                  AS fid,
    g.geom_iieg,
    g.geom_inegi,
    g.nomgeo::varchar(254)                        AS nombre,
    make_date(f.anio, 1, 1)                       AS fecha,
    '14'::char(2)                                 AS clave_entidad,
    LPAD(g.cvegeo::text, 5, '0')::varchar(5)     AS clave_municipio,
    CASE
        WHEN ia.indice IS NOT NULL AND ia.indice > 0 AND p.pob_total IS NOT NULL AND p.pob_total > 0
        THEN ROUND(((f.valor::numeric * (i2023.indice / ia.indice)) / p.pob_total)::numeric, 2)
        ELSE NULL
    END                                           AS valor
FROM stg_efipem f
JOIN cat_tema tm        ON f.tema_id = tm.id     AND tm.name = 'Ingresos'
JOIN cat_clasificador cl ON f.clasificador_id = cl.id AND cl.name = 'Tema'
JOIN cat_concepto cp     ON f.concepto_id = cp.id AND cp.name = 'Total de ingresos'
JOIN cvegeo_municipalities g ON f.cvegeo = LPAD(g.cvegeo::text, 5, '0')
CROSS JOIN idx_2023 i2023
LEFT JOIN idx_anual ia ON ia.anio = f.anio
LEFT JOIN pob p ON p.municipio_id = g.cvegeo AND p.anio = f.anio
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS ix_ingresos_totales_reales_per_capita_precios_2023_fid
    ON ingresos_totales_reales_per_capita_precios_2023 (fid);

-- ---------------------------------------------------------------------------
-- 4. ingresos_participaciones
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS ingresos_participaciones AS
SELECT
    ROW_NUMBER() OVER ()::bigint                  AS fid,
    g.geom_iieg,
    g.geom_inegi,
    g.nomgeo::varchar(254)                        AS nombre,
    make_date(f.anio, 1, 1)                       AS fecha,
    '14'::char(2)                                 AS clave_entidad,
    LPAD(g.cvegeo::text, 5, '0')::varchar(5)     AS clave_municipio,
    f.valor
FROM stg_efipem f
JOIN cat_tema tm        ON f.tema_id = tm.id     AND tm.name = 'Ingresos'
JOIN cat_clasificador cl ON f.clasificador_id = cl.id AND cl.name = 'Capítulo'
JOIN cat_concepto cp     ON f.concepto_id = cp.id AND cp.name = 'Participaciones federales'
JOIN cvegeo_municipalities g ON f.cvegeo = LPAD(g.cvegeo::text, 5, '0')
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS ix_ingresos_participaciones_fid ON ingresos_participaciones (fid);

-- ---------------------------------------------------------------------------
-- 5. ingresos_financiamiento
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS ingresos_financiamiento AS
SELECT
    ROW_NUMBER() OVER ()::bigint                  AS fid,
    g.geom_iieg,
    g.geom_inegi,
    g.nomgeo::varchar(254)                        AS nombre,
    make_date(f.anio, 1, 1)                       AS fecha,
    '14'::char(2)                                 AS clave_entidad,
    LPAD(g.cvegeo::text, 5, '0')::varchar(5)     AS clave_municipio,
    f.valor
FROM stg_efipem f
JOIN cat_tema tm        ON f.tema_id = tm.id     AND tm.name = 'Ingresos'
JOIN cat_clasificador cl ON f.clasificador_id = cl.id AND cl.name = 'Capítulo'
JOIN cat_concepto cp     ON f.concepto_id = cp.id AND cp.name = 'Financiamiento'
JOIN cvegeo_municipalities g ON f.cvegeo = LPAD(g.cvegeo::text, 5, '0')
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS ix_ingresos_financiamiento_fid ON ingresos_financiamiento (fid);

-- ---------------------------------------------------------------------------
-- 6. porcentaje_ingresos_participaciones
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS porcentaje_ingresos_participaciones AS
WITH tot AS (
    SELECT f.anio, f.cvegeo, f.valor AS total
    FROM stg_efipem f
    JOIN cat_tema tm        ON f.tema_id = tm.id     AND tm.name = 'Ingresos'
    JOIN cat_clasificador cl ON f.clasificador_id = cl.id AND cl.name = 'Tema'
    JOIN cat_concepto cp     ON f.concepto_id = cp.id AND cp.name = 'Total de ingresos'
),
part AS (
    SELECT f.anio, f.cvegeo, f.valor AS participaciones
    FROM stg_efipem f
    JOIN cat_tema tm        ON f.tema_id = tm.id     AND tm.name = 'Ingresos'
    JOIN cat_clasificador cl ON f.clasificador_id = cl.id AND cl.name = 'Capítulo'
    JOIN cat_concepto cp     ON f.concepto_id = cp.id AND cp.name = 'Participaciones federales'
)
SELECT
    ROW_NUMBER() OVER ()::bigint                  AS fid,
    g.geom_iieg,
    g.geom_inegi,
    g.nomgeo::varchar(254)                        AS nombre,
    make_date(p.anio, 1, 1)                       AS fecha,
    '14'::char(2)                                 AS clave_entidad,
    LPAD(g.cvegeo::text, 5, '0')::varchar(5)     AS clave_municipio,
    CASE WHEN t.total IS NOT NULL AND t.total > 0
        THEN ROUND((p.participaciones::numeric / t.total) * 100, 2)
        ELSE NULL
    END                                           AS valor
FROM part p
JOIN tot t ON p.anio = t.anio AND p.cvegeo = t.cvegeo
JOIN cvegeo_municipalities g ON p.cvegeo = LPAD(g.cvegeo::text, 5, '0')
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS ix_porcentaje_ingresos_participaciones_fid
    ON porcentaje_ingresos_participaciones (fid);

-- ---------------------------------------------------------------------------
-- 7. porcentaje_ingresos_financiamiento
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS porcentaje_ingresos_financiamiento AS
WITH tot AS (
    SELECT f.anio, f.cvegeo, f.valor AS total
    FROM stg_efipem f
    JOIN cat_tema tm        ON f.tema_id = tm.id     AND tm.name = 'Ingresos'
    JOIN cat_clasificador cl ON f.clasificador_id = cl.id AND cl.name = 'Tema'
    JOIN cat_concepto cp     ON f.concepto_id = cp.id AND cp.name = 'Total de ingresos'
),
fin AS (
    SELECT f.anio, f.cvegeo, f.valor AS financiamiento
    FROM stg_efipem f
    JOIN cat_tema tm        ON f.tema_id = tm.id     AND tm.name = 'Ingresos'
    JOIN cat_clasificador cl ON f.clasificador_id = cl.id AND cl.name = 'Capítulo'
    JOIN cat_concepto cp     ON f.concepto_id = cp.id AND cp.name = 'Financiamiento'
)
SELECT
    ROW_NUMBER() OVER ()::bigint                  AS fid,
    g.geom_iieg,
    g.geom_inegi,
    g.nomgeo::varchar(254)                        AS nombre,
    make_date(fin.anio, 1, 1)                     AS fecha,
    '14'::char(2)                                 AS clave_entidad,
    LPAD(g.cvegeo::text, 5, '0')::varchar(5)     AS clave_municipio,
    CASE WHEN t.total IS NOT NULL AND t.total > 0
        THEN ROUND((fin.financiamiento::numeric / t.total) * 100, 2)
        ELSE NULL
    END                                           AS valor
FROM fin
JOIN tot t ON fin.anio = t.anio AND fin.cvegeo = t.cvegeo
JOIN cvegeo_municipalities g ON fin.cvegeo = LPAD(g.cvegeo::text, 5, '0')
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS ix_porcentaje_ingresos_financiamiento_fid
    ON porcentaje_ingresos_financiamiento (fid);

-- ---------------------------------------------------------------------------
-- 8. porcentaje_ingresos_propios
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS porcentaje_ingresos_propios AS
WITH tot AS (
    SELECT f.anio, f.cvegeo, f.valor AS total
    FROM stg_efipem f
    JOIN cat_tema tm        ON f.tema_id = tm.id     AND tm.name = 'Ingresos'
    JOIN cat_clasificador cl ON f.clasificador_id = cl.id AND cl.name = 'Tema'
    JOIN cat_concepto cp     ON f.concepto_id = cp.id AND cp.name = 'Total de ingresos'
),
propios AS (
    SELECT f.anio, f.cvegeo, SUM(f.valor) AS ingresos_propios
    FROM stg_efipem f
    JOIN cat_tema tm        ON f.tema_id = tm.id     AND tm.name = 'Ingresos'
    JOIN cat_clasificador cl ON f.clasificador_id = cl.id AND cl.name = 'Capítulo'
    JOIN cat_concepto cp     ON f.concepto_id = cp.id
        AND cp.name IN ('Impuestos', 'Productos', 'Aprovechamientos')
    GROUP BY f.anio, f.cvegeo
)
SELECT
    ROW_NUMBER() OVER ()::bigint                  AS fid,
    g.geom_iieg,
    g.geom_inegi,
    g.nomgeo::varchar(254)                        AS nombre,
    make_date(p.anio, 1, 1)                       AS fecha,
    '14'::char(2)                                 AS clave_entidad,
    LPAD(g.cvegeo::text, 5, '0')::varchar(5)     AS clave_municipio,
    CASE WHEN t.total IS NOT NULL AND t.total > 0
        THEN ROUND((p.ingresos_propios::numeric / t.total) * 100, 2)
        ELSE NULL
    END                                           AS valor
FROM propios p
JOIN tot t ON p.anio = t.anio AND p.cvegeo = t.cvegeo
JOIN cvegeo_municipalities g ON p.cvegeo = LPAD(g.cvegeo::text, 5, '0')
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS ix_porcentaje_ingresos_propios_fid
    ON porcentaje_ingresos_propios (fid);

-- ---------------------------------------------------------------------------
-- 9. egresos_totales
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS egresos_totales AS
SELECT
    ROW_NUMBER() OVER ()::bigint                  AS fid,
    g.geom_iieg,
    g.geom_inegi,
    g.nomgeo::varchar(254)                        AS nombre,
    make_date(f.anio, 1, 1)                       AS fecha,
    '14'::char(2)                                 AS clave_entidad,
    LPAD(g.cvegeo::text, 5, '0')::varchar(5)     AS clave_municipio,
    f.valor
FROM stg_efipem f
JOIN cat_tema tm        ON f.tema_id = tm.id     AND tm.name = 'Egresos'
JOIN cat_clasificador cl ON f.clasificador_id = cl.id AND cl.name = 'Tema'
JOIN cat_concepto cp     ON f.concepto_id = cp.id AND cp.name = 'Total de egresos'
JOIN cvegeo_municipalities g ON f.cvegeo = LPAD(g.cvegeo::text, 5, '0')
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS ix_egresos_totales_fid ON egresos_totales (fid);

-- ---------------------------------------------------------------------------
-- 10. egresos_deuda_publica
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS egresos_deuda_publica AS
SELECT
    ROW_NUMBER() OVER ()::bigint                  AS fid,
    g.geom_iieg,
    g.geom_inegi,
    g.nomgeo::varchar(254)                        AS nombre,
    make_date(f.anio, 1, 1)                       AS fecha,
    '14'::char(2)                                 AS clave_entidad,
    LPAD(g.cvegeo::text, 5, '0')::varchar(5)     AS clave_municipio,
    f.valor
FROM stg_efipem f
JOIN cat_tema tm        ON f.tema_id = tm.id     AND tm.name = 'Egresos'
JOIN cat_clasificador cl ON f.clasificador_id = cl.id AND cl.name = 'Capítulo'
JOIN cat_concepto cp     ON f.concepto_id = cp.id AND cp.name = 'Deuda pública'
JOIN cvegeo_municipalities g ON f.cvegeo = LPAD(g.cvegeo::text, 5, '0')
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS ix_egresos_deuda_publica_fid ON egresos_deuda_publica (fid);

-- ---------------------------------------------------------------------------
-- 11. porcentaje_egresos_deuda_publica
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS porcentaje_egresos_deuda_publica AS
WITH tot AS (
    SELECT f.anio, f.cvegeo, f.valor AS total
    FROM stg_efipem f
    JOIN cat_tema tm        ON f.tema_id = tm.id     AND tm.name = 'Egresos'
    JOIN cat_clasificador cl ON f.clasificador_id = cl.id AND cl.name = 'Tema'
    JOIN cat_concepto cp     ON f.concepto_id = cp.id AND cp.name = 'Total de egresos'
),
deuda AS (
    SELECT f.anio, f.cvegeo, f.valor AS deuda_publica
    FROM stg_efipem f
    JOIN cat_tema tm        ON f.tema_id = tm.id     AND tm.name = 'Egresos'
    JOIN cat_clasificador cl ON f.clasificador_id = cl.id AND cl.name = 'Capítulo'
    JOIN cat_concepto cp     ON f.concepto_id = cp.id AND cp.name = 'Deuda pública'
)
SELECT
    ROW_NUMBER() OVER ()::bigint                  AS fid,
    g.geom_iieg,
    g.geom_inegi,
    g.nomgeo::varchar(254)                        AS nombre,
    make_date(d.anio, 1, 1)                       AS fecha,
    '14'::char(2)                                 AS clave_entidad,
    LPAD(g.cvegeo::text, 5, '0')::varchar(5)     AS clave_municipio,
    CASE WHEN t.total IS NOT NULL AND t.total > 0
        THEN ROUND((d.deuda_publica::numeric / t.total) * 100, 2)
        ELSE NULL
    END                                           AS valor
FROM deuda d
JOIN tot t ON d.anio = t.anio AND d.cvegeo = t.cvegeo
JOIN cvegeo_municipalities g ON d.cvegeo = LPAD(g.cvegeo::text, 5, '0')
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS ix_porcentaje_egresos_deuda_publica_fid
    ON porcentaje_egresos_deuda_publica (fid);
