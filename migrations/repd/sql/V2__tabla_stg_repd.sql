-- =======================================================================
-- V2: Tablas case_current y case_history del REPD
-- =======================================================================

-- Tabla actual: una fila vigente por FEB
CREATE TABLE IF NOT EXISTS stg_repd_case_current (
    id                              SERIAL PRIMARY KEY,
    feb                             VARCHAR(64) NOT NULL,
    sex_id                          INTEGER NOT NULL REFERENCES stg_repd_cat_sex (id),
    nationality_id                  INTEGER NOT NULL REFERENCES stg_repd_cat_nationality (id),
    age_range_id                    INTEGER NOT NULL REFERENCES stg_repd_cat_age_range (id),
    report_date                     DATE NOT NULL,
    disappearance_date              DATE,
    disappearance_state_name        VARCHAR(100),
    disappearance_municipality_id   INTEGER,
    status_id                       INTEGER NOT NULL REFERENCES stg_repd_cat_status (id),
    location_date                   DATE,
    location_condition_id           INTEGER REFERENCES stg_repd_cat_location_condition (id),
    location_classification_id      INTEGER REFERENCES stg_repd_cat_location_classification (id),
    location_state_name             VARCHAR(100),
    location_municipality_id        INTEGER,
    closure_date                    DATE,
    closure_type_id                 INTEGER REFERENCES stg_repd_cat_closure_type (id),
    linked_feb                      VARCHAR(64),
    has_investigation_folder        BOOLEAN,
    record_hash                     VARCHAR(64) NOT NULL,
    current_version                 INTEGER NOT NULL DEFAULT 1,
    created_at                      TIMESTAMP DEFAULT now(),
    updated_at                      TIMESTAMP DEFAULT now(),
    CONSTRAINT uq_repd_case_current_feb UNIQUE (feb)
);

CREATE UNIQUE INDEX IF NOT EXISTS ix_repd_case_current_feb
    ON stg_repd_case_current (feb);

-- Tabla historial: snapshot por version
CREATE TABLE IF NOT EXISTS stg_repd_case_history (
    id                              SERIAL PRIMARY KEY,
    case_current_id                 INTEGER REFERENCES stg_repd_case_current (id),
    feb                             VARCHAR(64) NOT NULL,
    version_num                     INTEGER NOT NULL,
    is_current                      BOOLEAN NOT NULL DEFAULT TRUE,
    valid_from                      TIMESTAMP NOT NULL DEFAULT now(),
    valid_to                        TIMESTAMP,
    sex_id                          INTEGER NOT NULL REFERENCES stg_repd_cat_sex (id),
    nationality_id                  INTEGER NOT NULL REFERENCES stg_repd_cat_nationality (id),
    age_range_id                    INTEGER NOT NULL REFERENCES stg_repd_cat_age_range (id),
    report_date                     DATE NOT NULL,
    disappearance_date              DATE,
    disappearance_state_name        VARCHAR(100),
    disappearance_municipality_id   INTEGER,
    status_id                       INTEGER NOT NULL REFERENCES stg_repd_cat_status (id),
    location_date                   DATE,
    location_condition_id           INTEGER REFERENCES stg_repd_cat_location_condition (id),
    location_classification_id      INTEGER REFERENCES stg_repd_cat_location_classification (id),
    location_state_name             VARCHAR(100),
    location_municipality_id        INTEGER,
    closure_date                    DATE,
    closure_type_id                 INTEGER REFERENCES stg_repd_cat_closure_type (id),
    linked_feb                      VARCHAR(64),
    has_investigation_folder        BOOLEAN,
    record_hash                     VARCHAR(64) NOT NULL,
    created_at                      TIMESTAMP DEFAULT now(),
    CONSTRAINT uq_repd_case_history_feb_version UNIQUE (feb, version_num)
);

CREATE INDEX IF NOT EXISTS ix_repd_case_history_feb
    ON stg_repd_case_history (feb);

CREATE INDEX IF NOT EXISTS ix_repd_case_history_is_current
    ON stg_repd_case_history (is_current);