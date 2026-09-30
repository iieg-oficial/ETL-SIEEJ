CREATE TABLE IF NOT EXISTS cat_turnos (
    id INTEGER PRIMARY KEY,
    turno VARCHAR(30) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS cat_medios (
    id SERIAL PRIMARY KEY,
    medio VARCHAR(20) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS cat_sostenimientos (
    id SERIAL PRIMARY KEY,
    sostenimiento VARCHAR(30) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS cat_niveles (
    id SERIAL PRIMARY KEY,
    nivel VARCHAR(60) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS cat_programas (
    id SERIAL PRIMARY KEY,
    programa VARCHAR(120) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS cat_regiones (
    id INTEGER PRIMARY KEY,
    region VARCHAR(80) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS cat_localidades (
    id SERIAL PRIMARY KEY,
    cve_geo_id INTEGER NOT NULL UNIQUE,
    entidad_id INTEGER NOT NULL,
    municipio_id INTEGER NOT NULL,
    clave_localidad INTEGER NOT NULL,
    localidad VARCHAR(150) NOT NULL,
    CONSTRAINT uq_cat_localidades_clave UNIQUE (entidad_id, municipio_id, clave_localidad)
);

CREATE TABLE IF NOT EXISTS cat_colonias (
    id SERIAL PRIMARY KEY,
    localidad_id INTEGER NOT NULL REFERENCES cat_localidades(id),
    clave_colonia INTEGER,
    colonia VARCHAR(150) NOT NULL,
    CONSTRAINT uq_cat_colonias_clave UNIQUE (localidad_id, clave_colonia)
);

CREATE TABLE IF NOT EXISTS cat_programas_estrategicos (
    id SERIAL PRIMARY KEY,
    programa_estrategico VARCHAR(120) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS cat_regiones_operativas (
    id SERIAL PRIMARY KEY,
    region_operativa VARCHAR(80) NOT NULL UNIQUE
);
