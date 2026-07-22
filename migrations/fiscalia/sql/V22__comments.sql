-- =======================================================================
-- V22__comments.sql  |  Pipeline: fiscalia
-- Comentarios en tablas base, catálogos, vista mapalab y vistas materializadas.
-- =======================================================================

-- =============================================================================
-- cvegeo_municipalities (foreign table, FDW a cvegeo)
-- =============================================================================
COMMENT ON FOREIGN TABLE cvegeo_municipalities IS
    'Catálogo de municipios de Jalisco vía FDW al servidor cvegeo.';
COMMENT ON COLUMN cvegeo_municipalities.id IS 'Identificador interno del municipio en cvegeo.';
COMMENT ON COLUMN cvegeo_municipalities.cvegeo IS 'Clave geoestadística completa del municipio (INEGI).';
COMMENT ON COLUMN cvegeo_municipalities.cve_ent IS 'Clave de la entidad federativa (14 = Jalisco).';
COMMENT ON COLUMN cvegeo_municipalities.cve_mun IS 'Clave del municipio dentro de la entidad.';
COMMENT ON COLUMN cvegeo_municipalities.nomgeo IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN cvegeo_municipalities.nom_ent IS 'Nombre oficial de la entidad federativa.';

-- =============================================================================
-- zonas_geograficas
-- =============================================================================
COMMENT ON TABLE zonas_geograficas IS
    'Catálogo de zonas geográficas del estado.';
COMMENT ON COLUMN zonas_geograficas.id IS 'Identificador de la zona geográfica.';
COMMENT ON COLUMN zonas_geograficas.zona_geografica IS 'Zona geográfica: AMG (Área Metropolitana de Guadalajara) o Interior.';

-- =============================================================================
-- bien_afectado
-- =============================================================================
COMMENT ON TABLE bien_afectado IS
    'Catálogo de bienes jurídicos afectados por los delitos.';
COMMENT ON COLUMN bien_afectado.id IS 'Identificador del bien afectado.';
COMMENT ON COLUMN bien_afectado.bien_afectado IS 'Nombre del bien jurídico afectado.';

-- =============================================================================
-- delitos
-- =============================================================================
COMMENT ON TABLE delitos IS
    'Catálogo de tipos de delito.';
COMMENT ON COLUMN delitos.id IS 'Identificador del tipo de delito.';
COMMENT ON COLUMN delitos.delito IS 'Nombre del tipo de delito.';
COMMENT ON COLUMN delitos.bien_afectado_id IS 'FK al catálogo bien_afectado.';

-- =============================================================================
-- violencia
-- =============================================================================
COMMENT ON TABLE violencia IS
    'Catálogo de modalidad de violencia.';
COMMENT ON COLUMN violencia.id IS 'Identificador de la modalidad de violencia.';
COMMENT ON COLUMN violencia.violencia IS 'Modalidad: Con violencia o Sin violencia.';

-- =============================================================================
-- colonias
-- =============================================================================
COMMENT ON TABLE colonias IS
    'Catálogo dinámico de colonias.';
COMMENT ON COLUMN colonias.id IS 'Identificador autoincremental de la colonia.';
COMMENT ON COLUMN colonias.colonia IS 'Nombre de la colonia.';

-- =============================================================================
-- calles
-- =============================================================================
COMMENT ON TABLE calles IS
    'Catálogo dinámico de calles.';
COMMENT ON COLUMN calles.id IS 'Identificador autoincremental de la calle.';
COMMENT ON COLUMN calles.calle IS 'Nombre de la calle.';

-- =============================================================================
-- cruces
-- =============================================================================
COMMENT ON TABLE cruces IS
    'Catálogo dinámico de cruces.';
COMMENT ON COLUMN cruces.id IS 'Identificador autoincremental del cruce.';
COMMENT ON COLUMN cruces.cruce IS 'Nombre del cruce (intersección).';

-- =============================================================================
-- casos (tabla de hechos)
-- =============================================================================
COMMENT ON TABLE casos IS
    'Carpetas de investigación de la Fiscalía del Estado de Jalisco (un registro por caso).';
COMMENT ON COLUMN casos.id IS 'Identificador autoincremental del caso.';
COMMENT ON COLUMN casos.delitos_id IS 'FK al catálogo delitos.';
COMMENT ON COLUMN casos.violencia_id IS 'FK al catálogo violencia (modalidad).';
COMMENT ON COLUMN casos.zonas_geograficas_id IS 'FK al catálogo zonas_geograficas.';
COMMENT ON COLUMN casos.municipios_id IS 'Clave del municipio (cve_mun de cvegeo, entidad 14).';
COMMENT ON COLUMN casos.colonias_id IS 'FK al catálogo colonias.';
COMMENT ON COLUMN casos.calles_id IS 'FK al catálogo calles.';
COMMENT ON COLUMN casos.cruces_id IS 'FK al catálogo cruces.';
COMMENT ON COLUMN casos.hora IS 'Hora de la denuncia en formato HH:MM.';
COMMENT ON COLUMN casos.longitud IS 'Coordenada X proyectada en EPSG:6368 (metros); el origen la nombra longitud.';
COMMENT ON COLUMN casos.latitud IS 'Coordenada Y proyectada en EPSG:6368 (metros); el origen la nombra latitud.';
COMMENT ON COLUMN casos.fecha_denuncia IS 'Fecha de la denuncia.';
COMMENT ON COLUMN casos.fecha_actualizacion IS 'Fecha de la última actualización del registro en el pipeline.';

-- =============================================================================
-- vw_mapalab_fiscalia (vista base mapalab)
-- =============================================================================
COMMENT ON VIEW vw_mapalab_fiscalia IS
    'Vista base mapalab de delitos de fiscalía: aplana casos y catálogos al formato del servidor iieg_gis.';
COMMENT ON COLUMN vw_mapalab_fiscalia.fecha IS 'Fecha de la denuncia.';
COMMENT ON COLUMN vw_mapalab_fiscalia.entidad IS 'Entidad federativa (constante: Jalisco).';
COMMENT ON COLUMN vw_mapalab_fiscalia.municipio IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN vw_mapalab_fiscalia.x_6368 IS 'Coordenada X proyectada en EPSG:6368 (metros).';
COMMENT ON COLUMN vw_mapalab_fiscalia.y_6368 IS 'Coordenada Y proyectada en EPSG:6368 (metros).';
COMMENT ON COLUMN vw_mapalab_fiscalia.bien_juridico IS 'Bien jurídico afectado por el delito.';
COMMENT ON COLUMN vw_mapalab_fiscalia.delito IS 'Tipo de delito.';
COMMENT ON COLUMN vw_mapalab_fiscalia.modalidad IS 'Modalidad de violencia: Con violencia / Sin violencia (NULL si no aplica).';
COMMENT ON COLUMN vw_mapalab_fiscalia.dia_semana IS 'Día de la semana de la denuncia (en español, minúsculas).';
COMMENT ON COLUMN vw_mapalab_fiscalia.rango_hora IS 'Franja horaria: Madrugada 00-06 h, Mañana 06-12 h, Tarde 12-18 h, Noche 18-24 h, No disponible.';
COMMENT ON COLUMN vw_mapalab_fiscalia.geom IS 'Geometría del punto del delito (EPSG:6368).';

-- =============================================================================
-- Vista materializada: delitos_fiscalia_abuso_sexual_infantil
-- =============================================================================
COMMENT ON MATERIALIZED VIEW delitos_fiscalia_abuso_sexual_infantil IS
    'Delitos de fiscalía del tipo: Abuso sexual infantil. Solo registros con coordenadas válidas; consumida en vivo por mapalab.';
COMMENT ON COLUMN delitos_fiscalia_abuso_sexual_infantil.fid IS 'Identificador secuencial de la fila.';
COMMENT ON COLUMN delitos_fiscalia_abuso_sexual_infantil.fecha IS 'Fecha de la denuncia.';
COMMENT ON COLUMN delitos_fiscalia_abuso_sexual_infantil.entidad IS 'Entidad federativa (constante: Jalisco).';
COMMENT ON COLUMN delitos_fiscalia_abuso_sexual_infantil.municipio IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN delitos_fiscalia_abuso_sexual_infantil.x_6368 IS 'Coordenada X proyectada en EPSG:6368 (metros).';
COMMENT ON COLUMN delitos_fiscalia_abuso_sexual_infantil.y_6368 IS 'Coordenada Y proyectada en EPSG:6368 (metros).';
COMMENT ON COLUMN delitos_fiscalia_abuso_sexual_infantil.bien_juridico IS 'Bien jurídico afectado por el delito.';
COMMENT ON COLUMN delitos_fiscalia_abuso_sexual_infantil.delito IS 'Tipo de delito.';
COMMENT ON COLUMN delitos_fiscalia_abuso_sexual_infantil.dia_semana IS 'Día de la semana de la denuncia (en español, minúsculas).';
COMMENT ON COLUMN delitos_fiscalia_abuso_sexual_infantil.rango_hora IS 'Franja horaria: Madrugada 00-06 h, Mañana 06-12 h, Tarde 12-18 h, Noche 18-24 h, No disponible.';
COMMENT ON COLUMN delitos_fiscalia_abuso_sexual_infantil.geom IS 'Geometría del punto del delito (EPSG:6368).';

-- =============================================================================
-- Vista materializada: delitos_fiscalia_feminicidio
-- =============================================================================
COMMENT ON MATERIALIZED VIEW delitos_fiscalia_feminicidio IS
    'Delitos de fiscalía del tipo: Feminicidio. Solo registros con coordenadas válidas; consumida en vivo por mapalab.';
COMMENT ON COLUMN delitos_fiscalia_feminicidio.fid IS 'Identificador secuencial de la fila.';
COMMENT ON COLUMN delitos_fiscalia_feminicidio.fecha IS 'Fecha de la denuncia.';
COMMENT ON COLUMN delitos_fiscalia_feminicidio.entidad IS 'Entidad federativa (constante: Jalisco).';
COMMENT ON COLUMN delitos_fiscalia_feminicidio.municipio IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN delitos_fiscalia_feminicidio.x_6368 IS 'Coordenada X proyectada en EPSG:6368 (metros).';
COMMENT ON COLUMN delitos_fiscalia_feminicidio.y_6368 IS 'Coordenada Y proyectada en EPSG:6368 (metros).';
COMMENT ON COLUMN delitos_fiscalia_feminicidio.bien_juridico IS 'Bien jurídico afectado por el delito.';
COMMENT ON COLUMN delitos_fiscalia_feminicidio.delito IS 'Tipo de delito.';
COMMENT ON COLUMN delitos_fiscalia_feminicidio.dia_semana IS 'Día de la semana de la denuncia (en español, minúsculas).';
COMMENT ON COLUMN delitos_fiscalia_feminicidio.rango_hora IS 'Franja horaria: Madrugada 00-06 h, Mañana 06-12 h, Tarde 12-18 h, Noche 18-24 h, No disponible.';
COMMENT ON COLUMN delitos_fiscalia_feminicidio.geom IS 'Geometría del punto del delito (EPSG:6368).';

-- =============================================================================
-- Vista materializada: delitos_fiscalia_homicidio_doloso
-- =============================================================================
COMMENT ON MATERIALIZED VIEW delitos_fiscalia_homicidio_doloso IS
    'Delitos de fiscalía del tipo: Homicidio doloso. Solo registros con coordenadas válidas; consumida en vivo por mapalab.';
COMMENT ON COLUMN delitos_fiscalia_homicidio_doloso.fid IS 'Identificador secuencial de la fila.';
COMMENT ON COLUMN delitos_fiscalia_homicidio_doloso.fecha IS 'Fecha de la denuncia.';
COMMENT ON COLUMN delitos_fiscalia_homicidio_doloso.entidad IS 'Entidad federativa (constante: Jalisco).';
COMMENT ON COLUMN delitos_fiscalia_homicidio_doloso.municipio IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN delitos_fiscalia_homicidio_doloso.x_6368 IS 'Coordenada X proyectada en EPSG:6368 (metros).';
COMMENT ON COLUMN delitos_fiscalia_homicidio_doloso.y_6368 IS 'Coordenada Y proyectada en EPSG:6368 (metros).';
COMMENT ON COLUMN delitos_fiscalia_homicidio_doloso.bien_juridico IS 'Bien jurídico afectado por el delito.';
COMMENT ON COLUMN delitos_fiscalia_homicidio_doloso.delito IS 'Tipo de delito.';
COMMENT ON COLUMN delitos_fiscalia_homicidio_doloso.dia_semana IS 'Día de la semana de la denuncia (en español, minúsculas).';
COMMENT ON COLUMN delitos_fiscalia_homicidio_doloso.rango_hora IS 'Franja horaria: Madrugada 00-06 h, Mañana 06-12 h, Tarde 12-18 h, Noche 18-24 h, No disponible.';
COMMENT ON COLUMN delitos_fiscalia_homicidio_doloso.geom IS 'Geometría del punto del delito (EPSG:6368).';

-- =============================================================================
-- Vista materializada: delitos_fiscalia_lesiones_dolosas
-- =============================================================================
COMMENT ON MATERIALIZED VIEW delitos_fiscalia_lesiones_dolosas IS
    'Delitos de fiscalía del tipo: Lesiones dolosas. Solo registros con coordenadas válidas; consumida en vivo por mapalab.';
COMMENT ON COLUMN delitos_fiscalia_lesiones_dolosas.fid IS 'Identificador secuencial de la fila.';
COMMENT ON COLUMN delitos_fiscalia_lesiones_dolosas.fecha IS 'Fecha de la denuncia.';
COMMENT ON COLUMN delitos_fiscalia_lesiones_dolosas.entidad IS 'Entidad federativa (constante: Jalisco).';
COMMENT ON COLUMN delitos_fiscalia_lesiones_dolosas.municipio IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN delitos_fiscalia_lesiones_dolosas.x_6368 IS 'Coordenada X proyectada en EPSG:6368 (metros).';
COMMENT ON COLUMN delitos_fiscalia_lesiones_dolosas.y_6368 IS 'Coordenada Y proyectada en EPSG:6368 (metros).';
COMMENT ON COLUMN delitos_fiscalia_lesiones_dolosas.bien_juridico IS 'Bien jurídico afectado por el delito.';
COMMENT ON COLUMN delitos_fiscalia_lesiones_dolosas.delito IS 'Tipo de delito.';
COMMENT ON COLUMN delitos_fiscalia_lesiones_dolosas.dia_semana IS 'Día de la semana de la denuncia (en español, minúsculas).';
COMMENT ON COLUMN delitos_fiscalia_lesiones_dolosas.rango_hora IS 'Franja horaria: Madrugada 00-06 h, Mañana 06-12 h, Tarde 12-18 h, Noche 18-24 h, No disponible.';
COMMENT ON COLUMN delitos_fiscalia_lesiones_dolosas.geom IS 'Geometría del punto del delito (EPSG:6368).';

-- =============================================================================
-- Vista materializada: delitos_fiscalia_robo_bancos
-- =============================================================================
COMMENT ON MATERIALIZED VIEW delitos_fiscalia_robo_bancos IS
    'Delitos de fiscalía del tipo: Robo a bancos. Solo registros con coordenadas válidas; consumida en vivo por mapalab.';
COMMENT ON COLUMN delitos_fiscalia_robo_bancos.fid IS 'Identificador secuencial de la fila.';
COMMENT ON COLUMN delitos_fiscalia_robo_bancos.fecha IS 'Fecha de la denuncia.';
COMMENT ON COLUMN delitos_fiscalia_robo_bancos.entidad IS 'Entidad federativa (constante: Jalisco).';
COMMENT ON COLUMN delitos_fiscalia_robo_bancos.municipio IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN delitos_fiscalia_robo_bancos.x_6368 IS 'Coordenada X proyectada en EPSG:6368 (metros).';
COMMENT ON COLUMN delitos_fiscalia_robo_bancos.y_6368 IS 'Coordenada Y proyectada en EPSG:6368 (metros).';
COMMENT ON COLUMN delitos_fiscalia_robo_bancos.bien_juridico IS 'Bien jurídico afectado por el delito.';
COMMENT ON COLUMN delitos_fiscalia_robo_bancos.delito IS 'Tipo de delito.';
COMMENT ON COLUMN delitos_fiscalia_robo_bancos.modalidad IS 'Modalidad de violencia: Con violencia / Sin violencia.';
COMMENT ON COLUMN delitos_fiscalia_robo_bancos.dia_semana IS 'Día de la semana de la denuncia (en español, minúsculas).';
COMMENT ON COLUMN delitos_fiscalia_robo_bancos.rango_hora IS 'Franja horaria: Madrugada 00-06 h, Mañana 06-12 h, Tarde 12-18 h, Noche 18-24 h, No disponible.';
COMMENT ON COLUMN delitos_fiscalia_robo_bancos.geom IS 'Geometría del punto del delito (EPSG:6368).';

-- =============================================================================
-- Vista materializada: delitos_fiscalia_robo_carga_pesada
-- =============================================================================
COMMENT ON MATERIALIZED VIEW delitos_fiscalia_robo_carga_pesada IS
    'Delitos de fiscalía del tipo: Robo a vehículos de carga pesada. Solo registros con coordenadas válidas; consumida en vivo por mapalab.';
COMMENT ON COLUMN delitos_fiscalia_robo_carga_pesada.fid IS 'Identificador secuencial de la fila.';
COMMENT ON COLUMN delitos_fiscalia_robo_carga_pesada.fecha IS 'Fecha de la denuncia.';
COMMENT ON COLUMN delitos_fiscalia_robo_carga_pesada.entidad IS 'Entidad federativa (constante: Jalisco).';
COMMENT ON COLUMN delitos_fiscalia_robo_carga_pesada.municipio IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN delitos_fiscalia_robo_carga_pesada.x_6368 IS 'Coordenada X proyectada en EPSG:6368 (metros).';
COMMENT ON COLUMN delitos_fiscalia_robo_carga_pesada.y_6368 IS 'Coordenada Y proyectada en EPSG:6368 (metros).';
COMMENT ON COLUMN delitos_fiscalia_robo_carga_pesada.bien_juridico IS 'Bien jurídico afectado por el delito.';
COMMENT ON COLUMN delitos_fiscalia_robo_carga_pesada.delito IS 'Tipo de delito.';
COMMENT ON COLUMN delitos_fiscalia_robo_carga_pesada.modalidad IS 'Modalidad de violencia: Con violencia / Sin violencia.';
COMMENT ON COLUMN delitos_fiscalia_robo_carga_pesada.dia_semana IS 'Día de la semana de la denuncia (en español, minúsculas).';
COMMENT ON COLUMN delitos_fiscalia_robo_carga_pesada.rango_hora IS 'Franja horaria: Madrugada 00-06 h, Mañana 06-12 h, Tarde 12-18 h, Noche 18-24 h, No disponible.';
COMMENT ON COLUMN delitos_fiscalia_robo_carga_pesada.geom IS 'Geometría del punto del delito (EPSG:6368).';

-- =============================================================================
-- Vista materializada: delitos_fiscalia_robo_cuentahabientes
-- =============================================================================
COMMENT ON MATERIALIZED VIEW delitos_fiscalia_robo_cuentahabientes IS
    'Delitos de fiscalía del tipo: Robo a cuentahabientes. Solo registros con coordenadas válidas; consumida en vivo por mapalab.';
COMMENT ON COLUMN delitos_fiscalia_robo_cuentahabientes.fid IS 'Identificador secuencial de la fila.';
COMMENT ON COLUMN delitos_fiscalia_robo_cuentahabientes.fecha IS 'Fecha de la denuncia.';
COMMENT ON COLUMN delitos_fiscalia_robo_cuentahabientes.entidad IS 'Entidad federativa (constante: Jalisco).';
COMMENT ON COLUMN delitos_fiscalia_robo_cuentahabientes.municipio IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN delitos_fiscalia_robo_cuentahabientes.x_6368 IS 'Coordenada X proyectada en EPSG:6368 (metros).';
COMMENT ON COLUMN delitos_fiscalia_robo_cuentahabientes.y_6368 IS 'Coordenada Y proyectada en EPSG:6368 (metros).';
COMMENT ON COLUMN delitos_fiscalia_robo_cuentahabientes.bien_juridico IS 'Bien jurídico afectado por el delito.';
COMMENT ON COLUMN delitos_fiscalia_robo_cuentahabientes.delito IS 'Tipo de delito.';
COMMENT ON COLUMN delitos_fiscalia_robo_cuentahabientes.modalidad IS 'Modalidad de violencia: Con violencia / Sin violencia.';
COMMENT ON COLUMN delitos_fiscalia_robo_cuentahabientes.dia_semana IS 'Día de la semana de la denuncia (en español, minúsculas).';
COMMENT ON COLUMN delitos_fiscalia_robo_cuentahabientes.rango_hora IS 'Franja horaria: Madrugada 00-06 h, Mañana 06-12 h, Tarde 12-18 h, Noche 18-24 h, No disponible.';
COMMENT ON COLUMN delitos_fiscalia_robo_cuentahabientes.geom IS 'Geometría del punto del delito (EPSG:6368).';

-- =============================================================================
-- Vista materializada: delitos_fiscalia_robo_int_vehiculos
-- =============================================================================
COMMENT ON MATERIALIZED VIEW delitos_fiscalia_robo_int_vehiculos IS
    'Delitos de fiscalía del tipo: Robo a interior de vehículos. Solo registros con coordenadas válidas; consumida en vivo por mapalab.';
COMMENT ON COLUMN delitos_fiscalia_robo_int_vehiculos.fid IS 'Identificador secuencial de la fila.';
COMMENT ON COLUMN delitos_fiscalia_robo_int_vehiculos.fecha IS 'Fecha de la denuncia.';
COMMENT ON COLUMN delitos_fiscalia_robo_int_vehiculos.entidad IS 'Entidad federativa (constante: Jalisco).';
COMMENT ON COLUMN delitos_fiscalia_robo_int_vehiculos.municipio IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN delitos_fiscalia_robo_int_vehiculos.x_6368 IS 'Coordenada X proyectada en EPSG:6368 (metros).';
COMMENT ON COLUMN delitos_fiscalia_robo_int_vehiculos.y_6368 IS 'Coordenada Y proyectada en EPSG:6368 (metros).';
COMMENT ON COLUMN delitos_fiscalia_robo_int_vehiculos.bien_juridico IS 'Bien jurídico afectado por el delito.';
COMMENT ON COLUMN delitos_fiscalia_robo_int_vehiculos.delito IS 'Tipo de delito.';
COMMENT ON COLUMN delitos_fiscalia_robo_int_vehiculos.modalidad IS 'Modalidad de violencia: Con violencia / Sin violencia.';
COMMENT ON COLUMN delitos_fiscalia_robo_int_vehiculos.dia_semana IS 'Día de la semana de la denuncia (en español, minúsculas).';
COMMENT ON COLUMN delitos_fiscalia_robo_int_vehiculos.rango_hora IS 'Franja horaria: Madrugada 00-06 h, Mañana 06-12 h, Tarde 12-18 h, Noche 18-24 h, No disponible.';
COMMENT ON COLUMN delitos_fiscalia_robo_int_vehiculos.geom IS 'Geometría del punto del delito (EPSG:6368).';

-- =============================================================================
-- Vista materializada: delitos_fiscalia_robo_negocio
-- =============================================================================
COMMENT ON MATERIALIZED VIEW delitos_fiscalia_robo_negocio IS
    'Delitos de fiscalía del tipo: Robo a negocio. Solo registros con coordenadas válidas; consumida en vivo por mapalab.';
COMMENT ON COLUMN delitos_fiscalia_robo_negocio.fid IS 'Identificador secuencial de la fila.';
COMMENT ON COLUMN delitos_fiscalia_robo_negocio.fecha IS 'Fecha de la denuncia.';
COMMENT ON COLUMN delitos_fiscalia_robo_negocio.entidad IS 'Entidad federativa (constante: Jalisco).';
COMMENT ON COLUMN delitos_fiscalia_robo_negocio.municipio IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN delitos_fiscalia_robo_negocio.x_6368 IS 'Coordenada X proyectada en EPSG:6368 (metros).';
COMMENT ON COLUMN delitos_fiscalia_robo_negocio.y_6368 IS 'Coordenada Y proyectada en EPSG:6368 (metros).';
COMMENT ON COLUMN delitos_fiscalia_robo_negocio.bien_juridico IS 'Bien jurídico afectado por el delito.';
COMMENT ON COLUMN delitos_fiscalia_robo_negocio.delito IS 'Tipo de delito.';
COMMENT ON COLUMN delitos_fiscalia_robo_negocio.modalidad IS 'Modalidad de violencia: Con violencia / Sin violencia.';
COMMENT ON COLUMN delitos_fiscalia_robo_negocio.dia_semana IS 'Día de la semana de la denuncia (en español, minúsculas).';
COMMENT ON COLUMN delitos_fiscalia_robo_negocio.rango_hora IS 'Franja horaria: Madrugada 00-06 h, Mañana 06-12 h, Tarde 12-18 h, Noche 18-24 h, No disponible.';
COMMENT ON COLUMN delitos_fiscalia_robo_negocio.geom IS 'Geometría del punto del delito (EPSG:6368).';

-- =============================================================================
-- Vista materializada: delitos_fiscalia_robo_persona
-- =============================================================================
COMMENT ON MATERIALIZED VIEW delitos_fiscalia_robo_persona IS
    'Delitos de fiscalía del tipo: Robo a persona. Solo registros con coordenadas válidas; consumida en vivo por mapalab.';
COMMENT ON COLUMN delitos_fiscalia_robo_persona.fid IS 'Identificador secuencial de la fila.';
COMMENT ON COLUMN delitos_fiscalia_robo_persona.fecha IS 'Fecha de la denuncia.';
COMMENT ON COLUMN delitos_fiscalia_robo_persona.entidad IS 'Entidad federativa (constante: Jalisco).';
COMMENT ON COLUMN delitos_fiscalia_robo_persona.municipio IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN delitos_fiscalia_robo_persona.x_6368 IS 'Coordenada X proyectada en EPSG:6368 (metros).';
COMMENT ON COLUMN delitos_fiscalia_robo_persona.y_6368 IS 'Coordenada Y proyectada en EPSG:6368 (metros).';
COMMENT ON COLUMN delitos_fiscalia_robo_persona.bien_juridico IS 'Bien jurídico afectado por el delito.';
COMMENT ON COLUMN delitos_fiscalia_robo_persona.delito IS 'Tipo de delito.';
COMMENT ON COLUMN delitos_fiscalia_robo_persona.modalidad IS 'Modalidad de violencia: Con violencia / Sin violencia.';
COMMENT ON COLUMN delitos_fiscalia_robo_persona.dia_semana IS 'Día de la semana de la denuncia (en español, minúsculas).';
COMMENT ON COLUMN delitos_fiscalia_robo_persona.rango_hora IS 'Franja horaria: Madrugada 00-06 h, Mañana 06-12 h, Tarde 12-18 h, Noche 18-24 h, No disponible.';
COMMENT ON COLUMN delitos_fiscalia_robo_persona.geom IS 'Geometría del punto del delito (EPSG:6368).';

-- =============================================================================
-- Vista materializada: delitos_fiscalia_robo_vehiculos_particulares
-- =============================================================================
COMMENT ON MATERIALIZED VIEW delitos_fiscalia_robo_vehiculos_particulares IS
    'Delitos de fiscalía del tipo: Robo a vehículos particulares. Solo registros con coordenadas válidas; consumida en vivo por mapalab.';
COMMENT ON COLUMN delitos_fiscalia_robo_vehiculos_particulares.fid IS 'Identificador secuencial de la fila.';
COMMENT ON COLUMN delitos_fiscalia_robo_vehiculos_particulares.fecha IS 'Fecha de la denuncia.';
COMMENT ON COLUMN delitos_fiscalia_robo_vehiculos_particulares.entidad IS 'Entidad federativa (constante: Jalisco).';
COMMENT ON COLUMN delitos_fiscalia_robo_vehiculos_particulares.municipio IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN delitos_fiscalia_robo_vehiculos_particulares.x_6368 IS 'Coordenada X proyectada en EPSG:6368 (metros).';
COMMENT ON COLUMN delitos_fiscalia_robo_vehiculos_particulares.y_6368 IS 'Coordenada Y proyectada en EPSG:6368 (metros).';
COMMENT ON COLUMN delitos_fiscalia_robo_vehiculos_particulares.bien_juridico IS 'Bien jurídico afectado por el delito.';
COMMENT ON COLUMN delitos_fiscalia_robo_vehiculos_particulares.delito IS 'Tipo de delito.';
COMMENT ON COLUMN delitos_fiscalia_robo_vehiculos_particulares.modalidad IS 'Modalidad de violencia: Con violencia / Sin violencia.';
COMMENT ON COLUMN delitos_fiscalia_robo_vehiculos_particulares.dia_semana IS 'Día de la semana de la denuncia (en español, minúsculas).';
COMMENT ON COLUMN delitos_fiscalia_robo_vehiculos_particulares.rango_hora IS 'Franja horaria: Madrugada 00-06 h, Mañana 06-12 h, Tarde 12-18 h, Noche 18-24 h, No disponible.';
COMMENT ON COLUMN delitos_fiscalia_robo_vehiculos_particulares.geom IS 'Geometría del punto del delito (EPSG:6368).';

-- =============================================================================
-- Vista materializada: delitos_fiscalia_robo_casa_habitacion
-- =============================================================================
COMMENT ON MATERIALIZED VIEW delitos_fiscalia_robo_casa_habitacion IS
    'Delitos de fiscalía del tipo: Robo a casa habitación. Solo registros con coordenadas válidas; consumida en vivo por mapalab.';
COMMENT ON COLUMN delitos_fiscalia_robo_casa_habitacion.fid IS 'Identificador secuencial de la fila.';
COMMENT ON COLUMN delitos_fiscalia_robo_casa_habitacion.fecha IS 'Fecha de la denuncia.';
COMMENT ON COLUMN delitos_fiscalia_robo_casa_habitacion.entidad IS 'Entidad federativa (constante: Jalisco).';
COMMENT ON COLUMN delitos_fiscalia_robo_casa_habitacion.municipio IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN delitos_fiscalia_robo_casa_habitacion.x_6368 IS 'Coordenada X proyectada en EPSG:6368 (metros).';
COMMENT ON COLUMN delitos_fiscalia_robo_casa_habitacion.y_6368 IS 'Coordenada Y proyectada en EPSG:6368 (metros).';
COMMENT ON COLUMN delitos_fiscalia_robo_casa_habitacion.bien_juridico IS 'Bien jurídico afectado por el delito.';
COMMENT ON COLUMN delitos_fiscalia_robo_casa_habitacion.delito IS 'Tipo de delito.';
COMMENT ON COLUMN delitos_fiscalia_robo_casa_habitacion.modalidad IS 'Modalidad de violencia: Con violencia / Sin violencia.';
COMMENT ON COLUMN delitos_fiscalia_robo_casa_habitacion.dia_semana IS 'Día de la semana de la denuncia (en español, minúsculas).';
COMMENT ON COLUMN delitos_fiscalia_robo_casa_habitacion.rango_hora IS 'Franja horaria: Madrugada 00-06 h, Mañana 06-12 h, Tarde 12-18 h, Noche 18-24 h, No disponible.';
COMMENT ON COLUMN delitos_fiscalia_robo_casa_habitacion.geom IS 'Geometría del punto del delito (EPSG:6368).';

-- =============================================================================
-- Vista materializada: delitos_fiscalia_robo_autopartes
-- =============================================================================
COMMENT ON MATERIALIZED VIEW delitos_fiscalia_robo_autopartes IS
    'Delitos de fiscalía del tipo: Robo de autopartes. Solo registros con coordenadas válidas; consumida en vivo por mapalab.';
COMMENT ON COLUMN delitos_fiscalia_robo_autopartes.fid IS 'Identificador secuencial de la fila.';
COMMENT ON COLUMN delitos_fiscalia_robo_autopartes.fecha IS 'Fecha de la denuncia.';
COMMENT ON COLUMN delitos_fiscalia_robo_autopartes.entidad IS 'Entidad federativa (constante: Jalisco).';
COMMENT ON COLUMN delitos_fiscalia_robo_autopartes.municipio IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN delitos_fiscalia_robo_autopartes.x_6368 IS 'Coordenada X proyectada en EPSG:6368 (metros).';
COMMENT ON COLUMN delitos_fiscalia_robo_autopartes.y_6368 IS 'Coordenada Y proyectada en EPSG:6368 (metros).';
COMMENT ON COLUMN delitos_fiscalia_robo_autopartes.bien_juridico IS 'Bien jurídico afectado por el delito.';
COMMENT ON COLUMN delitos_fiscalia_robo_autopartes.delito IS 'Tipo de delito.';
COMMENT ON COLUMN delitos_fiscalia_robo_autopartes.modalidad IS 'Modalidad de violencia: Con violencia / Sin violencia.';
COMMENT ON COLUMN delitos_fiscalia_robo_autopartes.dia_semana IS 'Día de la semana de la denuncia (en español, minúsculas).';
COMMENT ON COLUMN delitos_fiscalia_robo_autopartes.rango_hora IS 'Franja horaria: Madrugada 00-06 h, Mañana 06-12 h, Tarde 12-18 h, Noche 18-24 h, No disponible.';
COMMENT ON COLUMN delitos_fiscalia_robo_autopartes.geom IS 'Geometría del punto del delito (EPSG:6368).';

-- =============================================================================
-- Vista materializada: delitos_fiscalia_robo_motocicleta
-- =============================================================================
COMMENT ON MATERIALIZED VIEW delitos_fiscalia_robo_motocicleta IS
    'Delitos de fiscalía del tipo: Robo de motocicletas. Solo registros con coordenadas válidas; consumida en vivo por mapalab.';
COMMENT ON COLUMN delitos_fiscalia_robo_motocicleta.fid IS 'Identificador secuencial de la fila.';
COMMENT ON COLUMN delitos_fiscalia_robo_motocicleta.fecha IS 'Fecha de la denuncia.';
COMMENT ON COLUMN delitos_fiscalia_robo_motocicleta.entidad IS 'Entidad federativa (constante: Jalisco).';
COMMENT ON COLUMN delitos_fiscalia_robo_motocicleta.municipio IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN delitos_fiscalia_robo_motocicleta.x_6368 IS 'Coordenada X proyectada en EPSG:6368 (metros).';
COMMENT ON COLUMN delitos_fiscalia_robo_motocicleta.y_6368 IS 'Coordenada Y proyectada en EPSG:6368 (metros).';
COMMENT ON COLUMN delitos_fiscalia_robo_motocicleta.bien_juridico IS 'Bien jurídico afectado por el delito.';
COMMENT ON COLUMN delitos_fiscalia_robo_motocicleta.delito IS 'Tipo de delito.';
COMMENT ON COLUMN delitos_fiscalia_robo_motocicleta.modalidad IS 'Modalidad de violencia: Con violencia / Sin violencia.';
COMMENT ON COLUMN delitos_fiscalia_robo_motocicleta.dia_semana IS 'Día de la semana de la denuncia (en español, minúsculas).';
COMMENT ON COLUMN delitos_fiscalia_robo_motocicleta.rango_hora IS 'Franja horaria: Madrugada 00-06 h, Mañana 06-12 h, Tarde 12-18 h, Noche 18-24 h, No disponible.';
COMMENT ON COLUMN delitos_fiscalia_robo_motocicleta.geom IS 'Geometría del punto del delito (EPSG:6368).';

-- =============================================================================
-- Vista materializada: delitos_fiscalia_violacion
-- =============================================================================
COMMENT ON MATERIALIZED VIEW delitos_fiscalia_violacion IS
    'Delitos de fiscalía del tipo: Violación. Solo registros con coordenadas válidas; consumida en vivo por mapalab.';
COMMENT ON COLUMN delitos_fiscalia_violacion.fid IS 'Identificador secuencial de la fila.';
COMMENT ON COLUMN delitos_fiscalia_violacion.fecha IS 'Fecha de la denuncia.';
COMMENT ON COLUMN delitos_fiscalia_violacion.entidad IS 'Entidad federativa (constante: Jalisco).';
COMMENT ON COLUMN delitos_fiscalia_violacion.municipio IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN delitos_fiscalia_violacion.x_6368 IS 'Coordenada X proyectada en EPSG:6368 (metros).';
COMMENT ON COLUMN delitos_fiscalia_violacion.y_6368 IS 'Coordenada Y proyectada en EPSG:6368 (metros).';
COMMENT ON COLUMN delitos_fiscalia_violacion.bien_juridico IS 'Bien jurídico afectado por el delito.';
COMMENT ON COLUMN delitos_fiscalia_violacion.delito IS 'Tipo de delito.';
COMMENT ON COLUMN delitos_fiscalia_violacion.dia_semana IS 'Día de la semana de la denuncia (en español, minúsculas).';
COMMENT ON COLUMN delitos_fiscalia_violacion.rango_hora IS 'Franja horaria: Madrugada 00-06 h, Mañana 06-12 h, Tarde 12-18 h, Noche 18-24 h, No disponible.';
COMMENT ON COLUMN delitos_fiscalia_violacion.geom IS 'Geometría del punto del delito (EPSG:6368).';

-- =============================================================================
-- Vista materializada: delitos_fiscalia_violencia_familiar
-- =============================================================================
COMMENT ON MATERIALIZED VIEW delitos_fiscalia_violencia_familiar IS
    'Delitos de fiscalía del tipo: Violencia familiar. Solo registros con coordenadas válidas; consumida en vivo por mapalab.';
COMMENT ON COLUMN delitos_fiscalia_violencia_familiar.fid IS 'Identificador secuencial de la fila.';
COMMENT ON COLUMN delitos_fiscalia_violencia_familiar.fecha IS 'Fecha de la denuncia.';
COMMENT ON COLUMN delitos_fiscalia_violencia_familiar.entidad IS 'Entidad federativa (constante: Jalisco).';
COMMENT ON COLUMN delitos_fiscalia_violencia_familiar.municipio IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN delitos_fiscalia_violencia_familiar.x_6368 IS 'Coordenada X proyectada en EPSG:6368 (metros).';
COMMENT ON COLUMN delitos_fiscalia_violencia_familiar.y_6368 IS 'Coordenada Y proyectada en EPSG:6368 (metros).';
COMMENT ON COLUMN delitos_fiscalia_violencia_familiar.bien_juridico IS 'Bien jurídico afectado por el delito.';
COMMENT ON COLUMN delitos_fiscalia_violencia_familiar.delito IS 'Tipo de delito.';
COMMENT ON COLUMN delitos_fiscalia_violencia_familiar.dia_semana IS 'Día de la semana de la denuncia (en español, minúsculas).';
COMMENT ON COLUMN delitos_fiscalia_violencia_familiar.rango_hora IS 'Franja horaria: Madrugada 00-06 h, Mañana 06-12 h, Tarde 12-18 h, Noche 18-24 h, No disponible.';
COMMENT ON COLUMN delitos_fiscalia_violencia_familiar.geom IS 'Geometría del punto del delito (EPSG:6368).';
