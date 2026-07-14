-- =======================================================================
-- V2: Tablas casos e historial del REPD
-- =======================================================================

-- Tabla actual: una fila vigente por FEB
CREATE TABLE IF NOT EXISTS stg_repd_casos (
    id                              SERIAL PRIMARY KEY,
    feb                             VARCHAR(64) NOT NULL,
    sexo_id                         INTEGER NOT NULL REFERENCES cat_sexo (id),
    nacionalidad_id                 INTEGER NOT NULL REFERENCES cat_nacionalidad (id),
    rango_edad_id                   INTEGER NOT NULL REFERENCES cat_rango_edad (id),
    fecha_reporte                   DATE NOT NULL,
    fecha_desaparicion              DATE,
    estado_desaparicion             VARCHAR(100),
    municipio_desaparicion_id       INTEGER,
    estatus_id                      INTEGER NOT NULL REFERENCES cat_estatus (id),
    fecha_localizacion              DATE,
    condicion_localizacion_id       INTEGER REFERENCES cat_condicion_localizacion (id),
    clasificacion_localizacion_id   INTEGER REFERENCES cat_clasificacion_localizacion (id),
    estado_localizacion             VARCHAR(100),
    municipio_localizacion_id       INTEGER,
    fecha_cierre                    DATE,
    tipo_cierre_id                  INTEGER REFERENCES cat_tipo_cierre (id),
    feb_vinculado                   VARCHAR(64),
    tiene_carpeta_investigacion     BOOLEAN,
    record_hash                     VARCHAR(64) NOT NULL,
    version_actual                  INTEGER NOT NULL DEFAULT 1,
    fecha_creacion                  TIMESTAMP DEFAULT now(),
    fecha_actualizacion             TIMESTAMP DEFAULT now(),
    CONSTRAINT uq_repd_casos_feb UNIQUE (feb)
);

CREATE UNIQUE INDEX IF NOT EXISTS ix_repd_casos_feb
    ON stg_repd_casos (feb);

-- Tabla historial: snapshot por version
CREATE TABLE IF NOT EXISTS stg_repd_casos_historial (
    id                              SERIAL PRIMARY KEY,
    caso_id                         INTEGER REFERENCES stg_repd_casos (id),
    feb                             VARCHAR(64) NOT NULL,
    numero_version                  INTEGER NOT NULL,
    es_vigente                      BOOLEAN NOT NULL DEFAULT TRUE,
    vigente_desde                   TIMESTAMP NOT NULL DEFAULT now(),
    vigente_hasta                   TIMESTAMP,
    sexo_id                         INTEGER NOT NULL REFERENCES cat_sexo (id),
    nacionalidad_id                 INTEGER NOT NULL REFERENCES cat_nacionalidad (id),
    rango_edad_id                   INTEGER NOT NULL REFERENCES cat_rango_edad (id),
    fecha_reporte                   DATE NOT NULL,
    fecha_desaparicion              DATE,
    estado_desaparicion             VARCHAR(100),
    municipio_desaparicion_id       INTEGER,
    estatus_id                      INTEGER NOT NULL REFERENCES cat_estatus (id),
    fecha_localizacion              DATE,
    condicion_localizacion_id       INTEGER REFERENCES cat_condicion_localizacion (id),
    clasificacion_localizacion_id   INTEGER REFERENCES cat_clasificacion_localizacion (id),
    estado_localizacion             VARCHAR(100),
    municipio_localizacion_id       INTEGER,
    fecha_cierre                    DATE,
    tipo_cierre_id                  INTEGER REFERENCES cat_tipo_cierre (id),
    feb_vinculado                   VARCHAR(64),
    tiene_carpeta_investigacion     BOOLEAN,
    record_hash                     VARCHAR(64) NOT NULL,
    fecha_creacion                  TIMESTAMP DEFAULT now(),
    CONSTRAINT uq_repd_casos_historial_feb_version UNIQUE (feb, numero_version)
);

CREATE INDEX IF NOT EXISTS ix_repd_casos_historial_feb
    ON stg_repd_casos_historial (feb);

CREATE INDEX IF NOT EXISTS ix_repd_casos_historial_es_vigente
    ON stg_repd_casos_historial (es_vigente);
