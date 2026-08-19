-- =============================================================================
-- V9__homologar_vwm_asg_imss_proxmox.sql  |  Pipeline: asg_imss
-- Corrige 2 bugs de logica en V6, encontrados al verificar las vistas
-- materializadas contra proxmox (economia.*, desarrollo_social.*) con datos
-- reales de 2026 (issue #243):
--   - trabajadores_asegurados_hombres / _mujeres: porcentaje_hombres /
--     porcentaje_mujeres estaba hardcodeado a 100.00 en vez de calcularse
--     sobre el total de trabajadores del municipio (igual que ya lo hace
--     correctamente trabajadores_asegurados).
--   - brecha_salarial: salario_promedio_diario_mujeres / _hombres dividia de
--     mas por EXTRACT(DAY FROM fecha_corte); la formula correcta es
--     masa_sal_ta / ta_sal, sin multiplicar por dias del mes.
-- No modifica trabajadores_asegurados (ya coincide exacto con proxmox).
-- Ver comparaciones/compare_asg_imss.py.
-- =============================================================================

DROP MATERIALIZED VIEW IF EXISTS brecha_salarial;
DROP MATERIALIZED VIEW IF EXISTS trabajadores_asegurados_mujeres;
DROP MATERIALIZED VIEW IF EXISTS trabajadores_asegurados_hombres;

-- ---------------------------------------------------------------------------
-- 1. trabajadores_asegurados_hombres
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW trabajadores_asegurados_hombres AS
WITH agg AS (
    SELECT
        DATE_TRUNC('month', v.fecha_corte)::date AS fecha,
        v.cvegeo                                AS cvegeo,
        SUM(v.ta)                               AS total,
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
    CASE WHEN a.total > 0
        THEN ROUND((a.total_hombres::numeric / a.total) * 100, 2)
        ELSE NULL
    END                                        AS porcentaje_hombres
FROM agg a
JOIN cvegeo_municipalities g ON a.cvegeo = g.cvegeo
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX ix_trabajadores_asegurados_hombres_fid
    ON trabajadores_asegurados_hombres (fid);

CREATE INDEX idx_trabajadores_asegurados_hombres_geom_iieg
    ON trabajadores_asegurados_hombres USING GIST (geom_iieg);

CREATE INDEX idx_trabajadores_asegurados_hombres_fecha
    ON trabajadores_asegurados_hombres (fecha);

-- ---------------------------------------------------------------------------
-- 2. trabajadores_asegurados_mujeres
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW trabajadores_asegurados_mujeres AS
WITH agg AS (
    SELECT
        DATE_TRUNC('month', v.fecha_corte)::date AS fecha,
        v.cvegeo                                AS cvegeo,
        SUM(v.ta)                               AS total,
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
    CASE WHEN a.total > 0
        THEN ROUND((a.total_mujeres::numeric / a.total) * 100, 2)
        ELSE NULL
    END                                        AS porcentaje_mujeres
FROM agg a
JOIN cvegeo_municipalities g ON a.cvegeo = g.cvegeo
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX ix_trabajadores_asegurados_mujeres_fid
    ON trabajadores_asegurados_mujeres (fid);

CREATE INDEX idx_trabajadores_asegurados_mujeres_geom_iieg
    ON trabajadores_asegurados_mujeres USING GIST (geom_iieg);

CREATE INDEX idx_trabajadores_asegurados_mujeres_fecha
    ON trabajadores_asegurados_mujeres (fecha);

-- ---------------------------------------------------------------------------
-- 3. brecha_salarial
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW brecha_salarial AS
WITH salarios AS (
    SELECT
        DATE_TRUNC('month', v.fecha_corte)::date AS fecha,
        v.cvegeo                                     AS cvegeo,
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
            THEN ROUND((s.masa_sal_mujeres / s.ta_sal_mujeres)::numeric, 2)
            ELSE NULL
        END AS salario_promedio_diario_mujeres,
        CASE WHEN s.ta_sal_hombres > 0
            THEN ROUND((s.masa_sal_hombres / s.ta_sal_hombres)::numeric, 2)
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

CREATE UNIQUE INDEX ix_brecha_salarial_fid
    ON brecha_salarial (fid);

CREATE INDEX idx_brecha_salarial_geom_iieg
    ON brecha_salarial USING GIST (geom_iieg);

CREATE INDEX idx_brecha_salarial_fecha
    ON brecha_salarial (fecha);

-- ---------------------------------------------------------------------------
-- Comentarios actualizados (corrigen la descripcion del bug ya corregido)
-- ---------------------------------------------------------------------------
COMMENT ON MATERIALIZED VIEW trabajadores_asegurados_hombres IS
'Puestos de trabajo afiliados al IMSS ocupados por hombres por municipio de Jalisco.';

COMMENT ON COLUMN trabajadores_asegurados_hombres.fid IS
'Identificador unico de fila para herramientas GIS.';
COMMENT ON COLUMN trabajadores_asegurados_hombres.geom_iieg IS
'Geometria municipal (EPSG:6368) alineada por el IIEG.';
COMMENT ON COLUMN trabajadores_asegurados_hombres.geom_inegi IS
'Geometria municipal (EPSG:6368) original INEGI.';
COMMENT ON COLUMN trabajadores_asegurados_hombres.nombre IS
'Nombre oficial del municipio.';
COMMENT ON COLUMN trabajadores_asegurados_hombres.fecha IS
'Fecha de corte (primer dia del mes de la fuente IMSS).';
COMMENT ON COLUMN trabajadores_asegurados_hombres.clave_entidad IS
'Clave de la entidad federativa (14 = Jalisco).';
COMMENT ON COLUMN trabajadores_asegurados_hombres.clave_municipio IS
'Clave INEGI del municipio (5 digitos, con entidad).';
COMMENT ON COLUMN trabajadores_asegurados_hombres.total_hombres IS
'Total de puestos de trabajo asegurados para hombres (sexo=1).';
COMMENT ON COLUMN trabajadores_asegurados_hombres.porcentaje_hombres IS
'Porcentaje de puestos de trabajo asegurados ocupados por hombres, respecto al total del municipio.';

COMMENT ON MATERIALIZED VIEW trabajadores_asegurados_mujeres IS
'Puestos de trabajo afiliados al IMSS ocupados por mujeres por municipio de Jalisco.';

COMMENT ON COLUMN trabajadores_asegurados_mujeres.fid IS
'Identificador unico de fila para herramientas GIS.';
COMMENT ON COLUMN trabajadores_asegurados_mujeres.geom_iieg IS
'Geometria municipal (EPSG:6368) alineada por el IIEG.';
COMMENT ON COLUMN trabajadores_asegurados_mujeres.geom_inegi IS
'Geometria municipal (EPSG:6368) original INEGI.';
COMMENT ON COLUMN trabajadores_asegurados_mujeres.nombre IS
'Nombre oficial del municipio.';
COMMENT ON COLUMN trabajadores_asegurados_mujeres.fecha IS
'Fecha de corte (primer dia del mes de la fuente IMSS).';
COMMENT ON COLUMN trabajadores_asegurados_mujeres.clave_entidad IS
'Clave de la entidad federativa (14 = Jalisco).';
COMMENT ON COLUMN trabajadores_asegurados_mujeres.clave_municipio IS
'Clave INEGI del municipio (5 digitos, con entidad).';
COMMENT ON COLUMN trabajadores_asegurados_mujeres.total_mujeres IS
'Total de puestos de trabajo asegurados para mujeres (sexo=2).';
COMMENT ON COLUMN trabajadores_asegurados_mujeres.porcentaje_mujeres IS
'Porcentaje de puestos de trabajo asegurados ocupados por mujeres, respecto al total del municipio.';

COMMENT ON MATERIALIZED VIEW brecha_salarial IS
'Brecha salarial estimada entre hombres y mujeres en Jalisco a partir de la masa salarial (masa_sal_ta) y puestos con salario (ta_sal) del IMSS.';

COMMENT ON COLUMN brecha_salarial.fid IS
'Identificador unico de fila para herramientas GIS.';
COMMENT ON COLUMN brecha_salarial.geom_iieg IS
'Geometria municipal (EPSG:6368) alineada por el IIEG.';
COMMENT ON COLUMN brecha_salarial.geom_inegi IS
'Geometria municipal (EPSG:6368) original INEGI.';
COMMENT ON COLUMN brecha_salarial.nombre IS
'Nombre oficial del municipio.';
COMMENT ON COLUMN brecha_salarial.fecha IS
'Fecha de corte (primer dia del mes de la fuente IMSS).';
COMMENT ON COLUMN brecha_salarial.clave_entidad IS
'Clave de la entidad federativa (14 = Jalisco).';
COMMENT ON COLUMN brecha_salarial.clave_municipio IS
'Clave INEGI del municipio (5 digitos, con entidad).';
COMMENT ON COLUMN brecha_salarial.brecha_salarial IS
'Porcentaje de diferencia del salario promedio diario de mujeres respecto al de hombres.';
COMMENT ON COLUMN brecha_salarial.salario_promedio_diario_mujeres IS
'Salario promedio diario estimado para mujeres (masa_sal_ta / ta_sal).';
COMMENT ON COLUMN brecha_salarial.salario_promedio_diario_hombres IS
'Salario promedio diario estimado para hombres (masa_sal_ta / ta_sal).';
