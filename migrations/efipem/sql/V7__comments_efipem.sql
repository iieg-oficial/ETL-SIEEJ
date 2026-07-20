-- =======================================================================
-- V7: Comentarios en vistas materializadas EFIPEM
-- =======================================================================

COMMENT ON MATERIALIZED VIEW ingresos_totales IS
    'Ingresos municipales totales en pesos corrientes (fuente: EFIPEM INEGI).';
COMMENT ON COLUMN ingresos_totales.fid IS 'Identificador unico de la fila';
COMMENT ON COLUMN ingresos_totales.geom_iieg IS 'Geometria del municipio (marco geoestadistico IIEG, SRID 6368)';
COMMENT ON COLUMN ingresos_totales.geom_inegi IS 'Geometria del municipio (marco geoestadistico INEGI, SRID 6368)';
COMMENT ON COLUMN ingresos_totales.nombre IS 'Nombre del municipio';
COMMENT ON COLUMN ingresos_totales.fecha IS 'Fecha del periodo anual (YYYY-01-01)';
COMMENT ON COLUMN ingresos_totales.clave_entidad IS 'Clave de la entidad federativa (14 = Jalisco)';
COMMENT ON COLUMN ingresos_totales.clave_municipio IS 'Clave del municipio (EEMMM, 5 digitos)';
COMMENT ON COLUMN ingresos_totales.valor IS 'Ingresos totales en pesos corrientes';

COMMENT ON MATERIALIZED VIEW ingresos_totales_reales_precios_2023 IS
    'Ingresos municipales totales deflactados a precios constantes de 2023 (INPC base 2023=100).';
COMMENT ON COLUMN ingresos_totales_reales_precios_2023.fid IS 'Identificador unico de la fila';
COMMENT ON COLUMN ingresos_totales_reales_precios_2023.geom_iieg IS 'Geometria del municipio (marco geoestadistico IIEG, SRID 6368)';
COMMENT ON COLUMN ingresos_totales_reales_precios_2023.geom_inegi IS 'Geometria del municipio (marco geoestadistico INEGI, SRID 6368)';
COMMENT ON COLUMN ingresos_totales_reales_precios_2023.nombre IS 'Nombre del municipio';
COMMENT ON COLUMN ingresos_totales_reales_precios_2023.fecha IS 'Fecha del periodo anual (YYYY-01-01)';
COMMENT ON COLUMN ingresos_totales_reales_precios_2023.clave_entidad IS 'Clave de la entidad federativa (14 = Jalisco)';
COMMENT ON COLUMN ingresos_totales_reales_precios_2023.clave_municipio IS 'Clave del municipio (EEMMM, 5 digitos)';
COMMENT ON COLUMN ingresos_totales_reales_precios_2023.valor IS 'Ingresos totales en pesos reales de 2023 (deflactado por INPC)';

COMMENT ON MATERIALIZED VIEW ingresos_totales_reales_per_capita_precios_2023 IS
    'Ingresos reales per capita deflactados a precios de 2023 (valor real / poblacion CONAPO).';
COMMENT ON COLUMN ingresos_totales_reales_per_capita_precios_2023.fid IS 'Identificador unico de la fila';
COMMENT ON COLUMN ingresos_totales_reales_per_capita_precios_2023.geom_iieg IS 'Geometria del municipio (marco geoestadistico IIEG, SRID 6368)';
COMMENT ON COLUMN ingresos_totales_reales_per_capita_precios_2023.geom_inegi IS 'Geometria del municipio (marco geoestadistico INEGI, SRID 6368)';
COMMENT ON COLUMN ingresos_totales_reales_per_capita_precios_2023.nombre IS 'Nombre del municipio';
COMMENT ON COLUMN ingresos_totales_reales_per_capita_precios_2023.fecha IS 'Fecha del periodo anual (YYYY-01-01)';
COMMENT ON COLUMN ingresos_totales_reales_per_capita_precios_2023.clave_entidad IS 'Clave de la entidad federativa (14 = Jalisco)';
COMMENT ON COLUMN ingresos_totales_reales_per_capita_precios_2023.clave_municipio IS 'Clave del municipio (EEMMM, 5 digitos)';
COMMENT ON COLUMN ingresos_totales_reales_per_capita_precios_2023.valor IS 'Ingresos reales per capita en pesos de 2023';

COMMENT ON MATERIALIZED VIEW ingresos_participaciones IS
    'Monto de participaciones federales recibidas por municipio (pesos corrientes).';
COMMENT ON COLUMN ingresos_participaciones.fid IS 'Identificador unico de la fila';
COMMENT ON COLUMN ingresos_participaciones.geom_iieg IS 'Geometria del municipio (marco geoestadistico IIEG, SRID 6368)';
COMMENT ON COLUMN ingresos_participaciones.geom_inegi IS 'Geometria del municipio (marco geoestadistico INEGI, SRID 6368)';
COMMENT ON COLUMN ingresos_participaciones.nombre IS 'Nombre del municipio';
COMMENT ON COLUMN ingresos_participaciones.fecha IS 'Fecha del periodo anual (YYYY-01-01)';
COMMENT ON COLUMN ingresos_participaciones.clave_entidad IS 'Clave de la entidad federativa (14 = Jalisco)';
COMMENT ON COLUMN ingresos_participaciones.clave_municipio IS 'Clave del municipio (EEMMM, 5 digitos)';
COMMENT ON COLUMN ingresos_participaciones.valor IS 'Participaciones federales en pesos corrientes';

COMMENT ON MATERIALIZED VIEW ingresos_financiamiento IS
    'Ingresos por financiamiento / deuda publica (pesos corrientes).';
COMMENT ON COLUMN ingresos_financiamiento.fid IS 'Identificador unico de la fila';
COMMENT ON COLUMN ingresos_financiamiento.geom_iieg IS 'Geometria del municipio (marco geoestadistico IIEG, SRID 6368)';
COMMENT ON COLUMN ingresos_financiamiento.geom_inegi IS 'Geometria del municipio (marco geoestadistico INEGI, SRID 6368)';
COMMENT ON COLUMN ingresos_financiamiento.nombre IS 'Nombre del municipio';
COMMENT ON COLUMN ingresos_financiamiento.fecha IS 'Fecha del periodo anual (YYYY-01-01)';
COMMENT ON COLUMN ingresos_financiamiento.clave_entidad IS 'Clave de la entidad federativa (14 = Jalisco)';
COMMENT ON COLUMN ingresos_financiamiento.clave_municipio IS 'Clave del municipio (EEMMM, 5 digitos)';
COMMENT ON COLUMN ingresos_financiamiento.valor IS 'Financiamiento / deuda publica en pesos corrientes';

COMMENT ON MATERIALIZED VIEW porcentaje_ingresos_participaciones IS
    'Porcentaje de participaciones federales sobre ingresos totales.';
COMMENT ON COLUMN porcentaje_ingresos_participaciones.fid IS 'Identificador unico de la fila';
COMMENT ON COLUMN porcentaje_ingresos_participaciones.geom_iieg IS 'Geometria del municipio (marco geoestadistico IIEG, SRID 6368)';
COMMENT ON COLUMN porcentaje_ingresos_participaciones.geom_inegi IS 'Geometria del municipio (marco geoestadistico INEGI, SRID 6368)';
COMMENT ON COLUMN porcentaje_ingresos_participaciones.nombre IS 'Nombre del municipio';
COMMENT ON COLUMN porcentaje_ingresos_participaciones.fecha IS 'Fecha del periodo anual (YYYY-01-01)';
COMMENT ON COLUMN porcentaje_ingresos_participaciones.clave_entidad IS 'Clave de la entidad federativa (14 = Jalisco)';
COMMENT ON COLUMN porcentaje_ingresos_participaciones.clave_municipio IS 'Clave del municipio (EEMMM, 5 digitos)';
COMMENT ON COLUMN porcentaje_ingresos_participaciones.valor IS 'Porcentaje de participaciones sobre ingresos totales (0-100)';

COMMENT ON MATERIALIZED VIEW porcentaje_ingresos_financiamiento IS
    'Porcentaje de financiamiento sobre ingresos totales.';
COMMENT ON COLUMN porcentaje_ingresos_financiamiento.fid IS 'Identificador unico de la fila';
COMMENT ON COLUMN porcentaje_ingresos_financiamiento.geom_iieg IS 'Geometria del municipio (marco geoestadistico IIEG, SRID 6368)';
COMMENT ON COLUMN porcentaje_ingresos_financiamiento.geom_inegi IS 'Geometria del municipio (marco geoestadistico INEGI, SRID 6368)';
COMMENT ON COLUMN porcentaje_ingresos_financiamiento.nombre IS 'Nombre del municipio';
COMMENT ON COLUMN porcentaje_ingresos_financiamiento.fecha IS 'Fecha del periodo anual (YYYY-01-01)';
COMMENT ON COLUMN porcentaje_ingresos_financiamiento.clave_entidad IS 'Clave de la entidad federativa (14 = Jalisco)';
COMMENT ON COLUMN porcentaje_ingresos_financiamiento.clave_municipio IS 'Clave del municipio (EEMMM, 5 digitos)';
COMMENT ON COLUMN porcentaje_ingresos_financiamiento.valor IS 'Porcentaje de financiamiento sobre ingresos totales (0-100)';

COMMENT ON MATERIALIZED VIEW porcentaje_ingresos_propios IS
    'Porcentaje de ingresos propios (Impuestos + Productos + Aprovechamientos) sobre ingresos totales.';
COMMENT ON COLUMN porcentaje_ingresos_propios.fid IS 'Identificador unico de la fila';
COMMENT ON COLUMN porcentaje_ingresos_propios.geom_iieg IS 'Geometria del municipio (marco geoestadistico IIEG, SRID 6368)';
COMMENT ON COLUMN porcentaje_ingresos_propios.geom_inegi IS 'Geometria del municipio (marco geoestadistico INEGI, SRID 6368)';
COMMENT ON COLUMN porcentaje_ingresos_propios.nombre IS 'Nombre del municipio';
COMMENT ON COLUMN porcentaje_ingresos_propios.fecha IS 'Fecha del periodo anual (YYYY-01-01)';
COMMENT ON COLUMN porcentaje_ingresos_propios.clave_entidad IS 'Clave de la entidad federativa (14 = Jalisco)';
COMMENT ON COLUMN porcentaje_ingresos_propios.clave_municipio IS 'Clave del municipio (EEMMM, 5 digitos)';
COMMENT ON COLUMN porcentaje_ingresos_propios.valor IS 'Porcentaje de ingresos propios sobre total (0-100)';

COMMENT ON MATERIALIZED VIEW egresos_totales IS
    'Egresos municipales totales en pesos corrientes (fuente: EFIPEM INEGI).';
COMMENT ON COLUMN egresos_totales.fid IS 'Identificador unico de la fila';
COMMENT ON COLUMN egresos_totales.geom_iieg IS 'Geometria del municipio (marco geoestadistico IIEG, SRID 6368)';
COMMENT ON COLUMN egresos_totales.geom_inegi IS 'Geometria del municipio (marco geoestadistico INEGI, SRID 6368)';
COMMENT ON COLUMN egresos_totales.nombre IS 'Nombre del municipio';
COMMENT ON COLUMN egresos_totales.fecha IS 'Fecha del periodo anual (YYYY-01-01)';
COMMENT ON COLUMN egresos_totales.clave_entidad IS 'Clave de la entidad federativa (14 = Jalisco)';
COMMENT ON COLUMN egresos_totales.clave_municipio IS 'Clave del municipio (EEMMM, 5 digitos)';
COMMENT ON COLUMN egresos_totales.valor IS 'Egresos totales en pesos corrientes';

COMMENT ON MATERIALIZED VIEW egresos_deuda_publica IS
    'Pago de deuda publica (capital + intereses) en pesos corrientes.';
COMMENT ON COLUMN egresos_deuda_publica.fid IS 'Identificador unico de la fila';
COMMENT ON COLUMN egresos_deuda_publica.geom_iieg IS 'Geometria del municipio (marco geoestadistico IIEG, SRID 6368)';
COMMENT ON COLUMN egresos_deuda_publica.geom_inegi IS 'Geometria del municipio (marco geoestadistico INEGI, SRID 6368)';
COMMENT ON COLUMN egresos_deuda_publica.nombre IS 'Nombre del municipio';
COMMENT ON COLUMN egresos_deuda_publica.fecha IS 'Fecha del periodo anual (YYYY-01-01)';
COMMENT ON COLUMN egresos_deuda_publica.clave_entidad IS 'Clave de la entidad federativa (14 = Jalisco)';
COMMENT ON COLUMN egresos_deuda_publica.clave_municipio IS 'Clave del municipio (EEMMM, 5 digitos)';
COMMENT ON COLUMN egresos_deuda_publica.valor IS 'Deuda publica en pesos corrientes';

COMMENT ON MATERIALIZED VIEW porcentaje_egresos_deuda_publica IS
    'Porcentaje de pago de deuda publica sobre egresos totales.';
COMMENT ON COLUMN porcentaje_egresos_deuda_publica.fid IS 'Identificador unico de la fila';
COMMENT ON COLUMN porcentaje_egresos_deuda_publica.geom_iieg IS 'Geometria del municipio (marco geoestadistico IIEG, SRID 6368)';
COMMENT ON COLUMN porcentaje_egresos_deuda_publica.geom_inegi IS 'Geometria del municipio (marco geoestadistico INEGI, SRID 6368)';
COMMENT ON COLUMN porcentaje_egresos_deuda_publica.nombre IS 'Nombre del municipio';
COMMENT ON COLUMN porcentaje_egresos_deuda_publica.fecha IS 'Fecha del periodo anual (YYYY-01-01)';
COMMENT ON COLUMN porcentaje_egresos_deuda_publica.clave_entidad IS 'Clave de la entidad federativa (14 = Jalisco)';
COMMENT ON COLUMN porcentaje_egresos_deuda_publica.clave_municipio IS 'Clave del municipio (EEMMM, 5 digitos)';
COMMENT ON COLUMN porcentaje_egresos_deuda_publica.valor IS 'Porcentaje de deuda publica sobre egresos totales (0-100)';
