-- ========================================================================
-- V8: Comentarios en vistas materializadas CONAPO
-- ========================================================================

-- poblacion
COMMENT ON MATERIALIZED VIEW poblacion IS
    'Proyeccion anual de poblacion total por municipio con geometrias (fuente: CONAPO).';

COMMENT ON COLUMN poblacion.fid IS 'Identificador unico de la fila';
COMMENT ON COLUMN poblacion.geom_iieg IS 'Geometria del municipio (marco geoestadistico IIEG, SRID 6368)';
COMMENT ON COLUMN poblacion.geom_inegi IS 'Geometria del municipio (marco geoestadistico INEGI, SRID 6368)';
COMMENT ON COLUMN poblacion.nombre IS 'Nombre del municipio';
COMMENT ON COLUMN poblacion.fecha IS 'Fecha del periodo anual (YYYY-01-01)';
COMMENT ON COLUMN poblacion.clave_entidad IS 'Clave de la entidad federativa (14 = Jalisco)';
COMMENT ON COLUMN poblacion.clave_municipio IS 'Clave del municipio (EEMMM, 5 digitos)';
COMMENT ON COLUMN poblacion.poblacion_total IS 'Poblacion total a mitad de ano del municipio';
COMMENT ON COLUMN poblacion.poblacion_hombres IS 'Poblacion masculina a mitad de ano del municipio';
COMMENT ON COLUMN poblacion.poblacion_mujeres IS 'Poblacion femenina a mitad de ano del municipio';
COMMENT ON COLUMN poblacion.poblacion_respecto_jalisco IS 'Porcentaje de la poblacion municipal respecto al total de Jalisco';

-- poblacion_hombres
COMMENT ON MATERIALIZED VIEW poblacion_hombres IS
    'Proyeccion anual de poblacion masculina por municipio con geometrias (fuente: CONAPO).';

COMMENT ON COLUMN poblacion_hombres.fid IS 'Identificador unico de la fila';
COMMENT ON COLUMN poblacion_hombres.geom_iieg IS 'Geometria del municipio (marco geoestadistico IIEG, SRID 6368)';
COMMENT ON COLUMN poblacion_hombres.geom_inegi IS 'Geometria del municipio (marco geoestadistico INEGI, SRID 6368)';
COMMENT ON COLUMN poblacion_hombres.nombre IS 'Nombre del municipio';
COMMENT ON COLUMN poblacion_hombres.fecha IS 'Fecha del periodo anual (YYYY-01-01)';
COMMENT ON COLUMN poblacion_hombres.clave_entidad IS 'Clave de la entidad federativa (14 = Jalisco)';
COMMENT ON COLUMN poblacion_hombres.clave_municipio IS 'Clave del municipio (EEMMM, 5 digitos)';
COMMENT ON COLUMN poblacion_hombres.poblacion_hombres IS 'Poblacion masculina a mitad de ano del municipio';

-- poblacion_mujeres
COMMENT ON MATERIALIZED VIEW poblacion_mujeres IS
    'Proyeccion anual de poblacion femenina por municipio con geometrias (fuente: CONAPO).';

COMMENT ON COLUMN poblacion_mujeres.fid IS 'Identificador unico de la fila';
COMMENT ON COLUMN poblacion_mujeres.geom_iieg IS 'Geometria del municipio (marco geoestadistico IIEG, SRID 6368)';
COMMENT ON COLUMN poblacion_mujeres.geom_inegi IS 'Geometria del municipio (marco geoestadistico INEGI, SRID 6368)';
COMMENT ON COLUMN poblacion_mujeres.nombre IS 'Nombre del municipio';
COMMENT ON COLUMN poblacion_mujeres.fecha IS 'Fecha del periodo anual (YYYY-01-01)';
COMMENT ON COLUMN poblacion_mujeres.clave_entidad IS 'Clave de la entidad federativa (14 = Jalisco)';
COMMENT ON COLUMN poblacion_mujeres.clave_municipio IS 'Clave del municipio (EEMMM, 5 digitos)';
COMMENT ON COLUMN poblacion_mujeres.poblacion_mujeres IS 'Poblacion femenina a mitad de ano del municipio';

-- edad_mediana
COMMENT ON MATERIALIZED VIEW edad_mediana IS
    'Edad mediana proyectada por municipio y ano con geometrias (fuente: CONAPO).';

COMMENT ON COLUMN edad_mediana.fid IS 'Identificador unico de la fila';
COMMENT ON COLUMN edad_mediana.geom_iieg IS 'Geometria del municipio (marco geoestadistico IIEG, SRID 6368)';
COMMENT ON COLUMN edad_mediana.geom_inegi IS 'Geometria del municipio (marco geoestadistico INEGI, SRID 6368)';
COMMENT ON COLUMN edad_mediana.nombre IS 'Nombre del municipio';
COMMENT ON COLUMN edad_mediana.fecha IS 'Fecha del periodo anual (YYYY-01-01)';
COMMENT ON COLUMN edad_mediana.clave_entidad IS 'Clave de la entidad federativa (14 = Jalisco)';
COMMENT ON COLUMN edad_mediana.clave_municipio IS 'Clave del municipio (EEMMM, 5 digitos)';
COMMENT ON COLUMN edad_mediana.edad_mediana IS 'Edad mediana de la poblacion del municipio';

-- porcentaje_poblacional_municipal_en_entidad
COMMENT ON MATERIALIZED VIEW porcentaje_poblacional_municipal_en_entidad IS
    'Peso demografico del municipio respecto al total de Jalisco con geometrias (fuente: CONAPO).';

COMMENT ON COLUMN porcentaje_poblacional_municipal_en_entidad.fid IS 'Identificador unico de la fila';
COMMENT ON COLUMN porcentaje_poblacional_municipal_en_entidad.geom_iieg IS 'Geometria del municipio (marco geoestadistico IIEG, SRID 6368)';
COMMENT ON COLUMN porcentaje_poblacional_municipal_en_entidad.geom_inegi IS 'Geometria del municipio (marco geoestadistico INEGI, SRID 6368)';
COMMENT ON COLUMN porcentaje_poblacional_municipal_en_entidad.nombre IS 'Nombre del municipio';
COMMENT ON COLUMN porcentaje_poblacional_municipal_en_entidad.fecha IS 'Fecha del periodo anual (YYYY-01-01)';
COMMENT ON COLUMN porcentaje_poblacional_municipal_en_entidad.clave_entidad IS 'Clave de la entidad federativa (14 = Jalisco)';
COMMENT ON COLUMN porcentaje_poblacional_municipal_en_entidad.clave_municipio IS 'Clave del municipio (EEMMM, 5 digitos)';
COMMENT ON COLUMN porcentaje_poblacional_municipal_en_entidad.porcentaje IS 'Porcentaje de la poblacion del municipio respecto al total de la entidad';

-- razon_dependencia
COMMENT ON MATERIALIZED VIEW razon_dependencia IS
    'Razon de dependencia total por municipio y ano con geometrias (fuente: CONAPO).';

COMMENT ON COLUMN razon_dependencia.fid IS 'Identificador unico de la fila';
COMMENT ON COLUMN razon_dependencia.geom_iieg IS 'Geometria del municipio (marco geoestadistico IIEG, SRID 6368)';
COMMENT ON COLUMN razon_dependencia.geom_inegi IS 'Geometria del municipio (marco geoestadistico INEGI, SRID 6368)';
COMMENT ON COLUMN razon_dependencia.nombre IS 'Nombre del municipio';
COMMENT ON COLUMN razon_dependencia.fecha IS 'Fecha del periodo anual (YYYY-01-01)';
COMMENT ON COLUMN razon_dependencia.clave_entidad IS 'Clave de la entidad federativa (14 = Jalisco)';
COMMENT ON COLUMN razon_dependencia.clave_municipio IS 'Clave del municipio (EEMMM, 5 digitos)';
COMMENT ON COLUMN razon_dependencia.razon_dependencia IS 'Razon de dependencia total (dependientes / PEA * 100)';

-- razon_dependencia_adulta
COMMENT ON MATERIALIZED VIEW razon_dependencia_adulta IS
    'Razon de dependencia adulta (65+ / PEA) por municipio y ano con geometrias (fuente: CONAPO).';

COMMENT ON COLUMN razon_dependencia_adulta.fid IS 'Identificador unico de la fila';
COMMENT ON COLUMN razon_dependencia_adulta.geom_iieg IS 'Geometria del municipio (marco geoestadistico IIEG, SRID 6368)';
COMMENT ON COLUMN razon_dependencia_adulta.geom_inegi IS 'Geometria del municipio (marco geoestadistico INEGI, SRID 6368)';
COMMENT ON COLUMN razon_dependencia_adulta.nombre IS 'Nombre del municipio';
COMMENT ON COLUMN razon_dependencia_adulta.fecha IS 'Fecha del periodo anual (YYYY-01-01)';
COMMENT ON COLUMN razon_dependencia_adulta.clave_entidad IS 'Clave de la entidad federativa (14 = Jalisco)';
COMMENT ON COLUMN razon_dependencia_adulta.clave_municipio IS 'Clave del municipio (EEMMM, 5 digitos)';
COMMENT ON COLUMN razon_dependencia_adulta.razon_dependencia_adulta IS 'Razon de dependencia adulta (poblacion 60+ / poblacion 15-59 * 100)';

-- razon_dependencia_infantil
COMMENT ON MATERIALIZED VIEW razon_dependencia_infantil IS
    'Razon de dependencia infantil (0-14 / PEA) por municipio y ano con geometrias (fuente: CONAPO).';

COMMENT ON COLUMN razon_dependencia_infantil.fid IS 'Identificador unico de la fila';
COMMENT ON COLUMN razon_dependencia_infantil.geom_iieg IS 'Geometria del municipio (marco geoestadistico IIEG, SRID 6368)';
COMMENT ON COLUMN razon_dependencia_infantil.geom_inegi IS 'Geometria del municipio (marco geoestadistico INEGI, SRID 6368)';
COMMENT ON COLUMN razon_dependencia_infantil.nombre IS 'Nombre del municipio';
COMMENT ON COLUMN razon_dependencia_infantil.fecha IS 'Fecha del periodo anual (YYYY-01-01)';
COMMENT ON COLUMN razon_dependencia_infantil.clave_entidad IS 'Clave de la entidad federativa (14 = Jalisco)';
COMMENT ON COLUMN razon_dependencia_infantil.clave_municipio IS 'Clave del municipio (EEMMM, 5 digitos)';
COMMENT ON COLUMN razon_dependencia_infantil.razon_dependencia_infantil IS 'Razon de dependencia infantil (poblacion 0-14 / poblacion 15-64 * 100)';
