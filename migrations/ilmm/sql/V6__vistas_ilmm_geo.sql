-- ---------------------------------------------------------------------------
-- cvegeo_municipalities es una foreign table (FDW, ver V1__foreign_tables.sql)
-- que solo importaba id/cvegeo/cve_ent/cve_mun/nomgeo/nom_ent. Se extiende
-- para traer también la geometría del lado remoto (base cvegeo).
-- ---------------------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS postgis;

ALTER FOREIGN TABLE cvegeo_municipalities ADD COLUMN geom_iieg public.geometry(MultiPolygon, 6368);
ALTER FOREIGN TABLE cvegeo_municipalities ADD COLUMN geom_inegi public.geometry(MultiPolygon, 6368);

-- ---------------------------------------------------------------------------
-- Recrear vw_ocupacion_informal y vw_tasa_desocupacion con la estructura de
-- economia.ocupacion_informal / economia.tasa_desocupacion en proxmox:
-- fid, geom_iieg, geom_inegi, nombre, clave_entidad, valor/error_estandar en
-- numeric(12,2). clave_entidad se deriva de cvegeo_municipalities.cve_ent
-- (no se fija a Jalisco: stg_ilmm cubre todo México).
-- Ver comparaciones/comparacion_ilmm_etl_proxmox.md sección 6.
-- ---------------------------------------------------------------------------
DROP MATERIALIZED VIEW IF EXISTS vw_ocupacion_informal CASCADE;
DROP MATERIALIZED VIEW IF EXISTS vw_tasa_desocupacion CASCADE;

CREATE MATERIALIZED VIEW vw_ocupacion_informal AS
SELECT
    row_number() OVER (ORDER BY m.nomgeo, s1.fecha)  AS fid,
    m.geom_iieg,
    m.geom_inegi,
    m.nomgeo::character varying(254)                 AS nombre,
    s1.fecha,
    LPAD(m.cve_ent::text, 2, '0')::character(2)       AS clave_entidad,
    s1.clave_municipio,
    ROUND(s1.informales, 2)::numeric(12, 2)           AS valor,
    ROUND(s2.informales, 2)::numeric(12, 2)           AS error_estandar
FROM stg_ilmm s1
JOIN stg_ilmm s2
    ON  s1.clave_municipio = s2.clave_municipio
    AND s1.fecha           = s2.fecha
    AND s1.estimador_id    = 1
    AND s2.estimador_id    = 2
JOIN cvegeo_municipalities m
    ON LPAD(m.cvegeo::text, 5, '0') = s1.clave_municipio;

CREATE UNIQUE INDEX idx_mvw_ocupacion_informal_pk ON vw_ocupacion_informal (clave_municipio, fecha);

COMMENT ON MATERIALIZED VIEW vw_ocupacion_informal IS 'Porcentaje de ocupación en el sector informal por municipio y fecha, con geometría y estructura homologada a economia.ocupacion_informal (proxmox).';

CREATE MATERIALIZED VIEW vw_tasa_desocupacion AS
SELECT
    row_number() OVER (ORDER BY m.nomgeo, s1.fecha)  AS fid,
    m.geom_iieg,
    m.geom_inegi,
    m.nomgeo::character varying(254)                 AS nombre,
    s1.fecha,
    LPAD(m.cve_ent::text, 2, '0')::character(2)       AS clave_entidad,
    s1.clave_municipio,
    ROUND((100 - s1.ocupados), 2)::numeric(12, 2)     AS valor,
    ROUND(s2.ocupados, 2)::numeric(12, 2)             AS error_estandar
FROM stg_ilmm s1
JOIN stg_ilmm s2
    ON  s1.clave_municipio = s2.clave_municipio
    AND s1.fecha           = s2.fecha
    AND s1.estimador_id    = 1
    AND s2.estimador_id    = 2
JOIN cvegeo_municipalities m
    ON LPAD(m.cvegeo::text, 5, '0') = s1.clave_municipio;

CREATE UNIQUE INDEX idx_mvw_tasa_desocupacion_pk ON vw_tasa_desocupacion (clave_municipio, fecha);

COMMENT ON MATERIALIZED VIEW vw_tasa_desocupacion IS 'Tasa de desocupación por municipio y fecha, con geometría y estructura homologada a economia.tasa_desocupacion (proxmox).';
