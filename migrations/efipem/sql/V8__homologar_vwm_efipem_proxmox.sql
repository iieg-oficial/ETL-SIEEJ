-- =============================================================================
-- V8__homologar_vwm_efipem_proxmox.sql  |  Pipeline: efipem
-- Homologa las 11 MVs de efipem con sus equivalentes en proxmox
-- (gobierno_y_ciudadania.*):
--   - Grid completo municipio x anio: el comentario original de
--     V6__vistas_materializadas_efipem.sql ya describia que las MVs debian
--     construirse con CROSS JOIN de municipios x anios y LEFT JOIN de los
--     conceptos, pero el SQL nunca lo implemento (usaba JOIN normal, solo
--     filas con dato real). Proxmox si arma el grid completo: 125 municipios
--     x 35 anios (1990-2024) = 4375 filas fijas por vista, con valor NULL
--     donde no hay dato reportado.
--   - Rango de anios: se excluye 1989 (existe en stg_efipem pero proxmox
--     arranca en 1990) para igualar exactamente el grid de proxmox.
--   - Tipo de valor: numeric en vez de bigint / double precision, redondeado
--     a 2 decimales, igual que proxmox.
--   - 6 vistas "monto" (ingresos_totales, ingresos_totales_reales_precios_2023,
--     ingresos_participaciones, ingresos_financiamiento, egresos_totales,
--     egresos_deuda_publica) mantienen columna clave_municipio + valor
--     numeric(24,2), igual que proxmox.
--   - 5 vistas "derivadas" (porcentajes + per capita) en proxmox NO tienen
--     clave_municipio y exponen 3 columnas numericas con nombre descriptivo
--     en vez de una sola "valor" (total base, monto del concepto, ratio
--     calculado). Verificado con datos reales (Guadalajara 2020) que los
--     valores coinciden exactamente con las vistas "monto" correspondientes.
-- Ver comparaciones/compare_efipem.py
-- =============================================================================

DROP MATERIALIZED VIEW IF EXISTS porcentaje_egresos_deuda_publica;
DROP MATERIALIZED VIEW IF EXISTS egresos_deuda_publica;
DROP MATERIALIZED VIEW IF EXISTS egresos_totales;
DROP MATERIALIZED VIEW IF EXISTS porcentaje_ingresos_propios;
DROP MATERIALIZED VIEW IF EXISTS porcentaje_ingresos_financiamiento;
DROP MATERIALIZED VIEW IF EXISTS porcentaje_ingresos_participaciones;
DROP MATERIALIZED VIEW IF EXISTS ingresos_financiamiento;
DROP MATERIALIZED VIEW IF EXISTS ingresos_participaciones;
DROP MATERIALIZED VIEW IF EXISTS ingresos_totales_reales_per_capita_precios_2023;
DROP MATERIALIZED VIEW IF EXISTS ingresos_totales_reales_precios_2023;
DROP MATERIALIZED VIEW IF EXISTS ingresos_totales;

-- ---------------------------------------------------------------------------
-- 1. ingresos_totales
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW ingresos_totales AS
WITH anios AS (
    SELECT generate_series(1990, 2024) AS anio
),
grid AS (
    SELECT g.cvegeo, g.nomgeo, g.geom_iieg, g.geom_inegi, a.anio
    FROM cvegeo_municipalities g
    CROSS JOIN anios a
    WHERE g.cve_ent = 14
),
datos AS (
    SELECT f.anio, f.cvegeo, f.valor
    FROM stg_efipem f
    JOIN cat_tema tm        ON f.tema_id = tm.id     AND tm.name = 'Ingresos'
    JOIN cat_clasificador cl ON f.clasificador_id = cl.id AND cl.name = 'Tema'
    JOIN cat_concepto cp     ON f.concepto_id = cp.id AND cp.name = 'Total de ingresos'
)
SELECT
    ROW_NUMBER() OVER ()::bigint                  AS fid,
    grid.geom_iieg,
    grid.geom_inegi,
    grid.nomgeo::varchar(254)                     AS nombre,
    make_date(grid.anio, 1, 1)                    AS fecha,
    CASE WHEN d.valor IS NOT NULL THEN '14' ELSE NULL END::char(2) AS clave_entidad,
    LPAD(grid.cvegeo::text, 5, '0')::varchar(5)   AS clave_municipio,
    ROUND(d.valor::numeric, 2)::numeric(24,2)     AS valor
FROM grid
LEFT JOIN datos d ON d.cvegeo = LPAD(grid.cvegeo::text, 5, '0') AND d.anio = grid.anio
WITH NO DATA;

CREATE UNIQUE INDEX ix_ingresos_totales_fid ON ingresos_totales (fid);

-- ---------------------------------------------------------------------------
-- 2. ingresos_totales_reales_precios_2023
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW ingresos_totales_reales_precios_2023 AS
WITH anios AS (
    SELECT generate_series(1990, 2024) AS anio
),
grid AS (
    SELECT g.cvegeo, g.nomgeo, g.geom_iieg, g.geom_inegi, a.anio
    FROM cvegeo_municipalities g
    CROSS JOIN anios a
    WHERE g.cve_ent = 14
),
datos AS (
    SELECT f.anio, f.cvegeo, f.valor
    FROM stg_efipem f
    JOIN cat_tema tm        ON f.tema_id = tm.id     AND tm.name = 'Ingresos'
    JOIN cat_clasificador cl ON f.clasificador_id = cl.id AND cl.name = 'Tema'
    JOIN cat_concepto cp     ON f.concepto_id = cp.id AND cp.name = 'Total de ingresos'
),
idx_2023 AS (
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
    grid.geom_iieg,
    grid.geom_inegi,
    grid.nomgeo::varchar(254)                     AS nombre,
    make_date(grid.anio, 1, 1)                    AS fecha,
    CASE WHEN d.valor IS NOT NULL THEN '14' ELSE NULL END::char(2) AS clave_entidad,
    LPAD(grid.cvegeo::text, 5, '0')::varchar(5)   AS clave_municipio,
    CASE WHEN ia.indice IS NOT NULL AND ia.indice > 0 AND d.valor IS NOT NULL
        THEN ROUND((d.valor::numeric * (i2023.indice / ia.indice))::numeric, 2)
        ELSE NULL
    END::numeric(24,2)                            AS valor
FROM grid
CROSS JOIN idx_2023 i2023
LEFT JOIN datos d   ON d.cvegeo = LPAD(grid.cvegeo::text, 5, '0') AND d.anio = grid.anio
LEFT JOIN idx_anual ia ON ia.anio = grid.anio
WITH NO DATA;

CREATE UNIQUE INDEX ix_ingresos_totales_reales_precios_2023_fid
    ON ingresos_totales_reales_precios_2023 (fid);

-- ---------------------------------------------------------------------------
-- 3. ingresos_totales_reales_per_capita_precios_2023
-- (patron B: sin clave_municipio; 3 columnas: real, nominal, per capita)
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW ingresos_totales_reales_per_capita_precios_2023 AS
WITH anios AS (
    SELECT generate_series(1990, 2024) AS anio
),
grid AS (
    SELECT g.cvegeo, g.nomgeo, g.geom_iieg, g.geom_inegi, a.anio
    FROM cvegeo_municipalities g
    CROSS JOIN anios a
    WHERE g.cve_ent = 14
),
datos AS (
    SELECT f.anio, f.cvegeo, f.valor
    FROM stg_efipem f
    JOIN cat_tema tm        ON f.tema_id = tm.id     AND tm.name = 'Ingresos'
    JOIN cat_clasificador cl ON f.clasificador_id = cl.id AND cl.name = 'Tema'
    JOIN cat_concepto cp     ON f.concepto_id = cp.id AND cp.name = 'Total de ingresos'
),
idx_2023 AS (
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
    grid.geom_iieg,
    grid.geom_inegi,
    grid.nomgeo::varchar(254)                     AS nombre,
    make_date(grid.anio, 1, 1)                    AS fecha,
    CASE WHEN d.valor IS NOT NULL THEN '14' ELSE NULL END::char(2) AS clave_entidad,
    CASE WHEN ia.indice IS NOT NULL AND ia.indice > 0 AND d.valor IS NOT NULL
        THEN ROUND((d.valor::numeric * (i2023.indice / ia.indice))::numeric, 2)
        ELSE NULL
    END::numeric                                  AS ingresos_totales_reales,
    ROUND(d.valor::numeric, 2)::numeric           AS ingresos_totales,
    CASE
        WHEN ia.indice IS NOT NULL AND ia.indice > 0 AND d.valor IS NOT NULL
             AND p.pob_total IS NOT NULL AND p.pob_total > 0
        THEN ROUND(((d.valor::numeric * (i2023.indice / ia.indice)) / p.pob_total)::numeric, 2)
        ELSE NULL
    END::numeric                                  AS ingresos_reales_per_capita
FROM grid
CROSS JOIN idx_2023 i2023
LEFT JOIN datos d   ON d.cvegeo = LPAD(grid.cvegeo::text, 5, '0') AND d.anio = grid.anio
LEFT JOIN idx_anual ia ON ia.anio = grid.anio
LEFT JOIN pob p     ON p.municipio_id = grid.cvegeo AND p.anio = grid.anio
WITH NO DATA;

CREATE UNIQUE INDEX ix_ingresos_totales_reales_per_capita_precios_2023_fid
    ON ingresos_totales_reales_per_capita_precios_2023 (fid);

-- ---------------------------------------------------------------------------
-- 4. ingresos_participaciones
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW ingresos_participaciones AS
WITH anios AS (
    SELECT generate_series(1990, 2024) AS anio
),
grid AS (
    SELECT g.cvegeo, g.nomgeo, g.geom_iieg, g.geom_inegi, a.anio
    FROM cvegeo_municipalities g
    CROSS JOIN anios a
    WHERE g.cve_ent = 14
),
datos AS (
    SELECT f.anio, f.cvegeo, f.valor
    FROM stg_efipem f
    JOIN cat_tema tm        ON f.tema_id = tm.id     AND tm.name = 'Ingresos'
    JOIN cat_clasificador cl ON f.clasificador_id = cl.id AND cl.name = 'Capítulo'
    JOIN cat_concepto cp     ON f.concepto_id = cp.id AND cp.name = 'Participaciones federales'
)
SELECT
    ROW_NUMBER() OVER ()::bigint                  AS fid,
    grid.geom_iieg,
    grid.geom_inegi,
    grid.nomgeo::varchar(254)                     AS nombre,
    make_date(grid.anio, 1, 1)                    AS fecha,
    CASE WHEN d.valor IS NOT NULL THEN '14' ELSE NULL END::char(2) AS clave_entidad,
    LPAD(grid.cvegeo::text, 5, '0')::varchar(5)   AS clave_municipio,
    ROUND(d.valor::numeric, 2)::numeric(24,2)     AS valor
FROM grid
LEFT JOIN datos d ON d.cvegeo = LPAD(grid.cvegeo::text, 5, '0') AND d.anio = grid.anio
WITH NO DATA;

CREATE UNIQUE INDEX ix_ingresos_participaciones_fid ON ingresos_participaciones (fid);

-- ---------------------------------------------------------------------------
-- 5. ingresos_financiamiento
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW ingresos_financiamiento AS
WITH anios AS (
    SELECT generate_series(1990, 2024) AS anio
),
grid AS (
    SELECT g.cvegeo, g.nomgeo, g.geom_iieg, g.geom_inegi, a.anio
    FROM cvegeo_municipalities g
    CROSS JOIN anios a
    WHERE g.cve_ent = 14
),
datos AS (
    SELECT f.anio, f.cvegeo, f.valor
    FROM stg_efipem f
    JOIN cat_tema tm        ON f.tema_id = tm.id     AND tm.name = 'Ingresos'
    JOIN cat_clasificador cl ON f.clasificador_id = cl.id AND cl.name = 'Capítulo'
    JOIN cat_concepto cp     ON f.concepto_id = cp.id AND cp.name = 'Financiamiento'
)
SELECT
    ROW_NUMBER() OVER ()::bigint                  AS fid,
    grid.geom_iieg,
    grid.geom_inegi,
    grid.nomgeo::varchar(254)                     AS nombre,
    make_date(grid.anio, 1, 1)                    AS fecha,
    CASE WHEN d.valor IS NOT NULL THEN '14' ELSE NULL END::char(2) AS clave_entidad,
    LPAD(grid.cvegeo::text, 5, '0')::varchar(5)   AS clave_municipio,
    ROUND(d.valor::numeric, 2)::numeric(24,2)     AS valor
FROM grid
LEFT JOIN datos d ON d.cvegeo = LPAD(grid.cvegeo::text, 5, '0') AND d.anio = grid.anio
WITH NO DATA;

CREATE UNIQUE INDEX ix_ingresos_financiamiento_fid ON ingresos_financiamiento (fid);

-- ---------------------------------------------------------------------------
-- 6. porcentaje_ingresos_participaciones
-- (patron B: sin clave_municipio; 3 columnas: total, participaciones, %)
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW porcentaje_ingresos_participaciones AS
WITH anios AS (
    SELECT generate_series(1990, 2024) AS anio
),
grid AS (
    SELECT g.cvegeo, g.nomgeo, g.geom_iieg, g.geom_inegi, a.anio
    FROM cvegeo_municipalities g
    CROSS JOIN anios a
    WHERE g.cve_ent = 14
),
tot AS (
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
    grid.geom_iieg,
    grid.geom_inegi,
    grid.nomgeo::varchar(254)                     AS nombre,
    make_date(grid.anio, 1, 1)                    AS fecha,
    CASE WHEN t.total IS NOT NULL THEN '14' ELSE NULL END::char(2) AS clave_entidad,
    ROUND(t.total::numeric, 2)::numeric           AS ingresos_totales,
    ROUND(p.participaciones::numeric, 2)::numeric AS ingresos_por_participaciones,
    CASE WHEN t.total IS NOT NULL AND t.total > 0 AND p.participaciones IS NOT NULL
        THEN ROUND((p.participaciones::numeric / t.total) * 100, 2)
        ELSE NULL
    END::numeric                                  AS porcentaje_de_ingresos_por_participaciones
FROM grid
LEFT JOIN tot t   ON t.cvegeo = LPAD(grid.cvegeo::text, 5, '0') AND t.anio = grid.anio
LEFT JOIN part p  ON p.cvegeo = LPAD(grid.cvegeo::text, 5, '0') AND p.anio = grid.anio
WITH NO DATA;

CREATE UNIQUE INDEX ix_porcentaje_ingresos_participaciones_fid
    ON porcentaje_ingresos_participaciones (fid);

-- ---------------------------------------------------------------------------
-- 7. porcentaje_ingresos_financiamiento
-- (patron B: sin clave_municipio; 3 columnas: total, financiamiento, %)
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW porcentaje_ingresos_financiamiento AS
WITH anios AS (
    SELECT generate_series(1990, 2024) AS anio
),
grid AS (
    SELECT g.cvegeo, g.nomgeo, g.geom_iieg, g.geom_inegi, a.anio
    FROM cvegeo_municipalities g
    CROSS JOIN anios a
    WHERE g.cve_ent = 14
),
tot AS (
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
    grid.geom_iieg,
    grid.geom_inegi,
    grid.nomgeo::varchar(254)                     AS nombre,
    make_date(grid.anio, 1, 1)                    AS fecha,
    CASE WHEN t.total IS NOT NULL THEN '14' ELSE NULL END::char(2) AS clave_entidad,
    ROUND(t.total::numeric, 2)::numeric           AS ingresos_totales,
    ROUND(fin.financiamiento::numeric, 2)::numeric AS ingresos_por_financiamiento,
    CASE WHEN t.total IS NOT NULL AND t.total > 0 AND fin.financiamiento IS NOT NULL
        THEN ROUND((fin.financiamiento::numeric / t.total) * 100, 2)
        ELSE NULL
    END::numeric                                  AS porcentaje_de_ingresos_por_financiamiento
FROM grid
LEFT JOIN tot t  ON t.cvegeo = LPAD(grid.cvegeo::text, 5, '0') AND t.anio = grid.anio
LEFT JOIN fin    ON fin.cvegeo = LPAD(grid.cvegeo::text, 5, '0') AND fin.anio = grid.anio
WITH NO DATA;

CREATE UNIQUE INDEX ix_porcentaje_ingresos_financiamiento_fid
    ON porcentaje_ingresos_financiamiento (fid);

-- ---------------------------------------------------------------------------
-- 8. porcentaje_ingresos_propios
-- (patron B: sin clave_municipio; 3 columnas: total, propios, %)
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW porcentaje_ingresos_propios AS
WITH anios AS (
    SELECT generate_series(1990, 2024) AS anio
),
grid AS (
    SELECT g.cvegeo, g.nomgeo, g.geom_iieg, g.geom_inegi, a.anio
    FROM cvegeo_municipalities g
    CROSS JOIN anios a
    WHERE g.cve_ent = 14
),
tot AS (
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
        AND cp.name IN ('Impuestos', 'Derechos', 'Productos', 'Aprovechamientos', 'Contribuciones de Mejoras', 'Cuotas y Aportaciones de Seguridad Social')
    GROUP BY f.anio, f.cvegeo
)
SELECT
    ROW_NUMBER() OVER ()::bigint                  AS fid,
    grid.geom_iieg,
    grid.geom_inegi,
    grid.nomgeo::varchar(254)                     AS nombre,
    make_date(grid.anio, 1, 1)                    AS fecha,
    CASE WHEN t.total IS NOT NULL THEN '14' ELSE NULL END::char(2) AS clave_entidad,
    ROUND(t.total::numeric, 2)::numeric           AS ingresos_totales,
    ROUND(p.ingresos_propios::numeric, 2)::numeric AS ingresos_propios,
    CASE WHEN t.total IS NOT NULL AND t.total > 0 AND p.ingresos_propios IS NOT NULL
        THEN ROUND((p.ingresos_propios::numeric / t.total) * 100, 2)
        ELSE NULL
    END::numeric                                  AS porcentaje_ingresos_propios
FROM grid
LEFT JOIN tot t      ON t.cvegeo = LPAD(grid.cvegeo::text, 5, '0') AND t.anio = grid.anio
LEFT JOIN propios p  ON p.cvegeo = LPAD(grid.cvegeo::text, 5, '0') AND p.anio = grid.anio
WITH NO DATA;

CREATE UNIQUE INDEX ix_porcentaje_ingresos_propios_fid
    ON porcentaje_ingresos_propios (fid);

-- ---------------------------------------------------------------------------
-- 9. egresos_totales
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW egresos_totales AS
WITH anios AS (
    SELECT generate_series(1990, 2024) AS anio
),
grid AS (
    SELECT g.cvegeo, g.nomgeo, g.geom_iieg, g.geom_inegi, a.anio
    FROM cvegeo_municipalities g
    CROSS JOIN anios a
    WHERE g.cve_ent = 14
),
datos AS (
    SELECT f.anio, f.cvegeo, f.valor
    FROM stg_efipem f
    JOIN cat_tema tm        ON f.tema_id = tm.id     AND tm.name = 'Egresos'
    JOIN cat_clasificador cl ON f.clasificador_id = cl.id AND cl.name = 'Tema'
    JOIN cat_concepto cp     ON f.concepto_id = cp.id AND cp.name = 'Total de egresos'
)
SELECT
    ROW_NUMBER() OVER ()::bigint                  AS fid,
    grid.geom_iieg,
    grid.geom_inegi,
    grid.nomgeo::varchar(254)                     AS nombre,
    make_date(grid.anio, 1, 1)                    AS fecha,
    CASE WHEN d.valor IS NOT NULL THEN '14' ELSE NULL END::char(2) AS clave_entidad,
    LPAD(grid.cvegeo::text, 5, '0')::varchar(5)   AS clave_municipio,
    ROUND(d.valor::numeric, 2)::numeric(24,2)     AS valor
FROM grid
LEFT JOIN datos d ON d.cvegeo = LPAD(grid.cvegeo::text, 5, '0') AND d.anio = grid.anio
WITH NO DATA;

CREATE UNIQUE INDEX ix_egresos_totales_fid ON egresos_totales (fid);

-- ---------------------------------------------------------------------------
-- 10. egresos_deuda_publica
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW egresos_deuda_publica AS
WITH anios AS (
    SELECT generate_series(1990, 2024) AS anio
),
grid AS (
    SELECT g.cvegeo, g.nomgeo, g.geom_iieg, g.geom_inegi, a.anio
    FROM cvegeo_municipalities g
    CROSS JOIN anios a
    WHERE g.cve_ent = 14
),
datos AS (
    SELECT f.anio, f.cvegeo, f.valor
    FROM stg_efipem f
    JOIN cat_tema tm        ON f.tema_id = tm.id     AND tm.name = 'Egresos'
    JOIN cat_clasificador cl ON f.clasificador_id = cl.id AND cl.name = 'Capítulo'
    JOIN cat_concepto cp     ON f.concepto_id = cp.id AND cp.name = 'Deuda pública'
)
SELECT
    ROW_NUMBER() OVER ()::bigint                  AS fid,
    grid.geom_iieg,
    grid.geom_inegi,
    grid.nomgeo::varchar(254)                     AS nombre,
    make_date(grid.anio, 1, 1)                    AS fecha,
    CASE WHEN d.valor IS NOT NULL THEN '14' ELSE NULL END::char(2) AS clave_entidad,
    LPAD(grid.cvegeo::text, 5, '0')::varchar(5)   AS clave_municipio,
    ROUND(d.valor::numeric, 2)::numeric(24,2)     AS valor
FROM grid
LEFT JOIN datos d ON d.cvegeo = LPAD(grid.cvegeo::text, 5, '0') AND d.anio = grid.anio
WITH NO DATA;

CREATE UNIQUE INDEX ix_egresos_deuda_publica_fid ON egresos_deuda_publica (fid);

-- ---------------------------------------------------------------------------
-- 11. porcentaje_egresos_deuda_publica
-- (patron B: sin clave_municipio; 3 columnas: total, deuda, %)
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW porcentaje_egresos_deuda_publica AS
WITH anios AS (
    SELECT generate_series(1990, 2024) AS anio
),
grid AS (
    SELECT g.cvegeo, g.nomgeo, g.geom_iieg, g.geom_inegi, a.anio
    FROM cvegeo_municipalities g
    CROSS JOIN anios a
    WHERE g.cve_ent = 14
),
tot AS (
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
    grid.geom_iieg,
    grid.geom_inegi,
    grid.nomgeo::varchar(254)                     AS nombre,
    make_date(grid.anio, 1, 1)                    AS fecha,
    CASE WHEN t.total IS NOT NULL THEN '14' ELSE NULL END::char(2) AS clave_entidad,
    ROUND(t.total::numeric, 2)::numeric           AS egresos_totales,
    ROUND(d.deuda_publica::numeric, 2)::numeric   AS egresos_para_pago_deuda_publica,
    CASE WHEN t.total IS NOT NULL AND t.total > 0 AND d.deuda_publica IS NOT NULL
        THEN ROUND((d.deuda_publica::numeric / t.total) * 100, 2)
        ELSE NULL
    END::numeric                                  AS porcentaje_egresos_por_pago_deuda_publica
FROM grid
LEFT JOIN tot t    ON t.cvegeo = LPAD(grid.cvegeo::text, 5, '0') AND t.anio = grid.anio
LEFT JOIN deuda d  ON d.cvegeo = LPAD(grid.cvegeo::text, 5, '0') AND d.anio = grid.anio
WITH NO DATA;

CREATE UNIQUE INDEX ix_porcentaje_egresos_deuda_publica_fid
    ON porcentaje_egresos_deuda_publica (fid);

-- =============================================================================
-- Comentarios
-- =============================================================================

COMMENT ON MATERIALIZED VIEW ingresos_totales IS
    'Ingresos municipales totales en pesos corrientes (fuente: EFIPEM INEGI). Grid completo municipio x anio 1990-2024.';
COMMENT ON COLUMN ingresos_totales.fid IS 'Identificador unico de la fila';
COMMENT ON COLUMN ingresos_totales.geom_iieg IS 'Geometria del municipio (marco geoestadistico IIEG, SRID 6368)';
COMMENT ON COLUMN ingresos_totales.geom_inegi IS 'Geometria del municipio (marco geoestadistico INEGI, SRID 6368)';
COMMENT ON COLUMN ingresos_totales.nombre IS 'Nombre del municipio';
COMMENT ON COLUMN ingresos_totales.fecha IS 'Fecha del periodo anual (YYYY-01-01)';
COMMENT ON COLUMN ingresos_totales.clave_entidad IS 'Clave de la entidad federativa (14 = Jalisco)';
COMMENT ON COLUMN ingresos_totales.clave_municipio IS 'Clave del municipio (EEMMM, 5 digitos)';
COMMENT ON COLUMN ingresos_totales.valor IS 'Ingresos totales en pesos corrientes (NULL si no hay dato reportado ese anio)';

COMMENT ON MATERIALIZED VIEW ingresos_totales_reales_precios_2023 IS
    'Ingresos municipales totales deflactados a precios constantes de 2023 (INPC base 2023=100). Grid completo municipio x anio 1990-2024.';
COMMENT ON COLUMN ingresos_totales_reales_precios_2023.fid IS 'Identificador unico de la fila';
COMMENT ON COLUMN ingresos_totales_reales_precios_2023.geom_iieg IS 'Geometria del municipio (marco geoestadistico IIEG, SRID 6368)';
COMMENT ON COLUMN ingresos_totales_reales_precios_2023.geom_inegi IS 'Geometria del municipio (marco geoestadistico INEGI, SRID 6368)';
COMMENT ON COLUMN ingresos_totales_reales_precios_2023.nombre IS 'Nombre del municipio';
COMMENT ON COLUMN ingresos_totales_reales_precios_2023.fecha IS 'Fecha del periodo anual (YYYY-01-01)';
COMMENT ON COLUMN ingresos_totales_reales_precios_2023.clave_entidad IS 'Clave de la entidad federativa (14 = Jalisco)';
COMMENT ON COLUMN ingresos_totales_reales_precios_2023.clave_municipio IS 'Clave del municipio (EEMMM, 5 digitos)';
COMMENT ON COLUMN ingresos_totales_reales_precios_2023.valor IS 'Ingresos totales en pesos reales de 2023 (deflactado por INPC, NULL si no hay dato)';

COMMENT ON MATERIALIZED VIEW ingresos_totales_reales_per_capita_precios_2023 IS
    'Ingresos reales per capita deflactados a precios de 2023 (valor real / poblacion CONAPO). Grid completo municipio x anio 1990-2024.';
COMMENT ON COLUMN ingresos_totales_reales_per_capita_precios_2023.fid IS 'Identificador unico de la fila';
COMMENT ON COLUMN ingresos_totales_reales_per_capita_precios_2023.geom_iieg IS 'Geometria del municipio (marco geoestadistico IIEG, SRID 6368)';
COMMENT ON COLUMN ingresos_totales_reales_per_capita_precios_2023.geom_inegi IS 'Geometria del municipio (marco geoestadistico INEGI, SRID 6368)';
COMMENT ON COLUMN ingresos_totales_reales_per_capita_precios_2023.nombre IS 'Nombre del municipio';
COMMENT ON COLUMN ingresos_totales_reales_per_capita_precios_2023.fecha IS 'Fecha del periodo anual (YYYY-01-01)';
COMMENT ON COLUMN ingresos_totales_reales_per_capita_precios_2023.clave_entidad IS 'Clave de la entidad federativa (14 = Jalisco)';
COMMENT ON COLUMN ingresos_totales_reales_per_capita_precios_2023.ingresos_totales_reales IS 'Ingresos totales en pesos reales de 2023 (deflactado por INPC)';
COMMENT ON COLUMN ingresos_totales_reales_per_capita_precios_2023.ingresos_totales IS 'Ingresos totales en pesos corrientes (nominal)';
COMMENT ON COLUMN ingresos_totales_reales_per_capita_precios_2023.ingresos_reales_per_capita IS 'Ingresos reales per capita en pesos de 2023 (ingresos reales / poblacion CONAPO)';

COMMENT ON MATERIALIZED VIEW ingresos_participaciones IS
    'Monto de participaciones federales recibidas por municipio (pesos corrientes). Grid completo municipio x anio 1990-2024.';
COMMENT ON COLUMN ingresos_participaciones.fid IS 'Identificador unico de la fila';
COMMENT ON COLUMN ingresos_participaciones.geom_iieg IS 'Geometria del municipio (marco geoestadistico IIEG, SRID 6368)';
COMMENT ON COLUMN ingresos_participaciones.geom_inegi IS 'Geometria del municipio (marco geoestadistico INEGI, SRID 6368)';
COMMENT ON COLUMN ingresos_participaciones.nombre IS 'Nombre del municipio';
COMMENT ON COLUMN ingresos_participaciones.fecha IS 'Fecha del periodo anual (YYYY-01-01)';
COMMENT ON COLUMN ingresos_participaciones.clave_entidad IS 'Clave de la entidad federativa (14 = Jalisco)';
COMMENT ON COLUMN ingresos_participaciones.clave_municipio IS 'Clave del municipio (EEMMM, 5 digitos)';
COMMENT ON COLUMN ingresos_participaciones.valor IS 'Participaciones federales en pesos corrientes (NULL si no hay dato reportado ese anio)';

COMMENT ON MATERIALIZED VIEW ingresos_financiamiento IS
    'Ingresos por financiamiento / deuda publica (pesos corrientes). Grid completo municipio x anio 1990-2024.';
COMMENT ON COLUMN ingresos_financiamiento.fid IS 'Identificador unico de la fila';
COMMENT ON COLUMN ingresos_financiamiento.geom_iieg IS 'Geometria del municipio (marco geoestadistico IIEG, SRID 6368)';
COMMENT ON COLUMN ingresos_financiamiento.geom_inegi IS 'Geometria del municipio (marco geoestadistico INEGI, SRID 6368)';
COMMENT ON COLUMN ingresos_financiamiento.nombre IS 'Nombre del municipio';
COMMENT ON COLUMN ingresos_financiamiento.fecha IS 'Fecha del periodo anual (YYYY-01-01)';
COMMENT ON COLUMN ingresos_financiamiento.clave_entidad IS 'Clave de la entidad federativa (14 = Jalisco)';
COMMENT ON COLUMN ingresos_financiamiento.clave_municipio IS 'Clave del municipio (EEMMM, 5 digitos)';
COMMENT ON COLUMN ingresos_financiamiento.valor IS 'Financiamiento / deuda publica en pesos corrientes (NULL si no hay dato reportado ese anio)';

COMMENT ON MATERIALIZED VIEW porcentaje_ingresos_participaciones IS
    'Porcentaje de participaciones federales sobre ingresos totales. Grid completo municipio x anio 1990-2024.';
COMMENT ON COLUMN porcentaje_ingresos_participaciones.fid IS 'Identificador unico de la fila';
COMMENT ON COLUMN porcentaje_ingresos_participaciones.geom_iieg IS 'Geometria del municipio (marco geoestadistico IIEG, SRID 6368)';
COMMENT ON COLUMN porcentaje_ingresos_participaciones.geom_inegi IS 'Geometria del municipio (marco geoestadistico INEGI, SRID 6368)';
COMMENT ON COLUMN porcentaje_ingresos_participaciones.nombre IS 'Nombre del municipio';
COMMENT ON COLUMN porcentaje_ingresos_participaciones.fecha IS 'Fecha del periodo anual (YYYY-01-01)';
COMMENT ON COLUMN porcentaje_ingresos_participaciones.clave_entidad IS 'Clave de la entidad federativa (14 = Jalisco)';
COMMENT ON COLUMN porcentaje_ingresos_participaciones.ingresos_totales IS 'Ingresos totales en pesos corrientes';
COMMENT ON COLUMN porcentaje_ingresos_participaciones.ingresos_por_participaciones IS 'Participaciones federales en pesos corrientes';
COMMENT ON COLUMN porcentaje_ingresos_participaciones.porcentaje_de_ingresos_por_participaciones IS 'Porcentaje de participaciones sobre ingresos totales (0-100)';

COMMENT ON MATERIALIZED VIEW porcentaje_ingresos_financiamiento IS
    'Porcentaje de financiamiento sobre ingresos totales. Grid completo municipio x anio 1990-2024.';
COMMENT ON COLUMN porcentaje_ingresos_financiamiento.fid IS 'Identificador unico de la fila';
COMMENT ON COLUMN porcentaje_ingresos_financiamiento.geom_iieg IS 'Geometria del municipio (marco geoestadistico IIEG, SRID 6368)';
COMMENT ON COLUMN porcentaje_ingresos_financiamiento.geom_inegi IS 'Geometria del municipio (marco geoestadistico INEGI, SRID 6368)';
COMMENT ON COLUMN porcentaje_ingresos_financiamiento.nombre IS 'Nombre del municipio';
COMMENT ON COLUMN porcentaje_ingresos_financiamiento.fecha IS 'Fecha del periodo anual (YYYY-01-01)';
COMMENT ON COLUMN porcentaje_ingresos_financiamiento.clave_entidad IS 'Clave de la entidad federativa (14 = Jalisco)';
COMMENT ON COLUMN porcentaje_ingresos_financiamiento.ingresos_totales IS 'Ingresos totales en pesos corrientes';
COMMENT ON COLUMN porcentaje_ingresos_financiamiento.ingresos_por_financiamiento IS 'Financiamiento en pesos corrientes';
COMMENT ON COLUMN porcentaje_ingresos_financiamiento.porcentaje_de_ingresos_por_financiamiento IS 'Porcentaje de financiamiento sobre ingresos totales (0-100)';

COMMENT ON MATERIALIZED VIEW porcentaje_ingresos_propios IS
    'Porcentaje de ingresos propios (Impuestos + Derechos + Productos + Aprovechamientos + Contribuciones de Mejoras + Cuotas y Aportaciones de Seguridad Social) sobre ingresos totales. Grid completo municipio x anio 1990-2024.';
COMMENT ON COLUMN porcentaje_ingresos_propios.fid IS 'Identificador unico de la fila';
COMMENT ON COLUMN porcentaje_ingresos_propios.geom_iieg IS 'Geometria del municipio (marco geoestadistico IIEG, SRID 6368)';
COMMENT ON COLUMN porcentaje_ingresos_propios.geom_inegi IS 'Geometria del municipio (marco geoestadistico INEGI, SRID 6368)';
COMMENT ON COLUMN porcentaje_ingresos_propios.nombre IS 'Nombre del municipio';
COMMENT ON COLUMN porcentaje_ingresos_propios.fecha IS 'Fecha del periodo anual (YYYY-01-01)';
COMMENT ON COLUMN porcentaje_ingresos_propios.clave_entidad IS 'Clave de la entidad federativa (14 = Jalisco)';
COMMENT ON COLUMN porcentaje_ingresos_propios.ingresos_totales IS 'Ingresos totales en pesos corrientes';
COMMENT ON COLUMN porcentaje_ingresos_propios.ingresos_propios IS 'Ingresos propios (Impuestos + Derechos + Productos + Aprovechamientos + Contribuciones de Mejoras + Cuotas y Aportaciones de Seguridad Social) en pesos corrientes';
COMMENT ON COLUMN porcentaje_ingresos_propios.porcentaje_ingresos_propios IS 'Porcentaje de ingresos propios sobre total (0-100)';

COMMENT ON MATERIALIZED VIEW egresos_totales IS
    'Egresos municipales totales en pesos corrientes (fuente: EFIPEM INEGI). Grid completo municipio x anio 1990-2024.';
COMMENT ON COLUMN egresos_totales.fid IS 'Identificador unico de la fila';
COMMENT ON COLUMN egresos_totales.geom_iieg IS 'Geometria del municipio (marco geoestadistico IIEG, SRID 6368)';
COMMENT ON COLUMN egresos_totales.geom_inegi IS 'Geometria del municipio (marco geoestadistico INEGI, SRID 6368)';
COMMENT ON COLUMN egresos_totales.nombre IS 'Nombre del municipio';
COMMENT ON COLUMN egresos_totales.fecha IS 'Fecha del periodo anual (YYYY-01-01)';
COMMENT ON COLUMN egresos_totales.clave_entidad IS 'Clave de la entidad federativa (14 = Jalisco)';
COMMENT ON COLUMN egresos_totales.clave_municipio IS 'Clave del municipio (EEMMM, 5 digitos)';
COMMENT ON COLUMN egresos_totales.valor IS 'Egresos totales en pesos corrientes (NULL si no hay dato reportado ese anio)';

COMMENT ON MATERIALIZED VIEW egresos_deuda_publica IS
    'Pago de deuda publica (capital + intereses) en pesos corrientes. Grid completo municipio x anio 1990-2024.';
COMMENT ON COLUMN egresos_deuda_publica.fid IS 'Identificador unico de la fila';
COMMENT ON COLUMN egresos_deuda_publica.geom_iieg IS 'Geometria del municipio (marco geoestadistico IIEG, SRID 6368)';
COMMENT ON COLUMN egresos_deuda_publica.geom_inegi IS 'Geometria del municipio (marco geoestadistico INEGI, SRID 6368)';
COMMENT ON COLUMN egresos_deuda_publica.nombre IS 'Nombre del municipio';
COMMENT ON COLUMN egresos_deuda_publica.fecha IS 'Fecha del periodo anual (YYYY-01-01)';
COMMENT ON COLUMN egresos_deuda_publica.clave_entidad IS 'Clave de la entidad federativa (14 = Jalisco)';
COMMENT ON COLUMN egresos_deuda_publica.clave_municipio IS 'Clave del municipio (EEMMM, 5 digitos)';
COMMENT ON COLUMN egresos_deuda_publica.valor IS 'Deuda publica en pesos corrientes (NULL si no hay dato reportado ese anio)';

COMMENT ON MATERIALIZED VIEW porcentaje_egresos_deuda_publica IS
    'Porcentaje de pago de deuda publica sobre egresos totales. Grid completo municipio x anio 1990-2024.';
COMMENT ON COLUMN porcentaje_egresos_deuda_publica.fid IS 'Identificador unico de la fila';
COMMENT ON COLUMN porcentaje_egresos_deuda_publica.geom_iieg IS 'Geometria del municipio (marco geoestadistico IIEG, SRID 6368)';
COMMENT ON COLUMN porcentaje_egresos_deuda_publica.geom_inegi IS 'Geometria del municipio (marco geoestadistico INEGI, SRID 6368)';
COMMENT ON COLUMN porcentaje_egresos_deuda_publica.nombre IS 'Nombre del municipio';
COMMENT ON COLUMN porcentaje_egresos_deuda_publica.fecha IS 'Fecha del periodo anual (YYYY-01-01)';
COMMENT ON COLUMN porcentaje_egresos_deuda_publica.clave_entidad IS 'Clave de la entidad federativa (14 = Jalisco)';
COMMENT ON COLUMN porcentaje_egresos_deuda_publica.egresos_totales IS 'Egresos totales en pesos corrientes';
COMMENT ON COLUMN porcentaje_egresos_deuda_publica.egresos_para_pago_deuda_publica IS 'Deuda publica en pesos corrientes';
COMMENT ON COLUMN porcentaje_egresos_deuda_publica.porcentaje_egresos_por_pago_deuda_publica IS 'Porcentaje de deuda publica sobre egresos totales (0-100)';
