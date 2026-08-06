-- =============================================================================
-- V13__add_updated_at_historico.sql  |  Pipeline: delitos_fuero_comun
-- SESNSP revisa el histórico cada mes (correcciones a meses/años pasados), no
-- solo el año en curso. El update mensual ahora también re-carga el histórico
-- vía upsert, igual que ya hacía con la tabla 2026.
-- =============================================================================

ALTER TABLE stg_delitos_fuero_comun_2015_2025
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP NOT NULL DEFAULT NOW();
