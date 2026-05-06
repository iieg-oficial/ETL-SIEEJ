CREATE TABLE IF NOT EXISTS actualizaciones (
    id SERIAL PRIMARY KEY,
    fecha_actualizacion DATE NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS localidades (
    id SERIAL PRIMARY KEY,
    cve_geo_id INTEGER NOT NULL UNIQUE,
    clave_localidad INTEGER NOT NULL,
    municipio_id INTEGER NOT NULL,
    entidad_id INTEGER NOT NULL,
    localidad TEXT,
    CONSTRAINT uq_localidades_clave UNIQUE (municipio_id, entidad_id, clave_localidad)
);

CREATE TABLE IF NOT EXISTS actividades_economicas (
    id INTEGER PRIMARY KEY,
    nombre_actividad_economica TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS rangos_personal (
    id INTEGER PRIMARY KEY,
    descripcion TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tipos_establecimientos (
    id INTEGER PRIMARY KEY,
    descripcion TEXT NOT NULL
);
