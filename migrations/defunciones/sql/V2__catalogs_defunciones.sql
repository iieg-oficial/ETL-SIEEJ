-- Catálogos defunciones.

CREATE TABLE IF NOT EXISTS cat_edad (
	id INTEGER NOT NULL,
	nombre_edad VARCHAR(30) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (nombre_edad)
);

CREATE TABLE IF NOT EXISTS cat_sexo (
	id INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS cat_asistencia_medica (
	id INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS cat_escolaridad (
	id INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS cat_estado_civil (
	id INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS cat_nacionalidad (
	id INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS cat_condicion_actividad (
	id INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS cat_afromexicano (
	id INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS cat_condicion_indigena (
	id INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS cat_lengua_indigena (
	id INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS cat_lenguas (
	id INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS cat_edad_agrupada (
	id INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS cat_edad_gestacional (
	id INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS cat_origen (
	id INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS cat_lista_cie (
	id INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS cat_lugar_ocurrencia (
	id INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS cat_sitio_ocurrencia (
	id INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS cat_necropsia (
	id INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS cat_uso_necropsia (
	id INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS cat_certificante (
	id INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS cat_ocurrio_trabajo (
	id INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS cat_accidental_violenta (
	id INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS cat_cirugia (
	id INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS cat_muerte_encefalica (
	id INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS cat_donador (
	id INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS cat_area_urbana_rural (
	id INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS cat_tamano_localidad (
	id INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS cat_condicion_embarazo (
	id INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS cat_relacion_con_embarazo (
	id INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS cat_complicaron_embarazo (
	id INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS cat_violencia_familiar (
	id INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS cat_parentesco_agresor (
	id INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS cat_dia (
	id INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS cat_mes (
	id INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS cat_anio (
	id INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS cat_hora (
	id INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS cat_minuto (
	id INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS cat_causa_defuncion (
	id SERIAL NOT NULL,
	codigo VARCHAR(20) NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (codigo)
);

CREATE TABLE IF NOT EXISTS cat_codigo_adicional (
	id SERIAL NOT NULL,
	codigo VARCHAR(20) NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (codigo)
);

CREATE TABLE IF NOT EXISTS cat_lista_mexicana (
	id SERIAL NOT NULL,
	codigo VARCHAR(20) NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (codigo)
);

CREATE TABLE IF NOT EXISTS cat_grupo_lista_mexicana (
	id SERIAL NOT NULL,
	codigo VARCHAR(20) NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (codigo)
);

CREATE TABLE IF NOT EXISTS cat_peso_producto (
	id SERIAL NOT NULL,
	codigo VARCHAR(20) NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (codigo)
);

CREATE TABLE IF NOT EXISTS cat_razon_materna (
	id INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS cat_capitulo_grupo (
	id SERIAL NOT NULL,
	cap INTEGER NOT NULL,
	gpo INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT uq_capitulo_grupo UNIQUE (cap, gpo)
);

CREATE TABLE IF NOT EXISTS cat_edicion (
	id SERIAL NOT NULL,
	anio INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (anio)
);

CREATE TABLE IF NOT EXISTS cat_ocupacion (
	id SERIAL NOT NULL,
	codigo INTEGER NOT NULL,
	edicion_id INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT uq_ocupacion_edicion UNIQUE (codigo, edicion_id),
	FOREIGN KEY(edicion_id) REFERENCES cat_edicion (id)
);

CREATE TABLE IF NOT EXISTS cat_derecho_habiencia (
	id SERIAL NOT NULL,
	codigo INTEGER NOT NULL,
	edicion_id INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT uq_derechohabiencia_edicion UNIQUE (codigo, edicion_id),
	FOREIGN KEY(edicion_id) REFERENCES cat_edicion (id)
);

CREATE TABLE IF NOT EXISTS cat_presunta_defuncion_violenta (
	id SERIAL NOT NULL,
	codigo INTEGER NOT NULL,
	edicion_id INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT uq_presunta_violenta_edicion UNIQUE (codigo, edicion_id),
	FOREIGN KEY(edicion_id) REFERENCES cat_edicion (id)
);
