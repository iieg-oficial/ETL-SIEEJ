CREATE OR REPLACE VIEW mart_desaparecidos_vw AS
SELECT
    d.id,
    d.folio_estatal_busqueda,
    s.descripcion AS sexo,
    n.descripcion AS nacionalidad,
    r.descripcion AS rango_edad,
    d.fecha_reporte,
    d.fecha_desaparicion,
    e.descripcion AS estado_desaparicion,
    m.descripcion AS municipio_desaparicion,
    ed.descripcion AS estatus_desaparicion,
    d.fecha_localizacion,
    cl.descripcion AS condicion_localizacion,
    ccl.descripcion AS clasificacion_localizacion,
    el.descripcion AS estado_localizacion,
    ml.descripcion AS municipio_localizacion,
    d.fecha_cierre,
    tc.descripcion AS tipo_cierre,
    d.folio_estatal_busqueda_vinculado,
    d.carpeta_investigacion
FROM stg_desaparecidos d
LEFT JOIN cat_sexos s ON d.sexo_id = s.id
LEFT JOIN cat_nacionalidades n ON d.nacionalidad_id = n.id
LEFT JOIN cat_rangos_edades r ON d.rango_edad_id = r.id
LEFT JOIN cat_estados e ON d.estado_desaparicion_id = e.id
LEFT JOIN cat_municipios m ON d.municipio_desaparicion_id = m.id
LEFT JOIN cat_estatus_desapariciones ed ON d.estatus_desaparicion_id = ed.id
LEFT JOIN cat_condiciones_localizaciones cl ON d.condicion_localizacion_id = cl.id
LEFT JOIN cat_clasificaciones_localizaciones ccl ON d.clasificacion_localizacion_id = ccl.id
LEFT JOIN cat_estados el ON d.estado_localizacion_id = el.id
LEFT JOIN cat_municipios ml ON d.municipio_localizacion_id = ml.id
LEFT JOIN cat_tipos_cierres tc ON d.tipo_cierre_id = tc.id;