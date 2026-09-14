-- `dis_re_oax` se guardaba como entero suelto: 927 no se podía resolver contra
-- nada y el centinela 999 (registros fuera de Oaxaca) contaba como distrito.
-- Los 30 nombres ya venían en el catálogo de localidades, como filas con
-- `cve_loc` en cero, que el pipeline descartaba por no ser localidades.

CREATE TABLE cat_distrito_oaxaca (
	id SERIAL NOT NULL,
	clave INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (clave)
);

-- Las vistas se tiran y se recrean: `CREATE OR REPLACE` no puede cambiar una
-- columna existente de tipo ni de nombre. Sus COMMENT ON se reemiten abajo.
DROP VIEW vw_defunciones_jalisco;
DROP VIEW vw_defunciones;

ALTER TABLE stg_defunciones
	DROP COLUMN distrito_registro_oaxaca,
	ADD COLUMN distrito_registro_oaxaca_id INTEGER REFERENCES cat_distrito_oaxaca (id);

CREATE VIEW vw_defunciones AS
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
    c_distrito_oaxaca.clave AS distrito_registro_oaxaca_id,
    c_distrito_oaxaca.descripcion AS distrito_registro_oaxaca,
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
    LEFT JOIN cat_distrito_oaxaca c_distrito_oaxaca ON c_distrito_oaxaca.id = d.distrito_registro_oaxaca_id
    LEFT JOIN cat_cie10 c_causa_defuncion ON c_causa_defuncion.id = d.causa_defuncion_id
    LEFT JOIN cat_cie10 c_causa_materna ON c_causa_materna.id = d.causa_materna_id
    LEFT JOIN cat_capitulo_grupo cg ON cg.id = d.capitulo_grupo_id;

CREATE VIEW vw_defunciones_jalisco AS
SELECT v.*
FROM vw_defunciones v
JOIN stg_defunciones d ON d.id = v.id
WHERE d.entidad_registro_id = 14 OR d.entidad_residencia_id = 14 OR d.entidad_ocurrencia_id = 14 OR d.entidad_lesion_id = 14;

COMMENT ON TABLE cat_distrito_oaxaca IS 'Catálogo de distritos de registro de Oaxaca (901-930), publicado por INEGI dentro del catálogo de entidad, municipio y localidad.';
COMMENT ON COLUMN stg_defunciones.distrito_registro_oaxaca_id IS 'Distrito de registro de Oaxaca; nulo fuera de esa entidad, donde la fuente trae el centinela 999.';

-- Columnas que V4 y V7 dejaron sin comentar.
COMMENT ON COLUMN stg_defunciones.id IS 'Identificador único de la defunción; lo asigna el pipeline, no viene de la fuente.';
COMMENT ON COLUMN stg_defunciones.capitulo_grupo_id IS 'Capítulo y grupo de causas detalladas CIE.';
COMMENT ON COLUMN stg_defunciones.presunta_defuncion_violenta_id IS 'Presunción de defunción violenta. INEGI publica la variable como presunto hasta 2021 y como tipo_defun desde 2022.';
COMMENT ON COLUMN vw_defunciones.id IS 'Identificador único de la defunción.';
COMMENT ON COLUMN vw_defunciones.presunta_defuncion_violenta IS 'Presunción de defunción violenta.';
COMMENT ON COLUMN vw_defunciones_jalisco.id IS 'Identificador único de la defunción.';
COMMENT ON COLUMN vw_defunciones_jalisco.presunta_defuncion_violenta IS 'Presunción de defunción violenta.';
COMMENT ON COLUMN vw_defunciones.distrito_registro_oaxaca_id IS 'Distrito de registro de Oaxaca (clave).';
COMMENT ON COLUMN vw_defunciones.distrito_registro_oaxaca IS 'Distrito de registro de Oaxaca.';
COMMENT ON COLUMN vw_defunciones_jalisco.distrito_registro_oaxaca_id IS 'Distrito de registro de Oaxaca (clave).';
COMMENT ON COLUMN vw_defunciones_jalisco.distrito_registro_oaxaca IS 'Distrito de registro de Oaxaca.';

-- Reemitidos tras el DROP VIEW (V7 y V8).
COMMENT ON VIEW vw_defunciones IS 'Defunciones registradas por INEGI con los catálogos resueltos a su descripción y la geografía a su nombre oficial. Convención: X_id es la clave (código INEGI o clave del catálogo) y X la descripción.';
COMMENT ON VIEW vw_defunciones_jalisco IS 'Igual que vw_defunciones, acotada a las defunciones en que Jalisco (entidad 14) aparece en cualquiera de los cuatro ámbitos: registro, residencia, ocurrencia u ocurrencia de la lesión.';
COMMENT ON COLUMN vw_defunciones.anio_edicion IS 'Año de la edición EDR de la que proviene la fila.';
COMMENT ON COLUMN vw_defunciones.entidad_registro_id IS 'Entidad de registro (clave).';
COMMENT ON COLUMN vw_defunciones.entidad_registro IS 'Entidad de registro.';
COMMENT ON COLUMN vw_defunciones.municipio_registro_id IS 'Municipio o demarcación territorial de registro (clave).';
COMMENT ON COLUMN vw_defunciones.municipio_registro IS 'Municipio o demarcación territorial de registro.';
COMMENT ON COLUMN vw_defunciones.entidad_residencia_id IS 'Entidad de residencia habitual del (la) fallecido (a) (clave).';
COMMENT ON COLUMN vw_defunciones.entidad_residencia IS 'Entidad de residencia habitual del (la) fallecido (a).';
COMMENT ON COLUMN vw_defunciones.municipio_residencia_id IS 'Municipio o demarcación territorial de residencia habitual del (la) fallecido (a) (clave).';
COMMENT ON COLUMN vw_defunciones.municipio_residencia IS 'Municipio o demarcación territorial de residencia habitual del (la) fallecido (a).';
COMMENT ON COLUMN vw_defunciones.localidad_residencia_id IS 'Localidad de residencia habitual del (la) fallecido (a) (clave).';
COMMENT ON COLUMN vw_defunciones.localidad_residencia IS 'Localidad de residencia habitual del (la) fallecido (a).';
COMMENT ON COLUMN vw_defunciones.entidad_ocurrencia_id IS 'Entidad de ocurrencia (clave).';
COMMENT ON COLUMN vw_defunciones.entidad_ocurrencia IS 'Entidad de ocurrencia.';
COMMENT ON COLUMN vw_defunciones.municipio_ocurrencia_id IS 'Municipio o demarcación territorial de ocurrencia (clave).';
COMMENT ON COLUMN vw_defunciones.municipio_ocurrencia IS 'Municipio o demarcación territorial de ocurrencia.';
COMMENT ON COLUMN vw_defunciones.localidad_ocurrencia_id IS 'Localidad de ocurrencia (clave).';
COMMENT ON COLUMN vw_defunciones.localidad_ocurrencia IS 'Localidad de ocurrencia.';
COMMENT ON COLUMN vw_defunciones.entidad_lesion_id IS 'Entidad de ocurrencia de la lesión (clave).';
COMMENT ON COLUMN vw_defunciones.entidad_lesion IS 'Entidad de ocurrencia de la lesión.';
COMMENT ON COLUMN vw_defunciones.municipio_lesion_id IS 'Municipio o demarcación territorial de ocurrencia de la lesión (clave).';
COMMENT ON COLUMN vw_defunciones.municipio_lesion IS 'Municipio o demarcación territorial de ocurrencia de la lesión.';
COMMENT ON COLUMN vw_defunciones.localidad_lesion_id IS 'Localidad de ocurrencia de la lesión (clave).';
COMMENT ON COLUMN vw_defunciones.localidad_lesion IS 'Localidad de ocurrencia de la lesión.';
COMMENT ON COLUMN vw_defunciones.fecha_ocurrencia IS 'Fecha armada con dia_ocurr, mes_ocurr, anio_ocur de la fuente; nula si algún componente es centinela.';
COMMENT ON COLUMN vw_defunciones.fecha_registro IS 'Fecha armada con dia_regis, mes_regis, anio_regis de la fuente; nula si algún componente es centinela.';
COMMENT ON COLUMN vw_defunciones.fecha_nacimiento IS 'Fecha armada con dia_nacim, mes_nacim, anio_nacim de la fuente; nula si algún componente es centinela.';
COMMENT ON COLUMN vw_defunciones.fecha_certificacion IS 'Fecha armada con dia_cert, mes_cert, anio_cert de la fuente; nula si algún componente es centinela.';
COMMENT ON COLUMN vw_defunciones.hora_defuncion IS 'Hora de la defunción, armada con hora y minuto de la fuente.';
COMMENT ON COLUMN vw_defunciones.edad_cantidad IS 'Edad del fallecido, en la unidad que indica edad_unidad.';
COMMENT ON COLUMN vw_defunciones.edad_unidad IS 'Unidad de la edad: 1 horas, 2 días, 3 meses, 4 años.';
COMMENT ON COLUMN vw_defunciones.fecha_actualizacion IS 'Fecha en que el pipeline cargó la fila.';
COMMENT ON COLUMN vw_defunciones.capitulo IS 'Capítulo de causas detalladas CIE.';
COMMENT ON COLUMN vw_defunciones.grupo IS 'Grupo de causas detalladas CIE; nulo cuando la fila es el total del capítulo.';
COMMENT ON COLUMN vw_defunciones.capitulo_grupo IS 'Descripción del capítulo y grupo de causas detalladas CIE.';
COMMENT ON COLUMN vw_defunciones.sexo IS 'Sexo del (la) fallecido (a).';
COMMENT ON COLUMN vw_defunciones.edad_agrupada IS 'Edad (agrupada) del (la) fallecido (a).';
COMMENT ON COLUMN vw_defunciones.escolaridad IS 'Nivel de escolaridad del (la) fallecido (a) (escolaridad).';
COMMENT ON COLUMN vw_defunciones.estado_civil IS 'Estado conyugal (civil) del (la) fallecido (a).';
COMMENT ON COLUMN vw_defunciones.condicion_actividad IS 'Condición de actividad económica del (la) fallecido (a).';
COMMENT ON COLUMN vw_defunciones.nacionalidad IS 'Nacionalidad del (la) fallecido (a).';
COMMENT ON COLUMN vw_defunciones.lengua_indigena IS 'Condición de habla lengua indígena del (la) fallecido (a).';
COMMENT ON COLUMN vw_defunciones.area_urbana_rural IS 'Área urbana-rural de residencia habitual del (la) fallecido (a).';
COMMENT ON COLUMN vw_defunciones.asistencia_medica IS 'Condición de atención médica.';
COMMENT ON COLUMN vw_defunciones.necropsia IS 'Condición de necropsia.';
COMMENT ON COLUMN vw_defunciones.sitio_ocurrencia IS 'Sitio de ocurrencia de la defunción.';
COMMENT ON COLUMN vw_defunciones.lugar_ocurrencia IS 'Sitio de ocurrencia de la lesión.';
COMMENT ON COLUMN vw_defunciones.certificante IS 'Persona que certificó la defunción.';
COMMENT ON COLUMN vw_defunciones.ocurrio_trabajo IS 'Ocurrió en el desempeño de su trabajo.';
COMMENT ON COLUMN vw_defunciones.violencia_familiar IS 'Violencia familiar.';
COMMENT ON COLUMN vw_defunciones.parentesco_agresor IS 'Parentesco del presunto agresor.';
COMMENT ON COLUMN vw_defunciones.condicion_embarazo IS 'Condición de embarazo.';
COMMENT ON COLUMN vw_defunciones.relacion_embarazo IS 'Causas relacionadas con el embarazo.';
COMMENT ON COLUMN vw_defunciones.complicaron_embarazo IS 'Complicaron el embarazo.';
COMMENT ON COLUMN vw_defunciones.razon_materna IS 'Defunciones para calcular la razón de la mortalidad materna.';
COMMENT ON COLUMN vw_defunciones.lista_cie IS 'Lista de tabulación 1 para mortalidad de la CIE.';
COMMENT ON COLUMN vw_defunciones.lista_mexicana IS 'Causa de la defunción (lista mexicana).';
COMMENT ON COLUMN vw_defunciones.grupo_lista_mexicana IS 'Lista mexicana de enfermedades (grupo).';
COMMENT ON COLUMN vw_defunciones.tamanio_localidad_residencia IS 'Tamaño de localidad de residencia habitual del (la) fallecido (a).';
COMMENT ON COLUMN vw_defunciones.tamanio_localidad_ocurrencia IS 'Tamaño de localidad de ocurrencia.';
COMMENT ON COLUMN vw_defunciones.ocupacion_id IS 'Ocupación del (la) fallecido (a) (clave).';
COMMENT ON COLUMN vw_defunciones.ocupacion IS 'Ocupación del (la) fallecido (a).';
COMMENT ON COLUMN vw_defunciones.derechohabiencia_id IS 'Afiliación a los servicios de salud (derechohabiencia) del (la) fallecido (a) (clave).';
COMMENT ON COLUMN vw_defunciones.derechohabiencia IS 'Afiliación a los servicios de salud (derechohabiencia) del (la) fallecido (a).';
COMMENT ON COLUMN vw_defunciones.causa_defuncion_id IS 'Causa de la defunción (lista detallada) (clave).';
COMMENT ON COLUMN vw_defunciones.causa_defuncion IS 'Causa de la defunción (lista detallada).';
COMMENT ON COLUMN vw_defunciones.causa_materna_id IS 'Defunciones maternas totales (clave).';
COMMENT ON COLUMN vw_defunciones.causa_materna IS 'Defunciones maternas totales.';
COMMENT ON COLUMN vw_defunciones_jalisco.anio_edicion IS 'Año de la edición EDR de la que proviene la fila.';
COMMENT ON COLUMN vw_defunciones_jalisco.entidad_registro_id IS 'Entidad de registro (clave).';
COMMENT ON COLUMN vw_defunciones_jalisco.entidad_registro IS 'Entidad de registro.';
COMMENT ON COLUMN vw_defunciones_jalisco.municipio_registro_id IS 'Municipio o demarcación territorial de registro (clave).';
COMMENT ON COLUMN vw_defunciones_jalisco.municipio_registro IS 'Municipio o demarcación territorial de registro.';
COMMENT ON COLUMN vw_defunciones_jalisco.entidad_residencia_id IS 'Entidad de residencia habitual del (la) fallecido (a) (clave).';
COMMENT ON COLUMN vw_defunciones_jalisco.entidad_residencia IS 'Entidad de residencia habitual del (la) fallecido (a).';
COMMENT ON COLUMN vw_defunciones_jalisco.municipio_residencia_id IS 'Municipio o demarcación territorial de residencia habitual del (la) fallecido (a) (clave).';
COMMENT ON COLUMN vw_defunciones_jalisco.municipio_residencia IS 'Municipio o demarcación territorial de residencia habitual del (la) fallecido (a).';
COMMENT ON COLUMN vw_defunciones_jalisco.localidad_residencia_id IS 'Localidad de residencia habitual del (la) fallecido (a) (clave).';
COMMENT ON COLUMN vw_defunciones_jalisco.localidad_residencia IS 'Localidad de residencia habitual del (la) fallecido (a).';
COMMENT ON COLUMN vw_defunciones_jalisco.entidad_ocurrencia_id IS 'Entidad de ocurrencia (clave).';
COMMENT ON COLUMN vw_defunciones_jalisco.entidad_ocurrencia IS 'Entidad de ocurrencia.';
COMMENT ON COLUMN vw_defunciones_jalisco.municipio_ocurrencia_id IS 'Municipio o demarcación territorial de ocurrencia (clave).';
COMMENT ON COLUMN vw_defunciones_jalisco.municipio_ocurrencia IS 'Municipio o demarcación territorial de ocurrencia.';
COMMENT ON COLUMN vw_defunciones_jalisco.localidad_ocurrencia_id IS 'Localidad de ocurrencia (clave).';
COMMENT ON COLUMN vw_defunciones_jalisco.localidad_ocurrencia IS 'Localidad de ocurrencia.';
COMMENT ON COLUMN vw_defunciones_jalisco.entidad_lesion_id IS 'Entidad de ocurrencia de la lesión (clave).';
COMMENT ON COLUMN vw_defunciones_jalisco.entidad_lesion IS 'Entidad de ocurrencia de la lesión.';
COMMENT ON COLUMN vw_defunciones_jalisco.municipio_lesion_id IS 'Municipio o demarcación territorial de ocurrencia de la lesión (clave).';
COMMENT ON COLUMN vw_defunciones_jalisco.municipio_lesion IS 'Municipio o demarcación territorial de ocurrencia de la lesión.';
COMMENT ON COLUMN vw_defunciones_jalisco.localidad_lesion_id IS 'Localidad de ocurrencia de la lesión (clave).';
COMMENT ON COLUMN vw_defunciones_jalisco.localidad_lesion IS 'Localidad de ocurrencia de la lesión.';
COMMENT ON COLUMN vw_defunciones_jalisco.fecha_ocurrencia IS 'Fecha armada con dia_ocurr, mes_ocurr, anio_ocur de la fuente; nula si algún componente es centinela.';
COMMENT ON COLUMN vw_defunciones_jalisco.fecha_registro IS 'Fecha armada con dia_regis, mes_regis, anio_regis de la fuente; nula si algún componente es centinela.';
COMMENT ON COLUMN vw_defunciones_jalisco.fecha_nacimiento IS 'Fecha armada con dia_nacim, mes_nacim, anio_nacim de la fuente; nula si algún componente es centinela.';
COMMENT ON COLUMN vw_defunciones_jalisco.fecha_certificacion IS 'Fecha armada con dia_cert, mes_cert, anio_cert de la fuente; nula si algún componente es centinela.';
COMMENT ON COLUMN vw_defunciones_jalisco.hora_defuncion IS 'Hora de la defunción, armada con hora y minuto de la fuente.';
COMMENT ON COLUMN vw_defunciones_jalisco.edad_cantidad IS 'Edad del fallecido, en la unidad que indica edad_unidad.';
COMMENT ON COLUMN vw_defunciones_jalisco.edad_unidad IS 'Unidad de la edad: 1 horas, 2 días, 3 meses, 4 años.';
COMMENT ON COLUMN vw_defunciones_jalisco.fecha_actualizacion IS 'Fecha en que el pipeline cargó la fila.';
COMMENT ON COLUMN vw_defunciones_jalisco.capitulo IS 'Capítulo de causas detalladas CIE.';
COMMENT ON COLUMN vw_defunciones_jalisco.grupo IS 'Grupo de causas detalladas CIE; nulo cuando la fila es el total del capítulo.';
COMMENT ON COLUMN vw_defunciones_jalisco.capitulo_grupo IS 'Descripción del capítulo y grupo de causas detalladas CIE.';
COMMENT ON COLUMN vw_defunciones_jalisco.sexo IS 'Sexo del (la) fallecido (a).';
COMMENT ON COLUMN vw_defunciones_jalisco.edad_agrupada IS 'Edad (agrupada) del (la) fallecido (a).';
COMMENT ON COLUMN vw_defunciones_jalisco.escolaridad IS 'Nivel de escolaridad del (la) fallecido (a) (escolaridad).';
COMMENT ON COLUMN vw_defunciones_jalisco.estado_civil IS 'Estado conyugal (civil) del (la) fallecido (a).';
COMMENT ON COLUMN vw_defunciones_jalisco.condicion_actividad IS 'Condición de actividad económica del (la) fallecido (a).';
COMMENT ON COLUMN vw_defunciones_jalisco.nacionalidad IS 'Nacionalidad del (la) fallecido (a).';
COMMENT ON COLUMN vw_defunciones_jalisco.lengua_indigena IS 'Condición de habla lengua indígena del (la) fallecido (a).';
COMMENT ON COLUMN vw_defunciones_jalisco.area_urbana_rural IS 'Área urbana-rural de residencia habitual del (la) fallecido (a).';
COMMENT ON COLUMN vw_defunciones_jalisco.asistencia_medica IS 'Condición de atención médica.';
COMMENT ON COLUMN vw_defunciones_jalisco.necropsia IS 'Condición de necropsia.';
COMMENT ON COLUMN vw_defunciones_jalisco.sitio_ocurrencia IS 'Sitio de ocurrencia de la defunción.';
COMMENT ON COLUMN vw_defunciones_jalisco.lugar_ocurrencia IS 'Sitio de ocurrencia de la lesión.';
COMMENT ON COLUMN vw_defunciones_jalisco.certificante IS 'Persona que certificó la defunción.';
COMMENT ON COLUMN vw_defunciones_jalisco.ocurrio_trabajo IS 'Ocurrió en el desempeño de su trabajo.';
COMMENT ON COLUMN vw_defunciones_jalisco.violencia_familiar IS 'Violencia familiar.';
COMMENT ON COLUMN vw_defunciones_jalisco.parentesco_agresor IS 'Parentesco del presunto agresor.';
COMMENT ON COLUMN vw_defunciones_jalisco.condicion_embarazo IS 'Condición de embarazo.';
COMMENT ON COLUMN vw_defunciones_jalisco.relacion_embarazo IS 'Causas relacionadas con el embarazo.';
COMMENT ON COLUMN vw_defunciones_jalisco.complicaron_embarazo IS 'Complicaron el embarazo.';
COMMENT ON COLUMN vw_defunciones_jalisco.razon_materna IS 'Defunciones para calcular la razón de la mortalidad materna.';
COMMENT ON COLUMN vw_defunciones_jalisco.lista_cie IS 'Lista de tabulación 1 para mortalidad de la CIE.';
COMMENT ON COLUMN vw_defunciones_jalisco.lista_mexicana IS 'Causa de la defunción (lista mexicana).';
COMMENT ON COLUMN vw_defunciones_jalisco.grupo_lista_mexicana IS 'Lista mexicana de enfermedades (grupo).';
COMMENT ON COLUMN vw_defunciones_jalisco.tamanio_localidad_residencia IS 'Tamaño de localidad de residencia habitual del (la) fallecido (a).';
COMMENT ON COLUMN vw_defunciones_jalisco.tamanio_localidad_ocurrencia IS 'Tamaño de localidad de ocurrencia.';
COMMENT ON COLUMN vw_defunciones_jalisco.ocupacion_id IS 'Ocupación del (la) fallecido (a) (clave).';
COMMENT ON COLUMN vw_defunciones_jalisco.ocupacion IS 'Ocupación del (la) fallecido (a).';
COMMENT ON COLUMN vw_defunciones_jalisco.derechohabiencia_id IS 'Afiliación a los servicios de salud (derechohabiencia) del (la) fallecido (a) (clave).';
COMMENT ON COLUMN vw_defunciones_jalisco.derechohabiencia IS 'Afiliación a los servicios de salud (derechohabiencia) del (la) fallecido (a).';
COMMENT ON COLUMN vw_defunciones_jalisco.causa_defuncion_id IS 'Causa de la defunción (lista detallada) (clave).';
COMMENT ON COLUMN vw_defunciones_jalisco.causa_defuncion IS 'Causa de la defunción (lista detallada).';
COMMENT ON COLUMN vw_defunciones_jalisco.causa_materna_id IS 'Defunciones maternas totales (clave).';
COMMENT ON COLUMN vw_defunciones_jalisco.causa_materna IS 'Defunciones maternas totales.';
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
