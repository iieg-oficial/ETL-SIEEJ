-- =============================================================================
-- stg_nacimientos
-- =============================================================================
COMMENT ON TABLE stg_nacimientos IS
    'Staging de nacimientos por municipio, año y edad de la madre. Fuente: SINAC/DGIS.';

COMMENT ON COLUMN stg_nacimientos.id IS 'Identificador único';
COMMENT ON COLUMN stg_nacimientos.anio IS 'Año de nacimiento';
COMMENT ON COLUMN stg_nacimientos.cve_geo IS 'Clave geoestadística del municipio (EEMMM)';
COMMENT ON COLUMN stg_nacimientos.edad_madre IS 'Edad de la madre al momento del nacimiento';
COMMENT ON COLUMN stg_nacimientos.tot_nac IS 'Total de nacimientos registrados';
COMMENT ON COLUMN stg_nacimientos.nac_padre_conocido IS 'Nacimientos donde la edad del padre es conocida';
COMMENT ON COLUMN stg_nacimientos.nac_padre_18_mas IS 'Nacimientos donde el padre tiene 18 años o más';
COMMENT ON COLUMN stg_nacimientos.nac_padre_25_mas IS 'Nacimientos donde el padre tiene 25 años o más';
COMMENT ON COLUMN stg_nacimientos.fecha_actualizacion IS 'Fecha de la última actualización del registro';

-- =============================================================================
-- vw_nacimientos
-- =============================================================================
COMMENT ON VIEW vw_nacimientos IS
    'Vista de nacimientos con nombres de municipio y entidad.';

COMMENT ON COLUMN vw_nacimientos.id IS 'Identificador único';
COMMENT ON COLUMN vw_nacimientos.anio IS 'Año de nacimiento';
COMMENT ON COLUMN vw_nacimientos.municipio IS 'Nombre del municipio';
COMMENT ON COLUMN vw_nacimientos.entidad IS 'Nombre de la entidad federativa';
COMMENT ON COLUMN vw_nacimientos.cve_geo IS 'Clave geoestadística del municipio (EEMMM)';
COMMENT ON COLUMN vw_nacimientos.edad_madre IS 'Edad de la madre al momento del nacimiento';
COMMENT ON COLUMN vw_nacimientos.tot_nac IS 'Total de nacimientos registrados';
COMMENT ON COLUMN vw_nacimientos.nac_padre_conocido IS 'Nacimientos donde la edad del padre es conocida';
COMMENT ON COLUMN vw_nacimientos.nac_padre_18_mas IS 'Nacimientos donde el padre tiene 18 años o más';
COMMENT ON COLUMN vw_nacimientos.nac_padre_25_mas IS 'Nacimientos donde el padre tiene 25 años o más';
COMMENT ON COLUMN vw_nacimientos.fecha_actualizacion IS 'Fecha de la última actualización del registro';

-- =============================================================================
-- vw_tasa_fecundidad
-- =============================================================================
COMMENT ON VIEW vw_tasa_fecundidad IS
    'Vista de tasa de fecundidad general con nombres de municipio y entidad.';

COMMENT ON COLUMN vw_tasa_fecundidad.fecha IS 'Fecha del periodo (1 de enero del año)';
COMMENT ON COLUMN vw_tasa_fecundidad.municipio IS 'Nombre del municipio';
COMMENT ON COLUMN vw_tasa_fecundidad.entidad IS 'Nombre de la entidad federativa';
COMMENT ON COLUMN vw_tasa_fecundidad.municipio_id IS 'Clave del municipio (EEMMM)';
COMMENT ON COLUMN vw_tasa_fecundidad.pob_mujeres_15_49 IS 'Población femenina de 15 a 49 años (CONAPO)';
COMMENT ON COLUMN vw_tasa_fecundidad.nacimientos IS 'Total de nacimientos registrados';
COMMENT ON COLUMN vw_tasa_fecundidad.tasa_fec_gen IS 'Tasa de fecundidad general por cada 1,000 mujeres de 15-49 años';

-- =============================================================================
-- vw_nacimientos_adolescentes
-- =============================================================================
COMMENT ON VIEW vw_nacimientos_adolescentes IS
    'Vista de indicadores de nacimientos adolescentes con nombres de municipio y entidad.';

COMMENT ON COLUMN vw_nacimientos_adolescentes.fecha IS 'Fecha del periodo (1 de enero del año)';
COMMENT ON COLUMN vw_nacimientos_adolescentes.municipio IS 'Nombre del municipio';
COMMENT ON COLUMN vw_nacimientos_adolescentes.entidad IS 'Nombre de la entidad federativa';
COMMENT ON COLUMN vw_nacimientos_adolescentes.municipio_id IS 'Clave del municipio (EEMMM)';
COMMENT ON COLUMN vw_nacimientos_adolescentes.nac_madres_10_14 IS 'Nacimientos de madres de 10-14 años';
COMMENT ON COLUMN vw_nacimientos_adolescentes.tasa_esp_fec_madres_10_14 IS 'Tasa de fecundidad específica por cada 1,000 mujeres de 10-14 años';
COMMENT ON COLUMN vw_nacimientos_adolescentes.pct_padres_18_mas_madres_10_14 IS 'Porcentaje de padres con 18 años o más (madres 10-14)';
COMMENT ON COLUMN vw_nacimientos_adolescentes.pct_edad_padre_sin_dato_madres_10_14 IS 'Porcentaje sin dato de edad del padre (madres 10-14)';
COMMENT ON COLUMN vw_nacimientos_adolescentes.nac_madres_15_19 IS 'Nacimientos de madres de 15-19 años';
COMMENT ON COLUMN vw_nacimientos_adolescentes.tasa_esp_fec_madres_15_19 IS 'Tasa de fecundidad específica por cada 1,000 mujeres de 15-19 años';
COMMENT ON COLUMN vw_nacimientos_adolescentes.pct_padres_25_mas_madres_15_19 IS 'Porcentaje de padres con 25 años o más (madres 15-19)';
COMMENT ON COLUMN vw_nacimientos_adolescentes.pct_edad_padre_sin_dato_madres_15_19 IS 'Porcentaje sin dato de edad del padre (madres 15-19)';

-- =============================================================================
-- stg_tasa_fecundidad
-- =============================================================================
COMMENT ON TABLE stg_tasa_fecundidad IS
    'Tasa de fecundidad general por municipio y año (mujeres 15-49 años).';

COMMENT ON COLUMN stg_tasa_fecundidad.fecha IS 'Fecha del periodo (1 de enero del año)';
COMMENT ON COLUMN stg_tasa_fecundidad.entidad_id IS 'Clave de la entidad federativa';
COMMENT ON COLUMN stg_tasa_fecundidad.municipio_id IS 'Clave del municipio (EEMMM)';
COMMENT ON COLUMN stg_tasa_fecundidad.pob_mujeres_15_49 IS 'Población femenina de 15 a 49 años (CONAPO)';
COMMENT ON COLUMN stg_tasa_fecundidad.nacimientos IS 'Total de nacimientos registrados';
COMMENT ON COLUMN stg_tasa_fecundidad.tasa_fec_gen IS 'Tasa de fecundidad general por cada 1,000 mujeres de 15-49 años';

-- =============================================================================
-- stg_nacimientos_adolescentes
-- =============================================================================
COMMENT ON TABLE stg_nacimientos_adolescentes IS
    'Indicadores de nacimientos de madres adolescentes por grupo de edad (10-14 y 15-19 años).';

COMMENT ON COLUMN stg_nacimientos_adolescentes.fecha IS 'Fecha del periodo (1 de enero del año)';
COMMENT ON COLUMN stg_nacimientos_adolescentes.entidad_id IS 'Clave de la entidad federativa';
COMMENT ON COLUMN stg_nacimientos_adolescentes.municipio_id IS 'Clave del municipio (EEMMM)';
COMMENT ON COLUMN stg_nacimientos_adolescentes.nac_madres_10_14 IS 'Nacimientos de madres de 10-14 años';
COMMENT ON COLUMN stg_nacimientos_adolescentes.tasa_esp_fec_madres_10_14 IS 'Tasa de fecundidad específica por cada 1,000 mujeres de 10-14 años';
COMMENT ON COLUMN stg_nacimientos_adolescentes.pct_padres_18_mas_madres_10_14 IS 'Porcentaje de padres con 18 años o más (madres 10-14)';
COMMENT ON COLUMN stg_nacimientos_adolescentes.pct_edad_padre_sin_dato_madres_10_14 IS 'Porcentaje sin dato de edad del padre (madres 10-14)';
COMMENT ON COLUMN stg_nacimientos_adolescentes.nac_madres_15_19 IS 'Nacimientos de madres de 15-19 años';
COMMENT ON COLUMN stg_nacimientos_adolescentes.tasa_esp_fec_madres_15_19 IS 'Tasa de fecundidad específica por cada 1,000 mujeres de 15-19 años';
COMMENT ON COLUMN stg_nacimientos_adolescentes.pct_padres_25_mas_madres_15_19 IS 'Porcentaje de padres con 25 años o más (madres 15-19)';
COMMENT ON COLUMN stg_nacimientos_adolescentes.pct_edad_padre_sin_dato_madres_15_19 IS 'Porcentaje sin dato de edad del padre (madres 15-19)';

-- =============================================================================
-- tasa_fecundidad (vista materializada)
-- =============================================================================
COMMENT ON MATERIALIZED VIEW tasa_fecundidad IS
    'Vista materializada de tasa de fecundidad general con geometría municipal.';

COMMENT ON COLUMN tasa_fecundidad.fid IS 'Identificador único de la fila';
COMMENT ON COLUMN tasa_fecundidad.geom_iieg IS 'Geometría del municipio (marco geoestadístico IIEG, SRID 6368)';
COMMENT ON COLUMN tasa_fecundidad.geom_inegi IS 'Geometría del municipio (marco geoestadístico INEGI, SRID 6368)';
COMMENT ON COLUMN tasa_fecundidad.nombre IS 'Nombre del municipio';
COMMENT ON COLUMN tasa_fecundidad.fecha IS 'Fecha del periodo (1 de enero del año)';
COMMENT ON COLUMN tasa_fecundidad.clave_entidad IS 'Clave de la entidad federativa';
COMMENT ON COLUMN tasa_fecundidad.clave_municipio IS 'Clave del municipio (EEMMM)';
COMMENT ON COLUMN tasa_fecundidad.poblacion_mujeres_15_49 IS 'Población femenina de 15 a 49 años (CONAPO)';
COMMENT ON COLUMN tasa_fecundidad.nacimientos IS 'Total de nacimientos registrados';
COMMENT ON COLUMN tasa_fecundidad.tasa_fecundidad_general IS 'Tasa de fecundidad general por cada 1,000 mujeres de 15-49 años';

-- =============================================================================
-- nacimientos_adolescentes (vista materializada)
-- =============================================================================
COMMENT ON MATERIALIZED VIEW nacimientos_adolescentes IS
    'Vista materializada de nacimientos de madres de 15-19 años con geometría municipal.';

COMMENT ON COLUMN nacimientos_adolescentes.fid IS 'Identificador único de la fila';
COMMENT ON COLUMN nacimientos_adolescentes.geom_iieg IS 'Geometría del municipio (marco geoestadístico IIEG, SRID 6368)';
COMMENT ON COLUMN nacimientos_adolescentes.geom_inegi IS 'Geometría del municipio (marco geoestadístico INEGI, SRID 6368)';
COMMENT ON COLUMN nacimientos_adolescentes.nombre IS 'Nombre del municipio';
COMMENT ON COLUMN nacimientos_adolescentes.fecha IS 'Fecha del periodo (1 de enero del año)';
COMMENT ON COLUMN nacimientos_adolescentes.clave_entidad IS 'Clave de la entidad federativa';
COMMENT ON COLUMN nacimientos_adolescentes.nacimientos_madre_adelocente IS 'Nacimientos de madres de 15-19 años';
COMMENT ON COLUMN nacimientos_adolescentes.tasa_fecundidad_adolecente IS 'Tasa de fecundidad específica por cada 1,000 mujeres de 15-19 años';
COMMENT ON COLUMN nacimientos_adolescentes.porcentaje_con_edad_mayor_25 IS 'Porcentaje de padres con 25 años o más';

-- =============================================================================
-- nacimientos_infantiles (vista materializada)
-- =============================================================================
COMMENT ON MATERIALIZED VIEW nacimientos_infantiles IS
    'Vista materializada de nacimientos de madres de 10-14 años con geometría municipal.';

COMMENT ON COLUMN nacimientos_infantiles.fid IS 'Identificador único de la fila';
COMMENT ON COLUMN nacimientos_infantiles.geom_iieg IS 'Geometría del municipio (marco geoestadístico IIEG, SRID 6368)';
COMMENT ON COLUMN nacimientos_infantiles.geom_inegi IS 'Geometría del municipio (marco geoestadístico INEGI, SRID 6368)';
COMMENT ON COLUMN nacimientos_infantiles.nombre IS 'Nombre del municipio';
COMMENT ON COLUMN nacimientos_infantiles.fecha IS 'Fecha del periodo (1 de enero del año)';
COMMENT ON COLUMN nacimientos_infantiles.clave_entidad IS 'Clave de la entidad federativa';
COMMENT ON COLUMN nacimientos_infantiles.nacimientos IS 'Nacimientos de madres de 10-14 años';
COMMENT ON COLUMN nacimientos_infantiles.tasa_fecundidad_especifica IS 'Tasa de fecundidad específica por cada 1,000 mujeres de 10-14 años';
COMMENT ON COLUMN nacimientos_infantiles.porcentaje_con_edad_mayor_18 IS 'Porcentaje de padres con 18 años o más';
