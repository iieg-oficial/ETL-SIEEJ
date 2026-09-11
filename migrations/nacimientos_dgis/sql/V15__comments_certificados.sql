-- =======================================================================
-- V15: comentarios de los catalogos SINAC y del microdato
-- =======================================================================

-- ---------------------------------------------------------------------
COMMENT ON TABLE cat_si_no IS
    'Dominio SI/NO de SINAC: sí, no, no especificado, no aplica y se ignora. Fuente: catálogos SINAC/DGIS.';
COMMENT ON COLUMN cat_si_no.id IS 'Identificador único (surrogate)';
COMMENT ON COLUMN cat_si_no.clave IS 'Clave publicada por SINAC';
COMMENT ON COLUMN cat_si_no.descripcion IS 'Descripción publicada por SINAC';

-- ---------------------------------------------------------------------
COMMENT ON TABLE cat_sexo IS
    'Sexo del nacido vivo. Fuente: catálogos SINAC/DGIS.';
COMMENT ON COLUMN cat_sexo.id IS 'Identificador único (surrogate)';
COMMENT ON COLUMN cat_sexo.clave IS 'Clave publicada por SINAC';
COMMENT ON COLUMN cat_sexo.descripcion IS 'Descripción publicada por SINAC';

-- ---------------------------------------------------------------------
COMMENT ON TABLE cat_estado_conyugal IS
    'Situación conyugal de la madre. Fuente: catálogos SINAC/DGIS.';
COMMENT ON COLUMN cat_estado_conyugal.id IS 'Identificador único (surrogate)';
COMMENT ON COLUMN cat_estado_conyugal.clave IS 'Clave publicada por SINAC';
COMMENT ON COLUMN cat_estado_conyugal.descripcion IS 'Descripción publicada por SINAC';

-- ---------------------------------------------------------------------
COMMENT ON TABLE cat_escolaridad IS
    'Escolaridad de la madre. Fuente: catálogos SINAC/DGIS.';
COMMENT ON COLUMN cat_escolaridad.id IS 'Identificador único (surrogate)';
COMMENT ON COLUMN cat_escolaridad.clave IS 'Clave publicada por SINAC';
COMMENT ON COLUMN cat_escolaridad.descripcion IS 'Descripción publicada por SINAC';

-- ---------------------------------------------------------------------
COMMENT ON TABLE cat_afiliacion IS
    'Afiliación de la madre a los servicios de salud (derechohabiencia). Fuente: catálogos SINAC/DGIS.';
COMMENT ON COLUMN cat_afiliacion.id IS 'Identificador único (surrogate)';
COMMENT ON COLUMN cat_afiliacion.clave IS 'Clave publicada por SINAC';
COMMENT ON COLUMN cat_afiliacion.descripcion IS 'Descripción publicada por SINAC';

-- ---------------------------------------------------------------------
COMMENT ON TABLE cat_ocupacion_habitual IS
    'Ocupación habitual de la madre. Fuente: catálogos SINAC/DGIS.';
COMMENT ON COLUMN cat_ocupacion_habitual.id IS 'Identificador único (surrogate)';
COMMENT ON COLUMN cat_ocupacion_habitual.clave IS 'Clave publicada por SINAC';
COMMENT ON COLUMN cat_ocupacion_habitual.descripcion IS 'Descripción publicada por SINAC';

-- ---------------------------------------------------------------------
COMMENT ON TABLE cat_lugar_nacimiento IS
    'Lugar donde ocurrió el nacimiento. Fuente: catálogos SINAC/DGIS.';
COMMENT ON COLUMN cat_lugar_nacimiento.id IS 'Identificador único (surrogate)';
COMMENT ON COLUMN cat_lugar_nacimiento.clave IS 'Clave publicada por SINAC';
COMMENT ON COLUMN cat_lugar_nacimiento.descripcion IS 'Descripción publicada por SINAC';

-- ---------------------------------------------------------------------
COMMENT ON TABLE cat_producto_embarazo IS
    'Tipo de productos extraídos del embarazo. Fuente: catálogos SINAC/DGIS.';
COMMENT ON COLUMN cat_producto_embarazo.id IS 'Identificador único (surrogate)';
COMMENT ON COLUMN cat_producto_embarazo.clave IS 'Clave publicada por SINAC';
COMMENT ON COLUMN cat_producto_embarazo.descripcion IS 'Descripción publicada por SINAC';

-- ---------------------------------------------------------------------
COMMENT ON TABLE cat_resolucion_embarazo IS
    'Procedimiento utilizado en el nacimiento. Fuente: catálogos SINAC/DGIS.';
COMMENT ON COLUMN cat_resolucion_embarazo.id IS 'Identificador único (surrogate)';
COMMENT ON COLUMN cat_resolucion_embarazo.clave IS 'Clave publicada por SINAC';
COMMENT ON COLUMN cat_resolucion_embarazo.descripcion IS 'Descripción publicada por SINAC';

-- ---------------------------------------------------------------------
COMMENT ON TABLE cat_entidad IS
    'Entidad federativa, con los centinelas de SINAC (00, 88, 99). Fuente: catálogos SINAC/DGIS.';
COMMENT ON COLUMN cat_entidad.id IS 'Identificador único (surrogate)';
COMMENT ON COLUMN cat_entidad.clave IS 'Clave publicada por SINAC';
COMMENT ON COLUMN cat_entidad.descripcion IS 'Descripción publicada por SINAC';

-- ---------------------------------------------------------------------
COMMENT ON TABLE cat_municipio IS
    'Municipio con clave compuesta EEMMM, con los centinelas de SINAC. Fuente: catálogos SINAC/DGIS.';
COMMENT ON COLUMN cat_municipio.id IS 'Identificador único (surrogate)';
COMMENT ON COLUMN cat_municipio.clave IS 'Clave compuesta EEMMM publicada por SINAC';
COMMENT ON COLUMN cat_municipio.descripcion IS 'Descripción publicada por SINAC';

-- ---------------------------------------------------------------------
COMMENT ON TABLE cat_localidad IS
    'Localidad con clave compuesta EEMMMLLLL, con los centinelas de SINAC. Fuente: catálogos SINAC/DGIS.';
COMMENT ON COLUMN cat_localidad.id IS 'Identificador único (surrogate)';
COMMENT ON COLUMN cat_localidad.clave IS 'Clave compuesta EEMMMLLLL publicada por SINAC';
COMMENT ON COLUMN cat_localidad.descripcion IS 'Descripción publicada por SINAC';

-- ---------------------------------------------------------------------
COMMENT ON TABLE cat_diagnostico IS
    'Códigos CIE-10 de anomalía congénita, enfermedad o lesión del nacido vivo. Fuente: catálogos SINAC/DGIS.';
COMMENT ON COLUMN cat_diagnostico.id IS 'Identificador único (surrogate)';
COMMENT ON COLUMN cat_diagnostico.clave IS 'Clave CIE-10 de 3 o 4 caracteres';
COMMENT ON COLUMN cat_diagnostico.descripcion IS 'Descripción publicada por SINAC';

-- ---------------------------------------------------------------------
COMMENT ON TABLE cat_establecimiento_salud IS
    'Clave Única de Establecimientos en Salud (CLUES). Fuente: catálogos SINAC/DGIS.';
COMMENT ON COLUMN cat_establecimiento_salud.id IS 'Identificador único (surrogate)';
COMMENT ON COLUMN cat_establecimiento_salud.clave IS 'CLUES de 11 caracteres';
COMMENT ON COLUMN cat_establecimiento_salud.descripcion IS 'Descripción publicada por SINAC';

-- ---------------------------------------------------------------------
COMMENT ON TABLE stg_nacimientos_certificados IS
    'Microdato del certificado de nacimiento: una fila por nacido vivo de madre residente en Jalisco. Fuente: SINAC/DGIS.';
COMMENT ON COLUMN stg_nacimientos_certificados.id IS 'Identificador único de la fila (surrogate)';
COMMENT ON COLUMN stg_nacimientos_certificados.anio IS 'Año de nacimiento, tomado de FECHANACIMIENTO';
COMMENT ON COLUMN stg_nacimientos_certificados.fecha_nacimiento IS 'Fecha de nacimiento del nacido vivo';
COMMENT ON COLUMN stg_nacimientos_certificados.hora_nacimiento IS 'Hora de nacimiento. El centinela 99:99 de SINAC se guarda como NULL';
COMMENT ON COLUMN stg_nacimientos_certificados.cve_geo IS 'Clave geoestadística del municipio de residencia de la madre (EEMMM)';
COMMENT ON COLUMN stg_nacimientos_certificados.localidad_residencia_id IS 'Localidad de residencia de la madre, contra cat_localidad';
COMMENT ON COLUMN stg_nacimientos_certificados.edad_madre IS 'Edad de la madre al momento del nacimiento';
COMMENT ON COLUMN stg_nacimientos_certificados.edad_padre IS 'Edad del padre. Los centinelas 888 y 999 se guardan como NULL';
COMMENT ON COLUMN stg_nacimientos_certificados.se_considera_indigena_id IS 'La madre se considera indígena. Contra cat_si_no, que distingue no especificado, no aplica y se ignora en vez de colapsarlos en un solo NULL';
COMMENT ON COLUMN stg_nacimientos_certificados.habla_lengua_indigena_id IS 'La madre habla alguna lengua indígena. Contra cat_si_no, que distingue no especificado, no aplica y se ignora en vez de colapsarlos en un solo NULL';
COMMENT ON COLUMN stg_nacimientos_certificados.estado_conyugal_id IS 'Situación conyugal de la madre, contra cat_estado_conyugal';
COMMENT ON COLUMN stg_nacimientos_certificados.escolaridad_id IS 'Escolaridad de la madre, contra cat_escolaridad';
COMMENT ON COLUMN stg_nacimientos_certificados.interrumpio_estudios_id IS 'La madre interrumpió estudios por el embarazo. Contra cat_si_no, que distingue no especificado, no aplica y se ignora en vez de colapsarlos en un solo NULL';
COMMENT ON COLUMN stg_nacimientos_certificados.ocupacion_habitual_id IS 'Ocupación habitual de la madre, contra cat_ocupacion_habitual';
COMMENT ON COLUMN stg_nacimientos_certificados.trabaja_actualmente_id IS 'La madre trabaja actualmente. Contra cat_si_no, que distingue no especificado, no aplica y se ignora en vez de colapsarlos en un solo NULL';
COMMENT ON COLUMN stg_nacimientos_certificados.afiliacion_id IS 'Afiliación a servicios de salud, contra cat_afiliacion';
COMMENT ON COLUMN stg_nacimientos_certificados.numero_embarazos IS 'Embarazos de la madre incluyendo el actual. El centinela 99 se guarda como NULL';
COMMENT ON COLUMN stg_nacimientos_certificados.atencion_prenatal_id IS 'La madre recibió atención prenatal. Contra cat_si_no, que distingue no especificado, no aplica y se ignora en vez de colapsarlos en un solo NULL';
COMMENT ON COLUMN stg_nacimientos_certificados.total_consultas IS 'Consultas otorgadas durante el embarazo. El centinela 99 se guarda como NULL';
COMMENT ON COLUMN stg_nacimientos_certificados.sobrevivio_parto_id IS 'La madre sobrevivió al parto. Contra cat_si_no, que distingue no especificado, no aplica y se ignora en vez de colapsarlos en un solo NULL';
COMMENT ON COLUMN stg_nacimientos_certificados.sexo_id IS 'Sexo del nacido vivo, contra cat_sexo';
COMMENT ON COLUMN stg_nacimientos_certificados.edad_gestacional IS 'Semanas de gestación. El centinela 99 se guarda como NULL';
COMMENT ON COLUMN stg_nacimientos_certificados.talla IS 'Talla en centímetros. El centinela 99 se guarda como NULL';
COMMENT ON COLUMN stg_nacimientos_certificados.peso IS 'Peso en gramos. El centinela 9999 se guarda como NULL';
COMMENT ON COLUMN stg_nacimientos_certificados.producto_embarazo_id IS 'Tipo de producto, contra cat_producto_embarazo';
COMMENT ON COLUMN stg_nacimientos_certificados.orden_producto IS 'Número de producto según el orden de extracción del evento';
COMMENT ON COLUMN stg_nacimientos_certificados.total_productos IS 'Total de productos extraídos del evento';
COMMENT ON COLUMN stg_nacimientos_certificados.diagnostico_1_id IS 'Primera anomalía congénita CIE-10. El código 0000 (ninguna aparente) se guarda como NULL';
COMMENT ON COLUMN stg_nacimientos_certificados.diagnostico_2_id IS 'Segunda anomalía congénita CIE-10. Mismo criterio que diagnostico_1_id';
COMMENT ON COLUMN stg_nacimientos_certificados.lugar_nacimiento_id IS 'Lugar donde ocurrió el nacimiento, contra cat_lugar_nacimiento';
COMMENT ON COLUMN stg_nacimientos_certificados.establecimiento_salud_id IS 'CLUES del sitio de atención del parto, contra cat_establecimiento_salud';
COMMENT ON COLUMN stg_nacimientos_certificados.tiempo_traslado_minutos IS 'Tiempo de traslado del hogar al sitio de atención del parto, en minutos';
COMMENT ON COLUMN stg_nacimientos_certificados.resolucion_embarazo_id IS 'Procedimiento del nacimiento, contra cat_resolucion_embarazo';
COMMENT ON COLUMN stg_nacimientos_certificados.entidad_parto_id IS 'Entidad federativa de atención del parto, contra cat_entidad';
COMMENT ON COLUMN stg_nacimientos_certificados.municipio_parto_id IS 'Municipio de atención del parto, contra cat_municipio';
COMMENT ON COLUMN stg_nacimientos_certificados.localidad_parto_id IS 'Localidad de atención del parto, contra cat_localidad';
COMMENT ON COLUMN stg_nacimientos_certificados.fecha_actualizacion IS 'Fecha en que el pipeline transformó la fila';

-- ---------------------------------------------------------------------
COMMENT ON VIEW vw_nacimientos_certificados IS
    'Microdato del certificado de nacimiento con todos los catálogos resueltos a texto.';
COMMENT ON COLUMN vw_nacimientos_certificados.id IS 'Identificador único de la fila (surrogate)';
COMMENT ON COLUMN vw_nacimientos_certificados.anio IS 'Año de nacimiento';
COMMENT ON COLUMN vw_nacimientos_certificados.fecha_nacimiento IS 'Fecha de nacimiento del nacido vivo';
COMMENT ON COLUMN vw_nacimientos_certificados.hora_nacimiento IS 'Hora de nacimiento';
COMMENT ON COLUMN vw_nacimientos_certificados.cve_geo IS 'Clave geoestadística del municipio de residencia de la madre (EEMMM)';
COMMENT ON COLUMN vw_nacimientos_certificados.municipio_residencia IS 'Nombre del municipio de residencia de la madre';
COMMENT ON COLUMN vw_nacimientos_certificados.entidad_residencia IS 'Nombre de la entidad de residencia de la madre';
COMMENT ON COLUMN vw_nacimientos_certificados.localidad_residencia IS 'Nombre de la localidad de residencia de la madre';
COMMENT ON COLUMN vw_nacimientos_certificados.edad_madre IS 'Edad de la madre al momento del nacimiento';
COMMENT ON COLUMN vw_nacimientos_certificados.edad_padre IS 'Edad del padre';
COMMENT ON COLUMN vw_nacimientos_certificados.se_considera_indigena IS 'La madre se considera indígena';
COMMENT ON COLUMN vw_nacimientos_certificados.habla_lengua_indigena IS 'La madre habla alguna lengua indígena';
COMMENT ON COLUMN vw_nacimientos_certificados.estado_conyugal IS 'Situación conyugal de la madre';
COMMENT ON COLUMN vw_nacimientos_certificados.escolaridad IS 'Escolaridad de la madre';
COMMENT ON COLUMN vw_nacimientos_certificados.interrumpio_estudios IS 'La madre interrumpió estudios por el embarazo';
COMMENT ON COLUMN vw_nacimientos_certificados.ocupacion_habitual IS 'Ocupación habitual de la madre';
COMMENT ON COLUMN vw_nacimientos_certificados.trabaja_actualmente IS 'La madre trabaja actualmente';
COMMENT ON COLUMN vw_nacimientos_certificados.afiliacion IS 'Afiliación de la madre a los servicios de salud';
COMMENT ON COLUMN vw_nacimientos_certificados.numero_embarazos IS 'Embarazos de la madre incluyendo el actual';
COMMENT ON COLUMN vw_nacimientos_certificados.atencion_prenatal IS 'La madre recibió atención prenatal';
COMMENT ON COLUMN vw_nacimientos_certificados.total_consultas IS 'Consultas otorgadas durante el embarazo';
COMMENT ON COLUMN vw_nacimientos_certificados.sobrevivio_parto IS 'La madre sobrevivió al parto';
COMMENT ON COLUMN vw_nacimientos_certificados.sexo IS 'Sexo del nacido vivo';
COMMENT ON COLUMN vw_nacimientos_certificados.edad_gestacional IS 'Semanas de gestación';
COMMENT ON COLUMN vw_nacimientos_certificados.talla IS 'Talla en centímetros';
COMMENT ON COLUMN vw_nacimientos_certificados.peso IS 'Peso en gramos';
COMMENT ON COLUMN vw_nacimientos_certificados.producto_embarazo IS 'Tipo de producto del embarazo';
COMMENT ON COLUMN vw_nacimientos_certificados.orden_producto IS 'Número de producto según el orden de extracción';
COMMENT ON COLUMN vw_nacimientos_certificados.total_productos IS 'Total de productos extraídos del evento';
COMMENT ON COLUMN vw_nacimientos_certificados.diagnostico_1_clave IS 'Clave CIE-10 de la primera anomalía congénita';
COMMENT ON COLUMN vw_nacimientos_certificados.diagnostico_1 IS 'Descripción de la primera anomalía congénita';
COMMENT ON COLUMN vw_nacimientos_certificados.diagnostico_2_clave IS 'Clave CIE-10 de la segunda anomalía congénita';
COMMENT ON COLUMN vw_nacimientos_certificados.diagnostico_2 IS 'Descripción de la segunda anomalía congénita';
COMMENT ON COLUMN vw_nacimientos_certificados.lugar_nacimiento IS 'Lugar donde ocurrió el nacimiento';
COMMENT ON COLUMN vw_nacimientos_certificados.clues IS 'CLUES del sitio de atención del parto';
COMMENT ON COLUMN vw_nacimientos_certificados.establecimiento_salud IS 'Nombre del establecimiento de atención del parto';
COMMENT ON COLUMN vw_nacimientos_certificados.tiempo_traslado_minutos IS 'Tiempo de traslado del hogar al sitio de atención del parto, en minutos';
COMMENT ON COLUMN vw_nacimientos_certificados.resolucion_embarazo IS 'Procedimiento utilizado en el nacimiento';
COMMENT ON COLUMN vw_nacimientos_certificados.entidad_parto IS 'Entidad federativa de atención del parto';
COMMENT ON COLUMN vw_nacimientos_certificados.municipio_parto IS 'Municipio de atención del parto';
COMMENT ON COLUMN vw_nacimientos_certificados.localidad_parto IS 'Localidad de atención del parto';
COMMENT ON COLUMN vw_nacimientos_certificados.fecha_actualizacion IS 'Fecha en que el pipeline transformó la fila';
