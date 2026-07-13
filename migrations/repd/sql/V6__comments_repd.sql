-- =======================================================================
-- V5: Comentarios en vistas materializadas REPD
-- =======================================================================

-- personas_desaparecidas
COMMENT ON MATERIALIZED VIEW personas_desaparecidas IS
    'Vista materializada de personas desaparecidas por municipio y mes con geometrias y tasas CONAPO.';

COMMENT ON COLUMN personas_desaparecidas.fid IS 'Identificador unico de la fila';
COMMENT ON COLUMN personas_desaparecidas.geom_iieg IS 'Geometria del municipio (marco geoestadistico IIEG, SRID 6368)';
COMMENT ON COLUMN personas_desaparecidas.geom_inegi IS 'Geometria del municipio (marco geoestadistico INEGI, SRID 6368)';
COMMENT ON COLUMN personas_desaparecidas.nombre IS 'Nombre del municipio';
COMMENT ON COLUMN personas_desaparecidas.fecha IS 'Fecha del periodo mensual (YYYY-MM-01)';
COMMENT ON COLUMN personas_desaparecidas.clave_entidad IS 'Clave de la entidad federativa (14 = Jalisco)';
COMMENT ON COLUMN personas_desaparecidas.clave_municipio IS 'Clave del municipio (EEMMM, 5 digitos)';
COMMENT ON COLUMN personas_desaparecidas.total IS 'Total de personas desaparecidas en el periodo';
COMMENT ON COLUMN personas_desaparecidas.total_hombres IS 'Total de hombres desaparecidos en el periodo';
COMMENT ON COLUMN personas_desaparecidas.total_mujeres IS 'Total de mujeres desaparecidas en el periodo';
COMMENT ON COLUMN personas_desaparecidas.tasa_total IS 'Tasa de desaparicion por 100,000 habitantes (pob. total CONAPO)';
COMMENT ON COLUMN personas_desaparecidas.tasa_hombres IS 'Tasa de desaparicion por 100,000 hombres (pob. hombres CONAPO)';
COMMENT ON COLUMN personas_desaparecidas.tasa_mujeres IS 'Tasa de desaparicion por 100,000 mujeres (pob. mujeres CONAPO)';

-- personas_desaparecidas_hombres
COMMENT ON MATERIALIZED VIEW personas_desaparecidas_hombres IS
    'Vista materializada de hombres desaparecidos por municipio y mes con geometrias y tasa CONAPO.';

COMMENT ON COLUMN personas_desaparecidas_hombres.fid IS 'Identificador unico de la fila';
COMMENT ON COLUMN personas_desaparecidas_hombres.geom_iieg IS 'Geometria del municipio (marco geoestadistico IIEG, SRID 6368)';
COMMENT ON COLUMN personas_desaparecidas_hombres.geom_inegi IS 'Geometria del municipio (marco geoestadistico INEGI, SRID 6368)';
COMMENT ON COLUMN personas_desaparecidas_hombres.nombre IS 'Nombre del municipio';
COMMENT ON COLUMN personas_desaparecidas_hombres.fecha IS 'Fecha del periodo mensual (YYYY-MM-01)';
COMMENT ON COLUMN personas_desaparecidas_hombres.clave_entidad IS 'Clave de la entidad federativa (14 = Jalisco)';
COMMENT ON COLUMN personas_desaparecidas_hombres.clave_municipio IS 'Clave del municipio (EEMMM, 5 digitos)';
COMMENT ON COLUMN personas_desaparecidas_hombres.total_hombres IS 'Total de hombres desaparecidos en el periodo';
COMMENT ON COLUMN personas_desaparecidas_hombres.tasa_hombres IS 'Tasa de desaparicion por 100,000 hombres (pob. hombres CONAPO)';

-- personas_desaparecidas_mujeres
COMMENT ON MATERIALIZED VIEW personas_desaparecidas_mujeres IS
    'Vista materializada de mujeres desaparecidas por municipio y mes con geometrias y tasa CONAPO.';

COMMENT ON COLUMN personas_desaparecidas_mujeres.fid IS 'Identificador unico de la fila';
COMMENT ON COLUMN personas_desaparecidas_mujeres.geom_iieg IS 'Geometria del municipio (marco geoestadistico IIEG, SRID 6368)';
COMMENT ON COLUMN personas_desaparecidas_mujeres.geom_inegi IS 'Geometria del municipio (marco geoestadistico INEGI, SRID 6368)';
COMMENT ON COLUMN personas_desaparecidas_mujeres.nombre IS 'Nombre del municipio';
COMMENT ON COLUMN personas_desaparecidas_mujeres.fecha IS 'Fecha del periodo mensual (YYYY-MM-01)';
COMMENT ON COLUMN personas_desaparecidas_mujeres.clave_entidad IS 'Clave de la entidad federativa (14 = Jalisco)';
COMMENT ON COLUMN personas_desaparecidas_mujeres.clave_municipio IS 'Clave del municipio (EEMMM, 5 digitos)';
COMMENT ON COLUMN personas_desaparecidas_mujeres.total_mujeres IS 'Total de mujeres desaparecidas en el periodo';
COMMENT ON COLUMN personas_desaparecidas_mujeres.tasa_mujeres IS 'Tasa de desaparicion por 100,000 mujeres (pob. mujeres CONAPO)';

-- personas_localizadas
COMMENT ON MATERIALIZED VIEW personas_localizadas IS
    'Vista materializada de personas localizadas por municipio y mes con geometrias y tasas CONAPO.';

COMMENT ON COLUMN personas_localizadas.fid IS 'Identificador unico de la fila';
COMMENT ON COLUMN personas_localizadas.geom_iieg IS 'Geometria del municipio (marco geoestadistico IIEG, SRID 6368)';
COMMENT ON COLUMN personas_localizadas.geom_inegi IS 'Geometria del municipio (marco geoestadistico INEGI, SRID 6368)';
COMMENT ON COLUMN personas_localizadas.nombre IS 'Nombre del municipio';
COMMENT ON COLUMN personas_localizadas.fecha IS 'Fecha del periodo mensual (YYYY-MM-01)';
COMMENT ON COLUMN personas_localizadas.clave_entidad IS 'Clave de la entidad federativa (14 = Jalisco)';
COMMENT ON COLUMN personas_localizadas.clave_municipio IS 'Clave del municipio (EEMMM, 5 digitos)';
COMMENT ON COLUMN personas_localizadas.total IS 'Total de personas localizadas en el periodo';
COMMENT ON COLUMN personas_localizadas.total_hombres IS 'Total de hombres localizados en el periodo';
COMMENT ON COLUMN personas_localizadas.total_mujeres IS 'Total de mujeres localizadas en el periodo';
COMMENT ON COLUMN personas_localizadas.tasa_total IS 'Tasa de localizacion por 100,000 habitantes (pob. total CONAPO)';
COMMENT ON COLUMN personas_localizadas.tasa_hombres IS 'Tasa de localizacion por 100,000 hombres (pob. hombres CONAPO)';
COMMENT ON COLUMN personas_localizadas.tasa_mujeres IS 'Tasa de localizacion por 100,000 mujeres (pob. mujeres CONAPO)';

-- personas_localizadas_hombres
COMMENT ON MATERIALIZED VIEW personas_localizadas_hombres IS
    'Vista materializada de hombres localizados por municipio y mes con geometrias y tasa CONAPO.';

COMMENT ON COLUMN personas_localizadas_hombres.fid IS 'Identificador unico de la fila';
COMMENT ON COLUMN personas_localizadas_hombres.geom_iieg IS 'Geometria del municipio (marco geoestadistico IIEG, SRID 6368)';
COMMENT ON COLUMN personas_localizadas_hombres.geom_inegi IS 'Geometria del municipio (marco geoestadistico INEGI, SRID 6368)';
COMMENT ON COLUMN personas_localizadas_hombres.nombre IS 'Nombre del municipio';
COMMENT ON COLUMN personas_localizadas_hombres.fecha IS 'Fecha del periodo mensual (YYYY-MM-01)';
COMMENT ON COLUMN personas_localizadas_hombres.clave_entidad IS 'Clave de la entidad federativa (14 = Jalisco)';
COMMENT ON COLUMN personas_localizadas_hombres.clave_municipio IS 'Clave del municipio (EEMMM, 5 digitos)';
COMMENT ON COLUMN personas_localizadas_hombres.total_hombres IS 'Total de hombres localizados en el periodo';
COMMENT ON COLUMN personas_localizadas_hombres.tasa_hombres IS 'Tasa de localizacion por 100,000 hombres (pob. hombres CONAPO)';

-- personas_localizadas_mujeres
COMMENT ON MATERIALIZED VIEW personas_localizadas_mujeres IS
    'Vista materializada de mujeres localizadas por municipio y mes con geometrias y tasa CONAPO.';

COMMENT ON COLUMN personas_localizadas_mujeres.fid IS 'Identificador unico de la fila';
COMMENT ON COLUMN personas_localizadas_mujeres.geom_iieg IS 'Geometria del municipio (marco geoestadistico IIEG, SRID 6368)';
COMMENT ON COLUMN personas_localizadas_mujeres.geom_inegi IS 'Geometria del municipio (marco geoestadistico INEGI, SRID 6368)';
COMMENT ON COLUMN personas_localizadas_mujeres.nombre IS 'Nombre del municipio';
COMMENT ON COLUMN personas_localizadas_mujeres.fecha IS 'Fecha del periodo mensual (YYYY-MM-01)';
COMMENT ON COLUMN personas_localizadas_mujeres.clave_entidad IS 'Clave de la entidad federativa (14 = Jalisco)';
COMMENT ON COLUMN personas_localizadas_mujeres.clave_municipio IS 'Clave del municipio (EEMMM, 5 digitos)';
COMMENT ON COLUMN personas_localizadas_mujeres.total_mujeres IS 'Total de mujeres localizadas en el periodo';
COMMENT ON COLUMN personas_localizadas_mujeres.tasa_mujeres IS 'Tasa de localizacion por 100,000 mujeres (pob. mujeres CONAPO)';
