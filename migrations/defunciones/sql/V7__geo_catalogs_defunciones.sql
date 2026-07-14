-- Catálogos geográficos para resolver códigos crudos a nombres: entidad/país de nacimiento y localidades.

CREATE TABLE IF NOT EXISTS cat_entidad_pais (
	id INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id)
);

COMMENT ON TABLE cat_entidad_pais IS 'Catálogo combinado de entidades federativas mexicanas y países (fuente: paises.csv de DGIS), usado para resolver el lugar de nacimiento.';
COMMENT ON COLUMN cat_entidad_pais.id IS 'Clave DGIS: 001-032 entidades federativas, 100+ países, 888 No aplica, 998/999 sin especificar.';
COMMENT ON COLUMN cat_entidad_pais.descripcion IS 'Nombre de la entidad federativa o país.';

CREATE TABLE IF NOT EXISTS cat_localidades (
	id SERIAL NOT NULL,
	codigo INTEGER NOT NULL,
	edicion_id INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	cve_ent INTEGER NOT NULL,
	cve_mun INTEGER NOT NULL,
	cve_loc INTEGER NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT uq_localidades_edicion UNIQUE (codigo, edicion_id),
	FOREIGN KEY(edicion_id) REFERENCES cat_edicion (id)
);

COMMENT ON TABLE cat_localidades IS 'Catálogo versionado de localidades (fuente: entidad_municipio_localidad_<edicion>.csv de DGIS), incluye códigos sentinela (88/99 entidad, 999 municipio, 7777/9999 localidad).';
COMMENT ON COLUMN cat_localidades.codigo IS 'Clave geográfica de 9 dígitos: entidad (2) + municipio (3) + localidad (4).';
COMMENT ON COLUMN cat_localidades.edicion_id IS 'Edición DGIS de origen del catálogo.';
COMMENT ON COLUMN cat_localidades.descripcion IS 'Nombre de la localidad.';
COMMENT ON COLUMN cat_localidades.cve_ent IS 'Clave de entidad federativa de la localidad.';
COMMENT ON COLUMN cat_localidades.cve_mun IS 'Clave de municipio de la localidad.';
COMMENT ON COLUMN cat_localidades.cve_loc IS 'Clave de localidad.';

-- Las vistas de V5 dependen de las columnas que se reemplazan más abajo; se eliminan antes de alterar
-- la tabla y se recrean al final de esta migración.
DROP VIEW IF EXISTS vw_mortalidad_infantil;
DROP VIEW IF EXISTS vw_mortalidad_materna;
DROP VIEW IF EXISTS vw_defunciones_municipio;
DROP VIEW IF EXISTS vw_defunciones_principales_causas;
DROP VIEW IF EXISTS vw_defunciones;

ALTER TABLE stg_defunciones DROP COLUMN entidad_nac;
ALTER TABLE stg_defunciones ADD COLUMN entidad_pais_nac_id INTEGER;
ALTER TABLE stg_defunciones ADD CONSTRAINT stg_defunciones_entidad_pais_nac_id_fkey
	FOREIGN KEY(entidad_pais_nac_id) REFERENCES cat_entidad_pais (id);
COMMENT ON COLUMN stg_defunciones.entidad_pais_nac_id IS 'Lugar de nacimiento (entidad federativa o país), resuelto contra cat_entidad_pais.';

ALTER TABLE stg_defunciones DROP COLUMN localidad_regis;
ALTER TABLE stg_defunciones ADD COLUMN localidad_regis_id INTEGER;
ALTER TABLE stg_defunciones ADD CONSTRAINT stg_defunciones_localidad_regis_id_fkey
	FOREIGN KEY(localidad_regis_id) REFERENCES cat_localidades (id);
COMMENT ON COLUMN stg_defunciones.localidad_regis_id IS 'Localidad de registro, resuelta contra cat_localidades.';

ALTER TABLE stg_defunciones DROP COLUMN localidad_resid;
ALTER TABLE stg_defunciones ADD COLUMN localidad_resid_id INTEGER;
ALTER TABLE stg_defunciones ADD CONSTRAINT stg_defunciones_localidad_resid_id_fkey
	FOREIGN KEY(localidad_resid_id) REFERENCES cat_localidades (id);
COMMENT ON COLUMN stg_defunciones.localidad_resid_id IS 'Localidad de residencia habitual del (la) fallecido (a), resuelta contra cat_localidades.';

ALTER TABLE stg_defunciones DROP COLUMN localidad_ocurr;
ALTER TABLE stg_defunciones ADD COLUMN localidad_ocurr_id INTEGER;
ALTER TABLE stg_defunciones ADD CONSTRAINT stg_defunciones_localidad_ocurr_id_fkey
	FOREIGN KEY(localidad_ocurr_id) REFERENCES cat_localidades (id);
COMMENT ON COLUMN stg_defunciones.localidad_ocurr_id IS 'Localidad de ocurrencia, resuelta contra cat_localidades.';

ALTER TABLE stg_defunciones DROP COLUMN localidad_ocules;
ALTER TABLE stg_defunciones ADD COLUMN localidad_ocules_id INTEGER;
ALTER TABLE stg_defunciones ADD CONSTRAINT stg_defunciones_localidad_ocules_id_fkey
	FOREIGN KEY(localidad_ocules_id) REFERENCES cat_localidades (id);
COMMENT ON COLUMN stg_defunciones.localidad_ocules_id IS 'Localidad de ocurrencia de la lesión, resuelta contra cat_localidades.';

-- Nivel entidad y municipio de cada rol: cada nivel se resuelve contra cat_localidades desde su
-- propio código crudo (entidad -> (ent,0,0); municipio -> (ent,mun,0)), para que los sentinelas
-- (88 no aplica, 99 no especificado, 888/999 municipio) rindan su nombre en vez de NULL.
ALTER TABLE stg_defunciones ADD COLUMN entidad_registro_id INTEGER;
ALTER TABLE stg_defunciones ADD CONSTRAINT stg_defunciones_entidad_registro_id_fkey
	FOREIGN KEY(entidad_registro_id) REFERENCES cat_localidades (id);
COMMENT ON COLUMN stg_defunciones.entidad_registro_id IS 'Entidad de registro, resuelta contra cat_localidades.';

ALTER TABLE stg_defunciones ADD COLUMN municipio_regis_id INTEGER;
ALTER TABLE stg_defunciones ADD CONSTRAINT stg_defunciones_municipio_regis_id_fkey
	FOREIGN KEY(municipio_regis_id) REFERENCES cat_localidades (id);
COMMENT ON COLUMN stg_defunciones.municipio_regis_id IS 'Municipio de registro, resuelto contra cat_localidades.';

ALTER TABLE stg_defunciones ADD COLUMN entidad_resid_id INTEGER;
ALTER TABLE stg_defunciones ADD CONSTRAINT stg_defunciones_entidad_resid_id_fkey
	FOREIGN KEY(entidad_resid_id) REFERENCES cat_localidades (id);
COMMENT ON COLUMN stg_defunciones.entidad_resid_id IS 'Entidad de residencia habitual, resuelta contra cat_localidades.';

ALTER TABLE stg_defunciones ADD COLUMN entidad_ocurr_id INTEGER;
ALTER TABLE stg_defunciones ADD CONSTRAINT stg_defunciones_entidad_ocurr_id_fkey
	FOREIGN KEY(entidad_ocurr_id) REFERENCES cat_localidades (id);
COMMENT ON COLUMN stg_defunciones.entidad_ocurr_id IS 'Entidad de ocurrencia, resuelta contra cat_localidades.';

ALTER TABLE stg_defunciones ADD COLUMN entidad_ocules_id INTEGER;
ALTER TABLE stg_defunciones ADD CONSTRAINT stg_defunciones_entidad_ocules_id_fkey
	FOREIGN KEY(entidad_ocules_id) REFERENCES cat_localidades (id);
COMMENT ON COLUMN stg_defunciones.entidad_ocules_id IS 'Entidad de ocurrencia de la lesión, resuelta contra cat_localidades.';

ALTER TABLE stg_defunciones ADD COLUMN municipio_ocules_id INTEGER;
ALTER TABLE stg_defunciones ADD CONSTRAINT stg_defunciones_municipio_ocules_id_fkey
	FOREIGN KEY(municipio_ocules_id) REFERENCES cat_localidades (id);
COMMENT ON COLUMN stg_defunciones.municipio_ocules_id IS 'Municipio de ocurrencia de la lesión, resuelto contra cat_localidades.';

-- Repunta municipio_resid_id / municipio_ocurr_id a cat_localidades (etiqueta, con sentinelas) y
-- separa la clave geográfica en cvegeo_*_id, que solo sirve para mapas. Antes, el join contra
-- cvegeo convertía en NULL los municipios sentinela (999): 308 filas en resid y 1,071 en ocurr.
-- Los valores actuales son ids de cvegeo_municipalities, no de cat_localidades: se limpian antes de
-- crear la FK. El siguiente load los repuebla.
UPDATE stg_defunciones SET municipio_resid_id = NULL, municipio_ocurr_id = NULL;

ALTER TABLE stg_defunciones ADD CONSTRAINT stg_defunciones_municipio_resid_id_fkey
	FOREIGN KEY(municipio_resid_id) REFERENCES cat_localidades (id);
COMMENT ON COLUMN stg_defunciones.municipio_resid_id IS 'Municipio de residencia habitual, resuelto contra cat_localidades.';

ALTER TABLE stg_defunciones ADD CONSTRAINT stg_defunciones_municipio_ocurr_id_fkey
	FOREIGN KEY(municipio_ocurr_id) REFERENCES cat_localidades (id);
COMMENT ON COLUMN stg_defunciones.municipio_ocurr_id IS 'Municipio de ocurrencia, resuelto contra cat_localidades.';

ALTER TABLE stg_defunciones ADD COLUMN cvegeo_resid_id INTEGER;
COMMENT ON COLUMN stg_defunciones.cvegeo_resid_id IS 'Id del municipio de residencia en cvegeo_municipalities. Solo clave geográfica/geometría para mapas (sin FK: es una foreign table).';

ALTER TABLE stg_defunciones ADD COLUMN cvegeo_ocurr_id INTEGER;
COMMENT ON COLUMN stg_defunciones.cvegeo_ocurr_id IS 'Id del municipio de ocurrencia en cvegeo_municipalities. Solo clave geográfica/geometría para mapas (sin FK: es una foreign table).';

-- Las vistas dependen de las columnas que se reemplazan arriba, así que se recrean aquí.
-- vw_defunciones ahora expone NOMBRES para entidad/municipio/localidad en los cuatro roles
-- (registro, residencia, ocurrencia, ocurrencia de la lesión) y conserva la clave cvegeo para mapas.

CREATE VIEW vw_defunciones AS
SELECT
    f.id,
    er.descripcion AS entidad_registro,
    mre.descripcion AS municipio_regis,
    c0.descripcion AS tamanio_loc_regis,
    lr.descripcion AS localidad_regis,
    c1.descripcion AS tamanio_loc_resid,
    lres.descripcion AS localidad_resid,
    c2.descripcion AS tamanio_loc_ocurr,
    locc.descripcion AS localidad_ocurr,
    c3.descripcion AS causa_defuncion,
    c4.descripcion AS cod_adicional,
    c5.descripcion AS lista_mex,
    c6.descripcion AS sexo,
    ep.descripcion AS entidad_nac,
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
    eo.descripcion AS entidad_ocules,
    mo2.descripcion AS municipio_ocules,
    locu.descripcion AS localidad_ocules,
    c57.descripcion AS razon_m,
    f.dis_re_oax,
    mres.descripcion AS municipio_resid,
    eres.descripcion AS entidad_resid,
    mr.cvegeo AS cvegeo_resid,
    mocu.descripcion AS municipio_ocurr,
    eocu.descripcion AS entidad_ocurr,
    mo.cvegeo AS cvegeo_ocurr,
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
LEFT JOIN cvegeo_municipalities mr ON mr.id = f.cvegeo_resid_id
LEFT JOIN cvegeo_municipalities mo ON mo.id = f.cvegeo_ocurr_id
LEFT JOIN cat_edicion ed ON ed.id = f.edicion_id
LEFT JOIN cat_entidad_pais ep ON ep.id = f.entidad_pais_nac_id
LEFT JOIN cat_localidades er ON er.id = f.entidad_registro_id
LEFT JOIN cat_localidades mre ON mre.id = f.municipio_regis_id
LEFT JOIN cat_localidades lr ON lr.id = f.localidad_regis_id
LEFT JOIN cat_localidades eres ON eres.id = f.entidad_resid_id
LEFT JOIN cat_localidades mres ON mres.id = f.municipio_resid_id
LEFT JOIN cat_localidades lres ON lres.id = f.localidad_resid_id
LEFT JOIN cat_localidades eocu ON eocu.id = f.entidad_ocurr_id
LEFT JOIN cat_localidades mocu ON mocu.id = f.municipio_ocurr_id
LEFT JOIN cat_localidades locc ON locc.id = f.localidad_ocurr_id
LEFT JOIN cat_localidades eo ON eo.id = f.entidad_ocules_id
LEFT JOIN cat_localidades mo2 ON mo2.id = f.municipio_ocules_id
LEFT JOIN cat_localidades locu ON locu.id = f.localidad_ocules_id;

COMMENT ON VIEW vw_defunciones IS 'Defunciones de residentes de Jalisco con todos los catálogos resueltos a su descripción. La geografía (entidad, municipio y localidad de registro, residencia, ocurrencia y ocurrencia de la lesión) se resuelve contra cat_localidades, que conserva los códigos sentinela (no aplica / no especificado). Las claves cvegeo se mantienen solo para mapas.';
COMMENT ON COLUMN vw_defunciones.entidad_registro IS 'Entidad de registro (nombre)';
COMMENT ON COLUMN vw_defunciones.municipio_regis IS 'Municipio o demarcación territorial de registro (nombre)';
COMMENT ON COLUMN vw_defunciones.localidad_regis IS 'Localidad de registro (nombre)';
COMMENT ON COLUMN vw_defunciones.localidad_resid IS 'Localidad de residencia habitual del (la) fallecido (a) (nombre)';
COMMENT ON COLUMN vw_defunciones.localidad_ocurr IS 'Localidad de ocurrencia (nombre)';
COMMENT ON COLUMN vw_defunciones.entidad_nac IS 'Lugar de nacimiento: entidad federativa o país (nombre)';
COMMENT ON COLUMN vw_defunciones.entidad_ocules IS 'Entidad de ocurrencia de la lesión (nombre)';
COMMENT ON COLUMN vw_defunciones.municipio_ocules IS 'Municipio o demarcación territorial de ocurrencia de la lesión (nombre)';
COMMENT ON COLUMN vw_defunciones.localidad_ocules IS 'Localidad de ocurrencia de la lesión (nombre)';
COMMENT ON COLUMN vw_defunciones.municipio_resid IS 'Municipio de residencia habitual (nombre)';
COMMENT ON COLUMN vw_defunciones.entidad_resid IS 'Entidad de residencia habitual (nombre)';
COMMENT ON COLUMN vw_defunciones.cvegeo_resid IS 'Clave geoestadística (cvegeo) del municipio de residencia, solo para mapas';
COMMENT ON COLUMN vw_defunciones.municipio_ocurr IS 'Municipio de ocurrencia (nombre)';
COMMENT ON COLUMN vw_defunciones.entidad_ocurr IS 'Entidad de ocurrencia (nombre)';
COMMENT ON COLUMN vw_defunciones.cvegeo_ocurr IS 'Clave geoestadística (cvegeo) del municipio de ocurrencia, solo para mapas';

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
    ml.descripcion AS municipio,
    a.descripcion AS anio_registro,
    cd.descripcion AS causa_defuncion,
    COUNT(*) AS defunciones_maternas
FROM stg_defunciones f
LEFT JOIN cvegeo_municipalities mr ON mr.id = f.cvegeo_resid_id
LEFT JOIN cat_localidades ml ON ml.id = f.municipio_resid_id
LEFT JOIN cat_anio a ON a.id = f.anio_registro_id
LEFT JOIN cat_causa_defuncion cd ON cd.id = f.causa_defuncion_id
WHERE f.razon_m_id = 1
GROUP BY mr.cvegeo, ml.descripcion, a.descripcion, cd.descripcion;

COMMENT ON VIEW vw_mortalidad_materna IS 'Defunciones que contribuyen al cálculo de la razón de mortalidad materna (razon_m = 1), por municipio de residencia, año y causa.';
COMMENT ON COLUMN vw_mortalidad_materna.cvegeo IS 'Clave geoestadística (cvegeo) del municipio de residencia, solo para mapas.';
COMMENT ON COLUMN vw_mortalidad_materna.municipio IS 'Municipio de residencia habitual (nombre, resuelto contra cat_localidades).';
COMMENT ON COLUMN vw_mortalidad_materna.anio_registro IS 'Año de registro de la defunción.';
COMMENT ON COLUMN vw_mortalidad_materna.causa_defuncion IS 'Causa de la defunción (CIE-10, lista detallada).';
COMMENT ON COLUMN vw_mortalidad_materna.defunciones_maternas IS 'Número de defunciones maternas del grupo.';

-- Mortalidad infantil: defunciones de menores de un año.
CREATE VIEW vw_mortalidad_infantil AS
SELECT
    mr.cvegeo AS cvegeo,
    ml.descripcion AS municipio,
    a.descripcion AS anio_registro,
    s.descripcion AS sexo,
    cd.descripcion AS causa_defuncion,
    COUNT(*) AS defunciones_infantiles
FROM stg_defunciones f
LEFT JOIN cvegeo_municipalities mr ON mr.id = f.cvegeo_resid_id
LEFT JOIN cat_localidades ml ON ml.id = f.municipio_resid_id
LEFT JOIN cat_anio a ON a.id = f.anio_registro_id
LEFT JOIN cat_sexo s ON s.id = f.sexo_id
LEFT JOIN cat_causa_defuncion cd ON cd.id = f.causa_defuncion_id
WHERE f.edad_agrupada_id = 1
GROUP BY mr.cvegeo, ml.descripcion, a.descripcion, s.descripcion, cd.descripcion;

COMMENT ON VIEW vw_mortalidad_infantil IS 'Defunciones de menores de un año (edad_agrupada = 1), por municipio de residencia, año, sexo y causa.';
COMMENT ON COLUMN vw_mortalidad_infantil.cvegeo IS 'Clave geoestadística (cvegeo) del municipio de residencia, solo para mapas.';
COMMENT ON COLUMN vw_mortalidad_infantil.municipio IS 'Municipio de residencia habitual (nombre, resuelto contra cat_localidades).';
COMMENT ON COLUMN vw_mortalidad_infantil.anio_registro IS 'Año de registro de la defunción.';
COMMENT ON COLUMN vw_mortalidad_infantil.sexo IS 'Sexo del fallecido.';
COMMENT ON COLUMN vw_mortalidad_infantil.causa_defuncion IS 'Causa de la defunción (CIE-10, lista detallada).';
COMMENT ON COLUMN vw_mortalidad_infantil.defunciones_infantiles IS 'Número de defunciones de menores de un año del grupo.';
