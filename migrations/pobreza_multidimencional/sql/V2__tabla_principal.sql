-- =======================================================================
-- V2__tabla_principal.sql  |  Pipeline: pobreza_multidimencional
-- Indicadores de pobreza municipal CONEVAL — formato tidy (municipio × año).
-- Fuente: Concentrado_indicadores_de_pobreza_2020.xlsx / Concentrado municipal
-- Años: 2010, 2015, 2020  |  Registros esperados: ~7,458 (2,486 municipios × 3)
-- =======================================================================

CREATE TABLE IF NOT EXISTS public.stg_pobreza_multidimencional_datos (
    id               SERIAL PRIMARY KEY,

    -- Identificadores geográficos
    cve_mun          VARCHAR(5)   NOT NULL,  -- clave INEGI 5 dígitos (ej. "01001")
    nombre_municipio VARCHAR(150),
    cat_entidad_id   INTEGER      NOT NULL
        REFERENCES public.stg_pobreza_multidimencional_cat_entidad(id),

    -- Temporalidad
    anio             SMALLINT     NOT NULL,  -- 2010 | 2015 | 2020
    poblacion        INTEGER,               -- población total del año

    -- Pobreza total
    pobreza_porcentaje      FLOAT,
    pobreza_personas        INTEGER,
    pobreza_promedio FLOAT,

    -- Pobreza extrema
    pobreza_ext_porcentaje      FLOAT,
    pobreza_ext_personas        INTEGER,
    pobreza_ext_promedio FLOAT,

    -- Pobreza moderada
    pobreza_mod_porcentaje      FLOAT,
    pobreza_mod_personas        INTEGER,
    pobreza_mod_promedio FLOAT,

    -- Vulnerables por carencia social
    vul_carencia_porcentaje      FLOAT,
    vul_carencia_personas        INTEGER,
    vul_carencia_promedio FLOAT,

    -- Vulnerables por ingreso (sin carencias_promedio en fuente)
    vul_ingreso_porcentaje  FLOAT,
    vul_ingreso_personas    INTEGER,

    -- No pobre y no vulnerable (sin carencias_promedio en fuente)
    no_pobre_porcentaje     FLOAT,
    no_pobre_personas       INTEGER,

    -- Rezago educativo
    rez_edu_porcentaje      FLOAT,
    rez_edu_personas        INTEGER,
    rez_edu_promedio FLOAT,

    -- Carencia por acceso a servicios de salud
    car_salud_porcentaje      FLOAT,
    car_salud_personas        INTEGER,
    car_salud_promedio FLOAT,

    -- Carencia por acceso a seguridad social
    car_seg_soc_porcentaje      FLOAT,
    car_seg_soc_personas        INTEGER,
    car_seg_soc_promedio FLOAT,

    -- Carencia por calidad y espacios de la vivienda
    car_viv_porcentaje      FLOAT,
    car_viv_personas        INTEGER,
    car_viv_promedio FLOAT,

    -- Carencia por acceso a servicios básicos de la vivienda
    car_sbv_porcentaje      FLOAT,
    car_sbv_personas        INTEGER,
    car_sbv_promedio FLOAT,

    -- Carencia por acceso a la alimentación
    car_ali_porcentaje      FLOAT,
    car_ali_personas        INTEGER,
    car_ali_promedio FLOAT,

    -- Población con al menos una carencia social
    al_1_car_porcentaje      FLOAT,
    al_1_car_personas        INTEGER,
    al_1_car_promedio FLOAT,

    -- Población con tres o más carencias sociales
    tres_mas_car_porcentaje      FLOAT,
    tres_mas_car_personas        INTEGER,
    tres_mas_car_promedio FLOAT,

    -- Población con ingreso inferior a la línea de pobreza
    lpi_porcentaje      FLOAT,
    lpi_personas        INTEGER,
    lpi_promedio FLOAT,

    -- Población con ingreso inferior a la línea de pobreza extrema
    lpei_porcentaje      FLOAT,
    lpei_personas        INTEGER,
    lpei_promedio FLOAT,

    created_at  TIMESTAMP DEFAULT now(),
    updated_at  TIMESTAMP DEFAULT now(),

    CONSTRAINT uq_pobreza_multidimencional_datos_cve_anio
        UNIQUE (cve_mun, anio)
);

CREATE UNIQUE INDEX IF NOT EXISTS ix_pobreza_multidimencional_datos_cve_anio
    ON public.stg_pobreza_multidimencional_datos (cve_mun, anio);

CREATE INDEX IF NOT EXISTS ix_pobreza_multidimencional_datos_anio
    ON public.stg_pobreza_multidimencional_datos (anio);

CREATE INDEX IF NOT EXISTS ix_pobreza_multidimencional_datos_entidad
    ON public.stg_pobreza_multidimencional_datos (cat_entidad_id);
