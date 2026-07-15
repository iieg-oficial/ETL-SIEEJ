CREATE TABLE IF NOT EXISTS edafologias (
    id SERIAL PRIMARY KEY,
    source_version VARCHAR(80) NOT NULL,
    source_objectid INTEGER NOT NULL,
    clave_wrb VARCHAR(80) NOT NULL,
    grupo_edafologico_id INTEGER NOT NULL REFERENCES grupos_edafologicos(id),
    calificador_primario_id INTEGER NOT NULL REFERENCES calificadores_edafologicos(id),
    calificador_secundario_id INTEGER NOT NULL REFERENCES calificadores_edafologicos(id),
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
    shape_leng_origen FLOAT,
    shape_area_origen FLOAT,
    source_name VARCHAR(160) NOT NULL,
    source_url TEXT NOT NULL,
    source_file_name VARCHAR(160) NOT NULL,
    source_file_sha256 VARCHAR(64) NOT NULL,
    source_downloaded_at TIMESTAMP WITH TIME ZONE,
    processed_at TIMESTAMP WITH TIME ZONE NOT NULL,
    fecha_actualizacion DATE NOT NULL,
    geom geometry(MultiPolygon, 6368) NOT NULL,
    CONSTRAINT uq_edafologias_version_objectid UNIQUE (source_version, source_objectid)
);

CREATE INDEX IF NOT EXISTS idx_edafologias_source_version
    ON edafologias (source_version);

CREATE INDEX IF NOT EXISTS idx_edafologias_source_objectid
    ON edafologias (source_objectid);

CREATE INDEX IF NOT EXISTS idx_edafologias_grupo_edafologico_id
    ON edafologias (grupo_edafologico_id);

CREATE INDEX IF NOT EXISTS idx_edafologias_calificador_primario_id
    ON edafologias (calificador_primario_id);

CREATE INDEX IF NOT EXISTS idx_edafologias_calificador_secundario_id
    ON edafologias (calificador_secundario_id);

CREATE INDEX IF NOT EXISTS idx_edafologias_geom
    ON edafologias USING GIST (geom);
