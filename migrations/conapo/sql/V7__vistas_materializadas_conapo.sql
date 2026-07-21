-- ========================================================================
-- V7: Vistas materializadas CONAPO para consumo GIS (iieg_gis)
-- ========================================================================
-- 8 vistas materializadas con geometrias municipales a partir de los
-- indicadores demograficos de CONAPO (stg_indicadores_demograficos).
-- Fecha base: anual (anio -> YYYY-01-01).
-- Filtro geografico: Jalisco (cve_ent = 14).
-- ========================================================================

-- ---------------------------------------------------------------------------
-- 1. poblacion
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS poblacion AS
SELECT
    ROW_NUMBER() OVER ()::bigint               AS fid,
    g.geom_iieg,
    g.geom_inegi,
    g.nomgeo::varchar(254)                     AS nombre,
    make_date(i.anio, 1, 1)                    AS fecha,
    '14'::char(2)                              AS clave_entidad,
    LPAD(g.cvegeo::text, 5, '0')::varchar(5)   AS clave_municipio,
    i.pob_mit_mun                              AS poblacion_total,
    i.hom_mit_ano                              AS poblacion_hombres,
    i.muj_mit_ano                              AS poblacion_mujeres,
    ROUND(i.por_mun::numeric, 2)               AS poblacion_respecto_jalisco
FROM stg_indicadores_demograficos i
JOIN cvegeo_municipalities g ON i.municipio_id = g.cvegeo
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS ix_poblacion_fid
    ON poblacion (fid);

-- ---------------------------------------------------------------------------
-- 2. poblacion_hombres
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS poblacion_hombres AS
SELECT
    ROW_NUMBER() OVER ()::bigint               AS fid,
    g.geom_iieg,
    g.geom_inegi,
    g.nomgeo::varchar(254)                     AS nombre,
    make_date(i.anio, 1, 1)                    AS fecha,
    '14'::char(2)                              AS clave_entidad,
    LPAD(g.cvegeo::text, 5, '0')::varchar(5)   AS clave_municipio,
    i.hom_mit_ano                              AS poblacion_hombres
FROM stg_indicadores_demograficos i
JOIN cvegeo_municipalities g ON i.municipio_id = g.cvegeo
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS ix_poblacion_hombres_fid
    ON poblacion_hombres (fid);

-- ---------------------------------------------------------------------------
-- 3. poblacion_mujeres
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS poblacion_mujeres AS
SELECT
    ROW_NUMBER() OVER ()::bigint               AS fid,
    g.geom_iieg,
    g.geom_inegi,
    g.nomgeo::varchar(254)                     AS nombre,
    make_date(i.anio, 1, 1)                    AS fecha,
    '14'::char(2)                              AS clave_entidad,
    LPAD(g.cvegeo::text, 5, '0')::varchar(5)   AS clave_municipio,
    i.muj_mit_ano                              AS poblacion_mujeres
FROM stg_indicadores_demograficos i
JOIN cvegeo_municipalities g ON i.municipio_id = g.cvegeo
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS ix_poblacion_mujeres_fid
    ON poblacion_mujeres (fid);

-- ---------------------------------------------------------------------------
-- 4. edad_mediana
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS edad_mediana AS
SELECT
    ROW_NUMBER() OVER ()::bigint               AS fid,
    g.geom_iieg,
    g.geom_inegi,
    g.nomgeo::varchar(254)                     AS nombre,
    make_date(i.anio, 1, 1)                    AS fecha,
    '14'::char(2)                              AS clave_entidad,
    LPAD(g.cvegeo::text, 5, '0')::varchar(5)   AS clave_municipio,
    i.edad_med                                 AS edad_mediana
FROM stg_indicadores_demograficos i
JOIN cvegeo_municipalities g ON i.municipio_id = g.cvegeo
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS ix_edad_mediana_fid
    ON edad_mediana (fid);

-- ---------------------------------------------------------------------------
-- 5. porcentaje_poblacional_municipal_en_entidad
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS porcentaje_poblacional_municipal_en_entidad AS
SELECT
    ROW_NUMBER() OVER ()::bigint               AS fid,
    g.geom_iieg,
    g.geom_inegi,
    g.nomgeo::varchar(254)                     AS nombre,
    make_date(i.anio, 1, 1)                    AS fecha,
    '14'::char(2)                              AS clave_entidad,
    LPAD(g.cvegeo::text, 5, '0')::varchar(5)   AS clave_municipio,
    ROUND(i.por_mun::numeric, 2)               AS porcentaje
FROM stg_indicadores_demograficos i
JOIN cvegeo_municipalities g ON i.municipio_id = g.cvegeo
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS ix_porcentaje_poblacional_municipal_en_entidad_fid
    ON porcentaje_poblacional_municipal_en_entidad (fid);

-- ---------------------------------------------------------------------------
-- 6. razon_dependencia
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS razon_dependencia AS
SELECT
    ROW_NUMBER() OVER ()::bigint               AS fid,
    g.geom_iieg,
    g.geom_inegi,
    g.nomgeo::varchar(254)                     AS nombre,
    make_date(i.anio, 1, 1)                    AS fecha,
    '14'::char(2)                              AS clave_entidad,
    LPAD(g.cvegeo::text, 5, '0')::varchar(5)   AS clave_municipio,
    ROUND(i.raz_dep::numeric, 2)               AS razon_dependencia
FROM stg_indicadores_demograficos i
JOIN cvegeo_municipalities g ON i.municipio_id = g.cvegeo
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS ix_razon_dependencia_fid
    ON razon_dependencia (fid);

-- ---------------------------------------------------------------------------
-- 7. razon_dependencia_adulta
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS razon_dependencia_adulta AS
SELECT
    ROW_NUMBER() OVER ()::bigint               AS fid,
    g.geom_iieg,
    g.geom_inegi,
    g.nomgeo::varchar(254)                     AS nombre,
    make_date(i.anio, 1, 1)                    AS fecha,
    '14'::char(2)                              AS clave_entidad,
    LPAD(g.cvegeo::text, 5, '0')::varchar(5)   AS clave_municipio,
    ROUND(i.raz_dep_adu::numeric, 2)           AS razon_dependencia_adulta
FROM stg_indicadores_demograficos i
JOIN cvegeo_municipalities g ON i.municipio_id = g.cvegeo
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS ix_razon_dependencia_adulta_fid
    ON razon_dependencia_adulta (fid);

-- ---------------------------------------------------------------------------
-- 8. razon_dependencia_infantil
-- ---------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS razon_dependencia_infantil AS
SELECT
    ROW_NUMBER() OVER ()::bigint               AS fid,
    g.geom_iieg,
    g.geom_inegi,
    g.nomgeo::varchar(254)                     AS nombre,
    make_date(i.anio, 1, 1)                    AS fecha,
    '14'::char(2)                              AS clave_entidad,
    LPAD(g.cvegeo::text, 5, '0')::varchar(5)   AS clave_municipio,
    ROUND(i.raz_dep_inf::numeric, 2)           AS razon_dependencia_infantil
FROM stg_indicadores_demograficos i
JOIN cvegeo_municipalities g ON i.municipio_id = g.cvegeo
WHERE g.cve_ent = 14
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS ix_razon_dependencia_infantil_fid
    ON razon_dependencia_infantil (fid);
