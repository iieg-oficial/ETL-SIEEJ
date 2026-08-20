CREATE TABLE IF NOT EXISTS edafologias (
    id SERIAL PRIMARY KEY,
    identificador_objeto_fuente INTEGER NOT NULL,
    grupo_edafologico_id INTEGER NOT NULL REFERENCES grupos_edafologicos(id),
    calificador_primario_id INTEGER NOT NULL REFERENCES calificadores_edafologicos(id),
    calificador_secundario_id INTEGER NOT NULL REFERENCES calificadores_edafologicos(id),
    longitud_origen DOUBLE PRECISION,
    superficie_origen DOUBLE PRECISION,
    version_fuente VARCHAR(80) NOT NULL,
    clave_wrb VARCHAR(80) NOT NULL,
    grupo1_origen VARCHAR(20) NOT NULL,
    califp_g1_origen VARCHAR(20) NOT NULL,
    califs_g1_origen VARCHAR(20) NOT NULL,
    grupo2_origen VARCHAR(20),
    califp_g2_origen VARCHAR(20),
    califs_g2_origen VARCHAR(20),
    grupo3_origen VARCHAR(20),
    califp_g3_origen VARCHAR(20),
    clase_textural_origen VARCHAR(80),
    limite_superior_origen VARCHAR(80),
    fase_fisica_origen VARCHAR(80),
    fase_quimica_origen VARCHAR(80),
    nombre_fuente VARCHAR(160) NOT NULL,
    url_fuente TEXT NOT NULL,
    nombre_archivo_fuente VARCHAR(160) NOT NULL,
    sha256_archivo_fuente VARCHAR(64) NOT NULL,
    fecha_descarga_fuente TIMESTAMP WITH TIME ZONE,
    fecha_procesamiento TIMESTAMP WITH TIME ZONE NOT NULL,
    fecha_actualizacion DATE NOT NULL,
    geometria geometry(MultiPolygon, 6368) NOT NULL,
    CONSTRAINT uq_edafologias_version_fuente_identificador_objeto
        UNIQUE (version_fuente, identificador_objeto_fuente)
);

CREATE INDEX IF NOT EXISTS idx_edafologias_version_fuente
    ON edafologias (version_fuente);

CREATE INDEX IF NOT EXISTS idx_edafologias_identificador_objeto_fuente
    ON edafologias (identificador_objeto_fuente);

CREATE INDEX IF NOT EXISTS idx_edafologias_grupo_edafologico_id
    ON edafologias (grupo_edafologico_id);

CREATE INDEX IF NOT EXISTS idx_edafologias_calificador_primario_id
    ON edafologias (calificador_primario_id);

CREATE INDEX IF NOT EXISTS idx_edafologias_calificador_secundario_id
    ON edafologias (calificador_secundario_id);

CREATE INDEX IF NOT EXISTS idx_edafologias_geometria
    ON edafologias USING GIST (geometria);
