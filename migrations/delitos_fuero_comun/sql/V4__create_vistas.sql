-- =============================================================================
-- V4__create_vistas.sql  |  Pipeline: delitos_fuero_comun
-- Analytical views with monthly unpivot (enero..diciembre → mes, conteo).
-- Base view: v_delitos_serie_historica (UNION ALL of both staging tables).
-- Category views filter the base view for comparability rules.
-- =============================================================================

-- -----------------------------------------------------------------------------
-- v_delitos_serie_historica — full unified series (2015-2025 ∪ 2026)
-- Unpivots monthly columns into (mes, conteo) rows. Excludes NULL and zero.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_delitos_serie_historica AS
SELECT
    s.anio,
    LPAD(m.cvegeo::text, 5, '0')   AS cve_municipio,
    LPAD(m.cve_ent::text, 2, '0')  AS clave_ent,
    m.nom_ent                      AS entidad,
    m.nomgeo                       AS municipio,
    bja.bien_juridico_afectado,
    td.tipo_delito,
    sd.subtipo_delito,
    mo.modalidad,
    t.mes,
    t.conteo
FROM stg_delitos_fuero_comun_2015_2025 s
JOIN cvegeo_municipalities      m   ON s.cvegeo = m.cvegeo
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

SELECT
    s.anio,
    LPAD(m.cvegeo::text, 5, '0')   AS cve_municipio,
    LPAD(m.cve_ent::text, 2, '0')  AS clave_ent,
    m.nom_ent                      AS entidad,
    m.nomgeo                       AS municipio,
    bja.bien_juridico_afectado,
    td.tipo_delito,
    sd.subtipo_delito,
    mo.modalidad,
    t.mes,
    t.conteo
FROM stg_delitos_fuero_comun_2026 s
JOIN cvegeo_municipalities      m   ON s.cvegeo = m.cvegeo
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

-- =============================================================================
-- Category views — each filters v_delitos_serie_historica.
-- =============================================================================

-- 1. Homicidio doloso — subtipo = 'Homicidio doloso', both sources
CREATE OR REPLACE VIEW v_homicidio_doloso AS
SELECT * FROM v_delitos_serie_historica
WHERE subtipo_delito = 'Homicidio doloso';

-- 2. Tentativa de homicidio doloso — 2026 only (new category in 2026 schema)
CREATE OR REPLACE VIEW v_tentativa_homicidio_doloso AS
SELECT * FROM v_delitos_serie_historica
WHERE subtipo_delito = 'Tentativa de homicidio doloso'
  AND anio = 2026;

-- 3. Feminicidio — tipo = 'Feminicidio', excluding tentativa, both sources
CREATE OR REPLACE VIEW v_feminicidio AS
SELECT * FROM v_delitos_serie_historica
WHERE tipo_delito = 'Feminicidio'
  AND subtipo_delito <> 'Tentativa de feminicidio';

-- 4. Tentativa de feminicidio — 2026 only
CREATE OR REPLACE VIEW v_tentativa_feminicidio AS
SELECT * FROM v_delitos_serie_historica
WHERE subtipo_delito = 'Tentativa de feminicidio'
  AND anio = 2026;

-- 5. Otros delitos contra la vida e integridad corporal
--    Historical (2015-2025): tipo = 'Otros delitos que atentan contra la vida y la Integridad corporal'
--    2026: same tipo PLUS tentativa_homicidio_doloso + tentativa_feminicidio
--    (the two tentativa categories were carved out of this group in 2026)
CREATE OR REPLACE VIEW v_otros_vida_integridad AS
SELECT * FROM v_delitos_serie_historica
WHERE tipo_delito = 'Otros delitos que atentan contra la vida y la Integridad corporal'
   OR (anio = 2026
       AND subtipo_delito IN ('Tentativa de homicidio doloso', 'Tentativa de feminicidio'));

-- 6. Narcomenudeo — comparable sum across both sources
CREATE OR REPLACE VIEW v_narcomenudeo AS
SELECT * FROM v_delitos_serie_historica
WHERE subtipo_delito IN (
    'Narcomenudeo',
    'Narcomenudeo con fines de venta',
    'Narcomenudeo posesión simple'
);

-- 7. Extorsión — excluding tentativa subtipos (present only in 2026 schema)
CREATE OR REPLACE VIEW v_extorsion AS
SELECT * FROM v_delitos_serie_historica
WHERE tipo_delito = 'Extorsión'
  AND subtipo_delito NOT IN (
      'Tentativa de extorsión presencial',
      'Tentativa de extorsión por otros medios'
  );

-- 8. Tentativa de extorsión — 2026 only
CREATE OR REPLACE VIEW v_tentativa_extorsion AS
SELECT * FROM v_delitos_serie_historica
WHERE subtipo_delito IN (
    'Tentativa de extorsión presencial',
    'Tentativa de extorsión por otros medios'
)
  AND anio = 2026;

-- 9. Otros delitos contra el patrimonio
--    Historical: tipo = 'Otros delitos que atentan contra el patrimonio'
--    2026: same tipo PLUS tentativa_extorsion (carved out in 2026 schema)
CREATE OR REPLACE VIEW v_otros_patrimonio AS
SELECT * FROM v_delitos_serie_historica
WHERE tipo_delito = 'Otros delitos que atentan contra el patrimonio'
   OR (anio = 2026
       AND subtipo_delito IN (
           'Tentativa de extorsión presencial',
           'Tentativa de extorsión por otros medios'
       ));

-- 10. Trata de personas — both sources
CREATE OR REPLACE VIEW v_trata_personas AS
SELECT * FROM v_delitos_serie_historica
WHERE tipo_delito IN ('Trata de personas', 'Pornografía infantil');

-- 11. Otros delitos contra la libertad personal — both sources
CREATE OR REPLACE VIEW v_otros_libertad_personal AS
SELECT * FROM v_delitos_serie_historica
WHERE tipo_delito IN (
    'Otros delitos que atentan contra la libertad personal',
    'Retención o sustracción de menores e incapaces',
    'Privación ilegal de la libertad'
);

-- 12. Otros delitos contra la libertad y seguridad sexual — both sources
CREATE OR REPLACE VIEW v_otros_libertad_sexual AS
SELECT * FROM v_delitos_serie_historica
WHERE tipo_delito IN (
    'Otros delitos contra la libertad y la seguridad sexual',
    'Violencia de género en todas sus modalidades distintas a la violencia familiar',
    'Violación a la intimidad sexual'
);

-- 13. Otros delitos contra la sociedad — both sources
CREATE OR REPLACE VIEW v_otros_sociedad AS
SELECT * FROM v_delitos_serie_historica
WHERE tipo_delito IN ('Otros delitos contra la sociedad', 'Discriminación');

-- 14. Otros delitos del fuero común — both sources
CREATE OR REPLACE VIEW v_otros_fuero_comun AS
SELECT * FROM v_delitos_serie_historica
WHERE tipo_delito IN (
    'Otros delitos del fuero común',
    'Suplantación y usurpación de identidad'
);

-- 15. Delitos cometidos por servidores públicos — both sources
CREATE OR REPLACE VIEW v_servidores_publicos AS
SELECT * FROM v_delitos_serie_historica
WHERE tipo_delito IN (
    'Delitos cometidos por servidores públicos',
    'Delitos contra la administración de justicia',
    'Tortura'
);

-- =============================================================================
-- v_delitos_comparables_general — serie unificada 2015-2026 con re-etiquetado
-- de tipo_delito para subtipos exclusivos de 2026 que corresponden a
-- categorías históricas.
--
-- Rama 1 (2015-2025): pass-through sin modificaciones.
-- Rama 2 (2026): tipo_delito sobreescrito vía CASE para 10 reglas;
--                subtipo_delito y modalidad conservan el valor original.
--                Filas sin regla explícita pasan con tipo_delito original.
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
    LPAD(m.cvegeo::text, 5, '0')   AS cve_municipio,
    LPAD(m.cve_ent::text, 2, '0')  AS clave_ent,
    m.nom_ent                      AS entidad,
    m.nomgeo                       AS municipio,
    bja.bien_juridico_afectado,
    td.tipo_delito,
    sd.subtipo_delito,
    mo.modalidad,
    t.mes,
    t.conteo
FROM stg_delitos_fuero_comun_2015_2025 s
JOIN cvegeo_municipalities      m   ON s.cvegeo = m.cvegeo
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
    LPAD(m.cvegeo::text, 5, '0')   AS cve_municipio,
    LPAD(m.cve_ent::text, 2, '0')  AS clave_ent,
    m.nom_ent                      AS entidad,
    m.nomgeo                       AS municipio,
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
JOIN cvegeo_municipalities      m   ON s.cvegeo = m.cvegeo
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
