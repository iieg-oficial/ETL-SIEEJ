-- Componentes de fecha conservados por separado. INEGI publica el año sin el
-- día o el mes con frecuencia, y colapsar todo en DATE perdía ese año.

ALTER TABLE stg_defunciones
	ADD COLUMN dia_ocurrencia SMALLINT,
	ADD COLUMN mes_ocurrencia SMALLINT,
	ADD COLUMN anio_ocurrencia SMALLINT,
	ADD COLUMN dia_registro SMALLINT,
	ADD COLUMN mes_registro SMALLINT,
	ADD COLUMN anio_registro SMALLINT,
	ADD COLUMN dia_nacimiento SMALLINT,
	ADD COLUMN mes_nacimiento SMALLINT,
	ADD COLUMN anio_nacimiento SMALLINT,
	ADD COLUMN dia_certificacion SMALLINT,
	ADD COLUMN mes_certificacion SMALLINT,
	ADD COLUMN anio_certificacion SMALLINT;

CREATE INDEX ix_stg_defunciones_anio_ocurrencia ON stg_defunciones (anio_ocurrencia);

COMMENT ON COLUMN stg_defunciones.dia_ocurrencia IS 'Día de ocurrencia de la defunción; nulo cuando la fuente lo trae como no especificado (99).';
COMMENT ON COLUMN stg_defunciones.mes_ocurrencia IS 'Mes de ocurrencia de la defunción; nulo cuando la fuente lo trae como no especificado (99).';
COMMENT ON COLUMN stg_defunciones.anio_ocurrencia IS 'Año de ocurrencia de la defunción; nulo cuando la fuente lo trae como no especificado (9999). Se conserva aunque falten el día o el mes.';
COMMENT ON COLUMN stg_defunciones.dia_registro IS 'Día de registro de la defunción; nulo cuando la fuente lo trae como no especificado (99).';
COMMENT ON COLUMN stg_defunciones.mes_registro IS 'Mes de registro de la defunción; nulo cuando la fuente lo trae como no especificado (99).';
COMMENT ON COLUMN stg_defunciones.anio_registro IS 'Año de registro de la defunción; nulo cuando la fuente lo trae como no especificado (9999). Se conserva aunque falten el día o el mes.';
COMMENT ON COLUMN stg_defunciones.dia_nacimiento IS 'Día de nacimiento del (la) fallecido (a); nulo cuando la fuente lo trae como no especificado (99).';
COMMENT ON COLUMN stg_defunciones.mes_nacimiento IS 'Mes de nacimiento del (la) fallecido (a); nulo cuando la fuente lo trae como no especificado (99).';
COMMENT ON COLUMN stg_defunciones.anio_nacimiento IS 'Año de nacimiento del (la) fallecido (a); nulo cuando la fuente lo trae como no especificado (9999). Se conserva aunque falten el día o el mes.';
COMMENT ON COLUMN stg_defunciones.dia_certificacion IS 'Día de certificación de la defunción; nulo cuando la fuente lo trae como no especificado (99).';
COMMENT ON COLUMN stg_defunciones.mes_certificacion IS 'Mes de certificación de la defunción; nulo cuando la fuente lo trae como no especificado (99).';
COMMENT ON COLUMN stg_defunciones.anio_certificacion IS 'Año de certificación de la defunción; nulo cuando la fuente lo trae como no especificado (9999). Se conserva aunque falten el día o el mes.';

-- Las fechas completas ya no son la única fuente de sus componentes.
COMMENT ON COLUMN stg_defunciones.fecha_ocurrencia IS 'Fecha de ocurrencia armada con dia_ocurrencia, mes_ocurrencia y anio_ocurrencia; nula si falta algún componente o la fecha no existe en el calendario.';
COMMENT ON COLUMN stg_defunciones.fecha_registro IS 'Fecha de registro armada con dia_registro, mes_registro y anio_registro; nula si falta algún componente o la fecha no existe en el calendario.';
COMMENT ON COLUMN stg_defunciones.fecha_nacimiento IS 'Fecha de nacimiento armada con dia_nacimiento, mes_nacimiento y anio_nacimiento; nula si falta algún componente o la fecha no existe en el calendario.';
COMMENT ON COLUMN stg_defunciones.fecha_certificacion IS 'Fecha de certificación armada con dia_certificacion, mes_certificacion y anio_certificacion; nula si falta algún componente o la fecha no existe en el calendario.';

-- Las vistas se recrean para exponer los componentes. `CREATE OR REPLACE` sólo
-- admite columnas nuevas al final, y a cambio conserva los COMMENT ON de V7 y
-- evita tirar la vista _jalisco, que depende de esta.
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
    c_causa_materna.descripcion AS causa_materna,
    d.dia_ocurrencia,
    d.mes_ocurrencia,
    d.anio_ocurrencia,
    d.dia_registro,
    d.mes_registro,
    d.anio_registro,
    d.dia_nacimiento,
    d.mes_nacimiento,
    d.anio_nacimiento,
    d.dia_certificacion,
    d.mes_certificacion,
    d.anio_certificacion
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

-- `v.*` se expande al crear la vista, así que no hereda columnas nuevas sola.
CREATE OR REPLACE VIEW vw_defunciones_jalisco AS
SELECT v.*
FROM vw_defunciones v
JOIN stg_defunciones d ON d.id = v.id
WHERE d.entidad_registro_id = 14 OR d.entidad_residencia_id = 14 OR d.entidad_ocurrencia_id = 14 OR d.entidad_lesion_id = 14;

COMMENT ON COLUMN vw_defunciones.dia_ocurrencia IS 'Día de ocurrencia de la defunción; nulo cuando la fuente lo trae como no especificado (99).';
COMMENT ON COLUMN vw_defunciones.mes_ocurrencia IS 'Mes de ocurrencia de la defunción; nulo cuando la fuente lo trae como no especificado (99).';
COMMENT ON COLUMN vw_defunciones.anio_ocurrencia IS 'Año de ocurrencia de la defunción; nulo cuando la fuente lo trae como no especificado (9999). Se conserva aunque falten el día o el mes.';
COMMENT ON COLUMN vw_defunciones.dia_registro IS 'Día de registro de la defunción; nulo cuando la fuente lo trae como no especificado (99).';
COMMENT ON COLUMN vw_defunciones.mes_registro IS 'Mes de registro de la defunción; nulo cuando la fuente lo trae como no especificado (99).';
COMMENT ON COLUMN vw_defunciones.anio_registro IS 'Año de registro de la defunción; nulo cuando la fuente lo trae como no especificado (9999). Se conserva aunque falten el día o el mes.';
COMMENT ON COLUMN vw_defunciones.dia_nacimiento IS 'Día de nacimiento del (la) fallecido (a); nulo cuando la fuente lo trae como no especificado (99).';
COMMENT ON COLUMN vw_defunciones.mes_nacimiento IS 'Mes de nacimiento del (la) fallecido (a); nulo cuando la fuente lo trae como no especificado (99).';
COMMENT ON COLUMN vw_defunciones.anio_nacimiento IS 'Año de nacimiento del (la) fallecido (a); nulo cuando la fuente lo trae como no especificado (9999). Se conserva aunque falten el día o el mes.';
COMMENT ON COLUMN vw_defunciones.dia_certificacion IS 'Día de certificación de la defunción; nulo cuando la fuente lo trae como no especificado (99).';
COMMENT ON COLUMN vw_defunciones.mes_certificacion IS 'Mes de certificación de la defunción; nulo cuando la fuente lo trae como no especificado (99).';
COMMENT ON COLUMN vw_defunciones.anio_certificacion IS 'Año de certificación de la defunción; nulo cuando la fuente lo trae como no especificado (9999). Se conserva aunque falten el día o el mes.';

COMMENT ON COLUMN vw_defunciones.fecha_ocurrencia IS 'Fecha de ocurrencia de la defunción armada con dia_ocurrencia, mes_ocurrencia y anio_ocurrencia; nula si falta algún componente o la fecha no existe en el calendario.';
COMMENT ON COLUMN vw_defunciones.fecha_registro IS 'Fecha de registro de la defunción armada con dia_registro, mes_registro y anio_registro; nula si falta algún componente o la fecha no existe en el calendario.';
COMMENT ON COLUMN vw_defunciones.fecha_nacimiento IS 'Fecha de nacimiento del (la) fallecido (a) armada con dia_nacimiento, mes_nacimiento y anio_nacimiento; nula si falta algún componente o la fecha no existe en el calendario.';
COMMENT ON COLUMN vw_defunciones.fecha_certificacion IS 'Fecha de certificación de la defunción armada con dia_certificacion, mes_certificacion y anio_certificacion; nula si falta algún componente o la fecha no existe en el calendario.';

COMMENT ON COLUMN vw_defunciones_jalisco.dia_ocurrencia IS 'Día de ocurrencia de la defunción; nulo cuando la fuente lo trae como no especificado (99).';
COMMENT ON COLUMN vw_defunciones_jalisco.mes_ocurrencia IS 'Mes de ocurrencia de la defunción; nulo cuando la fuente lo trae como no especificado (99).';
COMMENT ON COLUMN vw_defunciones_jalisco.anio_ocurrencia IS 'Año de ocurrencia de la defunción; nulo cuando la fuente lo trae como no especificado (9999). Se conserva aunque falten el día o el mes.';
COMMENT ON COLUMN vw_defunciones_jalisco.dia_registro IS 'Día de registro de la defunción; nulo cuando la fuente lo trae como no especificado (99).';
COMMENT ON COLUMN vw_defunciones_jalisco.mes_registro IS 'Mes de registro de la defunción; nulo cuando la fuente lo trae como no especificado (99).';
COMMENT ON COLUMN vw_defunciones_jalisco.anio_registro IS 'Año de registro de la defunción; nulo cuando la fuente lo trae como no especificado (9999). Se conserva aunque falten el día o el mes.';
COMMENT ON COLUMN vw_defunciones_jalisco.dia_nacimiento IS 'Día de nacimiento del (la) fallecido (a); nulo cuando la fuente lo trae como no especificado (99).';
COMMENT ON COLUMN vw_defunciones_jalisco.mes_nacimiento IS 'Mes de nacimiento del (la) fallecido (a); nulo cuando la fuente lo trae como no especificado (99).';
COMMENT ON COLUMN vw_defunciones_jalisco.anio_nacimiento IS 'Año de nacimiento del (la) fallecido (a); nulo cuando la fuente lo trae como no especificado (9999). Se conserva aunque falten el día o el mes.';
COMMENT ON COLUMN vw_defunciones_jalisco.dia_certificacion IS 'Día de certificación de la defunción; nulo cuando la fuente lo trae como no especificado (99).';
COMMENT ON COLUMN vw_defunciones_jalisco.mes_certificacion IS 'Mes de certificación de la defunción; nulo cuando la fuente lo trae como no especificado (99).';
COMMENT ON COLUMN vw_defunciones_jalisco.anio_certificacion IS 'Año de certificación de la defunción; nulo cuando la fuente lo trae como no especificado (9999). Se conserva aunque falten el día o el mes.';

COMMENT ON COLUMN vw_defunciones_jalisco.fecha_ocurrencia IS 'Fecha de ocurrencia de la defunción armada con dia_ocurrencia, mes_ocurrencia y anio_ocurrencia; nula si falta algún componente o la fecha no existe en el calendario.';
COMMENT ON COLUMN vw_defunciones_jalisco.fecha_registro IS 'Fecha de registro de la defunción armada con dia_registro, mes_registro y anio_registro; nula si falta algún componente o la fecha no existe en el calendario.';
COMMENT ON COLUMN vw_defunciones_jalisco.fecha_nacimiento IS 'Fecha de nacimiento del (la) fallecido (a) armada con dia_nacimiento, mes_nacimiento y anio_nacimiento; nula si falta algún componente o la fecha no existe en el calendario.';
COMMENT ON COLUMN vw_defunciones_jalisco.fecha_certificacion IS 'Fecha de certificación de la defunción armada con dia_certificacion, mes_certificacion y anio_certificacion; nula si falta algún componente o la fecha no existe en el calendario.';
