-- =======================================================================
-- V3__vista.sql  |  Pipeline: pobreza_multidimencional
-- Vista analítica con nombre de entidad y porcentajes clave.
-- =======================================================================

CREATE OR REPLACE VIEW public.vw_pobreza_multidimencional AS
SELECT
    d.id,
    d.cve_mun,
    d.nombre_municipio,
    e.cve_ent,
    e.nombre_entidad,
    d.anio,
    d.poblacion,

    -- Pobreza
    d.pobreza_porcentaje,
    d.pobreza_personas,
    d.pobreza_promedio,

    -- Pobreza extrema
    d.pobreza_ext_porcentaje,
    d.pobreza_ext_personas,
    d.pobreza_ext_promedio,

    -- Pobreza moderada
    d.pobreza_mod_porcentaje,
    d.pobreza_mod_personas,
    d.pobreza_mod_promedio,

    -- Vulnerables
    d.vul_carencia_porcentaje,
    d.vul_carencia_personas,
    d.vul_carencia_promedio,
    d.vul_ingreso_porcentaje,
    d.vul_ingreso_personas,

    -- No pobre
    d.no_pobre_porcentaje,
    d.no_pobre_personas,

    -- Carencias sociales
    d.rez_edu_porcentaje,        d.rez_edu_personas,
    d.car_salud_porcentaje,      d.car_salud_personas,
    d.car_seg_soc_porcentaje,    d.car_seg_soc_personas,
    d.car_viv_porcentaje,        d.car_viv_personas,
    d.car_sbv_porcentaje,        d.car_sbv_personas,
    d.car_ali_porcentaje,        d.car_ali_personas,

    -- Resumen carencias
    d.al_1_car_porcentaje,       d.al_1_car_personas,
    d.tres_mas_car_porcentaje,   d.tres_mas_car_personas,

    -- Líneas de ingreso
    d.lpi_porcentaje,            d.lpi_personas,
    d.lpei_porcentaje,           d.lpei_personas,

    d.created_at
FROM public.stg_pobreza_multidimensional_datos d
JOIN public.stg_pobreza_multidimensional_cat_entidad e
    ON d.cat_entidad_id = e.id;
