-- =======================================================================
-- V14: vista del microdato con los catalogos ya resueltos
-- =======================================================================
-- Sin esta vista el consumidor ve enteros: un `sexo_id` no dice nada por si
-- solo. Los LEFT JOIN son deliberados: una clave que el catalogo de esa
-- edicion no publica debe salir en NULL, no desaparecer la fila.

CREATE OR REPLACE VIEW vw_nacimientos_certificados AS
SELECT
    n.id,
    n.anio,
    n.fecha_nacimiento,
    n.hora_nacimiento,

    n.cve_geo,
    m.nomgeo                   AS municipio_residencia,
    s.nom_ent                  AS entidad_residencia,
    c_loc_res.descripcion      AS localidad_residencia,

    n.edad_madre,
    n.edad_padre,
    c_indigena.descripcion     AS se_considera_indigena,
    c_lengua.descripcion       AS habla_lengua_indigena,
    c_conyugal.descripcion     AS estado_conyugal,
    c_escolaridad.descripcion  AS escolaridad,
    c_interrumpio.descripcion  AS interrumpio_estudios,
    c_ocupacion.descripcion    AS ocupacion_habitual,
    c_trabaja.descripcion      AS trabaja_actualmente,
    c_afiliacion.descripcion   AS afiliacion,

    n.numero_embarazos,
    c_prenatal.descripcion     AS atencion_prenatal,
    n.total_consultas,
    c_sobrevivio.descripcion   AS sobrevivio_parto,

    c_sexo.descripcion         AS sexo,
    n.edad_gestacional,
    n.talla,
    n.peso,

    c_producto.descripcion     AS producto_embarazo,
    n.orden_producto,
    n.total_productos,

    c_diag1.clave              AS diagnostico_1_clave,
    c_diag1.descripcion        AS diagnostico_1,
    c_diag2.clave              AS diagnostico_2_clave,
    c_diag2.descripcion        AS diagnostico_2,

    c_lugar.descripcion        AS lugar_nacimiento,
    c_clues.clave              AS clues,
    c_clues.descripcion        AS establecimiento_salud,
    n.tiempo_traslado_minutos,
    c_resolucion.descripcion   AS resolucion_embarazo,

    c_ent_parto.descripcion    AS entidad_parto,
    c_mun_parto.descripcion    AS municipio_parto,
    c_loc_parto.descripcion    AS localidad_parto,

    n.fecha_actualizacion
FROM stg_nacimientos_certificados n
LEFT JOIN cvegeo_municipalities      m              ON m.cvegeo = n.cve_geo
LEFT JOIN cvegeo_states              s              ON s.cve_ent = 14
LEFT JOIN cat_localidad              c_loc_res      ON c_loc_res.id = n.localidad_residencia_id
LEFT JOIN cat_si_no                  c_indigena     ON c_indigena.id = n.se_considera_indigena_id
LEFT JOIN cat_si_no                  c_lengua       ON c_lengua.id = n.habla_lengua_indigena_id
LEFT JOIN cat_si_no                  c_interrumpio  ON c_interrumpio.id = n.interrumpio_estudios_id
LEFT JOIN cat_si_no                  c_trabaja      ON c_trabaja.id = n.trabaja_actualmente_id
LEFT JOIN cat_si_no                  c_prenatal     ON c_prenatal.id = n.atencion_prenatal_id
LEFT JOIN cat_si_no                  c_sobrevivio   ON c_sobrevivio.id = n.sobrevivio_parto_id
LEFT JOIN cat_estado_conyugal        c_conyugal     ON c_conyugal.id = n.estado_conyugal_id
LEFT JOIN cat_escolaridad            c_escolaridad  ON c_escolaridad.id = n.escolaridad_id
LEFT JOIN cat_ocupacion_habitual     c_ocupacion    ON c_ocupacion.id = n.ocupacion_habitual_id
LEFT JOIN cat_afiliacion             c_afiliacion   ON c_afiliacion.id = n.afiliacion_id
LEFT JOIN cat_sexo                   c_sexo         ON c_sexo.id = n.sexo_id
LEFT JOIN cat_producto_embarazo      c_producto     ON c_producto.id = n.producto_embarazo_id
LEFT JOIN cat_diagnostico            c_diag1        ON c_diag1.id = n.diagnostico_1_id
LEFT JOIN cat_diagnostico            c_diag2        ON c_diag2.id = n.diagnostico_2_id
LEFT JOIN cat_lugar_nacimiento       c_lugar        ON c_lugar.id = n.lugar_nacimiento_id
LEFT JOIN cat_establecimiento_salud  c_clues        ON c_clues.id = n.establecimiento_salud_id
LEFT JOIN cat_resolucion_embarazo    c_resolucion   ON c_resolucion.id = n.resolucion_embarazo_id
LEFT JOIN cat_entidad                c_ent_parto    ON c_ent_parto.id = n.entidad_parto_id
LEFT JOIN cat_municipio              c_mun_parto    ON c_mun_parto.id = n.municipio_parto_id
LEFT JOIN cat_localidad              c_loc_parto    ON c_loc_parto.id = n.localidad_parto_id;
