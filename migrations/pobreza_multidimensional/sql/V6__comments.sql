-- =======================================================================
-- V6__comments.sql  |  Pipeline: pobreza_multidimensional
-- Comentarios en tablas base, columnas y vistas materializadas.
-- =======================================================================

-- =============================================================================
-- stg_pobreza_multidimensional_cat_entidad
-- =============================================================================
COMMENT ON TABLE public.stg_pobreza_multidimensional_cat_entidad IS
    'Catálogo de entidades federativas CONEVAL para el pipeline de pobreza multidimensional.';

COMMENT ON COLUMN public.stg_pobreza_multidimensional_cat_entidad.id IS 'Identificador interno autoincremental.';
COMMENT ON COLUMN public.stg_pobreza_multidimensional_cat_entidad.cve_ent IS 'Clave de la entidad federativa (2 dígitos, INEGI).';
COMMENT ON COLUMN public.stg_pobreza_multidimensional_cat_entidad.nombre_entidad IS 'Nombre oficial de la entidad federativa.';

-- =============================================================================
-- stg_pobreza_multidimensional_datos
-- =============================================================================
COMMENT ON TABLE public.stg_pobreza_multidimensional_datos IS
    'Indicadores de pobreza municipal CONEVAL en formato tidy (municipio × año). Años disponibles: 2010, 2015, 2020.';

COMMENT ON COLUMN public.stg_pobreza_multidimensional_datos.id IS 'Identificador interno autoincremental.';
COMMENT ON COLUMN public.stg_pobreza_multidimensional_datos.cve_mun IS 'Clave municipal INEGI de 5 dígitos (EEMMM).';
COMMENT ON COLUMN public.stg_pobreza_multidimensional_datos.nombre_municipio IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN public.stg_pobreza_multidimensional_datos.cat_entidad_id IS 'FK al catálogo de entidades federativas.';
COMMENT ON COLUMN public.stg_pobreza_multidimensional_datos.anio IS 'Año de medición (2010, 2015 ó 2020).';
COMMENT ON COLUMN public.stg_pobreza_multidimensional_datos.poblacion IS 'Población total del municipio en el año de medición.';
COMMENT ON COLUMN public.stg_pobreza_multidimensional_datos.pobreza_porcentaje IS 'Porcentaje de personas en situación de pobreza.';
COMMENT ON COLUMN public.stg_pobreza_multidimensional_datos.pobreza_personas IS 'Número de personas en situación de pobreza.';
COMMENT ON COLUMN public.stg_pobreza_multidimensional_datos.pobreza_promedio IS 'Promedio de carencias de la población en pobreza.';
COMMENT ON COLUMN public.stg_pobreza_multidimensional_datos.pobreza_ext_porcentaje IS 'Porcentaje de personas en pobreza extrema.';
COMMENT ON COLUMN public.stg_pobreza_multidimensional_datos.pobreza_ext_personas IS 'Número de personas en pobreza extrema.';
COMMENT ON COLUMN public.stg_pobreza_multidimensional_datos.pobreza_ext_promedio IS 'Promedio de carencias de la población en pobreza extrema.';
COMMENT ON COLUMN public.stg_pobreza_multidimensional_datos.pobreza_mod_porcentaje IS 'Porcentaje de personas en pobreza moderada.';
COMMENT ON COLUMN public.stg_pobreza_multidimensional_datos.pobreza_mod_personas IS 'Número de personas en pobreza moderada.';
COMMENT ON COLUMN public.stg_pobreza_multidimensional_datos.pobreza_mod_promedio IS 'Promedio de carencias de la población en pobreza moderada.';
COMMENT ON COLUMN public.stg_pobreza_multidimensional_datos.vul_carencia_porcentaje IS 'Porcentaje de vulnerables por carencia social.';
COMMENT ON COLUMN public.stg_pobreza_multidimensional_datos.vul_carencia_personas IS 'Número de vulnerables por carencia social.';
COMMENT ON COLUMN public.stg_pobreza_multidimensional_datos.vul_carencia_promedio IS 'Promedio de carencias de los vulnerables por carencia social.';
COMMENT ON COLUMN public.stg_pobreza_multidimensional_datos.vul_ingreso_porcentaje IS 'Porcentaje de vulnerables por ingresos (sin carencias sociales).';
COMMENT ON COLUMN public.stg_pobreza_multidimensional_datos.vul_ingreso_personas IS 'Número de vulnerables por ingresos (sin carencias sociales).';
COMMENT ON COLUMN public.stg_pobreza_multidimensional_datos.no_pobre_porcentaje IS 'Porcentaje de personas no pobres y no vulnerables.';
COMMENT ON COLUMN public.stg_pobreza_multidimensional_datos.no_pobre_personas IS 'Número de personas no pobres y no vulnerables.';
COMMENT ON COLUMN public.stg_pobreza_multidimensional_datos.rez_edu_porcentaje IS 'Porcentaje con carencia por rezago educativo.';
COMMENT ON COLUMN public.stg_pobreza_multidimensional_datos.rez_edu_personas IS 'Número de personas con carencia por rezago educativo.';
COMMENT ON COLUMN public.stg_pobreza_multidimensional_datos.rez_edu_promedio IS 'Promedio de carencias en la población con rezago educativo.';
COMMENT ON COLUMN public.stg_pobreza_multidimensional_datos.car_salud_porcentaje IS 'Porcentaje con carencia por acceso a servicios de salud.';
COMMENT ON COLUMN public.stg_pobreza_multidimensional_datos.car_salud_personas IS 'Número de personas con carencia por acceso a servicios de salud.';
COMMENT ON COLUMN public.stg_pobreza_multidimensional_datos.car_salud_promedio IS 'Promedio de carencias en la población con carencia de salud.';
COMMENT ON COLUMN public.stg_pobreza_multidimensional_datos.car_seg_soc_porcentaje IS 'Porcentaje con carencia por acceso a seguridad social.';
COMMENT ON COLUMN public.stg_pobreza_multidimensional_datos.car_seg_soc_personas IS 'Número de personas con carencia por acceso a seguridad social.';
COMMENT ON COLUMN public.stg_pobreza_multidimensional_datos.car_seg_soc_promedio IS 'Promedio de carencias en la población con carencia de seguridad social.';
COMMENT ON COLUMN public.stg_pobreza_multidimensional_datos.car_viv_porcentaje IS 'Porcentaje con carencia por calidad y espacios de vivienda.';
COMMENT ON COLUMN public.stg_pobreza_multidimensional_datos.car_viv_personas IS 'Número de personas con carencia por calidad y espacios de vivienda.';
COMMENT ON COLUMN public.stg_pobreza_multidimensional_datos.car_viv_promedio IS 'Promedio de carencias en la población con carencia de vivienda.';
COMMENT ON COLUMN public.stg_pobreza_multidimensional_datos.car_sbv_porcentaje IS 'Porcentaje con carencia por servicios básicos en vivienda.';
COMMENT ON COLUMN public.stg_pobreza_multidimensional_datos.car_sbv_personas IS 'Número de personas con carencia por servicios básicos en vivienda.';
COMMENT ON COLUMN public.stg_pobreza_multidimensional_datos.car_sbv_promedio IS 'Promedio de carencias en la población con carencia de servicios básicos.';
COMMENT ON COLUMN public.stg_pobreza_multidimensional_datos.car_ali_porcentaje IS 'Porcentaje con carencia por acceso a alimentación nutritiva y de calidad.';
COMMENT ON COLUMN public.stg_pobreza_multidimensional_datos.car_ali_personas IS 'Número de personas con carencia por acceso a alimentación.';
COMMENT ON COLUMN public.stg_pobreza_multidimensional_datos.car_ali_promedio IS 'Promedio de carencias en la población con carencia de alimentación.';
COMMENT ON COLUMN public.stg_pobreza_multidimensional_datos.al_1_car_porcentaje IS 'Porcentaje de personas con al menos una carencia social.';
COMMENT ON COLUMN public.stg_pobreza_multidimensional_datos.al_1_car_personas IS 'Número de personas con al menos una carencia social.';
COMMENT ON COLUMN public.stg_pobreza_multidimensional_datos.al_1_car_promedio IS 'Promedio de carencias en la población con al menos una carencia social.';
COMMENT ON COLUMN public.stg_pobreza_multidimensional_datos.tres_mas_car_porcentaje IS 'Porcentaje de personas con tres o más carencias sociales.';
COMMENT ON COLUMN public.stg_pobreza_multidimensional_datos.tres_mas_car_personas IS 'Número de personas con tres o más carencias sociales.';
COMMENT ON COLUMN public.stg_pobreza_multidimensional_datos.tres_mas_car_promedio IS 'Promedio de carencias en la población con tres o más carencias sociales.';
COMMENT ON COLUMN public.stg_pobreza_multidimensional_datos.lpi_porcentaje IS 'Porcentaje con ingreso inferior a la línea de pobreza por ingresos.';
COMMENT ON COLUMN public.stg_pobreza_multidimensional_datos.lpi_personas IS 'Número de personas con ingreso inferior a la línea de pobreza por ingresos.';
COMMENT ON COLUMN public.stg_pobreza_multidimensional_datos.lpi_promedio IS 'Promedio de carencias en la población con ingreso inferior a la LPI.';
COMMENT ON COLUMN public.stg_pobreza_multidimensional_datos.lpei_porcentaje IS 'Porcentaje con ingreso inferior a la línea de pobreza extrema por ingresos.';
COMMENT ON COLUMN public.stg_pobreza_multidimensional_datos.lpei_personas IS 'Número de personas con ingreso inferior a la línea de pobreza extrema.';
COMMENT ON COLUMN public.stg_pobreza_multidimensional_datos.lpei_promedio IS 'Promedio de carencias en la población con ingreso inferior a la LPEI.';
COMMENT ON COLUMN public.stg_pobreza_multidimensional_datos.created_at IS 'Fecha y hora de inserción del registro.';
COMMENT ON COLUMN public.stg_pobreza_multidimensional_datos.updated_at IS 'Fecha y hora de la última actualización del registro.';

-- =============================================================================
-- Vista materializada: pobreza
-- =============================================================================
COMMENT ON MATERIALIZED VIEW pobreza IS
    'Personas en situación de pobreza (ingresos + al menos 1 carencia). Municipios de Jalisco. Años: 2010, 2015, 2020.';

COMMENT ON COLUMN pobreza.fid IS 'Identificador secuencial de la fila.';
COMMENT ON COLUMN pobreza.geom_inegi IS 'Geometría del municipio (marco geoestadístico INEGI, SRID 6368).';
COMMENT ON COLUMN pobreza.clave_municipio IS 'Clave municipal INEGI de 5 dígitos (EEMMM).';
COMMENT ON COLUMN pobreza.geom_iieg IS 'Geometría del municipio (marco geoestadístico IIEG, SRID 6368).';
COMMENT ON COLUMN pobreza.fecha IS 'Fecha del periodo de medición (1 de enero del año).';
COMMENT ON COLUMN pobreza.nombre IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN pobreza.clave_entidad IS 'FK al catálogo de entidades federativas.';
COMMENT ON COLUMN pobreza.porcentaje IS 'Porcentaje de personas en situación de pobreza.';
COMMENT ON COLUMN pobreza.personas IS 'Número de personas en situación de pobreza.';
COMMENT ON COLUMN pobreza.carencias_promedio IS 'Promedio de carencias de la población en pobreza.';

-- =============================================================================
-- Vista materializada: pobreza_extrema
-- =============================================================================
COMMENT ON MATERIALIZED VIEW pobreza_extrema IS
    'Personas en pobreza extrema (ingresos + 3 o más carencias). Municipios de Jalisco. Años: 2010, 2015, 2020.';

COMMENT ON COLUMN pobreza_extrema.fid IS 'Identificador secuencial de la fila.';
COMMENT ON COLUMN pobreza_extrema.geom_inegi IS 'Geometría del municipio (marco geoestadístico INEGI, SRID 6368).';
COMMENT ON COLUMN pobreza_extrema.clave_municipio IS 'Clave municipal INEGI de 5 dígitos (EEMMM).';
COMMENT ON COLUMN pobreza_extrema.geom_iieg IS 'Geometría del municipio (marco geoestadístico IIEG, SRID 6368).';
COMMENT ON COLUMN pobreza_extrema.fecha IS 'Fecha del periodo de medición (1 de enero del año).';
COMMENT ON COLUMN pobreza_extrema.nombre IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN pobreza_extrema.clave_entidad IS 'FK al catálogo de entidades federativas.';
COMMENT ON COLUMN pobreza_extrema.personas IS 'Número de personas en pobreza extrema.';
COMMENT ON COLUMN pobreza_extrema.porcentaje IS 'Porcentaje de personas en pobreza extrema.';
COMMENT ON COLUMN pobreza_extrema.carencias_promedio IS 'Promedio de carencias de la población en pobreza extrema.';

-- =============================================================================
-- Vista materializada: pobreza_moderada
-- =============================================================================
COMMENT ON MATERIALIZED VIEW pobreza_moderada IS
    'Personas en pobreza moderada (pobreza no extrema). Municipios de Jalisco. Años: 2010, 2015, 2020.';

COMMENT ON COLUMN pobreza_moderada.fid IS 'Identificador secuencial de la fila.';
COMMENT ON COLUMN pobreza_moderada.geom_inegi IS 'Geometría del municipio (marco geoestadístico INEGI, SRID 6368).';
COMMENT ON COLUMN pobreza_moderada.clave_municipio IS 'Clave municipal INEGI de 5 dígitos (EEMMM).';
COMMENT ON COLUMN pobreza_moderada.geom_iieg IS 'Geometría del municipio (marco geoestadístico IIEG, SRID 6368).';
COMMENT ON COLUMN pobreza_moderada.fecha IS 'Fecha del periodo de medición (1 de enero del año).';
COMMENT ON COLUMN pobreza_moderada.nombre IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN pobreza_moderada.clave_entidad IS 'FK al catálogo de entidades federativas.';
COMMENT ON COLUMN pobreza_moderada.personas IS 'Número de personas en pobreza moderada.';
COMMENT ON COLUMN pobreza_moderada.porcentaje IS 'Porcentaje de personas en pobreza moderada.';
COMMENT ON COLUMN pobreza_moderada.carencias_promedio IS 'Promedio de carencias de la población en pobreza moderada.';

-- =============================================================================
-- Vista materializada: poblacion_ingreso_inferior_linea_pobreza_ingresos
-- =============================================================================
COMMENT ON MATERIALIZED VIEW poblacion_ingreso_inferior_linea_pobreza_ingresos IS
    'Personas con ingreso menor a la línea de pobreza por ingresos. Municipios de Jalisco. Años: 2010, 2015, 2020.';

COMMENT ON COLUMN poblacion_ingreso_inferior_linea_pobreza_ingresos.fid IS 'Identificador secuencial de la fila.';
COMMENT ON COLUMN poblacion_ingreso_inferior_linea_pobreza_ingresos.geom_inegi IS 'Geometría del municipio (marco geoestadístico INEGI, SRID 6368).';
COMMENT ON COLUMN poblacion_ingreso_inferior_linea_pobreza_ingresos.nombre IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN poblacion_ingreso_inferior_linea_pobreza_ingresos.fecha IS 'Fecha del periodo de medición (1 de enero del año).';
COMMENT ON COLUMN poblacion_ingreso_inferior_linea_pobreza_ingresos.clave_entidad IS 'FK al catálogo de entidades federativas.';
COMMENT ON COLUMN poblacion_ingreso_inferior_linea_pobreza_ingresos.clave_municipio IS 'Clave municipal INEGI de 5 dígitos (EEMMM).';
COMMENT ON COLUMN poblacion_ingreso_inferior_linea_pobreza_ingresos.geom_iieg IS 'Geometría del municipio (marco geoestadístico IIEG, SRID 6368).';
COMMENT ON COLUMN poblacion_ingreso_inferior_linea_pobreza_ingresos.personas IS 'Número de personas con ingreso inferior a la línea de pobreza por ingresos.';
COMMENT ON COLUMN poblacion_ingreso_inferior_linea_pobreza_ingresos.porcentaje IS 'Porcentaje de personas con ingreso inferior a la línea de pobreza por ingresos.';
COMMENT ON COLUMN poblacion_ingreso_inferior_linea_pobreza_ingresos.carencias_promedio IS 'Promedio de carencias en la población con ingreso inferior a la LPI.';

-- =============================================================================
-- Vista materializada: poblacion_ingreso_inferior_linea_pobreza_extrema_ingresos
-- =============================================================================
COMMENT ON MATERIALIZED VIEW poblacion_ingreso_inferior_linea_pobreza_extrema_ingresos IS
    'Personas con ingreso menor a la línea de pobreza extrema por ingresos. Municipios de Jalisco. Años: 2010, 2015, 2020.';

COMMENT ON COLUMN poblacion_ingreso_inferior_linea_pobreza_extrema_ingresos.fid IS 'Identificador secuencial de la fila.';
COMMENT ON COLUMN poblacion_ingreso_inferior_linea_pobreza_extrema_ingresos.geom_iieg IS 'Geometría del municipio (marco geoestadístico IIEG, SRID 6368).';
COMMENT ON COLUMN poblacion_ingreso_inferior_linea_pobreza_extrema_ingresos.geom_inegi IS 'Geometría del municipio (marco geoestadístico INEGI, SRID 6368).';
COMMENT ON COLUMN poblacion_ingreso_inferior_linea_pobreza_extrema_ingresos.nombre IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN poblacion_ingreso_inferior_linea_pobreza_extrema_ingresos.fecha IS 'Fecha del periodo de medición (1 de enero del año).';
COMMENT ON COLUMN poblacion_ingreso_inferior_linea_pobreza_extrema_ingresos.clave_entidad IS 'FK al catálogo de entidades federativas.';
COMMENT ON COLUMN poblacion_ingreso_inferior_linea_pobreza_extrema_ingresos.clave_municipio IS 'Clave municipal INEGI de 5 dígitos (EEMMM).';
COMMENT ON COLUMN poblacion_ingreso_inferior_linea_pobreza_extrema_ingresos.personas IS 'Número de personas con ingreso inferior a la línea de pobreza extrema.';
COMMENT ON COLUMN poblacion_ingreso_inferior_linea_pobreza_extrema_ingresos.porcentaje IS 'Porcentaje de personas con ingreso inferior a la línea de pobreza extrema.';
COMMENT ON COLUMN poblacion_ingreso_inferior_linea_pobreza_extrema_ingresos.carencias_promedio IS 'Promedio de carencias en la población con ingreso inferior a la LPEI.';

-- =============================================================================
-- Vista materializada: rezago_educativo
-- =============================================================================
COMMENT ON MATERIALIZED VIEW rezago_educativo IS
    'Personas con carencia por rezago educativo. Municipios de Jalisco. Años: 2010, 2015, 2020.';

COMMENT ON COLUMN rezago_educativo.fid IS 'Identificador secuencial de la fila.';
COMMENT ON COLUMN rezago_educativo.geom_iieg IS 'Geometría del municipio (marco geoestadístico IIEG, SRID 6368).';
COMMENT ON COLUMN rezago_educativo.geom_inegi IS 'Geometría del municipio (marco geoestadístico INEGI, SRID 6368).';
COMMENT ON COLUMN rezago_educativo.nombre IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN rezago_educativo.fecha IS 'Fecha del periodo de medición (1 de enero del año).';
COMMENT ON COLUMN rezago_educativo.clave_entidad IS 'FK al catálogo de entidades federativas.';
COMMENT ON COLUMN rezago_educativo.clave_municipio IS 'Clave municipal INEGI de 5 dígitos (EEMMM).';
COMMENT ON COLUMN rezago_educativo.personas IS 'Número de personas con carencia por rezago educativo.';
COMMENT ON COLUMN rezago_educativo.porcentaje IS 'Porcentaje de personas con carencia por rezago educativo.';
COMMENT ON COLUMN rezago_educativo.carencias_promedio IS 'Promedio de carencias en la población con rezago educativo.';

-- =============================================================================
-- Vista materializada: carencia_acceso_servicios_salud
-- =============================================================================
COMMENT ON MATERIALIZED VIEW carencia_acceso_servicios_salud IS
    'Personas con carencia por acceso a servicios de salud. Municipios de Jalisco. Años: 2010, 2015, 2020.';

COMMENT ON COLUMN carencia_acceso_servicios_salud.fid IS 'Identificador secuencial de la fila.';
COMMENT ON COLUMN carencia_acceso_servicios_salud.geom_iieg IS 'Geometría del municipio (marco geoestadístico IIEG, SRID 6368).';
COMMENT ON COLUMN carencia_acceso_servicios_salud.geom_inegi IS 'Geometría del municipio (marco geoestadístico INEGI, SRID 6368).';
COMMENT ON COLUMN carencia_acceso_servicios_salud.nombre IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN carencia_acceso_servicios_salud.fecha IS 'Fecha del periodo de medición (1 de enero del año).';
COMMENT ON COLUMN carencia_acceso_servicios_salud.clave_entidad IS 'FK al catálogo de entidades federativas.';
COMMENT ON COLUMN carencia_acceso_servicios_salud.clave_municipio IS 'Clave municipal INEGI de 5 dígitos (EEMMM).';
COMMENT ON COLUMN carencia_acceso_servicios_salud.personas IS 'Número de personas con carencia por acceso a servicios de salud.';
COMMENT ON COLUMN carencia_acceso_servicios_salud.porcentaje IS 'Porcentaje de personas con carencia por acceso a servicios de salud.';
COMMENT ON COLUMN carencia_acceso_servicios_salud.carencias_promedio IS 'Promedio de carencias en la población con esta carencia.';

-- =============================================================================
-- Vista materializada: carencia_acceso_seguridad_social
-- =============================================================================
COMMENT ON MATERIALIZED VIEW carencia_acceso_seguridad_social IS
    'Personas con carencia por acceso a seguridad social. Municipios de Jalisco. Años: 2010, 2015, 2020.';

COMMENT ON COLUMN carencia_acceso_seguridad_social.fid IS 'Identificador secuencial de la fila.';
COMMENT ON COLUMN carencia_acceso_seguridad_social.geom_iieg IS 'Geometría del municipio (marco geoestadístico IIEG, SRID 6368).';
COMMENT ON COLUMN carencia_acceso_seguridad_social.geom_inegi IS 'Geometría del municipio (marco geoestadístico INEGI, SRID 6368).';
COMMENT ON COLUMN carencia_acceso_seguridad_social.nombre IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN carencia_acceso_seguridad_social.fecha IS 'Fecha del periodo de medición (1 de enero del año).';
COMMENT ON COLUMN carencia_acceso_seguridad_social.clave_entidad IS 'FK al catálogo de entidades federativas.';
COMMENT ON COLUMN carencia_acceso_seguridad_social.clave_municipio IS 'Clave municipal INEGI de 5 dígitos (EEMMM).';
COMMENT ON COLUMN carencia_acceso_seguridad_social.personas IS 'Número de personas con carencia por acceso a seguridad social.';
COMMENT ON COLUMN carencia_acceso_seguridad_social.porcentaje IS 'Porcentaje de personas con carencia por acceso a seguridad social.';
COMMENT ON COLUMN carencia_acceso_seguridad_social.carencias_promedio IS 'Promedio de carencias en la población con esta carencia.';

-- =============================================================================
-- Vista materializada: carencia_calidad_espacios_vivienda
-- =============================================================================
COMMENT ON MATERIALIZED VIEW carencia_calidad_espacios_vivienda IS
    'Personas con carencia por calidad y espacios de vivienda. Municipios de Jalisco. Años: 2010, 2015, 2020.';

COMMENT ON COLUMN carencia_calidad_espacios_vivienda.fid IS 'Identificador secuencial de la fila.';
COMMENT ON COLUMN carencia_calidad_espacios_vivienda.geom_iieg IS 'Geometría del municipio (marco geoestadístico IIEG, SRID 6368).';
COMMENT ON COLUMN carencia_calidad_espacios_vivienda.geom_inegi IS 'Geometría del municipio (marco geoestadístico INEGI, SRID 6368).';
COMMENT ON COLUMN carencia_calidad_espacios_vivienda.nombre IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN carencia_calidad_espacios_vivienda.fecha IS 'Fecha del periodo de medición (1 de enero del año).';
COMMENT ON COLUMN carencia_calidad_espacios_vivienda.clave_entidad IS 'FK al catálogo de entidades federativas.';
COMMENT ON COLUMN carencia_calidad_espacios_vivienda.clave_municipio IS 'Clave municipal INEGI de 5 dígitos (EEMMM).';
COMMENT ON COLUMN carencia_calidad_espacios_vivienda.personas IS 'Número de personas con carencia por calidad y espacios de vivienda.';
COMMENT ON COLUMN carencia_calidad_espacios_vivienda.porcentaje IS 'Porcentaje de personas con carencia por calidad y espacios de vivienda.';
COMMENT ON COLUMN carencia_calidad_espacios_vivienda.carencias_promedio IS 'Promedio de carencias en la población con esta carencia.';

-- =============================================================================
-- Vista materializada: carencia_servicios_basicos_vivienda
-- =============================================================================
COMMENT ON MATERIALIZED VIEW carencia_servicios_basicos_vivienda IS
    'Personas con carencia por acceso a servicios básicos en vivienda. Municipios de Jalisco. Años: 2010, 2015, 2020.';

COMMENT ON COLUMN carencia_servicios_basicos_vivienda.fid IS 'Identificador secuencial de la fila.';
COMMENT ON COLUMN carencia_servicios_basicos_vivienda.geom_iieg IS 'Geometría del municipio (marco geoestadístico IIEG, SRID 6368).';
COMMENT ON COLUMN carencia_servicios_basicos_vivienda.geom_inegi IS 'Geometría del municipio (marco geoestadístico INEGI, SRID 6368).';
COMMENT ON COLUMN carencia_servicios_basicos_vivienda.nombre IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN carencia_servicios_basicos_vivienda.fecha IS 'Fecha del periodo de medición (1 de enero del año).';
COMMENT ON COLUMN carencia_servicios_basicos_vivienda.clave_entidad IS 'FK al catálogo de entidades federativas.';
COMMENT ON COLUMN carencia_servicios_basicos_vivienda.clave_municipio IS 'Clave municipal INEGI de 5 dígitos (EEMMM).';
COMMENT ON COLUMN carencia_servicios_basicos_vivienda.personas IS 'Número de personas con carencia por acceso a servicios básicos en vivienda.';
COMMENT ON COLUMN carencia_servicios_basicos_vivienda.porcentaje IS 'Porcentaje de personas con carencia por acceso a servicios básicos en vivienda.';
COMMENT ON COLUMN carencia_servicios_basicos_vivienda.carencias_promedio IS 'Promedio de carencias en la población con esta carencia.';

-- =============================================================================
-- Vista materializada: carencia_acceso_alimentacion
-- =============================================================================
COMMENT ON MATERIALIZED VIEW carencia_acceso_alimentacion IS
    'Personas con carencia por acceso a alimentación nutritiva y de calidad. Municipios de Jalisco. Años: 2010, 2015, 2020.';

COMMENT ON COLUMN carencia_acceso_alimentacion.fid IS 'Identificador secuencial de la fila.';
COMMENT ON COLUMN carencia_acceso_alimentacion.geom_iieg IS 'Geometría del municipio (marco geoestadístico IIEG, SRID 6368).';
COMMENT ON COLUMN carencia_acceso_alimentacion.geom_inegi IS 'Geometría del municipio (marco geoestadístico INEGI, SRID 6368).';
COMMENT ON COLUMN carencia_acceso_alimentacion.nombre IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN carencia_acceso_alimentacion.fecha IS 'Fecha del periodo de medición (1 de enero del año).';
COMMENT ON COLUMN carencia_acceso_alimentacion.clave_entidad IS 'FK al catálogo de entidades federativas.';
COMMENT ON COLUMN carencia_acceso_alimentacion.clave_municipio IS 'Clave municipal INEGI de 5 dígitos (EEMMM).';
COMMENT ON COLUMN carencia_acceso_alimentacion.personas IS 'Número de personas con carencia por acceso a alimentación nutritiva y de calidad.';
COMMENT ON COLUMN carencia_acceso_alimentacion.porcentaje IS 'Porcentaje de personas con carencia por acceso a alimentación nutritiva y de calidad.';
COMMENT ON COLUMN carencia_acceso_alimentacion.carencias_promedio IS 'Promedio de carencias en la población con esta carencia.';

-- =============================================================================
-- Vista materializada: poblacion_con_al_menos_una_carencia_social
-- =============================================================================
COMMENT ON MATERIALIZED VIEW poblacion_con_al_menos_una_carencia_social IS
    'Personas con al menos una carencia social. Municipios de Jalisco. Años: 2010, 2015, 2020.';

COMMENT ON COLUMN poblacion_con_al_menos_una_carencia_social.fid IS 'Identificador secuencial de la fila.';
COMMENT ON COLUMN poblacion_con_al_menos_una_carencia_social.geom_iieg IS 'Geometría del municipio (marco geoestadístico IIEG, SRID 6368).';
COMMENT ON COLUMN poblacion_con_al_menos_una_carencia_social.geom_inegi IS 'Geometría del municipio (marco geoestadístico INEGI, SRID 6368).';
COMMENT ON COLUMN poblacion_con_al_menos_una_carencia_social.nombre IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN poblacion_con_al_menos_una_carencia_social.fecha IS 'Fecha del periodo de medición (1 de enero del año).';
COMMENT ON COLUMN poblacion_con_al_menos_una_carencia_social.clave_entidad IS 'FK al catálogo de entidades federativas.';
COMMENT ON COLUMN poblacion_con_al_menos_una_carencia_social.clave_municipio IS 'Clave municipal INEGI de 5 dígitos (EEMMM).';
COMMENT ON COLUMN poblacion_con_al_menos_una_carencia_social.personas IS 'Número de personas con al menos una carencia social.';
COMMENT ON COLUMN poblacion_con_al_menos_una_carencia_social.porcentaje IS 'Porcentaje de personas con al menos una carencia social.';
COMMENT ON COLUMN poblacion_con_al_menos_una_carencia_social.carencias_promedio IS 'Promedio de carencias en la población con al menos una carencia social.';

-- =============================================================================
-- Vista materializada: poblacion_con_tres_o_mas_carencias_sociales
-- =============================================================================
COMMENT ON MATERIALIZED VIEW poblacion_con_tres_o_mas_carencias_sociales IS
    'Personas con tres o más carencias sociales. Municipios de Jalisco. Años: 2010, 2015, 2020.';

COMMENT ON COLUMN poblacion_con_tres_o_mas_carencias_sociales.fid IS 'Identificador secuencial de la fila.';
COMMENT ON COLUMN poblacion_con_tres_o_mas_carencias_sociales.geom_iieg IS 'Geometría del municipio (marco geoestadístico IIEG, SRID 6368).';
COMMENT ON COLUMN poblacion_con_tres_o_mas_carencias_sociales.geom_inegi IS 'Geometría del municipio (marco geoestadístico INEGI, SRID 6368).';
COMMENT ON COLUMN poblacion_con_tres_o_mas_carencias_sociales.nombre IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN poblacion_con_tres_o_mas_carencias_sociales.fecha IS 'Fecha del periodo de medición (1 de enero del año).';
COMMENT ON COLUMN poblacion_con_tres_o_mas_carencias_sociales.clave_entidad IS 'FK al catálogo de entidades federativas.';
COMMENT ON COLUMN poblacion_con_tres_o_mas_carencias_sociales.clave_municipio IS 'Clave municipal INEGI de 5 dígitos (EEMMM).';
COMMENT ON COLUMN poblacion_con_tres_o_mas_carencias_sociales.personas IS 'Número de personas con tres o más carencias sociales.';
COMMENT ON COLUMN poblacion_con_tres_o_mas_carencias_sociales.porcentaje IS 'Porcentaje de personas con tres o más carencias sociales.';
COMMENT ON COLUMN poblacion_con_tres_o_mas_carencias_sociales.carencias_promedio IS 'Promedio de carencias en la población con tres o más carencias sociales.';

-- =============================================================================
-- Vista materializada: vulnerables_por_carencia_social
-- =============================================================================
COMMENT ON MATERIALIZED VIEW vulnerables_por_carencia_social IS
    'Personas vulnerables por carencias (no pobres por ingresos). Municipios de Jalisco. Años: 2010, 2015, 2020.';

COMMENT ON COLUMN vulnerables_por_carencia_social.fid IS 'Identificador secuencial de la fila.';
COMMENT ON COLUMN vulnerables_por_carencia_social.geom_iieg IS 'Geometría del municipio (marco geoestadístico IIEG, SRID 6368).';
COMMENT ON COLUMN vulnerables_por_carencia_social.geom_inegi IS 'Geometría del municipio (marco geoestadístico INEGI, SRID 6368).';
COMMENT ON COLUMN vulnerables_por_carencia_social.nombre IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN vulnerables_por_carencia_social.fecha IS 'Fecha del periodo de medición (1 de enero del año).';
COMMENT ON COLUMN vulnerables_por_carencia_social.clave_entidad IS 'FK al catálogo de entidades federativas.';
COMMENT ON COLUMN vulnerables_por_carencia_social.clave_municipio IS 'Clave municipal INEGI de 5 dígitos (EEMMM).';
COMMENT ON COLUMN vulnerables_por_carencia_social.personas IS 'Número de personas vulnerables por carencia social.';
COMMENT ON COLUMN vulnerables_por_carencia_social.porcentaje IS 'Porcentaje de personas vulnerables por carencia social.';
COMMENT ON COLUMN vulnerables_por_carencia_social.carencias_promedio IS 'Promedio de carencias en la población vulnerable por carencia social.';

-- =============================================================================
-- Vista materializada: vulnerables_por_ingreso
-- =============================================================================
COMMENT ON MATERIALIZED VIEW vulnerables_por_ingreso IS
    'Personas vulnerables por ingresos (sin carencias). Municipios de Jalisco. Años: 2010, 2015, 2020.';

COMMENT ON COLUMN vulnerables_por_ingreso.fid IS 'Identificador secuencial de la fila.';
COMMENT ON COLUMN vulnerables_por_ingreso.geom_iieg IS 'Geometría del municipio (marco geoestadístico IIEG, SRID 6368).';
COMMENT ON COLUMN vulnerables_por_ingreso.geom_inegi IS 'Geometría del municipio (marco geoestadístico INEGI, SRID 6368).';
COMMENT ON COLUMN vulnerables_por_ingreso.nombre IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN vulnerables_por_ingreso.fecha IS 'Fecha del periodo de medición (1 de enero del año).';
COMMENT ON COLUMN vulnerables_por_ingreso.clave_entidad IS 'FK al catálogo de entidades federativas.';
COMMENT ON COLUMN vulnerables_por_ingreso.clave_municipio IS 'Clave municipal INEGI de 5 dígitos (EEMMM).';
COMMENT ON COLUMN vulnerables_por_ingreso.personas IS 'Número de personas vulnerables por ingresos.';
COMMENT ON COLUMN vulnerables_por_ingreso.porcentaje IS 'Porcentaje de personas vulnerables por ingresos.';
COMMENT ON COLUMN vulnerables_por_ingreso.carencias_promedio IS 'No disponible en la fuente CONEVAL para este indicador (siempre NULL).';

-- =============================================================================
-- Vista materializada: no_pobre_y_no_vulnerable
-- =============================================================================
COMMENT ON MATERIALIZED VIEW no_pobre_y_no_vulnerable IS
    'Personas no pobres y no vulnerables. Municipios de Jalisco. Años: 2010, 2015, 2020.';

COMMENT ON COLUMN no_pobre_y_no_vulnerable.fid IS 'Identificador secuencial de la fila.';
COMMENT ON COLUMN no_pobre_y_no_vulnerable.geom_iieg IS 'Geometría del municipio (marco geoestadístico IIEG, SRID 6368).';
COMMENT ON COLUMN no_pobre_y_no_vulnerable.geom_inegi IS 'Geometría del municipio (marco geoestadístico INEGI, SRID 6368).';
COMMENT ON COLUMN no_pobre_y_no_vulnerable.nombre IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN no_pobre_y_no_vulnerable.fecha IS 'Fecha del periodo de medición (1 de enero del año).';
COMMENT ON COLUMN no_pobre_y_no_vulnerable.clave_entidad IS 'FK al catálogo de entidades federativas.';
COMMENT ON COLUMN no_pobre_y_no_vulnerable.clave_municipio IS 'Clave municipal INEGI de 5 dígitos (EEMMM).';
COMMENT ON COLUMN no_pobre_y_no_vulnerable.personas IS 'Número de personas no pobres y no vulnerables.';
COMMENT ON COLUMN no_pobre_y_no_vulnerable.porcentaje IS 'Porcentaje de personas no pobres y no vulnerables.';
COMMENT ON COLUMN no_pobre_y_no_vulnerable.carencias_promedio IS 'No disponible en la fuente CONEVAL para este indicador (siempre NULL).';
