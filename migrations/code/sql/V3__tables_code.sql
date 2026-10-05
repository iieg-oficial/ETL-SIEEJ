CREATE TABLE IF NOT EXISTS stg_puntos_activacion_reto (
    id SERIAL PRIMARY KEY,
    clave_punto INTEGER NOT NULL,
    entidad_id INTEGER NOT NULL,
    municipio_id INTEGER NOT NULL,
    region_id INTEGER REFERENCES cat_regiones(id),
    nombre_espacio VARCHAR(255) NOT NULL,
    dias_horarios TEXT,
    actividad_id INTEGER REFERENCES cat_actividades(id),
    cantidad_usuarios INTEGER,
    longitud FLOAT,
    latitud FLOAT,
    fecha_corte DATE NOT NULL,
    fecha_actualizacion_fuente DATE,
    fecha_actualizacion DATE NOT NULL,
    CONSTRAINT uq_stg_puntos_activacion_reto UNIQUE (fecha_corte, municipio_id, nombre_espacio)
);

CREATE TABLE IF NOT EXISTS cargas_acervo (
    id SERIAL PRIMARY KEY,
    envio_id INTEGER NOT NULL,
    conjunto VARCHAR(255) NOT NULL,
    object_key TEXT NOT NULL,
    etag VARCHAR(64),
    fecha_corte DATE,
    fecha_actualizacion_fuente DATE,
    actualizado_en TIMESTAMPTZ NOT NULL,
    procesado_en TIMESTAMPTZ NOT NULL,
    CONSTRAINT uq_cargas_acervo UNIQUE (envio_id, object_key)
);
