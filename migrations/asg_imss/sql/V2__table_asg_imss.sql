-- =======================================================================
-- V2: Tabla principal stg_asg_imss.
--
-- Modelo append-only (solo-inserciones):
--   * PK sintética id BIGSERIAL.
--   * Sin UNIQUE sobre llaves naturales, sin columna hash, sin SCD2.
--   * fecha_corte es el último día del mes publicado (DATE).
--   * FKs NOT NULL a todos los catálogos EXCEPTO los tres sectores
--     (sector_1_id, sector_2_id, sector_4_id) que sí admiten NULL.
--   * Filtro geográfico (entidad = 14, Jalisco) vive en transform; el
--     modelo soporta cualquier entidad por flexibilidad futura.
-- =======================================================================

CREATE TABLE IF NOT EXISTS stg_asg_imss (
    id                              BIGSERIAL    PRIMARY KEY,
    fecha_corte                     DATE         NOT NULL,
    -- FKs a catálogos (sectores nullable)
    delegacion_id                   INTEGER      NOT NULL REFERENCES cat_delegacion (id),
    subdelegacion_id                INTEGER      NOT NULL REFERENCES cat_subdelegacion (id),
    entidad_id                      INTEGER      NOT NULL REFERENCES cat_entidad (id),
    municipio_id                    INTEGER      NOT NULL REFERENCES cat_municipio (id),
    sector_1_id                     INTEGER               REFERENCES cat_sector_1 (id),
    sector_2_id                     INTEGER               REFERENCES cat_sector_2 (id),
    sector_4_id                     INTEGER               REFERENCES cat_sector_4 (id),
    tamano_registro_patronal_id     INTEGER      NOT NULL REFERENCES cat_tamano_registro_patronal (id),
    sexo_id                         INTEGER      NOT NULL REFERENCES cat_sexo (id),
    rango_edad_id                   INTEGER      NOT NULL REFERENCES cat_rango_edad (id),
    rango_salario_id                INTEGER      NOT NULL REFERENCES cat_rango_salario (id),
    rango_uma_id                    INTEGER      NOT NULL REFERENCES cat_rango_uma (id),
    -- Métricas enteras (12)
    asegurados                      INTEGER      NOT NULL,
    no_trabajadores                 INTEGER      NOT NULL,
    ta                              INTEGER      NOT NULL,
    teu                             INTEGER      NOT NULL,
    tec                             INTEGER      NOT NULL,
    tpu                             INTEGER      NOT NULL,
    tpc                             INTEGER      NOT NULL,
    ta_sal                          INTEGER      NOT NULL,
    teu_sal                         INTEGER      NOT NULL,
    tec_sal                         INTEGER      NOT NULL,
    tpu_sal                         INTEGER      NOT NULL,
    tpc_sal                         INTEGER      NOT NULL,
    -- Métricas decimales (5) — masa salarial
    masa_sal_ta                     NUMERIC(18,2) NOT NULL,
    masa_sal_teu                    NUMERIC(18,2) NOT NULL,
    masa_sal_tec                    NUMERIC(18,2) NOT NULL,
    masa_sal_tpu                    NUMERIC(18,2) NOT NULL,
    masa_sal_tpc                    NUMERIC(18,2) NOT NULL,
    -- Auditoría
    created_at                      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- Índices principales (consultas típicas: por fecha y por catálogos)
CREATE INDEX IF NOT EXISTS ix_stg_asg_imss_fecha_corte
    ON stg_asg_imss (fecha_corte);

CREATE INDEX IF NOT EXISTS ix_stg_asg_imss_delegacion
    ON stg_asg_imss (delegacion_id);

CREATE INDEX IF NOT EXISTS ix_stg_asg_imss_subdelegacion
    ON stg_asg_imss (subdelegacion_id);

CREATE INDEX IF NOT EXISTS ix_stg_asg_imss_entidad
    ON stg_asg_imss (entidad_id);

CREATE INDEX IF NOT EXISTS ix_stg_asg_imss_municipio
    ON stg_asg_imss (municipio_id);

CREATE INDEX IF NOT EXISTS ix_stg_asg_imss_sector_4
    ON stg_asg_imss (sector_4_id);

CREATE INDEX IF NOT EXISTS ix_stg_asg_imss_tamano_registro_patronal
    ON stg_asg_imss (tamano_registro_patronal_id);

CREATE INDEX IF NOT EXISTS ix_stg_asg_imss_sexo
    ON stg_asg_imss (sexo_id);

CREATE INDEX IF NOT EXISTS ix_stg_asg_imss_rango_edad
    ON stg_asg_imss (rango_edad_id);

CREATE INDEX IF NOT EXISTS ix_stg_asg_imss_rango_salario
    ON stg_asg_imss (rango_salario_id);

CREATE INDEX IF NOT EXISTS ix_stg_asg_imss_rango_uma
    ON stg_asg_imss (rango_uma_id);

COMMENT ON TABLE stg_asg_imss IS
    'Hechos IMSS-ASG (append-only). Una fila por combinación de catálogos publicada en el corte mensual de IMSS, filtrada a Jalisco (entidad=14) en transform.';
