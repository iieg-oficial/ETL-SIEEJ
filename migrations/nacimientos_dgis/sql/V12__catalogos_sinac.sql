-- =======================================================================
-- V12: catalogos publicados por SINAC (paquete sinac_catalogos_*.zip)
-- =======================================================================

CREATE TABLE IF NOT EXISTS cat_si_no (
	id SERIAL NOT NULL,
	clave INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (clave)
);

CREATE TABLE IF NOT EXISTS cat_sexo (
	id SERIAL NOT NULL,
	clave INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (clave)
);

CREATE TABLE IF NOT EXISTS cat_estado_conyugal (
	id SERIAL NOT NULL,
	clave INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (clave)
);

CREATE TABLE IF NOT EXISTS cat_escolaridad (
	id SERIAL NOT NULL,
	clave INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (clave)
);

CREATE TABLE IF NOT EXISTS cat_afiliacion (
	id SERIAL NOT NULL,
	clave INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (clave)
);

CREATE TABLE IF NOT EXISTS cat_ocupacion_habitual (
	id SERIAL NOT NULL,
	clave INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (clave)
);

CREATE TABLE IF NOT EXISTS cat_lugar_nacimiento (
	id SERIAL NOT NULL,
	clave INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (clave)
);

CREATE TABLE IF NOT EXISTS cat_producto_embarazo (
	id SERIAL NOT NULL,
	clave INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (clave)
);

CREATE TABLE IF NOT EXISTS cat_resolucion_embarazo (
	id SERIAL NOT NULL,
	clave INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (clave)
);

CREATE TABLE IF NOT EXISTS cat_entidad (
	id SERIAL NOT NULL,
	clave INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (clave)
);

CREATE TABLE IF NOT EXISTS cat_municipio (
	id SERIAL NOT NULL,
	clave INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (clave)
);

CREATE TABLE IF NOT EXISTS cat_localidad (
	id SERIAL NOT NULL,
	clave INTEGER NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (clave)
);

CREATE TABLE IF NOT EXISTS cat_diagnostico (
	id SERIAL NOT NULL,
	clave VARCHAR(11) NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (clave)
);

CREATE TABLE IF NOT EXISTS cat_establecimiento_salud (
	id SERIAL NOT NULL,
	clave VARCHAR(11) NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (clave)
);
