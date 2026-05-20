CREATE TABLE IF NOT EXISTS cat_actualizaciones (
    id SERIAL PRIMARY KEY,
    fecha_actualizacion DATE NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS cat_localidades (
    id SERIAL PRIMARY KEY,
    cve_geo_id INTEGER NOT NULL UNIQUE,
    localidad_id INTEGER NOT NULL,
    municipio_id INTEGER NOT NULL,
    entidad_id INTEGER NOT NULL,
    localidad TEXT,
    CONSTRAINT uq_localidades_clave UNIQUE (municipio_id, entidad_id, localidad_id)
);

CREATE TABLE IF NOT EXISTS cat_sectores (
    id SERIAL PRIMARY KEY,
    codigo TEXT NOT NULL UNIQUE,
    sector TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS cat_subsectores (
    id SERIAL PRIMARY KEY,
    codigo TEXT NOT NULL UNIQUE,
    subsector TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS cat_ramas (
    id SERIAL PRIMARY KEY,
    codigo TEXT NOT NULL UNIQUE,
    rama TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS cat_subramas (
    id SERIAL PRIMARY KEY,
    codigo TEXT NOT NULL UNIQUE,
    subrama TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS cat_clases_actividad (
    id SERIAL PRIMARY KEY,
    codigo TEXT NOT NULL UNIQUE,
    clase TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS cat_rangos_personal (
    id INTEGER PRIMARY KEY,
    descripcion TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS cat_tipos_establecimientos (
    id INTEGER PRIMARY KEY,
    descripcion TEXT NOT NULL
);
