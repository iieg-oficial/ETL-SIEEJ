ALTER FOREIGN TABLE nacimientos_dgis_certificados
    ADD COLUMN IF NOT EXISTS sexo_id INTEGER;

CREATE FOREIGN TABLE IF NOT EXISTS nacimientos_dgis_cat_sexo (
    id INTEGER,
    clave INTEGER
)
SERVER nacimientos_dgis_server
OPTIONS (schema_name 'public', table_name 'cat_sexo');

CREATE MATERIALIZED VIEW vm_mortalidad_infantil_geo AS
WITH defunciones_infantiles AS (
    SELECT
        d.anio_ocurrencia,
        d.entidad_residencia_id,
        d.municipio_residencia_id,
        COUNT(*) AS defunciones_menor_1_anio,
        COUNT(*) FILTER (WHERE s.clave = 1) AS defunciones_menor_1_anio_hombres,
        COUNT(*) FILTER (WHERE s.clave = 2) AS defunciones_menor_1_anio_mujeres
    FROM stg_defunciones AS d
    LEFT JOIN cat_sexo AS s ON s.id = d.sexo_id
    INNER JOIN cvegeo_municipalities AS m
        ON m.cve_ent = d.entidad_residencia_id
        AND m.cve_mun = d.municipio_residencia_id
    WHERE d.edad_agrupada_id = 1
        AND d.entidad_residencia_id = 14
        AND d.anio_ocurrencia >= 2020
    GROUP BY d.anio_ocurrencia, d.entidad_residencia_id, d.municipio_residencia_id
),
nacimientos_vivos AS (
    SELECT
        EXTRACT(YEAR FROM n.fecha_nacimiento)::integer AS anio,
        n.cve_geo,
        COUNT(*) AS nacimientos_vivos,
        COUNT(*) FILTER (WHERE s.clave = 1) AS nacimientos_vivos_hombres,
        COUNT(*) FILTER (WHERE s.clave = 2) AS nacimientos_vivos_mujeres
    FROM nacimientos_dgis_certificados AS n
    LEFT JOIN nacimientos_dgis_cat_sexo AS s ON s.id = n.sexo_id
    WHERE n.fecha_nacimiento >= DATE '2020-01-01'
    GROUP BY EXTRACT(YEAR FROM n.fecha_nacimiento)::integer, n.cve_geo
)
SELECT
    (n.anio * 100000 + m.cvegeo)::integer AS fid,
    make_date(n.anio, 1, 1) AS fecha_periodo_seleccion,
    LPAD(m.cve_ent::text, 2, '0')::varchar(2) AS cve_ent,
    m.nom_ent AS entidad,
    LPAD(m.cvegeo::text, 5, '0')::varchar(5) AS cvegeo_municipio,
    m.nomgeo AS municipio,
    COALESCE(d.defunciones_menor_1_anio, 0) AS defunciones_menor_1_anio,
    n.nacimientos_vivos,
    COALESCE(d.defunciones_menor_1_anio, 0) * 1000.0 / NULLIF(n.nacimientos_vivos, 0) AS tasa_mortalidad_infantil,
    COALESCE(d.defunciones_menor_1_anio_mujeres, 0) AS defunciones_menor_1_anio_mujeres,
    n.nacimientos_vivos_mujeres,
    COALESCE(d.defunciones_menor_1_anio_mujeres, 0) * 1000.0 / NULLIF(n.nacimientos_vivos_mujeres, 0) AS tasa_mortalidad_infantil_mujeres,
    COALESCE(d.defunciones_menor_1_anio_hombres, 0) AS defunciones_menor_1_anio_hombres,
    n.nacimientos_vivos_hombres,
    COALESCE(d.defunciones_menor_1_anio_hombres, 0) * 1000.0 / NULLIF(n.nacimientos_vivos_hombres, 0) AS tasa_mortalidad_infantil_hombres,
    m.geom_iieg,
    m.geom_inegi
FROM nacimientos_vivos AS n
INNER JOIN cvegeo_municipalities AS m ON m.cvegeo = n.cve_geo AND m.cve_ent = 14
LEFT JOIN defunciones_infantiles AS d
    ON d.anio_ocurrencia = n.anio
    AND d.entidad_residencia_id = m.cve_ent
    AND d.municipio_residencia_id = m.cve_mun
ORDER BY n.anio, m.cvegeo
WITH NO DATA;

CREATE UNIQUE INDEX ix_vm_mortalidad_infantil_geo_fid ON vm_mortalidad_infantil_geo (fid);
CREATE UNIQUE INDEX ix_vm_mortalidad_infantil_geo_periodo_municipio ON vm_mortalidad_infantil_geo (fecha_periodo_seleccion, cvegeo_municipio);
CREATE INDEX ix_vm_mortalidad_infantil_geo_fecha_periodo_seleccion ON vm_mortalidad_infantil_geo (fecha_periodo_seleccion);
CREATE INDEX ix_vm_mortalidad_infantil_geo_geom_iieg ON vm_mortalidad_infantil_geo USING GIST (geom_iieg);
CREATE INDEX ix_vm_mortalidad_infantil_geo_geom_inegi ON vm_mortalidad_infantil_geo USING GIST (geom_inegi);

COMMENT ON MATERIALIZED VIEW vm_mortalidad_infantil_geo IS 'Tasas municipales de mortalidad infantil para residentes de Jalisco, desde 2020, para consumo GIS.';
COMMENT ON COLUMN vm_mortalidad_infantil_geo.tasa_mortalidad_infantil IS 'Defunciones de menores de un ano por cada 1000 nacimientos vivos.';
COMMENT ON COLUMN vm_mortalidad_infantil_geo.tasa_mortalidad_infantil_mujeres IS 'Defunciones de menores de un ano mujeres por cada 1000 nacimientos vivos mujeres.';
COMMENT ON COLUMN vm_mortalidad_infantil_geo.tasa_mortalidad_infantil_hombres IS 'Defunciones de menores de un ano hombres por cada 1000 nacimientos vivos hombres.';
