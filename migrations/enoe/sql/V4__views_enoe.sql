CREATE OR REPLACE VIEW v_enoe_jalisco AS
SELECT
    e.id,
    e.anio,
    e.trimestre,
    m.nomgeo                          AS municipio,
    tl.descripcion                    AS tipo_localidad,
    e.sex,
    e.eda,
    e.nac_anio,
    e.habla_lengua_indigena,
    e.n_inf,
    ec.descripcion                    AS estado_civil,
    ne.descripcion                    AS nivel_educativo,
    e.cs_p13_2,
    e.clase1,
    e.clase2,
    e.clase3,
    e.dur9c,
    e.hrsocup,
    e.ingocup,
    e.ma48me1sm,
    e.emp_ppal,
    s.descripcion                     AS sector,
    o.descripcion                     AS ocupacion,
    st.descripcion                    AS situacion_trabajo,
    e.seg_soc,
    e.pre_asa,
    e.fac,
    e.es_pea,
    e.es_ocupado,
    e.es_desocupado,
    e.es_informal
FROM stg_enoe e
LEFT JOIN cvegeo_municipalities m
    ON e.municipio_id = m.cve_mun AND e.entidad_id = m.cve_ent
LEFT JOIN cat_tipo_localidad  tl ON e.tipo_localidad_id    = tl.id
LEFT JOIN cat_estado_civil    ec ON e.estado_civil_id      = ec.id
LEFT JOIN cat_nivel_educativo ne ON e.nivel_educativo_id   = ne.id
LEFT JOIN cat_sector           s ON e.sector_id            = s.id
LEFT JOIN cat_ocupacion        o ON e.ocupacion_id         = o.id
LEFT JOIN cat_situacion_trabajo st ON e.situacion_trabajo_id = st.id;

COMMENT ON VIEW v_enoe_jalisco IS 'Vista de microdatos ENOE para Jalisco con catálogos decodificados. Un registro por persona entrevistada por trimestre';
COMMENT ON COLUMN v_enoe_jalisco.id                    IS 'Llave primaria de stg_enoe';
COMMENT ON COLUMN v_enoe_jalisco.anio                  IS 'Año de levantamiento';
COMMENT ON COLUMN v_enoe_jalisco.trimestre             IS 'Trimestre de levantamiento (1–4)';
COMMENT ON COLUMN v_enoe_jalisco.municipio             IS 'Nombre del municipio de residencia';
COMMENT ON COLUMN v_enoe_jalisco.tipo_localidad        IS 'Tamaño de localidad de residencia';
COMMENT ON COLUMN v_enoe_jalisco.sex                   IS 'Sexo (1=hombre, 2=mujer)';
COMMENT ON COLUMN v_enoe_jalisco.eda                   IS 'Edad en años cumplidos';
COMMENT ON COLUMN v_enoe_jalisco.nac_anio              IS 'Año de nacimiento';
COMMENT ON COLUMN v_enoe_jalisco.habla_lengua_indigena IS 'Habla alguna lengua indígena';
COMMENT ON COLUMN v_enoe_jalisco.n_inf                 IS 'Número de hijos nacidos vivos (mujeres)';
COMMENT ON COLUMN v_enoe_jalisco.estado_civil          IS 'Estado civil o conyugal';
COMMENT ON COLUMN v_enoe_jalisco.nivel_educativo       IS 'Nivel de instrucción máximo alcanzado';
COMMENT ON COLUMN v_enoe_jalisco.cs_p13_2             IS 'Grado dentro del nivel educativo';
COMMENT ON COLUMN v_enoe_jalisco.clase1                IS '1=PEA, 2=PNEA';
COMMENT ON COLUMN v_enoe_jalisco.clase2                IS '1=ocupado, 2=desocupado, 3=PNEA disponible, 4=PNEA no disponible';
COMMENT ON COLUMN v_enoe_jalisco.clase3                IS 'Subclasificación adicional de condición de actividad';
COMMENT ON COLUMN v_enoe_jalisco.dur9c                 IS 'Horas trabajadas en 9 categorías';
COMMENT ON COLUMN v_enoe_jalisco.hrsocup               IS 'Horas en empleo principal (semana de referencia)';
COMMENT ON COLUMN v_enoe_jalisco.ingocup               IS 'Ingreso mensual por ocupación (pesos corrientes)';
COMMENT ON COLUMN v_enoe_jalisco.ma48me1sm             IS 'Múltiplo del salario mínimo mensual';
COMMENT ON COLUMN v_enoe_jalisco.emp_ppal              IS 'Posición en el trabajo principal';
COMMENT ON COLUMN v_enoe_jalisco.sector                IS 'Sector económico del empleo principal';
COMMENT ON COLUMN v_enoe_jalisco.ocupacion             IS 'Grupo de ocupación principal (11 categorías)';
COMMENT ON COLUMN v_enoe_jalisco.situacion_trabajo     IS 'Clasificación informal/formal del empleo (sector informal o fuera)';
COMMENT ON COLUMN v_enoe_jalisco.seg_soc               IS 'Acceso a seguridad social: 1=con acceso, 2=sin acceso';
COMMENT ON COLUMN v_enoe_jalisco.pre_asa               IS 'Prestaciones laborales: 1=con prestaciones, 2=sin prestaciones';
COMMENT ON COLUMN v_enoe_jalisco.fac                   IS 'Factor de expansión trimestral';
COMMENT ON COLUMN v_enoe_jalisco.es_pea                IS 'Pertenece a la Población Económicamente Activa';
COMMENT ON COLUMN v_enoe_jalisco.es_ocupado            IS 'Está ocupado';
COMMENT ON COLUMN v_enoe_jalisco.es_desocupado         IS 'Está desocupado dentro de la PEA';
COMMENT ON COLUMN v_enoe_jalisco.es_informal           IS 'Empleo informal (TIL1 INEGI): ocupado en el sector informal';

-- --------------------------------------------------------------------------

CREATE OR REPLACE VIEW v_enoe_indicadores_municipio AS
SELECT
    e.anio,
    e.trimestre,
    e.municipio_id,
    m.nomgeo                                                          AS municipio,
    COUNT(*)                                                          AS total_personas,
    SUM(e.fac)                                                        AS poblacion_ponderada,
    COUNT(*) FILTER (WHERE e.es_pea)                                  AS pea_total,
    SUM(e.fac)  FILTER (WHERE e.es_pea)                               AS pea_ponderada,
    COUNT(*) FILTER (WHERE e.es_ocupado)                              AS ocupados_total,
    SUM(e.fac)  FILTER (WHERE e.es_ocupado)                           AS ocupados_ponderados,
    COUNT(*) FILTER (WHERE e.es_desocupado)                           AS desocupados_total,
    SUM(e.fac)  FILTER (WHERE e.es_desocupado)                        AS desocupados_ponderados,
    COUNT(*) FILTER (WHERE e.es_informal)                             AS informales_total,
    SUM(e.fac)  FILTER (WHERE e.es_informal)                          AS informales_ponderados,
    COUNT(*) FILTER (WHERE e.es_ocupado AND e.sex = 1)                AS ocupados_hombres,
    COUNT(*) FILTER (WHERE e.es_ocupado AND e.sex = 2)                AS ocupadas_mujeres,
    ROUND(
        (100.0 * COUNT(*) FILTER (WHERE e.es_desocupado)
              / NULLIF(COUNT(*) FILTER (WHERE e.es_pea), 0))::numeric, 2
    )                                                                 AS tasa_desocupacion,
    ROUND(
        (100.0 * COUNT(*) FILTER (WHERE e.es_informal)
              / NULLIF(COUNT(*) FILTER (WHERE e.es_ocupado), 0))::numeric, 2
    )                                                                 AS tasa_informalidad,
    ROUND(AVG(e.ingocup) FILTER (WHERE e.es_ocupado AND e.ingocup > 0)::numeric, 2) AS ingreso_promedio
FROM stg_enoe e
LEFT JOIN cvegeo_municipalities m
    ON e.municipio_id = m.cve_mun AND e.entidad_id = m.cve_ent
GROUP BY e.anio, e.trimestre, e.municipio_id, m.nomgeo;

COMMENT ON VIEW v_enoe_indicadores_municipio IS 'Indicadores de ocupación e informalidad ENOE agregados por municipio, año y trimestre para Jalisco. Las tasas están calculadas en conteos simples (sin ponderar); los totales ponderados usan fac_tri';
COMMENT ON COLUMN v_enoe_indicadores_municipio.anio                  IS 'Año de levantamiento';
COMMENT ON COLUMN v_enoe_indicadores_municipio.trimestre             IS 'Trimestre de levantamiento (1–4)';
COMMENT ON COLUMN v_enoe_indicadores_municipio.municipio_id          IS 'Clave de municipio INEGI';
COMMENT ON COLUMN v_enoe_indicadores_municipio.municipio             IS 'Nombre del municipio';
COMMENT ON COLUMN v_enoe_indicadores_municipio.total_personas        IS 'Total de personas entrevistadas en la muestra';
COMMENT ON COLUMN v_enoe_indicadores_municipio.poblacion_ponderada   IS 'Población estimada aplicando el factor de expansión trimestral';
COMMENT ON COLUMN v_enoe_indicadores_municipio.pea_total             IS 'Personas en la PEA (clase1=1) en la muestra';
COMMENT ON COLUMN v_enoe_indicadores_municipio.pea_ponderada         IS 'PEA estimada con factor de expansión';
COMMENT ON COLUMN v_enoe_indicadores_municipio.ocupados_total        IS 'Personas ocupadas (clase2=1) en la muestra';
COMMENT ON COLUMN v_enoe_indicadores_municipio.ocupados_ponderados   IS 'Ocupados estimados con factor de expansión';
COMMENT ON COLUMN v_enoe_indicadores_municipio.desocupados_total     IS 'Personas desocupadas (clase2=2) en la muestra';
COMMENT ON COLUMN v_enoe_indicadores_municipio.desocupados_ponderados IS 'Desocupados estimados con factor de expansión';
COMMENT ON COLUMN v_enoe_indicadores_municipio.informales_total      IS 'Ocupados en el sector informal (TIL1 INEGI) en la muestra';
COMMENT ON COLUMN v_enoe_indicadores_municipio.informales_ponderados IS 'Informales estimados con factor de expansión';
COMMENT ON COLUMN v_enoe_indicadores_municipio.ocupados_hombres      IS 'Hombres ocupados en la muestra';
COMMENT ON COLUMN v_enoe_indicadores_municipio.ocupadas_mujeres      IS 'Mujeres ocupadas en la muestra';
COMMENT ON COLUMN v_enoe_indicadores_municipio.tasa_desocupacion     IS 'Tasa de desocupación (%) = desocupados / PEA × 100 (sin ponderar)';
COMMENT ON COLUMN v_enoe_indicadores_municipio.tasa_informalidad     IS 'Tasa de informalidad laboral TIL1 (%) = informales / ocupados × 100 (sin ponderar)';
COMMENT ON COLUMN v_enoe_indicadores_municipio.ingreso_promedio      IS 'Ingreso mensual promedio por ocupación en pesos corrientes (solo ocupados con ingreso > 0)';
