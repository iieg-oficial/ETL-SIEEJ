CREATE MATERIALIZED VIEW vm_mortalidad_adulta_geo AS
WITH defunciones_adultas AS (
    SELECT
        d.anio_ocurrencia,
        d.entidad_residencia_id,
        d.municipio_residencia_id,
        COUNT(*) AS defunciones_15_59,
        COUNT(*) FILTER (WHERE d.sexo_id = 2) AS defunciones_mujeres_15_59,
        COUNT(*) FILTER (WHERE d.sexo_id = 1) AS defunciones_hombres_15_59
    FROM stg_defunciones AS d
    INNER JOIN cvegeo_municipalities AS m
        ON m.cve_ent = d.entidad_residencia_id
        AND m.cve_mun = d.municipio_residencia_id
    WHERE d.entidad_residencia_id = 14
        AND d.anio_ocurrencia >= 2017
        AND d.anio_ocurrencia IS NOT NULL
        AND d.edad_agrupada_id BETWEEN 8 AND 16
    GROUP BY
        d.anio_ocurrencia,
        d.entidad_residencia_id,
        d.municipio_residencia_id
),
periodos AS (
    SELECT DISTINCT anio_ocurrencia
    FROM defunciones_adultas
),
poblacion_adulta AS (
    SELECT
        p.anio,
        p.entidad_id,
        p.municipio_id,
        SUM(
            p.pob_15_19 + p.pob_20_24 + p.pob_25_29 + p.pob_30_34
            + p.pob_35_39 + p.pob_40_44 + p.pob_45_49 + p.pob_50_54
            + p.pob_55_59
        ) AS poblacion_15_59,
        SUM(
            p.pob_15_19 + p.pob_20_24 + p.pob_25_29 + p.pob_30_34
            + p.pob_35_39 + p.pob_40_44 + p.pob_45_49 + p.pob_50_54
            + p.pob_55_59
        ) FILTER (WHERE p.sexo_id = 2) AS poblacion_mujeres_15_59,
        SUM(
            p.pob_15_19 + p.pob_20_24 + p.pob_25_29 + p.pob_30_34
            + p.pob_35_39 + p.pob_40_44 + p.pob_45_49 + p.pob_50_54
            + p.pob_55_59
        ) FILTER (WHERE p.sexo_id = 1) AS poblacion_hombres_15_59
    FROM conapo_poblacion_mitad_anio AS p
    WHERE p.entidad_id = 14
        AND p.sexo_id IN (1, 2)
    GROUP BY p.anio, p.entidad_id, p.municipio_id
)
SELECT
    ROW_NUMBER() OVER (
        ORDER BY p.anio, m.cvegeo
    )::integer AS fid,
    make_date(p.anio, 1, 1) AS fecha_periodo_seleccion,
    LPAD(m.cve_ent::text, 2, '0')::varchar(2) AS cve_ent,
    m.nom_ent AS entidad,
    LPAD(m.cvegeo::text, 5, '0')::varchar(5) AS cvegeo_municipio,
    m.nomgeo AS municipio,
    COALESCE(d.defunciones_15_59, 0) AS defunciones_15_59,
    p.poblacion_15_59,
    COALESCE(d.defunciones_15_59, 0) * 100000.0
        / NULLIF(p.poblacion_15_59, 0) AS tasa_mortalidad_15_59,
    COALESCE(d.defunciones_mujeres_15_59, 0) AS defunciones_mujeres_15_59,
    p.poblacion_mujeres_15_59,
    COALESCE(d.defunciones_mujeres_15_59, 0) * 100000.0
        / NULLIF(p.poblacion_mujeres_15_59, 0) AS tasa_mortalidad_mujeres_15_59,
    COALESCE(d.defunciones_hombres_15_59, 0) AS defunciones_hombres_15_59,
    p.poblacion_hombres_15_59,
    COALESCE(d.defunciones_hombres_15_59, 0) * 100000.0
        / NULLIF(p.poblacion_hombres_15_59, 0) AS tasa_mortalidad_hombres_15_59,
    m.geom_iieg,
    m.geom_inegi
FROM poblacion_adulta AS p
INNER JOIN periodos AS periodo
    ON periodo.anio_ocurrencia = p.anio
INNER JOIN cvegeo_municipalities AS m
    ON m.cvegeo = p.municipio_id
    AND m.cve_ent = p.entidad_id
LEFT JOIN defunciones_adultas AS d
    ON d.anio_ocurrencia = p.anio
    AND d.entidad_residencia_id = p.entidad_id
    AND d.municipio_residencia_id = m.cve_mun
ORDER BY p.anio, m.cvegeo
WITH NO DATA;

CREATE UNIQUE INDEX ix_vm_mortalidad_adulta_geo_fid
    ON vm_mortalidad_adulta_geo (fid);

CREATE INDEX ix_vm_mortalidad_adulta_geo_fecha_periodo_seleccion
    ON vm_mortalidad_adulta_geo (fecha_periodo_seleccion);

CREATE INDEX ix_vm_mortalidad_adulta_geo_geom_iieg
    ON vm_mortalidad_adulta_geo USING GIST (geom_iieg);

CREATE INDEX ix_vm_mortalidad_adulta_geo_geom_inegi
    ON vm_mortalidad_adulta_geo USING GIST (geom_inegi);

COMMENT ON MATERIALIZED VIEW vm_mortalidad_adulta_geo IS
    'Tasas municipales de mortalidad de 15 a 59 anos para residentes de Jalisco, desde 2017, para consumo GIS.';
COMMENT ON COLUMN vm_mortalidad_adulta_geo.fid IS
    'Identificador estable por combinacion de anio y municipio.';
COMMENT ON COLUMN vm_mortalidad_adulta_geo.fecha_periodo_seleccion IS
    'Fecha de referencia anual de la defuncion (primer dia del ano).';
COMMENT ON COLUMN vm_mortalidad_adulta_geo.cve_ent IS
    'Clave INEGI de dos digitos de la entidad federativa.';
COMMENT ON COLUMN vm_mortalidad_adulta_geo.entidad IS
    'Nombre de la entidad federativa.';
COMMENT ON COLUMN vm_mortalidad_adulta_geo.cvegeo_municipio IS
    'Clave INEGI de cinco digitos del municipio.';
COMMENT ON COLUMN vm_mortalidad_adulta_geo.municipio IS
    'Nombre oficial del municipio.';
COMMENT ON COLUMN vm_mortalidad_adulta_geo.defunciones_15_59 IS
    'Defunciones de residentes de 15 a 59 anos, incluyendo sexo no especificado.';
COMMENT ON COLUMN vm_mortalidad_adulta_geo.poblacion_15_59 IS
    'Poblacion de 15 a 59 anos, suma de hombres y mujeres de CONAPO.';
COMMENT ON COLUMN vm_mortalidad_adulta_geo.tasa_mortalidad_15_59 IS
    'Defunciones de 15 a 59 anos por cada 100000 habitantes de 15 a 59 anos.';
COMMENT ON COLUMN vm_mortalidad_adulta_geo.defunciones_mujeres_15_59 IS
    'Defunciones de mujeres de 15 a 59 anos.';
COMMENT ON COLUMN vm_mortalidad_adulta_geo.poblacion_mujeres_15_59 IS
    'Poblacion de mujeres de 15 a 59 anos.';
COMMENT ON COLUMN vm_mortalidad_adulta_geo.tasa_mortalidad_mujeres_15_59 IS
    'Defunciones de mujeres de 15 a 59 anos por cada 100000 mujeres de 15 a 59 anos.';
COMMENT ON COLUMN vm_mortalidad_adulta_geo.defunciones_hombres_15_59 IS
    'Defunciones de hombres de 15 a 59 anos.';
COMMENT ON COLUMN vm_mortalidad_adulta_geo.poblacion_hombres_15_59 IS
    'Poblacion de hombres de 15 a 59 anos.';
COMMENT ON COLUMN vm_mortalidad_adulta_geo.tasa_mortalidad_hombres_15_59 IS
    'Defunciones de hombres de 15 a 59 anos por cada 100000 hombres de 15 a 59 anos.';
COMMENT ON COLUMN vm_mortalidad_adulta_geo.geom_iieg IS
    'Geometria municipal del marco geoestadistico IIEG, SRID 6368.';
COMMENT ON COLUMN vm_mortalidad_adulta_geo.geom_inegi IS
    'Geometria municipal del marco geoestadistico INEGI, SRID 6368.';
