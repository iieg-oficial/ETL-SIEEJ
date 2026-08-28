CREATE TABLE IF NOT EXISTS edafologia_fragmentos_municipales (
    id SERIAL PRIMARY KEY,
    edafologia_id INTEGER NOT NULL REFERENCES edafologias(id),
    municipio_id INTEGER NOT NULL,
    fuente_limite_municipal_id INTEGER NOT NULL REFERENCES fuentes_limites_municipales(id),
    superficie_m2 DOUBLE PRECISION NOT NULL,
    superficie_ha DOUBLE PRECISION NOT NULL,
    porcentaje_poligono_fuente DOUBLE PRECISION NOT NULL,
    porcentaje_municipio_total DOUBLE PRECISION NOT NULL,
    porcentaje_cobertura_edafologica DOUBLE PRECISION NOT NULL,
    es_fragmento_pequenio BOOLEAN NOT NULL DEFAULT FALSE,
    version_fuente VARCHAR(80) NOT NULL,
    geometria geometry(MultiPolygon, 6368) NOT NULL,
    CONSTRAINT uq_edafologia_fragmentos_fuente_municipio UNIQUE (
        edafologia_id,
        municipio_id,
        fuente_limite_municipal_id
    ),
    CONSTRAINT ck_edafologia_fragmentos_superficie_m2_positiva CHECK (superficie_m2 > 0),
    CONSTRAINT ck_edafologia_fragmentos_superficie_ha_positiva CHECK (superficie_ha > 0),
    CONSTRAINT ck_edafologia_fragmentos_porcentaje_poligono_no_negativo CHECK (porcentaje_poligono_fuente >= 0),
    CONSTRAINT ck_edafologia_fragmentos_porcentaje_municipio_no_negativo CHECK (porcentaje_municipio_total >= 0),
    CONSTRAINT ck_edafologia_fragmentos_porcentaje_cobertura_no_negativo
        CHECK (porcentaje_cobertura_edafologica >= 0)
);

CREATE INDEX IF NOT EXISTS idx_edafologia_fragmentos_municipio_id
    ON edafologia_fragmentos_municipales (municipio_id);

CREATE INDEX IF NOT EXISTS idx_edafologia_fragmentos_version_fuente
    ON edafologia_fragmentos_municipales (version_fuente);

CREATE INDEX IF NOT EXISTS idx_edafologia_fragmentos_fuente_municipio_version
    ON edafologia_fragmentos_municipales (
        fuente_limite_municipal_id,
        municipio_id,
        version_fuente
    );

CREATE INDEX IF NOT EXISTS idx_edafologia_fragmentos_edafologia_id
    ON edafologia_fragmentos_municipales (edafologia_id);

CREATE INDEX IF NOT EXISTS idx_edafologia_fragmentos_fuente_limite
    ON edafologia_fragmentos_municipales (fuente_limite_municipal_id);

CREATE INDEX IF NOT EXISTS idx_edafologia_fragmentos_geometria
    ON edafologia_fragmentos_municipales USING GIST (geometria);

CREATE OR REPLACE VIEW vw_edafologia_resumenes_municipales AS
SELECT
    f.fuente_limite_municipal_id,
    f.municipio_id,
    e.version_fuente,
    e.grupo_edafologico_id,
    e.calificador_primario_id,
    e.calificador_secundario_id,
    SUM(f.superficie_m2)::DOUBLE PRECISION AS superficie_m2,
    SUM(f.superficie_ha)::DOUBLE PRECISION AS superficie_ha,
    SUM(f.porcentaje_municipio_total)::DOUBLE PRECISION AS porcentaje_municipio,
    COUNT(*)::INTEGER AS cantidad_fragmentos
FROM edafologia_fragmentos_municipales AS f
JOIN edafologias AS e
    ON e.id = f.edafologia_id
GROUP BY
    f.fuente_limite_municipal_id,
    f.municipio_id,
    e.version_fuente,
    e.grupo_edafologico_id,
    e.calificador_primario_id,
    e.calificador_secundario_id;

COMMENT ON TABLE edafologia_fragmentos_municipales IS
    'Fragmentos persistentes resultantes del overlay futuro entre edafologias y limites municipales IIEG/INEGI.';

COMMENT ON VIEW vw_edafologia_resumenes_municipales IS
    'Vista agregada por municipio, fuente de limite, version edafologica y categoria; no materializa geometria ni duplica superficies.';
