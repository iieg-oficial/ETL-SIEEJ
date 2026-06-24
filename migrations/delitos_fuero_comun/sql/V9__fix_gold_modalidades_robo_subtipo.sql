-- =============================================================================
-- V9__fix_gold_modalidades_robo_subtipo.sql  |  Pipeline: delitos_fuero_comun
-- Corrige vw_gold_delitos_fuero_comun: agrega CTE modalidad_subtipo_robos para
-- exponer con_violencia / sin_violencia en los 6 subtipos de robo que carecían
-- de filas nivel_jerarquico='modalidad':
--   Robo de autopartes, Robo a transportista, Robo a transeúnte en vía pública,
--   Robo a institución bancaria, Robo a negocio, Robo a casa habitación.
-- Los datos existían en staging pero la CTE todas_modalidades de V6 no los
-- incluía, dejando con_violencia y sin_violencia en NULL en las vwm_ derivadas.
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. Eliminar MVs dependientes de vw_gold_delitos_fuero_comun
-- -----------------------------------------------------------------------------
DROP MATERIALIZED VIEW IF EXISTS vwm_feminicidios;
DROP MATERIALIZED VIEW IF EXISTS vwm_datos_delitos_robo_institucion_bancaria_secretariado;
DROP MATERIALIZED VIEW IF EXISTS vwm_datos_delitos_robo_transportista_secretariado;
DROP MATERIALIZED VIEW IF EXISTS vwm_datos_delitos_robo_transeunte_via_publica_secretariado;
DROP MATERIALIZED VIEW IF EXISTS vwm_datos_delitos_robo_negocio_secretariado;
DROP MATERIALIZED VIEW IF EXISTS vwm_datos_delitos_robo_casa_habitacion_secretariado;
DROP MATERIALIZED VIEW IF EXISTS vwm_datos_delitos_robo_autopartes_secretariado;
DROP MATERIALIZED VIEW IF EXISTS vwm_datos_delitos_robo_motocicleta_secretariado;
DROP MATERIALIZED VIEW IF EXISTS vwm_datos_delitos_robo_coche_cuatro_ruedas_secretariado;
DROP MATERIALIZED VIEW IF EXISTS vwm_datos_delitos_violencia_genero_no_familiar_secretariado;
DROP MATERIALIZED VIEW IF EXISTS vwm_datos_delitos_violencia_familiar_secretariado;
DROP MATERIALIZED VIEW IF EXISTS vwm_datos_delitos_abuso_sexual_secretariado;
DROP MATERIALIZED VIEW IF EXISTS vwm_datos_delitos_violacion_secretariado;
DROP MATERIALIZED VIEW IF EXISTS vwm_datos_delitos_lesiones_dolosas_secretariado;
DROP MATERIALIZED VIEW IF EXISTS vwm_datos_delitos_feminicidio_secretariado;
DROP MATERIALIZED VIEW IF EXISTS vwm_datos_delitos_homicidio_doloso_secretariado;

-- -----------------------------------------------------------------------------
-- 2. Eliminar gold MV
-- -----------------------------------------------------------------------------
DROP MATERIALIZED VIEW IF EXISTS vw_gold_delitos_fuero_comun;

-- -----------------------------------------------------------------------------
-- 3. Recrear vw_gold_delitos_fuero_comun con modalidad_subtipo_robos
-- -----------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS vw_gold_delitos_fuero_comun AS
WITH

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

-- A) Homicidio doloso, Lesiones dolosas, Feminicidio: modalidad directa del catálogo.
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

-- B) Robo de coche / motocicleta histórico 2015-2025.
--    El tipo de vehículo y la violencia están codificados en la columna modalidad.
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

-- C) Robo de coche / motocicleta 2026+.
--    El tipo de vehículo está en subtipo_delito; la violencia, en modalidad.
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

-- D) Con/sin violencia para los 6 subtipos de robo restantes.
--    El staging tiene modalidad_id con 'Con violencia' / 'Sin violencia' para estos subtipos,
--    pero V6 no los exponía en todas_modalidades.
modalidad_subtipo_robos AS (
    SELECT
        anio,
        mes_num,
        cve_municipio,
        bien_juridico_afectado,
        subtipo_delito                      AS delito,
        modalidad,
        SUM(conteo)                         AS carpetas_investigacion
    FROM base
    WHERE subtipo_delito IN (
        'Robo de autopartes',
        'Robo a transportista',
        'Robo a transeúnte en vía pública',
        'Robo a institución bancaria',
        'Robo a negocio',
        'Robo a casa habitación'
    )
      AND (
           modalidad ILIKE '%con violencia%'
        OR modalidad ILIKE '%sin violencia%'
      )
    GROUP BY anio, mes_num, cve_municipio, bien_juridico_afectado, subtipo_delito, modalidad
),

todas_modalidades AS (
    SELECT anio, mes_num, cve_municipio, bien_juridico_afectado, delito, modalidad, carpetas_investigacion
    FROM modalidad_directa

    UNION ALL

    SELECT anio, mes_num, cve_municipio, bien_juridico_afectado, delito, modalidad, carpetas_investigacion
    FROM modalidad_vehiculos

    UNION ALL

    SELECT anio, mes_num, cve_municipio, bien_juridico_afectado, delito, modalidad, carpetas_investigacion
    FROM modalidad_subtipo_robos
),

-- =============================================================================
-- RECONSTRUCCIÓN DE TOTALES VEHICULARES
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

-- -----------------------------------------------------------------------------
-- 4. Recrear las 16 MVs dependientes (idénticas a V7)
-- -----------------------------------------------------------------------------

CREATE MATERIALIZED VIEW IF NOT EXISTS vwm_datos_delitos_homicidio_doloso_secretariado AS
SELECT
    ROW_NUMBER() OVER (ORDER BY g.cve_municipio, g.fecha_mes)  AS fid,
    m.geom_iieg,
    m.geom_inegi,
    m.nomgeo                                                    AS nombre,
    (g.fecha_mes || '-01')::date                                AS fecha,
    '14'::VARCHAR(2)                                            AS clave_entidad,
    g.cve_municipio                                             AS clave_municipio,
    g.bien_juridico,
    g.delito,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%arma de fuego%')   AS con_arma_de_fuego,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%arma blanca%')     AS con_arma_blanca,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%otro elemento%')   AS con_otro_elemento,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%no especificado%') AS no_especificado,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%con violencia%')   AS con_violencia,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%sin violencia%')   AS sin_violencia,
    MAX(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'delito')                                              AS carpetas_investigacion,
    MAX(g.tasa_carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'delito')                                        AS tasa_carpetas_investigacion
FROM vw_gold_delitos_fuero_comun g
JOIN cvegeo_municipalities m ON m.cvegeo = g.cve_municipio::INTEGER
WHERE g.delito = 'Homicidio doloso'
GROUP BY g.fecha_mes, g.cve_municipio, g.bien_juridico, g.delito, m.geom_iieg, m.geom_inegi, m.nomgeo
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS uix_vwm_homicidio_doloso_nk  ON vwm_datos_delitos_homicidio_doloso_secretariado (clave_municipio, fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_homicidio_doloso_fecha        ON vwm_datos_delitos_homicidio_doloso_secretariado (fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_homicidio_doloso_mun          ON vwm_datos_delitos_homicidio_doloso_secretariado (clave_municipio);

CREATE MATERIALIZED VIEW IF NOT EXISTS vwm_datos_delitos_feminicidio_secretariado AS
SELECT
    ROW_NUMBER() OVER (ORDER BY g.cve_municipio, g.fecha_mes)  AS fid,
    m.geom_iieg,
    m.geom_inegi,
    m.nomgeo                                                    AS nombre,
    (g.fecha_mes || '-01')::date                                AS fecha,
    '14'::VARCHAR(2)                                            AS clave_entidad,
    g.cve_municipio                                             AS clave_municipio,
    g.bien_juridico,
    g.delito,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%arma de fuego%')   AS con_arma_de_fuego,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%arma blanca%')     AS con_arma_blanca,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%otro elemento%')   AS con_otro_elemento,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%no especificado%') AS no_especificado,
    MAX(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'delito')                                              AS carpetas_investigacion,
    MAX(g.tasa_carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'delito')                                        AS tasa_carpetas_investigacion
FROM vw_gold_delitos_fuero_comun g
JOIN cvegeo_municipalities m ON m.cvegeo = g.cve_municipio::INTEGER
WHERE g.delito = 'Feminicidio'
GROUP BY g.fecha_mes, g.cve_municipio, g.bien_juridico, g.delito, m.geom_iieg, m.geom_inegi, m.nomgeo
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS uix_vwm_feminicidio_sec_nk   ON vwm_datos_delitos_feminicidio_secretariado (clave_municipio, fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_feminicidio_sec_fecha         ON vwm_datos_delitos_feminicidio_secretariado (fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_feminicidio_sec_mun           ON vwm_datos_delitos_feminicidio_secretariado (clave_municipio);

CREATE MATERIALIZED VIEW IF NOT EXISTS vwm_datos_delitos_lesiones_dolosas_secretariado AS
SELECT
    ROW_NUMBER() OVER (ORDER BY g.cve_municipio, g.fecha_mes)  AS fid,
    m.geom_iieg,
    m.geom_inegi,
    m.nomgeo                                                    AS nombre,
    (g.fecha_mes || '-01')::date                                AS fecha,
    '14'::VARCHAR(2)                                            AS clave_entidad,
    g.cve_municipio                                             AS clave_municipio,
    g.bien_juridico,
    g.delito,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%arma de fuego%')   AS con_arma_de_fuego,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%arma blanca%')     AS con_arma_blanca,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%otro elemento%')   AS con_otro_elemento,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%no especificado%') AS no_especificado,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%con violencia%')   AS con_violencia,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%sin violencia%')   AS sin_violencia,
    MAX(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'delito')                                              AS carpetas_investigacion,
    MAX(g.tasa_carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'delito')                                        AS tasa_carpetas_investigacion
FROM vw_gold_delitos_fuero_comun g
JOIN cvegeo_municipalities m ON m.cvegeo = g.cve_municipio::INTEGER
WHERE g.delito = 'Lesiones dolosas'
GROUP BY g.fecha_mes, g.cve_municipio, g.bien_juridico, g.delito, m.geom_iieg, m.geom_inegi, m.nomgeo
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS uix_vwm_lesiones_dolosas_nk  ON vwm_datos_delitos_lesiones_dolosas_secretariado (clave_municipio, fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_lesiones_dolosas_fecha        ON vwm_datos_delitos_lesiones_dolosas_secretariado (fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_lesiones_dolosas_mun          ON vwm_datos_delitos_lesiones_dolosas_secretariado (clave_municipio);

CREATE MATERIALIZED VIEW IF NOT EXISTS vwm_datos_delitos_violacion_secretariado AS
SELECT
    ROW_NUMBER() OVER (ORDER BY g.cve_municipio, g.fecha_mes)  AS fid,
    m.geom_iieg,
    m.geom_inegi,
    m.nomgeo                                                    AS nombre,
    (g.fecha_mes || '-01')::date                                AS fecha,
    '14'::VARCHAR(2)                                            AS clave_entidad,
    g.cve_municipio                                             AS clave_municipio,
    g.bien_juridico,
    g.delito,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%arma de fuego%')   AS con_arma_de_fuego,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%arma blanca%')     AS con_arma_blanca,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%otro elemento%')   AS con_otro_elemento,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%no especificado%') AS no_especificado,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%con violencia%')   AS con_violencia,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%sin violencia%')   AS sin_violencia,
    MAX(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'delito')                                              AS carpetas_investigacion,
    MAX(g.tasa_carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'delito')                                        AS tasa_carpetas_investigacion
FROM vw_gold_delitos_fuero_comun g
JOIN cvegeo_municipalities m ON m.cvegeo = g.cve_municipio::INTEGER
WHERE g.delito = 'Violación'
GROUP BY g.fecha_mes, g.cve_municipio, g.bien_juridico, g.delito, m.geom_iieg, m.geom_inegi, m.nomgeo
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS uix_vwm_violacion_nk          ON vwm_datos_delitos_violacion_secretariado (clave_municipio, fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_violacion_fecha                ON vwm_datos_delitos_violacion_secretariado (fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_violacion_mun                  ON vwm_datos_delitos_violacion_secretariado (clave_municipio);

CREATE MATERIALIZED VIEW IF NOT EXISTS vwm_datos_delitos_abuso_sexual_secretariado AS
SELECT
    ROW_NUMBER() OVER (ORDER BY g.cve_municipio, g.fecha_mes)  AS fid,
    m.geom_iieg,
    m.geom_inegi,
    m.nomgeo                                                    AS nombre,
    (g.fecha_mes || '-01')::date                                AS fecha,
    '14'::VARCHAR(2)                                            AS clave_entidad,
    g.cve_municipio                                             AS clave_municipio,
    g.bien_juridico,
    g.delito,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%arma de fuego%')   AS con_arma_de_fuego,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%arma blanca%')     AS con_arma_blanca,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%otro elemento%')   AS con_otro_elemento,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%no especificado%') AS no_especificado,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%con violencia%')   AS con_violencia,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%sin violencia%')   AS sin_violencia,
    MAX(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'delito')                                              AS carpetas_investigacion,
    MAX(g.tasa_carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'delito')                                        AS tasa_carpetas_investigacion
FROM vw_gold_delitos_fuero_comun g
JOIN cvegeo_municipalities m ON m.cvegeo = g.cve_municipio::INTEGER
WHERE g.delito = 'Abuso sexual'
GROUP BY g.fecha_mes, g.cve_municipio, g.bien_juridico, g.delito, m.geom_iieg, m.geom_inegi, m.nomgeo
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS uix_vwm_abuso_sexual_nk       ON vwm_datos_delitos_abuso_sexual_secretariado (clave_municipio, fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_abuso_sexual_fecha             ON vwm_datos_delitos_abuso_sexual_secretariado (fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_abuso_sexual_mun               ON vwm_datos_delitos_abuso_sexual_secretariado (clave_municipio);

CREATE MATERIALIZED VIEW IF NOT EXISTS vwm_datos_delitos_violencia_familiar_secretariado AS
SELECT
    ROW_NUMBER() OVER (ORDER BY g.cve_municipio, g.fecha_mes)  AS fid,
    m.geom_iieg,
    m.geom_inegi,
    m.nomgeo                                                    AS nombre,
    (g.fecha_mes || '-01')::date                                AS fecha,
    '14'::VARCHAR(2)                                            AS clave_entidad,
    g.cve_municipio                                             AS clave_municipio,
    g.bien_juridico,
    g.delito,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%arma de fuego%')   AS con_arma_de_fuego,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%arma blanca%')     AS con_arma_blanca,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%otro elemento%')   AS con_otro_elemento,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%no especificado%') AS no_especificado,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%con violencia%')   AS con_violencia,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%sin violencia%')   AS sin_violencia,
    MAX(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'delito')                                              AS carpetas_investigacion,
    MAX(g.tasa_carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'delito')                                        AS tasa_carpetas_investigacion
FROM vw_gold_delitos_fuero_comun g
JOIN cvegeo_municipalities m ON m.cvegeo = g.cve_municipio::INTEGER
WHERE g.delito = 'Violencia familiar'
GROUP BY g.fecha_mes, g.cve_municipio, g.bien_juridico, g.delito, m.geom_iieg, m.geom_inegi, m.nomgeo
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS uix_vwm_viol_familiar_nk      ON vwm_datos_delitos_violencia_familiar_secretariado (clave_municipio, fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_viol_familiar_fecha            ON vwm_datos_delitos_violencia_familiar_secretariado (fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_viol_familiar_mun              ON vwm_datos_delitos_violencia_familiar_secretariado (clave_municipio);

CREATE MATERIALIZED VIEW IF NOT EXISTS vwm_datos_delitos_violencia_genero_no_familiar_secretariado AS
SELECT
    ROW_NUMBER() OVER (ORDER BY g.cve_municipio, g.fecha_mes)  AS fid,
    m.geom_iieg,
    m.geom_inegi,
    m.nomgeo                                                    AS nombre,
    (g.fecha_mes || '-01')::date                                AS fecha,
    '14'::VARCHAR(2)                                            AS clave_entidad,
    g.cve_municipio                                             AS clave_municipio,
    g.bien_juridico,
    g.delito,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%arma de fuego%')   AS con_arma_de_fuego,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%arma blanca%')     AS con_arma_blanca,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%otro elemento%')   AS con_otro_elemento,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%no especificado%') AS no_especificado,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%con violencia%')   AS con_violencia,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%sin violencia%')   AS sin_violencia,
    MAX(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'delito')                                              AS carpetas_investigacion,
    MAX(g.tasa_carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'delito')                                        AS tasa_carpetas_investigacion
FROM vw_gold_delitos_fuero_comun g
JOIN cvegeo_municipalities m ON m.cvegeo = g.cve_municipio::INTEGER
WHERE g.delito = 'Violencia de género en todas sus modalidades distinta a la violencia familiar'
GROUP BY g.fecha_mes, g.cve_municipio, g.bien_juridico, g.delito, m.geom_iieg, m.geom_inegi, m.nomgeo
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS uix_vwm_viol_genero_nf_nk     ON vwm_datos_delitos_violencia_genero_no_familiar_secretariado (clave_municipio, fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_viol_genero_nf_fecha           ON vwm_datos_delitos_violencia_genero_no_familiar_secretariado (fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_viol_genero_nf_mun             ON vwm_datos_delitos_violencia_genero_no_familiar_secretariado (clave_municipio);

CREATE MATERIALIZED VIEW IF NOT EXISTS vwm_datos_delitos_robo_coche_cuatro_ruedas_secretariado AS
SELECT
    ROW_NUMBER() OVER (ORDER BY g.cve_municipio, g.fecha_mes)  AS fid,
    m.geom_iieg,
    m.geom_inegi,
    m.nomgeo                                                    AS nombre,
    (g.fecha_mes || '-01')::date                                AS fecha,
    '14'::VARCHAR(2)                                            AS clave_entidad,
    g.cve_municipio                                             AS clave_municipio,
    g.bien_juridico,
    g.delito,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%arma de fuego%')   AS con_arma_de_fuego,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%arma blanca%')     AS con_arma_blanca,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%otro elemento%')   AS con_otro_elemento,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%no especificado%') AS no_especificado,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%con violencia%')   AS con_violencia,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%sin violencia%')   AS sin_violencia,
    MAX(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'delito')                                              AS carpetas_investigacion,
    MAX(g.tasa_carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'delito')                                        AS tasa_carpetas_investigacion
FROM vw_gold_delitos_fuero_comun g
JOIN cvegeo_municipalities m ON m.cvegeo = g.cve_municipio::INTEGER
WHERE g.delito = 'Robo de coche de cuatro ruedas'
GROUP BY g.fecha_mes, g.cve_municipio, g.bien_juridico, g.delito, m.geom_iieg, m.geom_inegi, m.nomgeo
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS uix_vwm_robo_coche_4r_nk      ON vwm_datos_delitos_robo_coche_cuatro_ruedas_secretariado (clave_municipio, fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_robo_coche_4r_fecha            ON vwm_datos_delitos_robo_coche_cuatro_ruedas_secretariado (fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_robo_coche_4r_mun              ON vwm_datos_delitos_robo_coche_cuatro_ruedas_secretariado (clave_municipio);

CREATE MATERIALIZED VIEW IF NOT EXISTS vwm_datos_delitos_robo_motocicleta_secretariado AS
SELECT
    ROW_NUMBER() OVER (ORDER BY g.cve_municipio, g.fecha_mes)  AS fid,
    m.geom_iieg,
    m.geom_inegi,
    m.nomgeo                                                    AS nombre,
    (g.fecha_mes || '-01')::date                                AS fecha,
    '14'::VARCHAR(2)                                            AS clave_entidad,
    g.cve_municipio                                             AS clave_municipio,
    g.bien_juridico,
    g.delito,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%arma de fuego%')   AS con_arma_de_fuego,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%arma blanca%')     AS con_arma_blanca,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%otro elemento%')   AS con_otro_elemento,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%no especificado%') AS no_especificado,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%con violencia%')   AS con_violencia,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%sin violencia%')   AS sin_violencia,
    MAX(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'delito')                                              AS carpetas_investigacion,
    MAX(g.tasa_carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'delito')                                        AS tasa_carpetas_investigacion
FROM vw_gold_delitos_fuero_comun g
JOIN cvegeo_municipalities m ON m.cvegeo = g.cve_municipio::INTEGER
WHERE g.delito = 'Robo de motocicleta'
GROUP BY g.fecha_mes, g.cve_municipio, g.bien_juridico, g.delito, m.geom_iieg, m.geom_inegi, m.nomgeo
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS uix_vwm_robo_moto_nk           ON vwm_datos_delitos_robo_motocicleta_secretariado (clave_municipio, fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_robo_moto_fecha                 ON vwm_datos_delitos_robo_motocicleta_secretariado (fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_robo_moto_mun                   ON vwm_datos_delitos_robo_motocicleta_secretariado (clave_municipio);

CREATE MATERIALIZED VIEW IF NOT EXISTS vwm_datos_delitos_robo_autopartes_secretariado AS
SELECT
    ROW_NUMBER() OVER (ORDER BY g.cve_municipio, g.fecha_mes)  AS fid,
    m.geom_iieg,
    m.geom_inegi,
    m.nomgeo                                                    AS nombre,
    (g.fecha_mes || '-01')::date                                AS fecha,
    '14'::VARCHAR(2)                                            AS clave_entidad,
    g.cve_municipio                                             AS clave_municipio,
    g.bien_juridico,
    g.delito,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%arma de fuego%')   AS con_arma_de_fuego,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%arma blanca%')     AS con_arma_blanca,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%otro elemento%')   AS con_otro_elemento,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%no especificado%') AS no_especificado,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%con violencia%')   AS con_violencia,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%sin violencia%')   AS sin_violencia,
    MAX(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'delito')                                              AS carpetas_investigacion,
    MAX(g.tasa_carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'delito')                                        AS tasa_carpetas_investigacion
FROM vw_gold_delitos_fuero_comun g
JOIN cvegeo_municipalities m ON m.cvegeo = g.cve_municipio::INTEGER
WHERE g.delito = 'Robo de autopartes'
GROUP BY g.fecha_mes, g.cve_municipio, g.bien_juridico, g.delito, m.geom_iieg, m.geom_inegi, m.nomgeo
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS uix_vwm_robo_autopartes_nk     ON vwm_datos_delitos_robo_autopartes_secretariado (clave_municipio, fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_robo_autopartes_fecha           ON vwm_datos_delitos_robo_autopartes_secretariado (fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_robo_autopartes_mun             ON vwm_datos_delitos_robo_autopartes_secretariado (clave_municipio);

CREATE MATERIALIZED VIEW IF NOT EXISTS vwm_datos_delitos_robo_casa_habitacion_secretariado AS
SELECT
    ROW_NUMBER() OVER (ORDER BY g.cve_municipio, g.fecha_mes)  AS fid,
    m.geom_iieg,
    m.geom_inegi,
    m.nomgeo                                                    AS nombre,
    (g.fecha_mes || '-01')::date                                AS fecha,
    '14'::VARCHAR(2)                                            AS clave_entidad,
    g.cve_municipio                                             AS clave_municipio,
    g.bien_juridico,
    g.delito,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%arma de fuego%')   AS con_arma_de_fuego,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%arma blanca%')     AS con_arma_blanca,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%otro elemento%')   AS con_otro_elemento,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%no especificado%') AS no_especificado,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%con violencia%')   AS con_violencia,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%sin violencia%')   AS sin_violencia,
    MAX(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'delito')                                              AS carpetas_investigacion,
    MAX(g.tasa_carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'delito')                                        AS tasa_carpetas_investigacion
FROM vw_gold_delitos_fuero_comun g
JOIN cvegeo_municipalities m ON m.cvegeo = g.cve_municipio::INTEGER
WHERE g.delito = 'Robo a casa habitación'
GROUP BY g.fecha_mes, g.cve_municipio, g.bien_juridico, g.delito, m.geom_iieg, m.geom_inegi, m.nomgeo
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS uix_vwm_robo_casa_nk           ON vwm_datos_delitos_robo_casa_habitacion_secretariado (clave_municipio, fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_robo_casa_fecha                 ON vwm_datos_delitos_robo_casa_habitacion_secretariado (fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_robo_casa_mun                   ON vwm_datos_delitos_robo_casa_habitacion_secretariado (clave_municipio);

CREATE MATERIALIZED VIEW IF NOT EXISTS vwm_datos_delitos_robo_negocio_secretariado AS
SELECT
    ROW_NUMBER() OVER (ORDER BY g.cve_municipio, g.fecha_mes)  AS fid,
    m.geom_iieg,
    m.geom_inegi,
    m.nomgeo                                                    AS nombre,
    (g.fecha_mes || '-01')::date                                AS fecha,
    '14'::VARCHAR(2)                                            AS clave_entidad,
    g.cve_municipio                                             AS clave_municipio,
    g.bien_juridico,
    g.delito,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%arma de fuego%')   AS con_arma_de_fuego,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%arma blanca%')     AS con_arma_blanca,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%otro elemento%')   AS con_otro_elemento,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%no especificado%') AS no_especificado,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%con violencia%')   AS con_violencia,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%sin violencia%')   AS sin_violencia,
    MAX(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'delito')                                              AS carpetas_investigacion,
    MAX(g.tasa_carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'delito')                                        AS tasa_carpetas_investigacion
FROM vw_gold_delitos_fuero_comun g
JOIN cvegeo_municipalities m ON m.cvegeo = g.cve_municipio::INTEGER
WHERE g.delito = 'Robo a negocio'
GROUP BY g.fecha_mes, g.cve_municipio, g.bien_juridico, g.delito, m.geom_iieg, m.geom_inegi, m.nomgeo
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS uix_vwm_robo_negocio_nk        ON vwm_datos_delitos_robo_negocio_secretariado (clave_municipio, fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_robo_negocio_fecha              ON vwm_datos_delitos_robo_negocio_secretariado (fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_robo_negocio_mun                ON vwm_datos_delitos_robo_negocio_secretariado (clave_municipio);

CREATE MATERIALIZED VIEW IF NOT EXISTS vwm_datos_delitos_robo_transeunte_via_publica_secretariado AS
SELECT
    ROW_NUMBER() OVER (ORDER BY g.cve_municipio, g.fecha_mes)  AS fid,
    m.geom_iieg,
    m.geom_inegi,
    m.nomgeo                                                    AS nombre,
    (g.fecha_mes || '-01')::date                                AS fecha,
    '14'::VARCHAR(2)                                            AS clave_entidad,
    g.cve_municipio                                             AS clave_municipio,
    g.bien_juridico,
    g.delito,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%arma de fuego%')   AS con_arma_de_fuego,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%arma blanca%')     AS con_arma_blanca,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%otro elemento%')   AS con_otro_elemento,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%no especificado%') AS no_especificado,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%con violencia%')   AS con_violencia,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%sin violencia%')   AS sin_violencia,
    MAX(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'delito')                                              AS carpetas_investigacion,
    MAX(g.tasa_carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'delito')                                        AS tasa_carpetas_investigacion
FROM vw_gold_delitos_fuero_comun g
JOIN cvegeo_municipalities m ON m.cvegeo = g.cve_municipio::INTEGER
WHERE g.delito = 'Robo a transeúnte en vía pública'
GROUP BY g.fecha_mes, g.cve_municipio, g.bien_juridico, g.delito, m.geom_iieg, m.geom_inegi, m.nomgeo
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS uix_vwm_robo_transeunte_nk     ON vwm_datos_delitos_robo_transeunte_via_publica_secretariado (clave_municipio, fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_robo_transeunte_fecha           ON vwm_datos_delitos_robo_transeunte_via_publica_secretariado (fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_robo_transeunte_mun             ON vwm_datos_delitos_robo_transeunte_via_publica_secretariado (clave_municipio);

CREATE MATERIALIZED VIEW IF NOT EXISTS vwm_datos_delitos_robo_transportista_secretariado AS
SELECT
    ROW_NUMBER() OVER (ORDER BY g.cve_municipio, g.fecha_mes)  AS fid,
    m.geom_iieg,
    m.geom_inegi,
    m.nomgeo                                                    AS nombre,
    (g.fecha_mes || '-01')::date                                AS fecha,
    '14'::VARCHAR(2)                                            AS clave_entidad,
    g.cve_municipio                                             AS clave_municipio,
    g.bien_juridico,
    g.delito,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%arma de fuego%')   AS con_arma_de_fuego,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%arma blanca%')     AS con_arma_blanca,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%otro elemento%')   AS con_otro_elemento,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%no especificado%') AS no_especificado,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%con violencia%')   AS con_violencia,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%sin violencia%')   AS sin_violencia,
    MAX(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'delito')                                              AS carpetas_investigacion,
    MAX(g.tasa_carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'delito')                                        AS tasa_carpetas_investigacion
FROM vw_gold_delitos_fuero_comun g
JOIN cvegeo_municipalities m ON m.cvegeo = g.cve_municipio::INTEGER
WHERE g.delito = 'Robo a transportista'
GROUP BY g.fecha_mes, g.cve_municipio, g.bien_juridico, g.delito, m.geom_iieg, m.geom_inegi, m.nomgeo
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS uix_vwm_robo_transportista_nk  ON vwm_datos_delitos_robo_transportista_secretariado (clave_municipio, fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_robo_transportista_fecha        ON vwm_datos_delitos_robo_transportista_secretariado (fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_robo_transportista_mun          ON vwm_datos_delitos_robo_transportista_secretariado (clave_municipio);

CREATE MATERIALIZED VIEW IF NOT EXISTS vwm_datos_delitos_robo_institucion_bancaria_secretariado AS
SELECT
    ROW_NUMBER() OVER (ORDER BY g.cve_municipio, g.fecha_mes)  AS fid,
    m.geom_iieg,
    m.geom_inegi,
    m.nomgeo                                                    AS nombre,
    (g.fecha_mes || '-01')::date                                AS fecha,
    '14'::VARCHAR(2)                                            AS clave_entidad,
    g.cve_municipio                                             AS clave_municipio,
    g.bien_juridico,
    g.delito,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%arma de fuego%')   AS con_arma_de_fuego,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%arma blanca%')     AS con_arma_blanca,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%otro elemento%')   AS con_otro_elemento,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%no especificado%') AS no_especificado,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%con violencia%')   AS con_violencia,
    SUM(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'modalidad' AND g.modalidad ILIKE '%sin violencia%')   AS sin_violencia,
    MAX(g.carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'delito')                                              AS carpetas_investigacion,
    MAX(g.tasa_carpetas_investigacion) FILTER (WHERE g.nivel_jerarquico = 'delito')                                        AS tasa_carpetas_investigacion
FROM vw_gold_delitos_fuero_comun g
JOIN cvegeo_municipalities m ON m.cvegeo = g.cve_municipio::INTEGER
WHERE g.delito = 'Robo a institución bancaria'
GROUP BY g.fecha_mes, g.cve_municipio, g.bien_juridico, g.delito, m.geom_iieg, m.geom_inegi, m.nomgeo
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS uix_vwm_robo_banco_nk          ON vwm_datos_delitos_robo_institucion_bancaria_secretariado (clave_municipio, fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_robo_banco_fecha                ON vwm_datos_delitos_robo_institucion_bancaria_secretariado (fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_robo_banco_mun                  ON vwm_datos_delitos_robo_institucion_bancaria_secretariado (clave_municipio);

CREATE MATERIALIZED VIEW IF NOT EXISTS vwm_feminicidios AS
SELECT
    ROW_NUMBER() OVER (
        ORDER BY g.cve_municipio, g.fecha_mes, g.nivel_jerarquico,
                 COALESCE(g.modalidad, '')
    )                                                           AS fid,
    m.geom_iieg,
    m.geom_inegi,
    m.nomgeo                                                    AS nombre,
    (g.fecha_mes || '-01')::date                                AS fecha,
    '14'::VARCHAR(2)                                            AS clave_entidad,
    g.cve_municipio                                             AS clave_municipio,
    g.nivel_jerarquico,
    g.modalidad,
    g.carpetas_investigacion,
    g.tasa_carpetas_investigacion
FROM vw_gold_delitos_fuero_comun g
JOIN cvegeo_municipalities m ON m.cvegeo = g.cve_municipio::INTEGER
WHERE g.delito = 'Feminicidio'
WITH NO DATA;

CREATE UNIQUE INDEX IF NOT EXISTS uix_vwm_feminicidios_nk
    ON vwm_feminicidios (clave_municipio, fecha, nivel_jerarquico, COALESCE(modalidad, ''));
CREATE INDEX IF NOT EXISTS ix_vwm_feminicidios_fecha             ON vwm_feminicidios (fecha);
CREATE INDEX IF NOT EXISTS ix_vwm_feminicidios_mun               ON vwm_feminicidios (clave_municipio);
