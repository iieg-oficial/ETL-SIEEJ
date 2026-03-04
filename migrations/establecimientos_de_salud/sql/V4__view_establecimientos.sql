CREATE OR REPLACE VIEW v_establecimientos AS
SELECT
    e.clues,
    e.fecha_actualizacion,
    i.institucion,
    s.nom_ent AS entidad,
    m.nomgeo AS municipio,
    l.clave_localidad,
    l.localidad,
    j.jurisdiccion,
    te.tipo_establecimiento,
    t.tipologia,
    st.subtipologia,
    um.nombre_unidad_movil,
    um.nombre_comercial,
    tv.tipo_vialidad,
    v.vialidad,
    e.numero_exterior,
    e.numero_interior,
    ta.tipo_asentamiento,
    es.estatus_establecimiento,
    na.nivel_atencion,
    eu.estrato_unidad,
    tob.tipo_obra,
    ia.instituto_administracion,
    r.rfc,
    mm.marca,
    mm.marca_especifica,
    mm.modelo,
    pm.programa_movil,
    tum.tipo_unidad_movil,
    tm.tipologia_movil,
    mo.movimiento,
    e.fecha_ultimo_movimiento,
    mb.motivo_baja,
    e.fecha_efectiva_baja,
    e.telefono_1,
    e.extension_1,
    e.telefono_2,
    e.extension_2,
    e.fecha_construccion,
    e.fecha_inicio_operacion,
    e.latitud,
    e.longitud
FROM establecimientos e
LEFT JOIN instituciones i ON e.institucion_id = i.id
LEFT JOIN cvegeo_states s ON e.entidad_id = s.cve_ent
LEFT JOIN cvegeo_municipalities m ON e.municipio_id = m.cve_mun AND e.entidad_id = m.cve_ent
LEFT JOIN localidades l ON e.localidad_id = l.id
LEFT JOIN jurisdicciones j ON e.jurisdiccion_id = j.id
LEFT JOIN tipos_establecimiento te ON e.tipo_establecimiento_id = te.id
LEFT JOIN tipologias t ON e.tipologia_id = t.id
LEFT JOIN subtipologias st ON e.subtipologia_id = st.id
LEFT JOIN unidades_moviles um ON e.unidad_movil_id = um.id
LEFT JOIN vialidades v ON e.vialidad_id = v.id
LEFT JOIN tipos_vialidad tv ON v.tipo_vialidad_id = tv.id
LEFT JOIN tipos_asentamiento ta ON e.tipo_asentamiento_id = ta.id
LEFT JOIN estatus_establecimiento es ON e.estatus_id = es.id
LEFT JOIN nivel_atencion na ON e.nivel_atencion_id = na.id
LEFT JOIN estrato_unidad eu ON e.estrato_unidad_id = eu.id
LEFT JOIN tipos_obra tob ON e.tipo_obra_id = tob.id
LEFT JOIN institutos_administracion ia ON e.instituto_adm_id = ia.id
LEFT JOIN rfc_establecimientos r ON e.rfc_id = r.id
LEFT JOIN marcas_moviles mm ON e.marca_movil_id = mm.id
LEFT JOIN programas_moviles pm ON e.programa_movil_id = pm.id
LEFT JOIN tipos_unidad_movil tum ON e.tipo_unidad_movil_id = tum.id
LEFT JOIN tipologias_moviles tm ON e.tipologia_movil_id = tm.id
LEFT JOIN movimientos mo ON e.movimiento_id = mo.id
LEFT JOIN motivos_baja mb ON e.motivo_baja_id = mb.id;
