CREATE TABLE IF NOT EXISTS edafologia_fragmentos_municipales (
    id SERIAL PRIMARY KEY,
    edafologia_id INTEGER NOT NULL REFERENCES edafologias(id),
    municipality_cvegeo INTEGER NOT NULL,
    source_version VARCHAR(80) NOT NULL,
    fuente_limite_municipal_id INTEGER NOT NULL REFERENCES fuentes_limites_municipales(id),
    area_m2 DOUBLE PRECISION NOT NULL,
    area_ha DOUBLE PRECISION NOT NULL,
    pct_poligono_fuente DOUBLE PRECISION NOT NULL,
    pct_municipio_total DOUBLE PRECISION NOT NULL,
    pct_cobertura_edafologica DOUBLE PRECISION NOT NULL,
    es_fragmento_pequenio BOOLEAN NOT NULL DEFAULT FALSE,
    geom geometry(MultiPolygon, 6368) NOT NULL,
    CONSTRAINT uq_edafologia_fragmentos_fuente_municipio UNIQUE (
        edafologia_id,
        municipality_cvegeo,
        fuente_limite_municipal_id
    ),
    CONSTRAINT ck_edafologia_fragmentos_area_m2_positive CHECK (area_m2 > 0),
    CONSTRAINT ck_edafologia_fragmentos_area_ha_positive CHECK (area_ha > 0),
    CONSTRAINT ck_edafologia_fragmentos_pct_poligono_non_negative CHECK (pct_poligono_fuente >= 0),
    CONSTRAINT ck_edafologia_fragmentos_pct_municipio_non_negative CHECK (pct_municipio_total >= 0),
    CONSTRAINT ck_edafologia_fragmentos_pct_cobertura_non_negative CHECK (pct_cobertura_edafologica >= 0)
);

CREATE INDEX IF NOT EXISTS idx_edafologia_fragmentos_municipality_cvegeo
    ON edafologia_fragmentos_municipales (municipality_cvegeo);

CREATE INDEX IF NOT EXISTS idx_edafologia_fragmentos_source_version
    ON edafologia_fragmentos_municipales (source_version);

CREATE INDEX IF NOT EXISTS idx_edafologia_fragmentos_fuente_municipio_version
    ON edafologia_fragmentos_municipales (
        fuente_limite_municipal_id,
        municipality_cvegeo,
        source_version
    );

CREATE INDEX IF NOT EXISTS idx_edafologia_fragmentos_edafologia_id
    ON edafologia_fragmentos_municipales (edafologia_id);

CREATE INDEX IF NOT EXISTS idx_edafologia_fragmentos_fuente_limite
    ON edafologia_fragmentos_municipales (fuente_limite_municipal_id);

CREATE INDEX IF NOT EXISTS idx_edafologia_fragmentos_geom
    ON edafologia_fragmentos_municipales USING GIST (geom);

CREATE OR REPLACE VIEW edafologia_resumenes_municipales AS
SELECT
    f.fuente_limite_municipal_id,
    f.municipality_cvegeo,
    e.source_version,
    e.grupo_edafologico_id,
    e.calificador_primario_id,
    e.calificador_secundario_id,
    SUM(f.area_m2)::DOUBLE PRECISION AS area_m2,
    SUM(f.area_ha)::DOUBLE PRECISION AS area_ha,
    SUM(f.pct_municipio_total)::DOUBLE PRECISION AS pct_municipio,
    COUNT(*)::INTEGER AS fragment_count
FROM edafologia_fragmentos_municipales AS f
JOIN edafologias AS e
    ON e.id = f.edafologia_id
GROUP BY
    f.fuente_limite_municipal_id,
    f.municipality_cvegeo,
    e.source_version,
    e.grupo_edafologico_id,
    e.calificador_primario_id,
    e.calificador_secundario_id;

COMMENT ON TABLE edafologia_fragmentos_municipales IS
    'Fragmentos persistentes resultantes del overlay futuro entre edafologias y limites municipales IIEG/INEGI.';

COMMENT ON VIEW edafologia_resumenes_municipales IS
    'Vista agregada por municipio, fuente de limite, version edafologica y categoria; no materializa geometria ni duplica superficies.';
