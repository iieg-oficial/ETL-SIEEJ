-- Censos Economicos: tablas de catalogos + seguimiento de archivos fuente

CREATE TABLE cat_ce_catalogo_actividad (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(10) NOT NULL,
    descripcion VARCHAR(500),
    clasificador VARCHAR(50),
    CONSTRAINT uq_cat_ce_catalogo_actividad_codigo UNIQUE (codigo)
);

CREATE TABLE cat_ce_catalogo_entidad_municipio (
    id SERIAL PRIMARY KEY,
    cvegeo VARCHAR(6) NOT NULL,
    cve_ent VARCHAR(2),
    nom_ent VARCHAR(100),
    nom_abr VARCHAR(20),
    cve_mun VARCHAR(3),
    nom_mun VARCHAR(100),
    CONSTRAINT uq_cat_ce_catalogo_geo_cvegeo UNIQUE (cvegeo)
);

CREATE TABLE cat_ce_catalogo_estrato (
    id SERIAL PRIMARY KEY,
    id_estrato VARCHAR(5) NOT NULL,
    descripcion VARCHAR(200),
    CONSTRAINT uq_cat_ce_catalogo_estrato_id UNIQUE (id_estrato)
);

CREATE TABLE stg_ce_source_files (
    id SERIAL PRIMARY KEY,
    year INTEGER NOT NULL,
    slug VARCHAR(10) NOT NULL,
    filename VARCHAR(200) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_path VARCHAR(500),
    file_size INTEGER,
    sha256 VARCHAR(64),
    source_url VARCHAR(500),
    downloaded_at TIMESTAMP,
    row_count INTEGER,
    status VARCHAR(20),
    error_message TEXT,
    loaded_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT uq_stg_ce_source_files_key UNIQUE (year, slug, file_type)
);
