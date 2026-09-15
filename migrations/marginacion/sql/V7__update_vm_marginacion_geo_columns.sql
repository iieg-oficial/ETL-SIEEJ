DROP MATERIALIZED VIEW IF EXISTS vm_marginacion_geo;

CREATE MATERIALIZED VIEW vm_marginacion_geo AS
SELECT
    mm.id AS fid,
    mm.fecha_actualizacion AS fecha_periodo_seleccion,
    LPAD(s.cve_ent::text, 2, '0')::varchar(2) AS cve_ent,
    s.nom_ent AS entidad,
    LPAD(mm.municipio_id::text, 5, '0')::varchar(5) AS cvegeo_municipio,
    s.nomgeo AS municipio,
    gm.grado_marginacion,
    mm.porc_pob15_analfabeta AS porcentaje_poblacion_15mas_analfabeta,
    mm.pob15_sin_educ_bas AS porcentaje_poblacion_15mas_sin_educacion_basica,
    mm.porc_viv_sin_drenaje_ni_excusado AS porcentaje_ocupantes_vivienda_sin_drenaje_ni_excusado,
    mm.porc_viv_sin_energia AS porcentaje_ocupantes_vivienda_sin_electricidad,
    mm.porc_viv_sin_agua_entubada AS porcentaje_ocupantes_vivienda_sin_agua_entubada,
    mm.porc_viv_piso_tierra AS porcentaje_ocupantes_vivienda_piso_tierra,
    mm.prom_ocup_por_cuarto AS porcentaje_viviendas_hacinamiento,
    mm.porc_pob_loc_menos5000_hab AS porcentaje_poblacion_localidades_menos_5k_habitantes,
    mm.pob_ocup_hasta_2_sal_min AS porcentaje_poblacion_ingresos_hasta_2_salarios_minimos,
    s.geom_iieg,
    s.geom_inegi
FROM marginaciones_municipales AS mm
INNER JOIN cvegeo_municipalities AS s
    ON s.cvegeo = mm.municipio_id
    AND s.cve_ent = 14
LEFT JOIN grados_marginacion AS gm
    ON gm.id = mm.grado_marginacion_id
ORDER BY mm.municipio_id, mm.fecha_actualizacion, mm.id
WITH NO DATA;

CREATE UNIQUE INDEX ix_vm_marginacion_geo_fid
    ON vm_marginacion_geo (fid);

CREATE INDEX ix_vm_marginacion_geo_geom_iieg
    ON vm_marginacion_geo USING GIST (geom_iieg);

CREATE INDEX ix_vm_marginacion_geo_geom_inegi
    ON vm_marginacion_geo USING GIST (geom_inegi);

COMMENT ON MATERIALIZED VIEW vm_marginacion_geo IS
    'Indice de Marginacion por municipio de Jalisco, para consumo GIS.';
COMMENT ON COLUMN vm_marginacion_geo.fid IS 'Identificador estable de la fila.';
COMMENT ON COLUMN vm_marginacion_geo.fecha_periodo_seleccion IS
    'Fecha de actualizacion del indice.';
COMMENT ON COLUMN vm_marginacion_geo.cve_ent IS 'Clave INEGI de la entidad federativa.';
COMMENT ON COLUMN vm_marginacion_geo.entidad IS 'Nombre de la entidad federativa.';
COMMENT ON COLUMN vm_marginacion_geo.cvegeo_municipio IS 'Clave INEGI del municipio.';
COMMENT ON COLUMN vm_marginacion_geo.municipio IS 'Nombre del municipio.';
COMMENT ON COLUMN vm_marginacion_geo.grado_marginacion IS 'Grado de marginacion en palabras.';
COMMENT ON COLUMN vm_marginacion_geo.geom_iieg IS
    'Geometria municipal del marco geoestadistico IIEG, SRID 6368.';
COMMENT ON COLUMN vm_marginacion_geo.geom_inegi IS
    'Geometria municipal del marco geoestadistico INEGI, SRID 6368.';
