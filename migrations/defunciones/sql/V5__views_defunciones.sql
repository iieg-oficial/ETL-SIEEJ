-- Vistas analíticas del pipeline defunciones.

CREATE VIEW vw_defunciones AS
SELECT
    f.id,
    f.entidad_registro,
    f.municipio_regis,
    c0.descripcion AS tamanio_loc_regis,
    f.localidad_regis,
    c1.descripcion AS tamanio_loc_resid,
    f.localidad_resid,
    c2.descripcion AS tamanio_loc_ocurr,
    f.localidad_ocurr,
    c3.descripcion AS causa_defuncion,
    c4.descripcion AS cod_adicional,
    c5.descripcion AS lista_mex,
    c6.descripcion AS sexo,
    f.entidad_nac,
    c7.descripcion AS afromex,
    c8.descripcion AS cond_indigena,
    c9.descripcion AS lengua_indigena,
    c10.descripcion AS lenguas,
    c11.descripcion AS nacionalid,
    c12.descripcion AS origen,
    c13.nombre_edad AS edad,
    c14.descripcion AS edad_gestacional,
    c15.descripcion AS gramos,
    c16.descripcion AS dia_ocurr,
    c17.descripcion AS mes_ocurr,
    c18.descripcion AS anio_ocurr,
    c19.descripcion AS dia_registro,
    c20.descripcion AS mes_registro,
    c21.descripcion AS anio_registro,
    c22.descripcion AS dia_nacimiento,
    c23.descripcion AS mes_nacimiento,
    c24.descripcion AS anio_nacimiento,
    c25.descripcion AS condicion_act,
    c26.descripcion AS ocupacion,
    c27.descripcion AS escolaridad,
    c28.descripcion AS edo_civil,
    c29.descripcion AS tipo_defuncion,
    c30.descripcion AS ocurr_trab,
    c31.descripcion AS lugar_ocurr,
    c32.descripcion AS parentesco_agre,
    c33.descripcion AS violencia_familiar,
    c34.descripcion AS asist_medica,
    c35.descripcion AS cirugia,
    c36.descripcion AS accidental_vio,
    c37.descripcion AS necropsia,
    c38.descripcion AS uso_necropsia,
    c39.descripcion AS encefalica,
    c40.descripcion AS donador,
    c41.descripcion AS sitio_ocur,
    c42.descripcion AS certificante,
    c43.descripcion AS derecho_hab,
    c44.descripcion AS embarazo,
    c45.descripcion AS rel_emba,
    c46.descripcion AS horas,
    c47.descripcion AS minutos,
    f.capitulo,
    f.grupo,
    cg.descripcion AS capitulo_grupo,
    c48.descripcion AS lista_cie,
    c49.descripcion AS gr_lismex,
    c50.descripcion AS area_urbana,
    c51.descripcion AS edad_agrupada,
    c52.descripcion AS complicaron,
    c53.descripcion AS dia_certificacion,
    c54.descripcion AS mes_certificacion,
    c55.descripcion AS anio_certificacion,
    c56.descripcion AS maternas,
    f.entidad_ocules,
    f.municipio_ocules,
    f.localidad_ocules,
    c57.descripcion AS razon_m,
    f.dis_re_oax,
    mr.nomgeo AS municipio_resid,
    mr.cvegeo AS cvegeo_resid,
    mr.nom_ent AS entidad_resid,
    mo.nomgeo AS municipio_ocurr,
    mo.cvegeo AS cvegeo_ocurr,
    mo.nom_ent AS entidad_ocurr,
    ed.anio AS edicion,
    f.fecha_actualizacion
FROM stg_defunciones f
LEFT JOIN cat_tamano_localidad c0 ON c0.id = f.tamanio_loc_regis_id
LEFT JOIN cat_tamano_localidad c1 ON c1.id = f.tamanio_loc_resid_id
LEFT JOIN cat_tamano_localidad c2 ON c2.id = f.tamanio_loc_ocurr_id
LEFT JOIN cat_causa_defuncion c3 ON c3.id = f.causa_defuncion_id
LEFT JOIN cat_codigo_adicional c4 ON c4.id = f.cod_adicional_id
LEFT JOIN cat_lista_mexicana c5 ON c5.id = f.lista_mex_id
LEFT JOIN cat_sexo c6 ON c6.id = f.sexo_id
LEFT JOIN cat_afromexicano c7 ON c7.id = f.afromex_id
LEFT JOIN cat_condicion_indigena c8 ON c8.id = f.cond_indigena_id
LEFT JOIN cat_lengua_indigena c9 ON c9.id = f.lengua_indigena_id
LEFT JOIN cat_lenguas c10 ON c10.id = f.lenguas_id
LEFT JOIN cat_nacionalidad c11 ON c11.id = f.nacionalid_id
LEFT JOIN cat_origen c12 ON c12.id = f.origen_id
LEFT JOIN cat_edad c13 ON c13.id = f.edad_id
LEFT JOIN cat_edad_gestacional c14 ON c14.id = f.edad_gestacional_id
LEFT JOIN cat_peso_producto c15 ON c15.id = f.gramos_id
LEFT JOIN cat_dia c16 ON c16.id = f.dia_ocurr_id
LEFT JOIN cat_mes c17 ON c17.id = f.mes_ocurr_id
LEFT JOIN cat_anio c18 ON c18.id = f.anio_ocurr_id
LEFT JOIN cat_dia c19 ON c19.id = f.dia_registro_id
LEFT JOIN cat_mes c20 ON c20.id = f.mes_registro_id
LEFT JOIN cat_anio c21 ON c21.id = f.anio_registro_id
LEFT JOIN cat_dia c22 ON c22.id = f.dia_nacimiento_id
LEFT JOIN cat_mes c23 ON c23.id = f.mes_nacimiento_id
LEFT JOIN cat_anio c24 ON c24.id = f.anio_nacimiento_id
LEFT JOIN cat_condicion_actividad c25 ON c25.id = f.condicion_act_id
LEFT JOIN cat_ocupacion c26 ON c26.id = f.ocupacion_id
LEFT JOIN cat_escolaridad c27 ON c27.id = f.escolaridad_id
LEFT JOIN cat_estado_civil c28 ON c28.id = f.edo_civil_id
LEFT JOIN cat_presunta_defuncion_violenta c29 ON c29.id = f.tipo_defuncion_id
LEFT JOIN cat_ocurrio_trabajo c30 ON c30.id = f.ocurr_trab_id
LEFT JOIN cat_lugar_ocurrencia c31 ON c31.id = f.lugar_ocurr_id
LEFT JOIN cat_parentesco_agresor c32 ON c32.id = f.parentesco_agre_id
LEFT JOIN cat_violencia_familiar c33 ON c33.id = f.violencia_familiar_id
LEFT JOIN cat_asistencia_medica c34 ON c34.id = f.asist_medica_id
LEFT JOIN cat_cirugia c35 ON c35.id = f.cirugia_id
LEFT JOIN cat_accidental_violenta c36 ON c36.id = f.accidental_vio_id
LEFT JOIN cat_necropsia c37 ON c37.id = f.necropsia_id
LEFT JOIN cat_uso_necropsia c38 ON c38.id = f.uso_necropsia_id
LEFT JOIN cat_muerte_encefalica c39 ON c39.id = f.encefalica_id
LEFT JOIN cat_donador c40 ON c40.id = f.donador_id
LEFT JOIN cat_sitio_ocurrencia c41 ON c41.id = f.sitio_ocur_id
LEFT JOIN cat_certificante c42 ON c42.id = f.certificante_id
LEFT JOIN cat_derecho_habiencia c43 ON c43.id = f.derecho_hab_id
LEFT JOIN cat_condicion_embarazo c44 ON c44.id = f.embarazo_id
LEFT JOIN cat_relacion_con_embarazo c45 ON c45.id = f.rel_emba_id
LEFT JOIN cat_hora c46 ON c46.id = f.horas_id
LEFT JOIN cat_minuto c47 ON c47.id = f.minutos_id
LEFT JOIN cat_capitulo_grupo cg ON cg.id = f.capitulo_grupo_id
LEFT JOIN cat_lista_cie c48 ON c48.id = f.lista_cie_id
LEFT JOIN cat_grupo_lista_mexicana c49 ON c49.id = f.gr_lismex_id
LEFT JOIN cat_area_urbana_rural c50 ON c50.id = f.area_urbana_id
LEFT JOIN cat_edad_agrupada c51 ON c51.id = f.edad_agrupada_id
LEFT JOIN cat_complicaron_embarazo c52 ON c52.id = f.complicaron_id
LEFT JOIN cat_dia c53 ON c53.id = f.dia_certificacion_id
LEFT JOIN cat_mes c54 ON c54.id = f.mes_certificacion_id
LEFT JOIN cat_anio c55 ON c55.id = f.anio_certificacion_id
LEFT JOIN cat_causa_defuncion c56 ON c56.id = f.maternas_id
LEFT JOIN cat_razon_materna c57 ON c57.id = f.razon_m_id
LEFT JOIN cvegeo_municipalities mr ON mr.id = f.municipio_resid_id
LEFT JOIN cvegeo_municipalities mo ON mo.id = f.municipio_ocurr_id
LEFT JOIN cat_edicion ed ON ed.id = f.edicion_id;

COMMENT ON VIEW vw_defunciones IS 'Defunciones de residentes de Jalisco con todos los catálogos resueltos a su descripción y los municipios de residencia/ocurrencia resueltos contra cvegeo.';
COMMENT ON COLUMN vw_defunciones.id IS 'Identificador único de la fila.';
COMMENT ON COLUMN vw_defunciones.entidad_registro IS 'Entidad de registro';
COMMENT ON COLUMN vw_defunciones.municipio_regis IS 'Municipio o demarcación territorial de registro';
COMMENT ON COLUMN vw_defunciones.tamanio_loc_regis IS 'Tamaño de localidad de registro';
COMMENT ON COLUMN vw_defunciones.localidad_regis IS 'Localidad de registro';
COMMENT ON COLUMN vw_defunciones.tamanio_loc_resid IS 'Tamaño de localidad de residencia habitual del (la) fallecido (a)';
COMMENT ON COLUMN vw_defunciones.localidad_resid IS 'Localidad de residencia habitual del (la) fallecido (a)';
COMMENT ON COLUMN vw_defunciones.tamanio_loc_ocurr IS 'Tamaño de localidad de ocurrencia';
COMMENT ON COLUMN vw_defunciones.localidad_ocurr IS 'Localidad de ocurrencia';
COMMENT ON COLUMN vw_defunciones.causa_defuncion IS 'Causa de la defunción (lista detallada)';
COMMENT ON COLUMN vw_defunciones.cod_adicional IS 'Código adicional CIE';
COMMENT ON COLUMN vw_defunciones.lista_mex IS 'Causa de la defunción (lista mexicana)';
COMMENT ON COLUMN vw_defunciones.sexo IS 'Sexo del (la) fallecido (a)';
COMMENT ON COLUMN vw_defunciones.entidad_nac IS 'Lugar de nacimiento';
COMMENT ON COLUMN vw_defunciones.afromex IS 'Condición de autoadscripción como persona afromexicana';
COMMENT ON COLUMN vw_defunciones.cond_indigena IS 'Condición de autoadscripción como persona indígena';
COMMENT ON COLUMN vw_defunciones.lengua_indigena IS 'Condición de habla lengua indígena del (la) fallecido (a)';
COMMENT ON COLUMN vw_defunciones.lenguas IS 'Clave de la lengua indígena';
COMMENT ON COLUMN vw_defunciones.nacionalid IS 'Nacionalidad del (la) fallecido (a)';
COMMENT ON COLUMN vw_defunciones.origen IS 'Origen específico (estado si mexicano, país si extranjero).';
COMMENT ON COLUMN vw_defunciones.edad IS 'Edad del (la) fallecido (a)';
COMMENT ON COLUMN vw_defunciones.edad_gestacional IS 'Semanas de gestación de las personas fallecidas';
COMMENT ON COLUMN vw_defunciones.gramos IS 'Peso en gramos de las personas fallecidas con menos de 28 días de edad';
COMMENT ON COLUMN vw_defunciones.dia_ocurr IS 'Día de ocurrencia';
COMMENT ON COLUMN vw_defunciones.mes_ocurr IS 'Mes de ocurrencia';
COMMENT ON COLUMN vw_defunciones.anio_ocurr IS 'Año de ocurrencia';
COMMENT ON COLUMN vw_defunciones.dia_registro IS 'Día de registro';
COMMENT ON COLUMN vw_defunciones.mes_registro IS 'Mes de registro';
COMMENT ON COLUMN vw_defunciones.anio_registro IS 'Año de registro';
COMMENT ON COLUMN vw_defunciones.dia_nacimiento IS 'Día de nacimiento del (la) fallecido (a)';
COMMENT ON COLUMN vw_defunciones.mes_nacimiento IS 'Mes de nacimiento del (la) fallecido (a)';
COMMENT ON COLUMN vw_defunciones.anio_nacimiento IS 'Año de nacimiento del (la) fallecido (a)';
COMMENT ON COLUMN vw_defunciones.condicion_act IS 'Condición de actividad económica del (la) fallecido (a)';
COMMENT ON COLUMN vw_defunciones.ocupacion IS 'Ocupación del (la) fallecido (a)';
COMMENT ON COLUMN vw_defunciones.escolaridad IS 'Nivel de escolaridad del (la) fallecido (a) (escolaridad)';
COMMENT ON COLUMN vw_defunciones.edo_civil IS 'Estado conyugal (civil) del (la) fallecido (a)';
COMMENT ON COLUMN vw_defunciones.tipo_defuncion IS 'Tipo de defunción (presunto)';
COMMENT ON COLUMN vw_defunciones.ocurr_trab IS 'Ocurrió en el desempeño de su trabajo';
COMMENT ON COLUMN vw_defunciones.lugar_ocurr IS 'Sitio de ocurrencia de la lesión';
COMMENT ON COLUMN vw_defunciones.parentesco_agre IS 'Parentesco del presunto agresor';
COMMENT ON COLUMN vw_defunciones.violencia_familiar IS 'Violencia familiar';
COMMENT ON COLUMN vw_defunciones.asist_medica IS 'Condición de atención médica';
COMMENT ON COLUMN vw_defunciones.cirugia IS 'Condición de cirugía';
COMMENT ON COLUMN vw_defunciones.accidental_vio IS 'La muerte fue accidental o violenta';
COMMENT ON COLUMN vw_defunciones.necropsia IS 'Condición de necropsia';
COMMENT ON COLUMN vw_defunciones.uso_necropsia IS 'Condición de uso de la necropsia';
COMMENT ON COLUMN vw_defunciones.encefalica IS 'Condición de muerte encefálica';
COMMENT ON COLUMN vw_defunciones.donador IS 'Condición de donador(a) de órganos';
COMMENT ON COLUMN vw_defunciones.sitio_ocur IS 'Sitio de ocurrencia de la defunción';
COMMENT ON COLUMN vw_defunciones.certificante IS 'Persona que certificó la defunción';
COMMENT ON COLUMN vw_defunciones.derecho_hab IS 'Afiliación a los servicios de salud (derechohabiencia) del (la) fallecido (a)';
COMMENT ON COLUMN vw_defunciones.embarazo IS 'Condición de embarazo';
COMMENT ON COLUMN vw_defunciones.rel_emba IS 'Causas relacionadas con el embarazo';
COMMENT ON COLUMN vw_defunciones.horas IS 'Hora de la defunción';
COMMENT ON COLUMN vw_defunciones.minutos IS 'Minuto de la defunción';
COMMENT ON COLUMN vw_defunciones.capitulo IS 'Causas detalladas CIE (capítulo)';
COMMENT ON COLUMN vw_defunciones.grupo IS 'Causas detalladas CIE (grupo)';
COMMENT ON COLUMN vw_defunciones.capitulo_grupo IS 'Clasificación CIE-10 capítulo/grupo';
COMMENT ON COLUMN vw_defunciones.lista_cie IS 'Lista de tabulación 1 para mortalidad de la CIE';
COMMENT ON COLUMN vw_defunciones.gr_lismex IS 'Lista mexicana de enfermedades (grupo)';
COMMENT ON COLUMN vw_defunciones.area_urbana IS 'Área urbana-rural de residencia habitual del (la) fallecido (a)';
COMMENT ON COLUMN vw_defunciones.edad_agrupada IS 'Edad (agrupada) del (la) fallecido (a)';
COMMENT ON COLUMN vw_defunciones.complicaron IS 'Complicaron el embarazo';
COMMENT ON COLUMN vw_defunciones.dia_certificacion IS 'Día de certificación';
COMMENT ON COLUMN vw_defunciones.mes_certificacion IS 'Mes de certificación';
COMMENT ON COLUMN vw_defunciones.anio_certificacion IS 'Año de certificación';
COMMENT ON COLUMN vw_defunciones.maternas IS 'Defunciones maternas totales';
COMMENT ON COLUMN vw_defunciones.entidad_ocules IS 'Entidad de ocurrencia de la lesión';
COMMENT ON COLUMN vw_defunciones.municipio_ocules IS 'Municipio o demarcación territorial de ocurrencia de la lesión';
COMMENT ON COLUMN vw_defunciones.localidad_ocules IS 'Localidad de ocurrencia de la lesión';
COMMENT ON COLUMN vw_defunciones.razon_m IS 'Defunciones para calcular la razón de la mortalidad materna';
COMMENT ON COLUMN vw_defunciones.dis_re_oax IS 'Distritos de registro de Oaxaca';
COMMENT ON COLUMN vw_defunciones.municipio_resid IS 'Municipio de residencia habitual (nombre)';
COMMENT ON COLUMN vw_defunciones.cvegeo_resid IS 'Clave geoestadística (cvegeo) del municipio de residencia';
COMMENT ON COLUMN vw_defunciones.entidad_resid IS 'Entidad de residencia habitual (nombre)';
COMMENT ON COLUMN vw_defunciones.municipio_ocurr IS 'Municipio de ocurrencia (nombre)';
COMMENT ON COLUMN vw_defunciones.cvegeo_ocurr IS 'Clave geoestadística (cvegeo) del municipio de ocurrencia';
COMMENT ON COLUMN vw_defunciones.entidad_ocurr IS 'Entidad de ocurrencia (nombre)';
COMMENT ON COLUMN vw_defunciones.edicion IS 'Año de la edición DGIS de origen';
COMMENT ON COLUMN vw_defunciones.fecha_actualizacion IS 'Fecha de carga ETL.';

-- Principales causas de muerte por municipio de residencia, año y sexo (lista CIE corta).
CREATE VIEW vw_defunciones_principales_causas AS
SELECT
    cvegeo_resid AS cvegeo,
    municipio_resid AS municipio,
    anio_registro,
    lista_cie,
    sexo,
    COUNT(*) AS defunciones
FROM vw_defunciones
GROUP BY cvegeo_resid, municipio_resid, anio_registro, lista_cie, sexo;

COMMENT ON VIEW vw_defunciones_principales_causas IS 'Conteo de defunciones por municipio de residencia, año, causa (lista de tabulación CIE) y sexo, para tablas de principales causas de muerte.';
COMMENT ON COLUMN vw_defunciones_principales_causas.cvegeo IS 'Clave geoestadística (cvegeo) del municipio de residencia.';
COMMENT ON COLUMN vw_defunciones_principales_causas.municipio IS 'Municipio de residencia habitual.';
COMMENT ON COLUMN vw_defunciones_principales_causas.anio_registro IS 'Año de registro de la defunción.';
COMMENT ON COLUMN vw_defunciones_principales_causas.lista_cie IS 'Causa de muerte según la lista de tabulación 1 de la CIE.';
COMMENT ON COLUMN vw_defunciones_principales_causas.sexo IS 'Sexo del fallecido.';
COMMENT ON COLUMN vw_defunciones_principales_causas.defunciones IS 'Número de defunciones del grupo.';

-- Defunciones por municipio de residencia, año, sexo y edad agrupada (para tasas y mapas).
CREATE VIEW vw_defunciones_municipio AS
SELECT
    cvegeo_resid AS cvegeo,
    municipio_resid AS municipio,
    anio_registro,
    sexo,
    edad_agrupada,
    COUNT(*) AS defunciones
FROM vw_defunciones
GROUP BY cvegeo_resid, municipio_resid, anio_registro, sexo, edad_agrupada;

COMMENT ON VIEW vw_defunciones_municipio IS 'Conteo de defunciones por municipio de residencia, año, sexo y edad agrupada, base para tasas de mortalidad y mapas.';
COMMENT ON COLUMN vw_defunciones_municipio.cvegeo IS 'Clave geoestadística (cvegeo) del municipio de residencia.';
COMMENT ON COLUMN vw_defunciones_municipio.municipio IS 'Municipio de residencia habitual.';
COMMENT ON COLUMN vw_defunciones_municipio.anio_registro IS 'Año de registro de la defunción.';
COMMENT ON COLUMN vw_defunciones_municipio.sexo IS 'Sexo del fallecido.';
COMMENT ON COLUMN vw_defunciones_municipio.edad_agrupada IS 'Grupo de edad del fallecido.';
COMMENT ON COLUMN vw_defunciones_municipio.defunciones IS 'Número de defunciones del grupo.';

-- Mortalidad materna: defunciones que contribuyen al cálculo de la razón de mortalidad materna.
CREATE VIEW vw_mortalidad_materna AS
SELECT
    mr.cvegeo AS cvegeo,
    mr.nomgeo AS municipio,
    a.descripcion AS anio_registro,
    cd.descripcion AS causa_defuncion,
    COUNT(*) AS defunciones_maternas
FROM stg_defunciones f
LEFT JOIN cvegeo_municipalities mr ON mr.id = f.municipio_resid_id
LEFT JOIN cat_anio a ON a.id = f.anio_registro_id
LEFT JOIN cat_causa_defuncion cd ON cd.id = f.causa_defuncion_id
WHERE f.razon_m_id = 1
GROUP BY mr.cvegeo, mr.nomgeo, a.descripcion, cd.descripcion;

COMMENT ON VIEW vw_mortalidad_materna IS 'Defunciones que contribuyen al cálculo de la razón de mortalidad materna (razon_m = 1), por municipio de residencia, año y causa.';
COMMENT ON COLUMN vw_mortalidad_materna.cvegeo IS 'Clave geoestadística (cvegeo) del municipio de residencia.';
COMMENT ON COLUMN vw_mortalidad_materna.municipio IS 'Municipio de residencia habitual.';
COMMENT ON COLUMN vw_mortalidad_materna.anio_registro IS 'Año de registro de la defunción.';
COMMENT ON COLUMN vw_mortalidad_materna.causa_defuncion IS 'Causa de la defunción (CIE-10, lista detallada).';
COMMENT ON COLUMN vw_mortalidad_materna.defunciones_maternas IS 'Número de defunciones maternas del grupo.';

-- Mortalidad infantil: defunciones de menores de un año.
CREATE VIEW vw_mortalidad_infantil AS
SELECT
    mr.cvegeo AS cvegeo,
    mr.nomgeo AS municipio,
    a.descripcion AS anio_registro,
    s.descripcion AS sexo,
    cd.descripcion AS causa_defuncion,
    COUNT(*) AS defunciones_infantiles
FROM stg_defunciones f
LEFT JOIN cvegeo_municipalities mr ON mr.id = f.municipio_resid_id
LEFT JOIN cat_anio a ON a.id = f.anio_registro_id
LEFT JOIN cat_sexo s ON s.id = f.sexo_id
LEFT JOIN cat_causa_defuncion cd ON cd.id = f.causa_defuncion_id
WHERE f.edad_agrupada_id = 1
GROUP BY mr.cvegeo, mr.nomgeo, a.descripcion, s.descripcion, cd.descripcion;

COMMENT ON VIEW vw_mortalidad_infantil IS 'Defunciones de menores de un año (edad_agrupada = 1), por municipio de residencia, año, sexo y causa.';
COMMENT ON COLUMN vw_mortalidad_infantil.cvegeo IS 'Clave geoestadística (cvegeo) del municipio de residencia.';
COMMENT ON COLUMN vw_mortalidad_infantil.municipio IS 'Municipio de residencia habitual.';
COMMENT ON COLUMN vw_mortalidad_infantil.anio_registro IS 'Año de registro de la defunción.';
COMMENT ON COLUMN vw_mortalidad_infantil.sexo IS 'Sexo del fallecido.';
COMMENT ON COLUMN vw_mortalidad_infantil.causa_defuncion IS 'Causa de la defunción (CIE-10, lista detallada).';
COMMENT ON COLUMN vw_mortalidad_infantil.defunciones_infantiles IS 'Número de defunciones de menores de un año del grupo.';
