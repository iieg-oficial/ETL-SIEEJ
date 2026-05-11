-- =============================================================================
-- V5__create_vista_comparables_general.sql  |  Pipeline: delitos_fuero_comun
-- Vista unificada 2015-2026 con re-etiquetado de tipo_delito para los
-- subtipos exclusivos de 2026 que corresponden a categorías históricas.
--
-- Lógica:
--   Rama 1 (2015-2025): pass-through sin modificaciones.
--   Rama 2 (2026): tipo_delito sobreescrito vía CASE para 10 reglas;
--                  subtipo_delito y modalidad conservan el valor original.
--                  Filas sin regla explícita pasan con tipo_delito original.
--
-- Reglas de re-etiquetado aplicadas a la rama 2026:
--   subtipo = 'Tentativa de homicidio doloso'            → 'Otros delitos que atentan contra la vida y la Integridad corporal'
--   subtipo = 'Tentativa de feminicidio'                 → 'Otros delitos que atentan contra la vida y la Integridad corporal'
--   subtipo = 'Tentativa de extorsión presencial'        → 'Otros delitos que atentan contra el patrimonio'
--   subtipo = 'Tentativa de extorsión por otros medios'  → 'Otros delitos que atentan contra el patrimonio'
--   tipo   = 'Pornografía infantil'                      → 'Trata de personas'
--   tipo   = 'Retención o sustracción de menores e incapaces' → 'Otros delitos que atentan contra la libertad personal'
--   tipo   = 'Privación ilegal de la libertad'           → 'Otros delitos que atentan contra la libertad personal'
--   tipo   = 'Discriminación'                            → 'Otros delitos contra la sociedad'
--   tipo   = 'Suplantación y usurpación de identidad'    → 'Otros delitos del fuero común'
--   tipo IN ('Delitos contra la administración de justicia','Tortura') → 'Delitos cometidos por servidores públicos'
-- =============================================================================

CREATE OR REPLACE VIEW v_delitos_comparables_general AS

-- -----------------------------------------------------------------------
-- Rama 1 — Serie histórica 2015-2025 (sin modificaciones)
-- -----------------------------------------------------------------------
SELECT
    s.anio,
    m.cve_municipio,
    m.clave_ent,
    m.entidad,
    m.municipio,
    bja.bien_juridico_afectado,
    td.tipo_delito,
    sd.subtipo_delito,
    mo.modalidad,
    t.mes,
    t.conteo
FROM stg_delitos_fuero_comun_2015_2025 s
JOIN cat_municipio              m   USING (cve_municipio)
JOIN cat_bien_juridico_afectado bja ON s.bien_juridico_afectado_id = bja.id
JOIN cat_tipo_delito            td  ON s.tipo_delito_id             = td.id
JOIN cat_subtipo_delito         sd  ON s.subtipo_delito_id          = sd.id
JOIN cat_modalidad              mo  ON s.modalidad_id               = mo.id
CROSS JOIN LATERAL (
    SELECT
        unnest(ARRAY['Enero','Febrero','Marzo','Abril','Mayo','Junio',
                     'Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']) AS mes,
        unnest(ARRAY[s.enero,s.febrero,s.marzo,s.abril,s.mayo,s.junio,
                     s.julio,s.agosto,s.septiembre,s.octubre,s.noviembre,s.diciembre]) AS conteo
) t
WHERE t.conteo IS NOT NULL AND t.conteo > 0

UNION ALL

-- -----------------------------------------------------------------------
-- Rama 2 — Serie 2026 con re-etiquetado de tipo_delito
-- -----------------------------------------------------------------------
SELECT
    s.anio,
    m.cve_municipio,
    m.clave_ent,
    m.entidad,
    m.municipio,
    bja.bien_juridico_afectado,
    CASE
        -- Tentativas de vida/integridad → categoría histórica
        WHEN sd.subtipo_delito IN (
            'Tentativa de homicidio doloso',
            'Tentativa de feminicidio'
        )                             THEN 'Otros delitos que atentan contra la vida y la Integridad corporal'

        -- Tentativas de extorsión → categoría histórica de patrimonio
        WHEN sd.subtipo_delito IN (
            'Tentativa de extorsión presencial',
            'Tentativa de extorsión por otros medios'
        )                             THEN 'Otros delitos que atentan contra el patrimonio'

        -- Pornografía infantil → Trata de personas
        WHEN td.tipo_delito = 'Pornografía infantil'
                                      THEN 'Trata de personas'

        -- Retención y privación de libertad → libertad personal
        WHEN td.tipo_delito IN (
            'Retención o sustracción de menores e incapaces',
            'Privación ilegal de la libertad'
        )                             THEN 'Otros delitos que atentan contra la libertad personal'

        -- Discriminación → otros contra la sociedad
        WHEN td.tipo_delito = 'Discriminación'
                                      THEN 'Otros delitos contra la sociedad'

        -- Suplantación de identidad → otros del fuero común
        WHEN td.tipo_delito = 'Suplantación y usurpación de identidad'
                                      THEN 'Otros delitos del fuero común'

        -- Delitos contra la administración de justicia y tortura → servidores públicos
        WHEN td.tipo_delito IN (
            'Delitos contra la administración de justicia',
            'Tortura'
        )                             THEN 'Delitos cometidos por servidores públicos'

        -- Sin regla: conservar tipo_delito original de 2026
        ELSE td.tipo_delito
    END                                 AS tipo_delito,
    sd.subtipo_delito,
    mo.modalidad,
    t.mes,
    t.conteo
FROM stg_delitos_fuero_comun_2026 s
JOIN cat_municipio              m   USING (cve_municipio)
JOIN cat_bien_juridico_afectado bja ON s.bien_juridico_afectado_id = bja.id
JOIN cat_tipo_delito            td  ON s.tipo_delito_id             = td.id
JOIN cat_subtipo_delito         sd  ON s.subtipo_delito_id          = sd.id
JOIN cat_modalidad              mo  ON s.modalidad_id               = mo.id
CROSS JOIN LATERAL (
    SELECT
        unnest(ARRAY['Enero','Febrero','Marzo','Abril','Mayo','Junio',
                     'Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']) AS mes,
        unnest(ARRAY[s.enero,s.febrero,s.marzo,s.abril,s.mayo,s.junio,
                     s.julio,s.agosto,s.septiembre,s.octubre,s.noviembre,s.diciembre]) AS conteo
) t
WHERE t.conteo IS NOT NULL AND t.conteo > 0;
