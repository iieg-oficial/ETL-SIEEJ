-- Generado desde core/pipelines/defunciones_inegi/schemas.py
CREATE TABLE cat_accidental_violenta (
	id SERIAL NOT NULL,
	clave INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (clave)
);

CREATE TABLE cat_afromexicano (
	id SERIAL NOT NULL,
	clave INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (clave)
);

CREATE TABLE cat_area_urbana_rural (
	id SERIAL NOT NULL,
	clave INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (clave)
);

CREATE TABLE cat_asistencia_medica (
	id SERIAL NOT NULL,
	clave INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (clave)
);

CREATE TABLE cat_capitulo_grupo (
	id SERIAL NOT NULL,
	capitulo SMALLINT NOT NULL,
	grupo SMALLINT,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT uq_capitulo_grupo UNIQUE (capitulo, grupo)
);

CREATE TABLE cat_certificante (
	id SERIAL NOT NULL,
	clave INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (clave)
);

CREATE TABLE cat_cirugia (
	id SERIAL NOT NULL,
	clave INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (clave)
);

CREATE TABLE cat_complicaron_embarazo (
	id SERIAL NOT NULL,
	clave INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (clave)
);

CREATE TABLE cat_condicion_actividad (
	id SERIAL NOT NULL,
	clave INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (clave)
);

CREATE TABLE cat_condicion_embarazo (
	id SERIAL NOT NULL,
	clave INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (clave)
);

CREATE TABLE cat_condicion_indigena (
	id SERIAL NOT NULL,
	clave INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (clave)
);

CREATE TABLE cat_donador (
	id SERIAL NOT NULL,
	clave INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (clave)
);

CREATE TABLE cat_edad_agrupada (
	id SERIAL NOT NULL,
	clave INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (clave)
);

CREATE TABLE cat_edicion (
	id SERIAL NOT NULL,
	anio SMALLINT NOT NULL,
	fecha_actualizacion DATE NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (anio)
);

CREATE TABLE cat_escolaridad (
	id SERIAL NOT NULL,
	clave INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (clave)
);

CREATE TABLE cat_estado_civil (
	id SERIAL NOT NULL,
	clave INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (clave)
);

CREATE TABLE cat_grupo_lista_mexicana (
	id SERIAL NOT NULL,
	clave VARCHAR(4) NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (clave)
);

CREATE TABLE cat_lengua (
	id SERIAL NOT NULL,
	clave INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (clave)
);

CREATE TABLE cat_lengua_indigena (
	id SERIAL NOT NULL,
	clave INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (clave)
);

CREATE TABLE cat_lista_cie (
	id SERIAL NOT NULL,
	clave INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (clave)
);

CREATE TABLE cat_lista_mexicana (
	id SERIAL NOT NULL,
	clave INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (clave)
);

CREATE TABLE cat_lugar_ocurrencia (
	id SERIAL NOT NULL,
	clave INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (clave)
);

CREATE TABLE cat_muerte_encefalica (
	id SERIAL NOT NULL,
	clave INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (clave)
);

CREATE TABLE cat_nacionalidad (
	id SERIAL NOT NULL,
	clave INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (clave)
);

CREATE TABLE cat_necropsia (
	id SERIAL NOT NULL,
	clave INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (clave)
);

CREATE TABLE cat_ocurrio_trabajo (
	id SERIAL NOT NULL,
	clave INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (clave)
);

CREATE TABLE cat_pais (
	id SERIAL NOT NULL,
	clave INTEGER NOT NULL,
	nombre_pais VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (clave)
);

CREATE TABLE cat_parentesco_agresor (
	id SERIAL NOT NULL,
	clave INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (clave)
);

CREATE TABLE cat_presunta_defuncion_violenta (
	id SERIAL NOT NULL,
	clave INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (clave)
);

CREATE TABLE cat_razon_materna (
	id SERIAL NOT NULL,
	clave INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (clave)
);

CREATE TABLE cat_relacion_embarazo (
	id SERIAL NOT NULL,
	clave INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (clave)
);

CREATE TABLE cat_sexo (
	id SERIAL NOT NULL,
	clave INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (clave)
);

CREATE TABLE cat_sitio_ocurrencia (
	id SERIAL NOT NULL,
	clave INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (clave)
);

CREATE TABLE cat_tamanio_localidad (
	id SERIAL NOT NULL,
	clave INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (clave)
);

CREATE TABLE cat_uso_necropsia (
	id SERIAL NOT NULL,
	clave INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (clave)
);

CREATE TABLE cat_violencia_familiar (
	id SERIAL NOT NULL,
	clave INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (clave)
);

CREATE TABLE cat_cie10 (
	id SERIAL NOT NULL,
	clave CHAR(4) NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	edicion_id INTEGER NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT uq_cie10_edicion UNIQUE (clave, edicion_id),
	FOREIGN KEY(edicion_id) REFERENCES cat_edicion (id)
);

CREATE TABLE cat_derechohabiencia (
	id SERIAL NOT NULL,
	clave INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	edicion_id INTEGER NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT uq_derechohabiencia_edicion UNIQUE (clave, edicion_id),
	FOREIGN KEY(edicion_id) REFERENCES cat_edicion (id)
);

CREATE TABLE cat_localidad (
	id SERIAL NOT NULL,
	cvegeo INTEGER NOT NULL,
	cve_ent SMALLINT NOT NULL,
	cve_mun SMALLINT NOT NULL,
	cve_loc INTEGER NOT NULL,
	localidad VARCHAR(150) NOT NULL,
	edicion_id INTEGER NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT uq_localidad_edicion UNIQUE (cvegeo, edicion_id),
	FOREIGN KEY(edicion_id) REFERENCES cat_edicion (id)
);

CREATE TABLE cat_ocupacion (
	id SERIAL NOT NULL,
	clave INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	edicion_id INTEGER NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT uq_ocupacion_edicion UNIQUE (clave, edicion_id),
	FOREIGN KEY(edicion_id) REFERENCES cat_edicion (id)
);
