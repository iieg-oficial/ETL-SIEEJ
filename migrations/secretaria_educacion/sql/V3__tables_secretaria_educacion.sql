CREATE TABLE IF NOT EXISTS stg_directorio_centros_trabajo (
    id SERIAL PRIMARY KEY,
    entidad_id INTEGER NOT NULL,
    municipio_id INTEGER NOT NULL,
    localidad_id INTEGER REFERENCES cat_localidades(id),
    colonia_id INTEGER REFERENCES cat_colonias(id),
    clave_ct VARCHAR(20) NOT NULL,
    turno_id INTEGER NOT NULL REFERENCES cat_turnos(id),
    nombre_ct VARCHAR(255) NOT NULL,
    domicilio TEXT,
    medio_id INTEGER REFERENCES cat_medios(id),
    director VARCHAR(255),
    codigo_postal VARCHAR(10),
    telefono VARCHAR(20),
    zona_escolar INTEGER,
    sector INTEGER,
    sostenimiento_id INTEGER REFERENCES cat_sostenimientos(id),
    nivel_id INTEGER NOT NULL REFERENCES cat_niveles(id),
    programa_id INTEGER NOT NULL REFERENCES cat_programas(id),
    region_id INTEGER REFERENCES cat_regiones(id),
    longitud FLOAT,
    latitud FLOAT,
    escuelas INTEGER NOT NULL,
    hombres_matriculados INTEGER NOT NULL,
    mujeres_matriculadas INTEGER NOT NULL,
    total_matriculados INTEGER NOT NULL,
    total_docentes_directivo INTEGER NOT NULL,
    fecha_corte DATE NOT NULL,
    fecha_actualizacion_fuente DATE,
    fecha_actualizacion DATE NOT NULL,
    CONSTRAINT uq_stg_directorio_centros_trabajo UNIQUE (fecha_corte, clave_ct, turno_id, nivel_id, programa_id)
);

CREATE TABLE IF NOT EXISTS stg_escuelas_programas_estrategicos (
    id SERIAL PRIMARY KEY,
    clave_ct VARCHAR(20) NOT NULL,
    programa_estrategico_id INTEGER NOT NULL REFERENCES cat_programas_estrategicos(id),
    fecha_corte DATE NOT NULL,
    fecha_actualizacion_fuente DATE,
    fecha_actualizacion DATE NOT NULL,
    CONSTRAINT uq_stg_escuelas_programas_estrategicos UNIQUE (fecha_corte, clave_ct, programa_estrategico_id)
);

CREATE TABLE IF NOT EXISTS stg_aulas_google (
    id SERIAL PRIMARY KEY,
    entidad_id INTEGER NOT NULL,
    municipio_id INTEGER,
    clave_ct VARCHAR(20) NOT NULL,
    nombre_ct VARCHAR(255) NOT NULL,
    inmueble VARCHAR(20),
    region_operativa_id INTEGER REFERENCES cat_regiones_operativas(id),
    aulas_asignadas INTEGER NOT NULL,
    fecha_corte DATE NOT NULL,
    fecha_actualizacion_fuente DATE,
    fecha_actualizacion DATE NOT NULL,
    CONSTRAINT uq_stg_aulas_google UNIQUE (fecha_corte, clave_ct, nombre_ct)
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
