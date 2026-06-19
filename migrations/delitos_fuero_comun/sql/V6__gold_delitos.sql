-- =============================================================================
-- V6__gold_delitos.sql  |  Pipeline: delitos_fuero_comun
-- Vista materializada vw_gold_delitos_fuero_comun.
-- Consolida 13 delitos con total + 5 con desagregación por modalidad para
-- Jalisco (cve_ent = 14), serie mensual 2015-presente, nivel municipal.
-- Las columnas geográficas se derivan vía JOIN a cvegeo_municipalities.
-- Tasa por 100k hab: LEFT JOIN a conapo_indicadores_demograficos (FDW de V5).
-- La MV se crea WITH NO DATA; el primer REFRESH ocurre en el DAG bootstrap.
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Drop legacy MV (renamed from gold_delitos_fuero_comun)
-- -----------------------------------------------------------------------------
DROP MATERIALIZED VIEW IF EXISTS gold_delitos_fuero_comun CASCADE;

CREATE MATERIALIZED VIEW IF NOT EXISTS vw_gold_delitos_fuero_comun AS
WITH

-- ---------------------------------------------------------------------------
-- Bases: unpivot mensual desde cada tabla staging.
-- Filtro Jalisco aplicado sobre cvegeo_municipalities.cve_ent = 14.
-- Las columnas de texto de catálogos se resuelven con JOIN a las tablas cat_.
-- ---------------------------------------------------------------------------
base_hist AS (
    SELECT
        s.anio,
        LPAD(m.cvegeo::text, 5, '0')    AS cve_municipio,
        bja.bien_juridico_afectado,
        td.tipo_delito,
        sd.subtipo_delito,
        mo.modalidad,
        t.mes_num,
        t.conteo
    FROM stg_delitos_fuero_comun_2015_2025 s
    JOIN cvegeo_municipalities      m   ON s.cvegeo = m.cvegeo
    JOIN cat_bien_juridico_afectado bja ON s.bien_juridico_afectado_id = bja.id
    JOIN cat_tipo_delito            td  ON s.tipo_delito_id             = td.id
    JOIN cat_subtipo_delito         sd  ON s.subtipo_delito_id          = sd.id
    JOIN cat_modalidad              mo  ON s.modalidad_id               = mo.id
    CROSS JOIN LATERAL (
        SELECT
            unnest(ARRAY[1,2,3,4,5,6,7,8,9,10,11,12])             AS mes_num,
            unnest(ARRAY[s.enero,s.febrero,s.marzo,s.abril,
                         s.mayo,s.junio,s.julio,s.agosto,
                         s.septiembre,s.octubre,s.noviembre,
                         s.diciembre])                              AS conteo
    ) t
    WHERE m.cve_ent = 14
      AND t.conteo IS NOT NULL AND t.conteo > 0
),

base_2026 AS (
    SELECT
        s.anio,
        LPAD(m.cvegeo::text, 5, '0')    AS cve_municipio,
        bja.bien_juridico_afectado,
        td.tipo_delito,
        sd.subtipo_delito,
        mo.modalidad,
        t.mes_num,
        t.conteo
    FROM stg_delitos_fuero_comun_2026 s
    JOIN cvegeo_municipalities      m   ON s.cvegeo = m.cvegeo
    JOIN cat_bien_juridico_afectado bja ON s.bien_juridico_afectado_id = bja.id
    JOIN cat_tipo_delito            td  ON s.tipo_delito_id             = td.id
    JOIN cat_subtipo_delito         sd  ON s.subtipo_delito_id          = sd.id
    JOIN cat_modalidad              mo  ON s.modalidad_id               = mo.id
    CROSS JOIN LATERAL (
        SELECT
            unnest(ARRAY[1,2,3,4,5,6,7,8,9,10,11,12])             AS mes_num,
            unnest(ARRAY[s.enero,s.febrero,s.marzo,s.abril,
                         s.mayo,s.junio,s.julio,s.agosto,
                         s.septiembre,s.octubre,s.noviembre,
                         s.diciembre])                              AS conteo
    ) t
    WHERE m.cve_ent = 14
      AND t.conteo IS NOT NULL AND t.conteo > 0
),

base AS (
    SELECT * FROM base_hist
    UNION ALL
    SELECT * FROM base_2026
),

-- =============================================================================
-- TOTALES  (nivel_jerarquico = 'delito')
-- =============================================================================

-- Nivel 2: agrupación por tipo_delito.
-- Cubre: Abuso sexual, Violencia familiar, Violencia de género...,
--        Feminicidio, Violación (fusiona Violación simple + equiparada).
total_tipo AS (
    SELECT
        anio,
        mes_num,
        cve_municipio,
        bien_juridico_afectado,
        CASE
            WHEN tipo_delito IN ('Violación simple', 'Violación equiparada', 'Violación')
                THEN 'Violación'
            WHEN tipo_delito ILIKE '%violencia de g_nero%distinta%'
                THEN 'Violencia de género en todas sus modalidades distinta a la violencia familiar'
            ELSE tipo_delito
        END                                 AS delito,
        SUM(conteo)                         AS carpetas_investigacion
    FROM base
    WHERE tipo_delito IN (
              'Abuso sexual',
              'Violencia familiar',
              'Feminicidio',
              'Violación simple',
              'Violación equiparada',
              'Violación'
          )
       OR tipo_delito ILIKE '%violencia de g_nero%distinta%'
    GROUP BY
        anio, mes_num, cve_municipio, bien_juridico_afectado,
        CASE
            WHEN tipo_delito IN ('Violación simple', 'Violación equiparada', 'Violación')
                THEN 'Violación'
            WHEN tipo_delito ILIKE '%violencia de g_nero%distinta%'
                THEN 'Violencia de género en todas sus modalidades distinta a la violencia familiar'
            ELSE tipo_delito
        END
),

-- Nivel 3: agrupación por subtipo_delito.
-- Cubre: Homicidio doloso, Lesiones dolosas y 6 robos específicos.
total_subtipo AS (
    SELECT
        anio,
        mes_num,
        cve_municipio,
        bien_juridico_afectado,
        subtipo_delito                      AS delito,
        SUM(conteo)                         AS carpetas_investigacion
    FROM base
    WHERE subtipo_delito IN (
        'Homicidio doloso',
        'Lesiones dolosas',
        'Robo de autopartes',
        'Robo a transportista',
        'Robo a transeúnte en vía pública',
        'Robo a institución bancaria',
        'Robo a negocio',
        'Robo a casa habitación'
    )
    GROUP BY anio, mes_num, cve_municipio, bien_juridico_afectado, subtipo_delito
),

-- =============================================================================
-- MODALIDADES  (nivel_jerarquico = 'modalidad')
-- =============================================================================

-- A) Modalidades directas del catálogo: Homicidio doloso, Lesiones dolosas, Feminicidio.
modalidad_directa AS (
    SELECT
        anio,
        mes_num,
        cve_municipio,
        bien_juridico_afectado,
        CASE
            WHEN tipo_delito = 'Feminicidio' THEN 'Feminicidio'
            ELSE subtipo_delito
        END                                 AS delito,
        modalidad,
        SUM(conteo)                         AS carpetas_investigacion
    FROM base
    WHERE subtipo_delito IN ('Homicidio doloso', 'Lesiones dolosas')
       OR tipo_delito = 'Feminicidio'
    GROUP BY
        anio, mes_num, cve_municipio, bien_juridico_afectado,
        CASE WHEN tipo_delito = 'Feminicidio' THEN 'Feminicidio' ELSE subtipo_delito END,
        modalidad
),

-- B) Vehículos histórico 2015-2025.
-- El tipo de vehículo y la violencia están codificados en la columna modalidad
-- del catálogo (ej. 'Robo de coche de 4 ruedas Con violencia').
modalidad_vehiculos_hist AS (
    SELECT
        anio,
        mes_num,
        cve_municipio,
        bien_juridico_afectado,
        CASE
            WHEN modalidad ILIKE '%coche%'
              OR modalidad ILIKE '%4 ruedas%'
              OR modalidad ILIKE '%cuatro ruedas%'
                THEN 'Robo de coche de cuatro ruedas'
            WHEN modalidad ILIKE '%motocicleta%'
                THEN 'Robo de motocicleta'
        END                                 AS delito,
        CASE
            WHEN modalidad ILIKE '%con violencia%' THEN 'Con violencia'
            WHEN modalidad ILIKE '%sin violencia%' THEN 'Sin violencia'
        END                                 AS modalidad_norm,
        SUM(conteo)                         AS carpetas_investigacion
    FROM base_hist
    WHERE subtipo_delito = 'Robo de vehículo automotor'
      AND (
           modalidad ILIKE '%coche%'
        OR modalidad ILIKE '%4 ruedas%'
        OR modalidad ILIKE '%cuatro ruedas%'
        OR modalidad ILIKE '%motocicleta%'
      )
      AND (
           modalidad ILIKE '%con violencia%'
        OR modalidad ILIKE '%sin violencia%'
      )
    GROUP BY
        anio, mes_num, cve_municipio, bien_juridico_afectado,
        CASE
            WHEN modalidad ILIKE '%coche%'
              OR modalidad ILIKE '%4 ruedas%'
              OR modalidad ILIKE '%cuatro ruedas%'
                THEN 'Robo de coche de cuatro ruedas'
            WHEN modalidad ILIKE '%motocicleta%'
                THEN 'Robo de motocicleta'
        END,
        CASE
            WHEN modalidad ILIKE '%con violencia%' THEN 'Con violencia'
            WHEN modalidad ILIKE '%sin violencia%' THEN 'Sin violencia'
        END
),

-- C) Vehículos 2026+.
-- El tipo de vehículo está en subtipo_delito; la violencia, en modalidad.
modalidad_vehiculos_2026 AS (
    SELECT
        anio,
        mes_num,
        cve_municipio,
        bien_juridico_afectado,
        CASE
            WHEN subtipo_delito ILIKE '%coche%'
             AND (subtipo_delito ILIKE '%4 ruedas%' OR subtipo_delito ILIKE '%cuatro ruedas%')
                THEN 'Robo de coche de cuatro ruedas'
            WHEN subtipo_delito ILIKE '%motocicleta%'
                THEN 'Robo de motocicleta'
        END                                 AS delito,
        CASE
            WHEN modalidad ILIKE '%con violencia%' THEN 'Con violencia'
            WHEN modalidad ILIKE '%sin violencia%' THEN 'Sin violencia'
        END                                 AS modalidad_norm,
        SUM(conteo)                         AS carpetas_investigacion
    FROM base_2026
    WHERE (
            (subtipo_delito ILIKE '%coche%'
             AND (subtipo_delito ILIKE '%4 ruedas%' OR subtipo_delito ILIKE '%cuatro ruedas%'))
         OR subtipo_delito ILIKE '%motocicleta%'
          )
      AND (
           modalidad ILIKE '%con violencia%'
        OR modalidad ILIKE '%sin violencia%'
      )
    GROUP BY
        anio, mes_num, cve_municipio, bien_juridico_afectado,
        CASE
            WHEN subtipo_delito ILIKE '%coche%'
             AND (subtipo_delito ILIKE '%4 ruedas%' OR subtipo_delito ILIKE '%cuatro ruedas%')
                THEN 'Robo de coche de cuatro ruedas'
            WHEN subtipo_delito ILIKE '%motocicleta%'
                THEN 'Robo de motocicleta'
        END,
        CASE
            WHEN modalidad ILIKE '%con violencia%' THEN 'Con violencia'
            WHEN modalidad ILIKE '%sin violencia%' THEN 'Sin violencia'
        END
),

-- Unión histórico + 2026 vehicular (descarta combinaciones sin clasificación)
modalidad_vehiculos AS (
    SELECT anio, mes_num, cve_municipio, bien_juridico_afectado,
           delito, modalidad_norm AS modalidad, carpetas_investigacion
    FROM modalidad_vehiculos_hist
    WHERE delito IS NOT NULL AND modalidad_norm IS NOT NULL

    UNION ALL

    SELECT anio, mes_num, cve_municipio, bien_juridico_afectado,
           delito, modalidad_norm AS modalidad, carpetas_investigacion
    FROM modalidad_vehiculos_2026
    WHERE delito IS NOT NULL AND modalidad_norm IS NOT NULL
),

todas_modalidades AS (
    SELECT anio, mes_num, cve_municipio, bien_juridico_afectado, delito, modalidad, carpetas_investigacion
    FROM modalidad_directa

    UNION ALL

    SELECT anio, mes_num, cve_municipio, bien_juridico_afectado, delito, modalidad, carpetas_investigacion
    FROM modalidad_vehiculos
),

-- =============================================================================
-- RECONSTRUCCIÓN DE TOTALES VEHICULARES
-- 'Robo de coche de cuatro ruedas' y 'Robo de motocicleta' no tienen regla
-- TOTAL directa; su total se genera sumando sus filas de modalidad.
-- =============================================================================
vehiculos_totales AS (
    SELECT
        anio,
        mes_num,
        cve_municipio,
        bien_juridico_afectado,
        delito,
        NULL::VARCHAR                       AS modalidad,
        SUM(carpetas_investigacion)         AS carpetas_investigacion
    FROM modalidad_vehiculos
    GROUP BY anio, mes_num, cve_municipio, bien_juridico_afectado, delito
),

todos_totales AS (
    SELECT anio, mes_num, cve_municipio, bien_juridico_afectado, delito,
           NULL::VARCHAR AS modalidad, carpetas_investigacion
    FROM total_tipo

    UNION ALL

    SELECT anio, mes_num, cve_municipio, bien_juridico_afectado, delito,
           NULL::VARCHAR AS modalidad, carpetas_investigacion
    FROM total_subtipo

    UNION ALL

    SELECT anio, mes_num, cve_municipio, bien_juridico_afectado, delito, modalidad, carpetas_investigacion
    FROM vehiculos_totales
),

combined AS (
    SELECT
        anio, mes_num, cve_municipio, bien_juridico_afectado, delito, modalidad,
        'delito'::VARCHAR                   AS nivel_jerarquico,
        carpetas_investigacion
    FROM todos_totales

    UNION ALL

    SELECT
        anio, mes_num, cve_municipio, bien_juridico_afectado, delito, modalidad,
        'modalidad'::VARCHAR                AS nivel_jerarquico,
        carpetas_investigacion
    FROM todas_modalidades
)

-- =============================================================================
-- SELECT FINAL: formato de columnas + tasa por 100k vía FDW CONAPO.
-- Join a CONAPO: municipio_id (INTEGER) = cve_municipio::integer.
-- =============================================================================
SELECT
    c.anio::SMALLINT                                            AS fecha_anio,
    TO_CHAR(make_date(c.anio::INT, c.mes_num, 1), 'YYYY-MM')  AS fecha_mes,
    '14'::VARCHAR(2)                                            AS clave_ent,
    c.cve_municipio,
    c.nivel_jerarquico,
    c.bien_juridico_afectado                                    AS bien_juridico,
    c.delito,
    c.modalidad,
    c.carpetas_investigacion,
    CASE
        WHEN p.pob_mit_mun IS NULL OR p.pob_mit_mun = 0
            THEN NULL
        ELSE ROUND(100000.0 * c.carpetas_investigacion / p.pob_mit_mun, 4)
    END::NUMERIC                                                AS tasa_carpetas_investigacion
FROM combined c
LEFT JOIN conapo_indicadores_demograficos p
    ON  p.municipio_id = c.cve_municipio::INTEGER
    AND p.anio         = c.anio::INT
WITH NO DATA;

-- =============================================================================
-- ÍNDICES
-- uix_vw_gold_delitos_nk: clave natural única, habilita REFRESH CONCURRENTLY
-- =============================================================================
CREATE UNIQUE INDEX IF NOT EXISTS uix_vw_gold_delitos_nk
    ON vw_gold_delitos_fuero_comun (
        fecha_mes,
        cve_municipio,
        nivel_jerarquico,
        delito,
        COALESCE(modalidad, '')
    );

CREATE INDEX IF NOT EXISTS ix_vw_gold_delitos_anio
    ON vw_gold_delitos_fuero_comun (fecha_anio);

CREATE INDEX IF NOT EXISTS ix_vw_gold_delitos_municipio
    ON vw_gold_delitos_fuero_comun (cve_municipio);

CREATE INDEX IF NOT EXISTS ix_vw_gold_delitos_delito
    ON vw_gold_delitos_fuero_comun (delito);
