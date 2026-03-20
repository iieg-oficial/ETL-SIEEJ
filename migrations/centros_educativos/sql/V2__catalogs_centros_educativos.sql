CREATE TABLE IF NOT EXISTS turnos (
    id INTEGER PRIMARY KEY,
    turno TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tipos_educativos (
    id INTEGER PRIMARY KEY,
    tipo_educativo TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS niveles_educativos (
    id INTEGER PRIMARY KEY,
    nivel_educativo TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS servicios_educativos (
    id INTEGER PRIMARY KEY,
    servicio_educativo TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tipos_controles (
    id INTEGER PRIMARY KEY,
    tipo_control TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tipos_sostenimiento (
    id INTEGER PRIMARY KEY,
    tipo_sostenimiento TEXT NOT NULL
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

CREATE TABLE IF NOT EXISTS domicilios (
    id SERIAL PRIMARY KEY,
    domicilio TEXT NOT NULL,
    numero_exterior TEXT,
    codigo_postal VARCHAR(10),
    entre_calle TEXT,
    y_calle TEXT,
    calle_posterior TEXT,
    CONSTRAINT uq_domicilios_completo UNIQUE (domicilio, numero_exterior, codigo_postal)
);

CREATE TABLE IF NOT EXISTS colonias (
    id SERIAL PRIMARY KEY,
    colonia TEXT NOT NULL,
    localidad_id INTEGER NOT NULL REFERENCES localidades(id),
    CONSTRAINT uq_colonias_nombre_localidad UNIQUE (colonia, localidad_id)
);
