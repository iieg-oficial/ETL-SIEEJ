CREATE TABLE IF NOT EXISTS cat_deportes (
    id INTEGER PRIMARY KEY,
    deporte VARCHAR(80) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS cat_tipos_academia (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(80) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS stg_academias_deportivas (
    id SERIAL PRIMARY KEY,
    entidad_id INTEGER NOT NULL,
    municipio_id INTEGER NOT NULL,
    deporte_id INTEGER NOT NULL REFERENCES cat_deportes(id),
    tipo_id INTEGER NOT NULL REFERENCES cat_tipos_academia(id),
    deporte_nombre_largo VARCHAR(255),
    beneficiarios_total INTEGER,
    beneficiarios_hombres INTEGER,
    beneficiarios_mujeres INTEGER,
    domicilio TEXT,
    horarios TEXT,
    longitud FLOAT,
    latitud FLOAT,
    fecha_corte DATE NOT NULL,
    fecha_actualizacion_fuente DATE,
    fecha_actualizacion DATE NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_stg_academias_deportivas_fecha_corte
    ON stg_academias_deportivas (fecha_corte);

CREATE TABLE IF NOT EXISTS stg_polideportivos (
    id SERIAL PRIMARY KEY,
    entidad_id INTEGER NOT NULL,
    municipio_id INTEGER NOT NULL,
    nombre_centro VARCHAR(255) NOT NULL,
    domicilio TEXT,
    horarios TEXT,
    servicios TEXT,
    longitud FLOAT,
    latitud FLOAT,
    fecha_corte DATE NOT NULL,
    fecha_actualizacion_fuente DATE,
    fecha_actualizacion DATE NOT NULL,
    CONSTRAINT uq_stg_polideportivos UNIQUE (fecha_corte, municipio_id, nombre_centro)
);

CREATE TABLE IF NOT EXISTS polideportivo_deportes (
    polideportivo_id INTEGER NOT NULL REFERENCES stg_polideportivos(id) ON DELETE CASCADE,
    deporte_id INTEGER NOT NULL REFERENCES cat_deportes(id),
    PRIMARY KEY (polideportivo_id, deporte_id)
);

CREATE INDEX IF NOT EXISTS ix_polideportivo_deportes_deporte_id
    ON polideportivo_deportes (deporte_id);
