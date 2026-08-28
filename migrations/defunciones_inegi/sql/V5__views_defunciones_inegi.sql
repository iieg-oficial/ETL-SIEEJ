-- Vistas legibles. Convención: `X_id` es la clave (código INEGI o clave del
-- catálogo) y `X` la descripción. Las variantes _jalisco acotan a la entidad 14
-- en cualquiera de los cuatro ámbitos (registro, residencia, ocurrencia, lesión).

CREATE OR REPLACE VIEW vw_defunciones AS
SELECT
    d.id,
    e.anio AS anio_edicion,
    d.entidad_registro_id,
    s_registro.nom_ent AS entidad_registro,
    d.municipio_registro_id,
    m_registro.nomgeo AS municipio_registro,
    d.entidad_residencia_id,
    s_residencia.nom_ent AS entidad_residencia,
    d.municipio_residencia_id,
    m_residencia.nomgeo AS municipio_residencia,
    d.localidad_residencia_id,
    l_residencia.localidad AS localidad_residencia,
    d.entidad_ocurrencia_id,
    s_ocurrencia.nom_ent AS entidad_ocurrencia,
    d.municipio_ocurrencia_id,
    m_ocurrencia.nomgeo AS municipio_ocurrencia,
    d.localidad_ocurrencia_id,
    l_ocurrencia.localidad AS localidad_ocurrencia,
    d.entidad_lesion_id,
    s_lesion.nom_ent AS entidad_lesion,
    d.municipio_lesion_id,
    m_lesion.nomgeo AS municipio_lesion,
    d.localidad_lesion_id,
    l_lesion.localidad AS localidad_lesion,
    d.fecha_ocurrencia,
    d.fecha_registro,
    d.fecha_nacimiento,
    d.fecha_certificacion,
    d.hora_defuncion,
    d.edad_cantidad,
    d.edad_unidad,
    d.distrito_registro_oaxaca,
    d.fecha_actualizacion,
    cg.capitulo,
    cg.grupo,
    cg.descripcion AS capitulo_grupo,
    c_sexo.descripcion AS sexo,
    c_edad_agrupada.descripcion AS edad_agrupada,
    c_escolaridad.descripcion AS escolaridad,
    c_estado_civil.descripcion AS estado_civil,
    c_condicion_actividad.descripcion AS condicion_actividad,
    c_nacionalidad.descripcion AS nacionalidad,
    c_lengua_indigena.descripcion AS lengua_indigena,
    c_area_urbana_rural.descripcion AS area_urbana_rural,
    c_asistencia_medica.descripcion AS asistencia_medica,
    c_necropsia.descripcion AS necropsia,
    c_sitio_ocurrencia.descripcion AS sitio_ocurrencia,
    c_lugar_ocurrencia.descripcion AS lugar_ocurrencia,
    c_certificante.descripcion AS certificante,
    c_presunta_defuncion_violenta.descripcion AS presunta_defuncion_violenta,
    c_ocurrio_trabajo.descripcion AS ocurrio_trabajo,
    c_violencia_familiar.descripcion AS violencia_familiar,
    c_parentesco_agresor.descripcion AS parentesco_agresor,
    c_condicion_embarazo.descripcion AS condicion_embarazo,
    c_relacion_embarazo.descripcion AS relacion_embarazo,
    c_complicaron_embarazo.descripcion AS complicaron_embarazo,
    c_razon_materna.descripcion AS razon_materna,
    c_lista_cie.descripcion AS lista_cie,
    c_lista_mexicana.descripcion AS lista_mexicana,
    c_grupo_lista_mexicana.descripcion AS grupo_lista_mexicana,
    c_tamanio_localidad_residencia.descripcion AS tamanio_localidad_residencia,
    c_tamanio_localidad_ocurrencia.descripcion AS tamanio_localidad_ocurrencia,
    c_ocupacion.clave AS ocupacion_id,
    c_ocupacion.descripcion AS ocupacion,
    c_derechohabiencia.clave AS derechohabiencia_id,
    c_derechohabiencia.descripcion AS derechohabiencia,
    c_causa_defuncion.clave AS causa_defuncion_id,
    c_causa_defuncion.descripcion AS causa_defuncion,
    c_causa_materna.clave AS causa_materna_id,
    c_causa_materna.descripcion AS causa_materna
FROM stg_defunciones d
    JOIN cat_edicion e ON e.id = d.edicion_id
    LEFT JOIN cvegeo_states s_registro ON s_registro.cve_ent = d.entidad_registro_id
    LEFT JOIN cvegeo_municipalities m_registro
        ON m_registro.cve_ent = d.entidad_registro_id AND m_registro.cve_mun = d.municipio_registro_id
    LEFT JOIN cvegeo_states s_residencia ON s_residencia.cve_ent = d.entidad_residencia_id
    LEFT JOIN cvegeo_municipalities m_residencia
        ON m_residencia.cve_ent = d.entidad_residencia_id AND m_residencia.cve_mun = d.municipio_residencia_id
    LEFT JOIN cat_localidad l_residencia ON l_residencia.id = d.localidad_residencia_id
    LEFT JOIN cvegeo_states s_ocurrencia ON s_ocurrencia.cve_ent = d.entidad_ocurrencia_id
    LEFT JOIN cvegeo_municipalities m_ocurrencia
        ON m_ocurrencia.cve_ent = d.entidad_ocurrencia_id AND m_ocurrencia.cve_mun = d.municipio_ocurrencia_id
    LEFT JOIN cat_localidad l_ocurrencia ON l_ocurrencia.id = d.localidad_ocurrencia_id
    LEFT JOIN cvegeo_states s_lesion ON s_lesion.cve_ent = d.entidad_lesion_id
    LEFT JOIN cvegeo_municipalities m_lesion
        ON m_lesion.cve_ent = d.entidad_lesion_id AND m_lesion.cve_mun = d.municipio_lesion_id
    LEFT JOIN cat_localidad l_lesion ON l_lesion.id = d.localidad_lesion_id
    LEFT JOIN cat_sexo c_sexo ON c_sexo.id = d.sexo_id
    LEFT JOIN cat_edad_agrupada c_edad_agrupada ON c_edad_agrupada.id = d.edad_agrupada_id
    LEFT JOIN cat_escolaridad c_escolaridad ON c_escolaridad.id = d.escolaridad_id
    LEFT JOIN cat_estado_civil c_estado_civil ON c_estado_civil.id = d.estado_civil_id
    LEFT JOIN cat_condicion_actividad c_condicion_actividad ON c_condicion_actividad.id = d.condicion_actividad_id
    LEFT JOIN cat_nacionalidad c_nacionalidad ON c_nacionalidad.id = d.nacionalidad_id
    LEFT JOIN cat_lengua_indigena c_lengua_indigena ON c_lengua_indigena.id = d.lengua_indigena_id
    LEFT JOIN cat_area_urbana_rural c_area_urbana_rural ON c_area_urbana_rural.id = d.area_urbana_rural_id
    LEFT JOIN cat_asistencia_medica c_asistencia_medica ON c_asistencia_medica.id = d.asistencia_medica_id
    LEFT JOIN cat_necropsia c_necropsia ON c_necropsia.id = d.necropsia_id
    LEFT JOIN cat_sitio_ocurrencia c_sitio_ocurrencia ON c_sitio_ocurrencia.id = d.sitio_ocurrencia_id
    LEFT JOIN cat_lugar_ocurrencia c_lugar_ocurrencia ON c_lugar_ocurrencia.id = d.lugar_ocurrencia_id
    LEFT JOIN cat_certificante c_certificante ON c_certificante.id = d.certificante_id
    LEFT JOIN cat_presunta_defuncion_violenta c_presunta_defuncion_violenta ON c_presunta_defuncion_violenta.id = d.presunta_defuncion_violenta_id
    LEFT JOIN cat_ocurrio_trabajo c_ocurrio_trabajo ON c_ocurrio_trabajo.id = d.ocurrio_trabajo_id
    LEFT JOIN cat_violencia_familiar c_violencia_familiar ON c_violencia_familiar.id = d.violencia_familiar_id
    LEFT JOIN cat_parentesco_agresor c_parentesco_agresor ON c_parentesco_agresor.id = d.parentesco_agresor_id
    LEFT JOIN cat_condicion_embarazo c_condicion_embarazo ON c_condicion_embarazo.id = d.condicion_embarazo_id
    LEFT JOIN cat_relacion_embarazo c_relacion_embarazo ON c_relacion_embarazo.id = d.relacion_embarazo_id
    LEFT JOIN cat_complicaron_embarazo c_complicaron_embarazo ON c_complicaron_embarazo.id = d.complicaron_embarazo_id
    LEFT JOIN cat_razon_materna c_razon_materna ON c_razon_materna.id = d.razon_materna_id
    LEFT JOIN cat_lista_cie c_lista_cie ON c_lista_cie.id = d.lista_cie_id
    LEFT JOIN cat_lista_mexicana c_lista_mexicana ON c_lista_mexicana.id = d.lista_mexicana_id
    LEFT JOIN cat_grupo_lista_mexicana c_grupo_lista_mexicana ON c_grupo_lista_mexicana.id = d.grupo_lista_mexicana_id
    LEFT JOIN cat_tamanio_localidad c_tamanio_localidad_residencia ON c_tamanio_localidad_residencia.id = d.tamanio_localidad_residencia_id
    LEFT JOIN cat_tamanio_localidad c_tamanio_localidad_ocurrencia ON c_tamanio_localidad_ocurrencia.id = d.tamanio_localidad_ocurrencia_id
    LEFT JOIN cat_ocupacion c_ocupacion ON c_ocupacion.id = d.ocupacion_id
    LEFT JOIN cat_derechohabiencia c_derechohabiencia ON c_derechohabiencia.id = d.derechohabiencia_id
    LEFT JOIN cat_cie10 c_causa_defuncion ON c_causa_defuncion.id = d.causa_defuncion_id
    LEFT JOIN cat_cie10 c_causa_materna ON c_causa_materna.id = d.causa_materna_id
    LEFT JOIN cat_capitulo_grupo cg ON cg.id = d.capitulo_grupo_id;

CREATE OR REPLACE VIEW vw_defunciones_jalisco AS
SELECT v.*
FROM vw_defunciones v
JOIN stg_defunciones d ON d.id = v.id
WHERE d.entidad_registro_id = 14 OR d.entidad_residencia_id = 14 OR d.entidad_ocurrencia_id = 14 OR d.entidad_lesion_id = 14;

CREATE OR REPLACE VIEW vw_defunciones_ampliacion AS
SELECT
    a.defuncion_id,
    e.anio AS anio_edicion,
    a.entidad_nacimiento_id,
    s_nac.nom_ent AS entidad_nacimiento,
    a.pais_nacimiento_id,
    p_nac.nombre_pais AS pais_nacimiento,
    a.pais_nacionalidad_id,
    p_nal.nombre_pais AS pais_nacionalidad,
    a.localidad_registro_id,
    l_reg.localidad AS localidad_registro,
    a.semanas_gestacion,
    a.peso_gramos,
    c_tamanio_localidad_registro.descripcion AS tamanio_localidad_registro,
    c_afromexicano.descripcion AS afromexicano,
    c_condicion_indigena.descripcion AS condicion_indigena,
    c_lengua.descripcion AS lengua,
    c_cirugia.descripcion AS cirugia,
    c_accidental_violenta.descripcion AS accidental_violenta,
    c_uso_necropsia.descripcion AS uso_necropsia,
    c_muerte_encefalica.descripcion AS muerte_encefalica,
    c_donador.descripcion AS donador,
    c_codigo_adicional.clave AS codigo_adicional_id,
    c_codigo_adicional.descripcion AS codigo_adicional
FROM stg_defunciones_ampliacion a
    JOIN stg_defunciones d ON d.id = a.defuncion_id
    JOIN cat_edicion e ON e.id = d.edicion_id
    LEFT JOIN cvegeo_states s_nac ON s_nac.cve_ent = a.entidad_nacimiento_id
    LEFT JOIN cat_localidad l_reg ON l_reg.id = a.localidad_registro_id
    LEFT JOIN cat_pais p_nac ON p_nac.id = a.pais_nacimiento_id
    LEFT JOIN cat_pais p_nal ON p_nal.id = a.pais_nacionalidad_id
    LEFT JOIN cat_tamanio_localidad c_tamanio_localidad_registro ON c_tamanio_localidad_registro.id = a.tamanio_localidad_registro_id
    LEFT JOIN cat_afromexicano c_afromexicano ON c_afromexicano.id = a.afromexicano_id
    LEFT JOIN cat_condicion_indigena c_condicion_indigena ON c_condicion_indigena.id = a.condicion_indigena_id
    LEFT JOIN cat_lengua c_lengua ON c_lengua.id = a.lengua_id
    LEFT JOIN cat_cirugia c_cirugia ON c_cirugia.id = a.cirugia_id
    LEFT JOIN cat_accidental_violenta c_accidental_violenta ON c_accidental_violenta.id = a.accidental_violenta_id
    LEFT JOIN cat_uso_necropsia c_uso_necropsia ON c_uso_necropsia.id = a.uso_necropsia_id
    LEFT JOIN cat_muerte_encefalica c_muerte_encefalica ON c_muerte_encefalica.id = a.muerte_encefalica_id
    LEFT JOIN cat_donador c_donador ON c_donador.id = a.donador_id
    LEFT JOIN cat_cie10 c_codigo_adicional ON c_codigo_adicional.id = a.codigo_adicional_id;

CREATE OR REPLACE VIEW vw_defunciones_ampliacion_jalisco AS
SELECT v.*
FROM vw_defunciones_ampliacion v
JOIN stg_defunciones d ON d.id = v.defuncion_id
WHERE d.entidad_registro_id = 14 OR d.entidad_residencia_id = 14 OR d.entidad_ocurrencia_id = 14 OR d.entidad_lesion_id = 14;
