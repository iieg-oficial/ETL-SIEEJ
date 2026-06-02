CREATE TABLE IF NOT EXISTS cat_turnos (
    id INTEGER PRIMARY KEY,
    nombre_turno VARCHAR(30) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS cat_sostenimientos (
    id SERIAL PRIMARY KEY,
    sostenimiento VARCHAR(30) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS cat_codigos_sostenimiento (
    id INTEGER PRIMARY KEY,
    sostenimiento_id INTEGER NOT NULL REFERENCES cat_sostenimientos(id)
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
    nombre_region VARCHAR(80) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS cat_medios (
    id SERIAL PRIMARY KEY,
    medio VARCHAR(20) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS cat_niveles_programa (
    id SERIAL PRIMARY KEY,
    nivel_programa VARCHAR(120) NOT NULL UNIQUE
);
