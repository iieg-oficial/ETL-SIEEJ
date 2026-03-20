-- Catálogos estáticos

CREATE TABLE IF NOT EXISTS zonas_geograficas (
    id INTEGER PRIMARY KEY,
    zona_geografica VARCHAR(10) NOT NULL
);

CREATE TABLE IF NOT EXISTS bien_afectado (
    id INTEGER PRIMARY KEY,
    bien_afectado VARCHAR(200) NOT NULL
);

CREATE TABLE IF NOT EXISTS delitos (
    id INTEGER PRIMARY KEY,
    delito VARCHAR(99) NOT NULL,
    bien_afectado_id INTEGER NOT NULL REFERENCES bien_afectado(id)
);

CREATE TABLE IF NOT EXISTS violencia (
    id INTEGER PRIMARY KEY,
    violencia VARCHAR(15) NOT NULL
);

-- Catálogos dinámicos

CREATE TABLE IF NOT EXISTS colonias (
    id SERIAL PRIMARY KEY,
    colonia VARCHAR(400) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS calles (
    id SERIAL PRIMARY KEY,
    calle VARCHAR(400) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS cruces (
    id SERIAL PRIMARY KEY,
    cruce VARCHAR(400) NOT NULL UNIQUE
);
