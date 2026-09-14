CREATE TABLE IF NOT EXISTS fuentes_limites_municipales (
    id INTEGER PRIMARY KEY,
    clave VARCHAR(20) NOT NULL UNIQUE,
    nombre_fuente VARCHAR(120) NOT NULL,
    descripcion TEXT NOT NULL,
    version VARCHAR(120) NOT NULL,
    procedencia TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS estadisticas_pendiente_municipales (
    id SERIAL PRIMARY KEY,
    municipality_id INTEGER NOT NULL,
    cve_mun INTEGER NOT NULL,
    cve_ent INTEGER NOT NULL CHECK (cve_ent = 14),
    cvegeo VARCHAR(5) NOT NULL,
    municipio VARCHAR(160) NOT NULL,
    fuente_limite_municipal_id INTEGER NOT NULL REFERENCES fuentes_limites_municipales(id),
    elevation_min_m DOUBLE PRECISION NOT NULL,
    elevation_max_m DOUBLE PRECISION NOT NULL,
    elevation_mean_m DOUBLE PRECISION NOT NULL,
    elevation_median_m DOUBLE PRECISION NOT NULL,
    elevation_std_m DOUBLE PRECISION NOT NULL,
    elevation_p05_m DOUBLE PRECISION NOT NULL,
    elevation_p95_m DOUBLE PRECISION NOT NULL,
    slope_degrees_min DOUBLE PRECISION NOT NULL,
    slope_degrees_max DOUBLE PRECISION NOT NULL,
    slope_degrees_mean DOUBLE PRECISION NOT NULL,
    slope_degrees_median DOUBLE PRECISION NOT NULL,
    slope_degrees_std DOUBLE PRECISION NOT NULL,
    slope_degrees_p05 DOUBLE PRECISION NOT NULL,
    slope_degrees_p95 DOUBLE PRECISION NOT NULL,
    slope_percent_mean DOUBLE PRECISION NOT NULL,
    slope_percent_median DOUBLE PRECISION NOT NULL,
    slope_percent_p95 DOUBLE PRECISION NOT NULL,
    slope_percent_max DOUBLE PRECISION NOT NULL,
    valid_pixel_count INTEGER NOT NULL CHECK (valid_pixel_count > 0),
    valid_area_ha DOUBLE PRECISION NOT NULL CHECK (valid_area_ha > 0),
    municipality_vector_area_ha DOUBLE PRECISION NOT NULL CHECK (municipality_vector_area_ha > 0),
    rasterized_area_difference_ha DOUBLE PRECISION NOT NULL,
    coverage_percent DOUBLE PRECISION NOT NULL CHECK (coverage_percent > 0),
    fecha_actualizacion DATE NOT NULL,
    CONSTRAINT uq_estadisticas_pendiente_municipio_fuente
        UNIQUE (municipality_id, fuente_limite_municipal_id),
    CONSTRAINT ck_estadisticas_pendiente_identity
        CHECK (municipality_id = cve_mun AND cvegeo::INTEGER = 14000 + cve_mun)
);

CREATE INDEX IF NOT EXISTS idx_estadisticas_pendiente_municipality_id
    ON estadisticas_pendiente_municipales (municipality_id);
CREATE INDEX IF NOT EXISTS idx_estadisticas_pendiente_fuente
    ON estadisticas_pendiente_municipales (fuente_limite_municipal_id);
