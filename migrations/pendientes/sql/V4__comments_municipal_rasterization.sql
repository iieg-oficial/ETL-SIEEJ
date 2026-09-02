COMMENT ON COLUMN estadisticas_pendiente_municipales.municipality_vector_area_ha IS
    'Area vectorial del municipio en EPSG:6368 para la fuente territorial de la fila.';

COMMENT ON COLUMN estadisticas_pendiente_municipales.rasterized_area_difference_ha IS
    'Area de centros de pixel validos menos area vectorial; puede ser positiva o negativa por discretizacion.';

COMMENT ON COLUMN estadisticas_pendiente_municipales.coverage_percent IS
    'Cociente entre area valida rasterizada y area vectorial; puede oscilar levemente alrededor de 100.';
