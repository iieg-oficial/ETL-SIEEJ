-- =======================================================================
-- V4__vista.sql  |  Pipeline: pobreza_multidimensional
-- Vista analítica con nombres humanos (joins a catálogos y cvegeo).
-- =======================================================================

CREATE OR REPLACE VIEW public.vw_pobreza_multidimensional AS
SELECT
    d.id,
    d.anio,
    d.folioviv,
    d.foliohog,
    d.numren,

    -- Geografía
    e.nombre      AS entidad_nombre,
    d.ubica_geo,
    m.nomgeo      AS municipio_nombre,
    m.nom_ent     AS municipio_entidad,
    m.cve_ent,
    m.cve_mun,
    m.cvegeo,

    -- Demografía
    d.edad,
    d.sexo,
    p.nombre      AS parentesco_nombre,

    -- Indicadores de pobreza
    d.pobreza,
    d.pobreza_m,
    d.pobreza_e,
    d.vul_car,
    d.vul_ing,
    d.no_pobv,
    d.cuadrantes,
    d.carencias,
    d.i_privacion,

    -- Indicadores de carencias sociales
    d.ic_rezedu,
    d.ic_asalud,
    d.ic_segsoc,
    d.ic_cv,
    d.ic_sbv,
    d.ic_ali,
    d.ic_ali_nc,

    -- Ingreso
    d.ictpc,
    d.ict,
    d.ing_mon,
    d.ing_lab,
    d.factor

FROM public.stg_pobreza_multidimensional_datos d
LEFT JOIN public.stg_pobreza_multidimensional_cat_entidad  e ON e.codigo = d.ent
LEFT JOIN public.stg_pobreza_multidimensional_cat_parentesco p ON p.codigo = d.parentesco
LEFT JOIN public.cvegeo_municipalities                       m ON m.id     = d.municipio_id;
