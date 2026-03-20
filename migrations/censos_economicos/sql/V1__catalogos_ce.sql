-- Censos Economicos: tablas de catalogos + seguimiento de archivos fuente

CREATE TABLE ce_catalogos_actividades (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(10) NOT NULL,
    descripcion VARCHAR(500),
    clasificador VARCHAR(50),
    CONSTRAINT uq_ce_catalogos_actividades_codigo UNIQUE (codigo)
);

CREATE TABLE ce_catalogos_entidades_municipios (
    id SERIAL PRIMARY KEY,
    cvegeo VARCHAR(6) NOT NULL,
    cve_ent VARCHAR(2),
    nom_ent VARCHAR(100),
    nom_abr VARCHAR(20),
    cve_mun VARCHAR(3),
    nom_mun VARCHAR(100),
    CONSTRAINT uq_ce_catalogos_entidades_municipios_cvegeo UNIQUE (cvegeo)
);

CREATE TABLE ce_catalogos_estratos (
    id SERIAL PRIMARY KEY,
    id_estrato VARCHAR(5) NOT NULL,
    descripcion VARCHAR(200),
    CONSTRAINT uq_ce_catalogos_estratos_id_estrato UNIQUE (id_estrato)
);

CREATE TABLE ce_archivos_fuente (
    id SERIAL PRIMARY KEY,
    anio INTEGER NOT NULL,
    slug VARCHAR(10) NOT NULL,
    nombre_archivo VARCHAR(200) NOT NULL,
    tipo_archivo VARCHAR(50) NOT NULL,
    ruta_archivo VARCHAR(500),
    tamanio_archivo INTEGER,
    sha256 VARCHAR(64),
    url_fuente VARCHAR(500),
    descargado_en TIMESTAMP,
    conteo_filas INTEGER,
    estado VARCHAR(20),
    mensaje_error TEXT,
    cargado_en TIMESTAMP,
    creado_en TIMESTAMP DEFAULT NOW(),
    CONSTRAINT uq_ce_archivos_fuente_clave UNIQUE (anio, slug, tipo_archivo)
);
