CREATE TABLE IF NOT EXISTS stg_indice_shf_vivienda_global (
    id                  SERIAL PRIMARY KEY,
    serie_global_id     INTEGER NOT NULL REFERENCES cat_serie_global (id),
    fecha               DATE NOT NULL,
    anio                SMALLINT NOT NULL,
    trimestre           SMALLINT NOT NULL,
    indice              NUMERIC(8, 2) NOT NULL,
    fecha_actualizacion DATE NOT NULL,
    CONSTRAINT uq_stg_indice_shf_vivienda_global UNIQUE (serie_global_id, anio, trimestre)
);

COMMENT ON TABLE stg_indice_shf_vivienda_global IS
    'Índice SHF de precios de la vivienda para las series sin desglose geográfico: nacional, por condición '
    '(nueva/usada), por tipo de vivienda, por segmento y por zona metropolitana. Año base 2017 = 100: el promedio '
    'de los cuatro trimestres de 2017 es exactamente 100 en las 121 series.';
COMMENT ON COLUMN stg_indice_shf_vivienda_global.id IS
    'Identificador interno del registro.';
COMMENT ON COLUMN stg_indice_shf_vivienda_global.serie_global_id IS
    'Serie a la que corresponde la medición. Referencia a cat_serie_global.id.';
COMMENT ON COLUMN stg_indice_shf_vivienda_global.fecha IS
    'Primer día del trimestre de referencia (T1 = 01-01, T2 = 04-01, T3 = 07-01, T4 = 10-01).';
COMMENT ON COLUMN stg_indice_shf_vivienda_global.anio IS
    'Año de referencia de la medición.';
COMMENT ON COLUMN stg_indice_shf_vivienda_global.trimestre IS
    'Trimestre de referencia de la medición (1 a 4).';
COMMENT ON COLUMN stg_indice_shf_vivienda_global.indice IS
    'Valor del índice de precios de la vivienda, con año base 2017 = 100.';
COMMENT ON COLUMN stg_indice_shf_vivienda_global.fecha_actualizacion IS
    'Fecha en que el pipeline cargó o actualizó el registro.';


CREATE TABLE IF NOT EXISTS stg_indice_shf_vivienda_estatal (
    id                  SERIAL PRIMARY KEY,
    entidad_id          SMALLINT NOT NULL,
    fecha               DATE NOT NULL,
    anio                SMALLINT NOT NULL,
    trimestre           SMALLINT NOT NULL,
    indice              NUMERIC(8, 2) NOT NULL,
    fecha_actualizacion DATE NOT NULL,
    CONSTRAINT uq_stg_indice_shf_vivienda_estatal UNIQUE (entidad_id, anio, trimestre)
);

COMMENT ON TABLE stg_indice_shf_vivienda_estatal IS
    'Índice SHF de precios de la vivienda desglosado por entidad federativa. Año base 2017 = 100: el promedio '
    'de los cuatro trimestres de 2017 es exactamente 100 en las 121 series.';
COMMENT ON COLUMN stg_indice_shf_vivienda_estatal.id IS
    'Identificador interno del registro.';
COMMENT ON COLUMN stg_indice_shf_vivienda_estatal.entidad_id IS
    'Clave de la entidad federativa (1 a 32) del INEGI. Referencia lógica a cvegeo_states.cve_ent, que es una tabla '
    'foránea y por eso no admite llave foránea declarada.';
COMMENT ON COLUMN stg_indice_shf_vivienda_estatal.fecha IS
    'Primer día del trimestre de referencia (T1 = 01-01, T2 = 04-01, T3 = 07-01, T4 = 10-01).';
COMMENT ON COLUMN stg_indice_shf_vivienda_estatal.anio IS
    'Año de referencia de la medición.';
COMMENT ON COLUMN stg_indice_shf_vivienda_estatal.trimestre IS
    'Trimestre de referencia de la medición (1 a 4).';
COMMENT ON COLUMN stg_indice_shf_vivienda_estatal.indice IS
    'Valor del índice de precios de la vivienda, con año base 2017 = 100.';
COMMENT ON COLUMN stg_indice_shf_vivienda_estatal.fecha_actualizacion IS
    'Fecha en que el pipeline cargó o actualizó el registro.';


CREATE TABLE IF NOT EXISTS stg_indice_shf_vivienda_municipal (
    id                  SERIAL PRIMARY KEY,
    municipio_id        INTEGER NOT NULL,
    entidad_id          SMALLINT NOT NULL,
    fecha               DATE NOT NULL,
    anio                SMALLINT NOT NULL,
    trimestre           SMALLINT NOT NULL,
    indice              NUMERIC(8, 2) NOT NULL,
    fecha_actualizacion DATE NOT NULL,
    CONSTRAINT uq_stg_indice_shf_vivienda_municipal UNIQUE (municipio_id, anio, trimestre)
);

COMMENT ON TABLE stg_indice_shf_vivienda_municipal IS
    'Índice SHF de precios de la vivienda desglosado por municipio. SHF publica una selección de municipios '
    '(74 en la edición del 2T 2026), no los 2,469 del país. Año base 2017 = 100: el promedio '
    'de los cuatro trimestres de 2017 es exactamente 100 en las 121 series.';
COMMENT ON COLUMN stg_indice_shf_vivienda_municipal.id IS
    'Identificador interno del registro.';
COMMENT ON COLUMN stg_indice_shf_vivienda_municipal.municipio_id IS
    'Clave geoestadística del municipio (cve_ent * 1000 + cve_mun). Referencia lógica a cvegeo_municipalities.cvegeo.';
COMMENT ON COLUMN stg_indice_shf_vivienda_municipal.entidad_id IS
    'Clave de la entidad federativa a la que pertenece el municipio. Se conserva porque la fuente identifica al '
    'municipio solo por nombre y hay nombres repetidos entre entidades '
    '("Benito Juárez", "Juárez").';
COMMENT ON COLUMN stg_indice_shf_vivienda_municipal.fecha IS
    'Primer día del trimestre de referencia (T1 = 01-01, T2 = 04-01, T3 = 07-01, T4 = 10-01).';
COMMENT ON COLUMN stg_indice_shf_vivienda_municipal.anio IS
    'Año de referencia de la medición.';
COMMENT ON COLUMN stg_indice_shf_vivienda_municipal.trimestre IS
    'Trimestre de referencia de la medición (1 a 4).';
COMMENT ON COLUMN stg_indice_shf_vivienda_municipal.indice IS
    'Valor del índice de precios de la vivienda, con año base 2017 = 100.';
COMMENT ON COLUMN stg_indice_shf_vivienda_municipal.fecha_actualizacion IS
    'Fecha en que el pipeline cargó o actualizó el registro.';
