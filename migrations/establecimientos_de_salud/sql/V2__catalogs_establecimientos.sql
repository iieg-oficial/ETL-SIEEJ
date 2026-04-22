CREATE TABLE IF NOT EXISTS localidades (
    id  SERIAL PRIMARY KEY,
    clave_localidad INTEGER NOT NULL,
    municipio_id INTEGER NOT NULL,
    entidad_id  INTEGER NOT NULL,
    localidad TEXT,
    CONSTRAINT uq_localidades_clave UNIQUE (municipio_id, entidad_id, clave_localidad)
);

CREATE TABLE IF NOT EXISTS jurisdicciones (
    id SERIAL PRIMARY KEY,
    jurisdiccion TEXT NOT NULL UNIQUE,
    municipio_id INTEGER NOT NULL,
    entidad_id  INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS instituciones (
    id  SERIAL PRIMARY KEY,
    institucion TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS tipos_establecimiento (
    id INTEGER PRIMARY KEY,
    tipo_establecimiento TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tipologias (
    id SERIAL PRIMARY KEY,
    tipologia TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS subtipologias (
    id SERIAL PRIMARY KEY,
    subtipologia TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS tipos_vialidad (
    id SERIAL PRIMARY KEY,
    tipo_vialidad TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS vialidades (
    id SERIAL PRIMARY KEY,
    vialidad TEXT NOT NULL,
    tipo_vialidad_id INTEGER NOT NULL REFERENCES tipos_vialidad(id),
    CONSTRAINT uq_vialidades_nombre_tipo UNIQUE (vialidad, tipo_vialidad_id)
);

CREATE TABLE IF NOT EXISTS tipos_asentamiento (
    id SERIAL PRIMARY KEY,
    tipo_asentamiento TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS estatus_establecimiento (
    id INTEGER PRIMARY KEY,
    estatus_establecimiento TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS nivel_atencion (
    id INTEGER PRIMARY KEY,
    nivel_atencion TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS estrato_unidad (
    id INTEGER PRIMARY KEY,
    estrato_unidad TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tipos_obra (
    id SERIAL PRIMARY KEY,
    tipo_obra TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS rfc_establecimientos (
    id  SERIAL PRIMARY KEY,
    rfc TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS marcas_moviles (
    id SERIAL PRIMARY KEY,
    marca TEXT NOT NULL,
    marca_especifica TEXT,
    modelo TEXT,
    CONSTRAINT uq_marcas_moviles UNIQUE (marca, marca_especifica, modelo)
);

CREATE TABLE IF NOT EXISTS programas_moviles (
    id SERIAL PRIMARY KEY,
    programa_movil TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS tipos_unidad_movil (
    id SERIAL PRIMARY KEY,
    tipo_unidad_movil TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS unidades_moviles (
    id SERIAL PRIMARY KEY,
    nombre_unidad_movil TEXT NOT NULL UNIQUE,
    nombre_comercial TEXT
);

CREATE TABLE IF NOT EXISTS tipologias_moviles (
    id SERIAL PRIMARY KEY,
    tipologia_movil TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS institutos_administracion (
    id SERIAL PRIMARY KEY,
    instituto_administracion TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS movimientos (
    id INTEGER PRIMARY KEY,
    movimiento TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS motivos_baja (
    id SERIAL PRIMARY KEY,
    motivo_baja TEXT NOT NULL UNIQUE
);
