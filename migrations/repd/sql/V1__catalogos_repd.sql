-- Flyway Migration: Catálogos y tabla principal según schemas.py


CREATE TABLE cat_sexos (
    id SERIAL PRIMARY KEY,
    descripcion VARCHAR(50) NOT NULL
);

CREATE TABLE cat_nacionalidades (
    id SERIAL PRIMARY KEY,
    descripcion VARCHAR(100) NOT NULL
);

CREATE TABLE cat_rangos_edades (
    id SERIAL PRIMARY KEY,
    descripcion VARCHAR(50) NOT NULL
);

CREATE TABLE cat_estados (
    id SERIAL PRIMARY KEY,
    descripcion VARCHAR(100) NOT NULL
);

CREATE TABLE cat_municipios (
    id SERIAL PRIMARY KEY,
    descripcion VARCHAR(100) NOT NULL
);

CREATE TABLE cat_estatus_desapariciones (
    id SERIAL PRIMARY KEY,
    descripcion VARCHAR(100) NOT NULL
);

CREATE TABLE cat_condiciones_localizaciones (
    id SERIAL PRIMARY KEY,
    descripcion VARCHAR(100) NOT NULL
);

CREATE TABLE cat_clasificaciones_localizaciones (
    id SERIAL PRIMARY KEY,
    descripcion VARCHAR(100) NOT NULL
);

CREATE TABLE cat_tipos_cierres (
    id SERIAL PRIMARY KEY,
    descripcion VARCHAR(100) NOT NULL
);

