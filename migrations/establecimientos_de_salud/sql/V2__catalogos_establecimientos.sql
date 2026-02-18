CREATE TABLE IF NOT EXISTS localidades (
    id  SERIAL PRIMARY KEY,
    clave_localidad INTEGER NOT NULL,
    municipio_id INTEGER NOT NULL,
    entidad_id  INTEGER NOT NULL,
    localidad VARCHAR(200) NOT NULL,
    CONSTRAINT uq_localidades_clave UNIQUE (municipio_id, entidad_id, clave_localidad)
);

CREATE TABLE IF NOT EXISTS jurisdicciones (
    id SERIAL PRIMARY KEY,
    jurisdiccion VARCHAR(200) NOT NULL UNIQUE,
    municipio_id INTEGER NOT NULL,
    entidad_id  INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS instituciones (
    id  SERIAL PRIMARY KEY,
    institucion VARCHAR(300) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS tipos_establecimiento (
    id VARCHAR(20) PRIMARY KEY,
    tipo_establecimiento VARCHAR(200) NOT NULL
);

CREATE TABLE IF NOT EXISTS tipologias (
    id SERIAL PRIMARY KEY,
    tipologia VARCHAR(300) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS subtipologias (
    id SERIAL PRIMARY KEY,
    subtipologia VARCHAR(300) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS tipos_vialidad (
    id SERIAL PRIMARY KEY,
    tipo_vialidad  VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS vialidades (
    id SERIAL PRIMARY KEY,
    vialidad VARCHAR(400) NOT NULL,
    tipo_vialidad_id INTEGER NOT NULL REFERENCES tipos_vialidad(id),
    CONSTRAINT uq_vialidades_nombre_tipo UNIQUE (vialidad, tipo_vialidad_id)
);

CREATE TABLE IF NOT EXISTS tipos_asentamiento (
    id VARCHAR(20) PRIMARY KEY,
    tipo_asentamiento VARCHAR(150) NOT NULL
);

CREATE TABLE IF NOT EXISTS estatus_establecimiento (
    id VARCHAR(20) PRIMARY KEY,
    estatus_establecimiento VARCHAR(150) NOT NULL
);

CREATE TABLE IF NOT EXISTS nivel_atencion (
    id VARCHAR(20) PRIMARY KEY,
    nivel_atencion VARCHAR(150) NOT NULL
);

CREATE TABLE IF NOT EXISTS estrato_unidad (
    id VARCHAR(20) PRIMARY KEY,
    estrato_unidad VARCHAR(150) NOT NULL
);

CREATE TABLE IF NOT EXISTS tipos_obra (
    id VARCHAR(20) PRIMARY KEY,
    tipo_obra VARCHAR(150) NOT NULL
);


CREATE TABLE IF NOT EXISTS rfc_establecimientos (
    id  SERIAL PRIMARY KEY,
    rfc VARCHAR(13) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS marcas_moviles (
    id SERIAL PRIMARY KEY,
    marca VARCHAR(200) NOT NULL,
    marca_especifica VARCHAR(200),
    modelo VARCHAR(200),
    CONSTRAINT uq_marcas_moviles UNIQUE (marca, marca_especifica, modelo)
);

CREATE TABLE IF NOT EXISTS programas_moviles (
    id SERIAL PRIMARY KEY,
    programa_movil VARCHAR(300) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS tipos_unidad_movil (
    id SERIAL PRIMARY KEY,
    tipo_unidad_movil VARCHAR(300) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS unidades_moviles (
    id SERIAL PRIMARY KEY,
    nombre_unidad_movil VARCHAR(300) NOT NULL UNIQUE,
    nombre_comercial VARCHAR(300)
);

CREATE TABLE IF NOT EXISTS tipologias_moviles (
    id SERIAL PRIMARY KEY,
    tipologia_movil VARCHAR(300) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS institutos_administracion (
    id SERIAL PRIMARY KEY,
    instituto_administracion VARCHAR(300) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS movimientos (
    id SERIAL PRIMARY KEY,
    movimiento VARCHAR(300) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS motivos_baja (
    id SERIAL PRIMARY KEY,
    motivo_baja VARCHAR(400) NOT NULL UNIQUE
);
