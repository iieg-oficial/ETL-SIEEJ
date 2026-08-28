CREATE MATERIALIZED VIEW vm_iim_geo AS
SELECT
    m.id AS fid,
    m.fecha,
    s.cve_ent AS clave_entidad,
    s.nom_ent AS entidad,
    m.municipio_id AS clave_municipio,
    s.nomgeo AS municipio,
    CASE m.fecha
        WHEN 2010 THEN m.gaim
        WHEN 2020 THEN m.gim_dp2
    END AS grado_absoluto_intensidad_migratoria,
    m.viv_totales AS total_viviendas,
    m.por_viv_remesas AS porcentaje_viviendas_remesas,
    m.por_viv_emigrantes AS porcentaje_viviendas_emigrantes,
    m.por_viv_circ AS porcentaje_viviendas_migrantes_circulares,
    m.por_viv_reto AS porcentaje_viviendas_migrantes_de_retorno,
    s.geom_iieg,
    s.geom_inegi
FROM iim_municipal AS m
INNER JOIN cvegeo_municipalities AS s
ON s.cvegeo = m.municipio_id
AND s.cve_ent = 14
ORDER BY m.municipio_id
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS ix_vm_iim_geo_fid
    ON vm_iim_geo (fid);

CREATE INDEX IF NOT EXISTS ix_vm_iim_geo_geom_iieg
    ON vm_iim_geo USING GIST (geom_iieg);

CREATE INDEX IF NOT EXISTS ix_vm_iim_geo_geom_inegi
    ON vm_iim_geo USING GIST (geom_inegi);

COMMENT ON MATERIALIZED VIEW vm_iim_geo IS
    'Indice de Intensidad Migratoria Mexico-EUA por municipio de Jalisco, para consumo GIS.';
COMMENT ON COLUMN vm_iim_geo.fid IS 'Identificador estable de la fila.';
COMMENT ON COLUMN vm_iim_geo.fecha IS 'Anio de referencia del indice.';
COMMENT ON COLUMN vm_iim_geo.clave_entidad IS 'Clave INEGI de la entidad federativa.';
COMMENT ON COLUMN vm_iim_geo.entidad IS 'Nombre de la entidad federativa.';
COMMENT ON COLUMN vm_iim_geo.clave_municipio IS 'Clave INEGI del municipio.';
COMMENT ON COLUMN vm_iim_geo.municipio IS 'Nombre del municipio.';
COMMENT ON COLUMN vm_iim_geo.grado_absoluto_intensidad_migratoria IS
    'Grado de intensidad migratoria disponible para el anio de referencia.';
COMMENT ON COLUMN vm_iim_geo.total_viviendas IS 'Total de viviendas.';
COMMENT ON COLUMN vm_iim_geo.porcentaje_viviendas_remesas IS
    'Porcentaje de viviendas que reciben remesas.';
COMMENT ON COLUMN vm_iim_geo.porcentaje_viviendas_emigrantes IS
    'Porcentaje de viviendas con emigrantes a Estados Unidos.';
COMMENT ON COLUMN vm_iim_geo.porcentaje_viviendas_migrantes_circulares IS
    'Porcentaje de viviendas con migrantes circulares.';
COMMENT ON COLUMN vm_iim_geo.porcentaje_viviendas_migrantes_de_retorno IS
    'Porcentaje de viviendas con migrantes de retorno.';
COMMENT ON COLUMN vm_iim_geo.geom_iieg IS
    'Geometria municipal del marco geoestadistico IIEG, SRID 6368.';
COMMENT ON COLUMN vm_iim_geo.geom_inegi IS
    'Geometria municipal del marco geoestadistico INEGI, SRID 6368.';
