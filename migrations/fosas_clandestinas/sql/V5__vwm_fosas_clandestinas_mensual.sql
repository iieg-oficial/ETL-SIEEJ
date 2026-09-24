-- Monthly aggregate by processing start date over the latest publication only:
-- each PDF reissues the full register, so summing across cuts would double count.
CREATE MATERIALIZED VIEW vwm_fosas_clandestinas_mensual AS
SELECT
    DATE_TRUNC('month', f.fecha_inicio)::date      AS fecha_periodo_seleccion,
    TO_CHAR(f.fecha_inicio, 'YYYY-MM')             AS mes_anio_inicio_procesamiento,
    COUNT(*)::integer                              AS sitios_inhumacion_clandestina,
    COALESCE(SUM(f.pre_victimas_loc), 0)::integer  AS total_preliminar_victimas_localizadas
FROM stg_fosas_clandestinas f
JOIN cat_publicaciones p
    ON p.id = f.publicacion_id
WHERE p.fecha_corte = (SELECT MAX(fecha_corte) FROM cat_publicaciones)
  AND f.fecha_inicio IS NOT NULL
GROUP BY 1, 2
WITH NO DATA;

CREATE UNIQUE INDEX uix_vwm_fosas_clandestinas_mensual_nk
    ON vwm_fosas_clandestinas_mensual (fecha_periodo_seleccion);

COMMENT ON MATERIALIZED VIEW vwm_fosas_clandestinas_mensual IS
    'Sitios de inhumación clandestina y víctimas preliminares localizadas por mes de inicio de procesamiento. Usa solo la publicación más reciente, porque cada PDF reemite el registro completo desde 2018.';
COMMENT ON COLUMN vwm_fosas_clandestinas_mensual.fecha_periodo_seleccion IS 'Primer día del mes de inicio de procesamiento.';
COMMENT ON COLUMN vwm_fosas_clandestinas_mensual.mes_anio_inicio_procesamiento IS 'Año y mes de inicio de procesamiento (YYYY-MM).';
COMMENT ON COLUMN vwm_fosas_clandestinas_mensual.sitios_inhumacion_clandestina IS 'Renglones del registro con ese mes de inicio; un sitio con varios periodos cuenta una vez por periodo.';
COMMENT ON COLUMN vwm_fosas_clandestinas_mensual.total_preliminar_victimas_localizadas IS 'Suma del total preliminar de víctimas localizadas; omite renglones sin cifra numérica.';
