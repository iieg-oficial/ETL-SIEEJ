COMMENT ON TABLE cat_turnos IS 'Catálogo de turnos escolares. El id es el código del origen y no es secuencial: 120 corresponde al turno mixto matutino-vespertino.';
COMMENT ON COLUMN cat_turnos.id IS 'Código de turno asignado por la dependencia.';
COMMENT ON COLUMN cat_turnos.turno IS 'Nombre del turno (ej: Matutino, Vespertino, Mat-Vesp).';

COMMENT ON TABLE cat_medios IS 'Catálogo del medio en que se ubica el centro de trabajo: Rural o Urbana.';
COMMENT ON COLUMN cat_medios.id IS 'Identificador único del medio.';
COMMENT ON COLUMN cat_medios.medio IS 'Nombre del medio (Rural, Urbana).';

COMMENT ON TABLE cat_sostenimientos IS 'Catálogo del origen del financiamiento del centro de trabajo.';
COMMENT ON COLUMN cat_sostenimientos.id IS 'Identificador único del sostenimiento.';
COMMENT ON COLUMN cat_sostenimientos.sostenimiento IS 'Nombre del sostenimiento (Federal, Federalizado, Estatal, Particular, Autónomo).';

COMMENT ON TABLE cat_niveles IS 'Catálogo de niveles educativos que reporta la dependencia.';
COMMENT ON COLUMN cat_niveles.id IS 'Identificador único del nivel educativo.';
COMMENT ON COLUMN cat_niveles.nivel IS 'Nombre del nivel educativo (Inicial, Especial, Preescolar, Primaria, Secundaria, Bachillerato, Profesional Técnico, Superior).';

COMMENT ON TABLE cat_programas IS 'Catálogo de la modalidad educativa del centro de trabajo. No confundir con cat_programas_estrategicos, que son los programas estatales que benefician a las escuelas.';
COMMENT ON COLUMN cat_programas.id IS 'Identificador único de la modalidad educativa.';
COMMENT ON COLUMN cat_programas.programa IS 'Nombre de la modalidad educativa (Escolarizado, CENDI, CONAFE, Indígena, CAM).';

COMMENT ON TABLE cat_regiones IS 'Catálogo de las 13 regiones del estado de Jalisco. El id es el código regional del origen.';
COMMENT ON COLUMN cat_regiones.id IS 'Código de región asignado por la dependencia: 121 corresponde a Centro ZMG.';
COMMENT ON COLUMN cat_regiones.region IS 'Nombre de la región (ej: Altos Norte, Centro ZMG).';

COMMENT ON TABLE cat_localidades IS 'Catálogo de localidades. cvegeo solo cubre entidad y municipio, así que la localidad se cataloga aquí. La clave de localidad solo es única dentro de su municipio.';
COMMENT ON COLUMN cat_localidades.id IS 'Identificador único de la localidad en este pipeline.';
COMMENT ON COLUMN cat_localidades.cve_geo_id IS 'Clave geoestadística compuesta: entidad a 2 dígitos, municipio a 3 y localidad a 4.';
COMMENT ON COLUMN cat_localidades.entidad_id IS 'Clave de la entidad federativa. Referencia lógica a cvegeo_states.cve_ent.';
COMMENT ON COLUMN cat_localidades.municipio_id IS 'Clave del municipio. Referencia lógica a cvegeo_municipalities.cve_mun.';
COMMENT ON COLUMN cat_localidades.clave_localidad IS 'Clave de la localidad dentro de su municipio.';
COMMENT ON COLUMN cat_localidades.localidad IS 'Nombre de la localidad.';

COMMENT ON TABLE cat_colonias IS 'Catálogo de colonias, dependiente de la localidad que las contiene. cvegeo no cubre este nivel.';
COMMENT ON COLUMN cat_colonias.id IS 'Identificador único de la colonia en este pipeline.';
COMMENT ON COLUMN cat_colonias.localidad_id IS 'Localidad que contiene a la colonia.';
COMMENT ON COLUMN cat_colonias.clave_colonia IS 'Clave de la colonia en el origen. Queda nula cuando el origen la reporta en cero.';
COMMENT ON COLUMN cat_colonias.colonia IS 'Nombre de la colonia.';

COMMENT ON TABLE cat_programas_estrategicos IS 'Catálogo de los programas estratégicos estatales que benefician escuelas. Concepto distinto de cat_programas, que es la modalidad educativa del plantel.';
COMMENT ON COLUMN cat_programas_estrategicos.id IS 'Identificador único del programa estratégico.';
COMMENT ON COLUMN cat_programas_estrategicos.programa_estrategico IS 'Nombre del programa estratégico (ej: Vida saludable, Jalisco bilingüe, Aulas de música).';

COMMENT ON TABLE cat_regiones_operativas IS 'Regionalización operativa de la dependencia, distinta de la estatal de cat_regiones: subdivide el centro del estado en Centro 1, Centro 2 y Centro 3.';
COMMENT ON COLUMN cat_regiones_operativas.id IS 'Identificador único de la región operativa.';
COMMENT ON COLUMN cat_regiones_operativas.region_operativa IS 'Nombre de la región operativa.';

COMMENT ON TABLE stg_directorio_centros_trabajo IS 'Directorio de centros de trabajo de educación básica, especial, media superior y superior, con su estadística educativa. Una fila por combinación de centro de trabajo, turno, nivel y modalidad.';
COMMENT ON COLUMN stg_directorio_centros_trabajo.id IS 'Identificador único del registro.';
COMMENT ON COLUMN stg_directorio_centros_trabajo.entidad_id IS 'Clave de la entidad federativa. Siempre 14 (Jalisco). Referencia lógica a cvegeo_states.cve_ent.';
COMMENT ON COLUMN stg_directorio_centros_trabajo.municipio_id IS 'Clave del municipio. Referencia lógica a cvegeo_municipalities.cve_mun.';
COMMENT ON COLUMN stg_directorio_centros_trabajo.localidad_id IS 'Localidad del centro de trabajo, en cat_localidades.';
COMMENT ON COLUMN stg_directorio_centros_trabajo.colonia_id IS 'Colonia del centro de trabajo, en cat_colonias. Nula cuando el origen no reporta colonia.';
COMMENT ON COLUMN stg_directorio_centros_trabajo.clave_ct IS 'Clave del centro de trabajo (CCT), llave de relación con los demás conjuntos de la dependencia.';
COMMENT ON COLUMN stg_directorio_centros_trabajo.turno_id IS 'Turno en que opera el centro de trabajo.';
COMMENT ON COLUMN stg_directorio_centros_trabajo.nombre_ct IS 'Nombre del centro de trabajo.';
COMMENT ON COLUMN stg_directorio_centros_trabajo.domicilio IS 'Domicilio del centro de trabajo, tal como lo reporta el origen.';
COMMENT ON COLUMN stg_directorio_centros_trabajo.medio_id IS 'Medio en que se ubica el centro de trabajo: rural o urbano.';
COMMENT ON COLUMN stg_directorio_centros_trabajo.director IS 'Nombre del director. Conserva el title case sin restituir acentos, porque el origen los omite y son miles de valores distintos.';
COMMENT ON COLUMN stg_directorio_centros_trabajo.codigo_postal IS 'Código postal del domicilio. Nulo cuando el origen lo reporta en cero.';
COMMENT ON COLUMN stg_directorio_centros_trabajo.telefono IS 'Teléfono de contacto. Nulo cuando el origen lo reporta en cero.';
COMMENT ON COLUMN stg_directorio_centros_trabajo.zona_escolar IS 'Zona escolar a la que pertenece el centro de trabajo. Nula cuando el origen la reporta en 0 (sin asignar) o en 999 (no especificado).';
COMMENT ON COLUMN stg_directorio_centros_trabajo.sector IS 'Sector educativo al que pertenece el centro de trabajo. Nulo cuando el origen lo reporta en 0, que corresponde a los niveles donde el sector no aplica: bachillerato, superior, inicial, especial y casi toda secundaria.';
COMMENT ON COLUMN stg_directorio_centros_trabajo.sostenimiento_id IS 'Origen del financiamiento del centro de trabajo.';
COMMENT ON COLUMN stg_directorio_centros_trabajo.nivel_id IS 'Nivel educativo que imparte el centro de trabajo.';
COMMENT ON COLUMN stg_directorio_centros_trabajo.programa_id IS 'Modalidad educativa del centro de trabajo.';
COMMENT ON COLUMN stg_directorio_centros_trabajo.region_id IS 'Región del estado a la que pertenece el centro de trabajo.';
COMMENT ON COLUMN stg_directorio_centros_trabajo.longitud IS 'Longitud geográfica del centro de trabajo, en grados decimales.';
COMMENT ON COLUMN stg_directorio_centros_trabajo.latitud IS 'Latitud geográfica del centro de trabajo, en grados decimales.';
COMMENT ON COLUMN stg_directorio_centros_trabajo.escuelas IS 'Indicador 0/1 que marca si la fila cuenta como escuela para el total oficial. Las filas en 0 corresponden a planteles en proceso de liquidación.';
COMMENT ON COLUMN stg_directorio_centros_trabajo.hombres_matriculados IS 'Matrícula de hombres inscritos.';
COMMENT ON COLUMN stg_directorio_centros_trabajo.mujeres_matriculadas IS 'Matrícula de mujeres inscritas.';
COMMENT ON COLUMN stg_directorio_centros_trabajo.total_matriculados IS 'Matrícula total inscrita.';
COMMENT ON COLUMN stg_directorio_centros_trabajo.total_docentes_directivo IS 'Total de docentes y directivos frente a grupo.';
COMMENT ON COLUMN stg_directorio_centros_trabajo.fecha_corte IS 'Fecha a la que corresponden los datos, capturada por la dependencia en el formulario.';
COMMENT ON COLUMN stg_directorio_centros_trabajo.fecha_actualizacion_fuente IS 'Fecha en que la dependencia actualizó el conjunto de datos.';
COMMENT ON COLUMN stg_directorio_centros_trabajo.fecha_actualizacion IS 'Fecha en que el ETL cargó el registro.';

COMMENT ON TABLE stg_escuelas_programas_estrategicos IS 'Relación entre centros de trabajo y los programas estratégicos estatales que los benefician. Un centro de trabajo puede participar en varios programas, y esta relación no existe en ningún otro conjunto de la dependencia.';
COMMENT ON COLUMN stg_escuelas_programas_estrategicos.id IS 'Identificador único del registro.';
COMMENT ON COLUMN stg_escuelas_programas_estrategicos.clave_ct IS 'Clave del centro de trabajo. Sin llave foránea al directorio porque los cortes de ambos conjuntos son independientes.';
COMMENT ON COLUMN stg_escuelas_programas_estrategicos.programa_estrategico_id IS 'Programa estratégico que beneficia al centro de trabajo.';
COMMENT ON COLUMN stg_escuelas_programas_estrategicos.fecha_corte IS 'Fecha a la que corresponden los datos.';
COMMENT ON COLUMN stg_escuelas_programas_estrategicos.fecha_actualizacion_fuente IS 'Fecha en que la dependencia actualizó el conjunto de datos.';
COMMENT ON COLUMN stg_escuelas_programas_estrategicos.fecha_actualizacion IS 'Fecha en que el ETL cargó el registro.';

COMMENT ON TABLE stg_aulas_google IS 'Equipamiento tecnológico de aulas Google asignadas por centro de trabajo. Un centro de trabajo puede aparecer más de una vez cuando comparte inmueble con otra escuela.';
COMMENT ON COLUMN stg_aulas_google.id IS 'Identificador único del registro.';
COMMENT ON COLUMN stg_aulas_google.entidad_id IS 'Clave de la entidad federativa. Siempre 14 (Jalisco). Referencia lógica a cvegeo_states.cve_ent.';
COMMENT ON COLUMN stg_aulas_google.municipio_id IS 'Clave del municipio, resuelta contra cvegeo a partir del nombre que envía el origen. Queda nula cuando el nombre no coincide con el oficial.';
COMMENT ON COLUMN stg_aulas_google.clave_ct IS 'Clave del centro de trabajo. Sin llave foránea al directorio porque los cortes de ambos conjuntos son independientes.';
COMMENT ON COLUMN stg_aulas_google.nombre_ct IS 'Nombre del centro de trabajo.';
COMMENT ON COLUMN stg_aulas_google.inmueble IS 'Clave del inmueble que ocupa el centro de trabajo.';
COMMENT ON COLUMN stg_aulas_google.region_operativa_id IS 'Región operativa de la dependencia a la que pertenece el centro de trabajo.';
COMMENT ON COLUMN stg_aulas_google.aulas_asignadas IS 'Número de aulas Google asignadas al centro de trabajo.';
COMMENT ON COLUMN stg_aulas_google.fecha_corte IS 'Fecha a la que corresponden los datos.';
COMMENT ON COLUMN stg_aulas_google.fecha_actualizacion_fuente IS 'Fecha en que la dependencia actualizó el conjunto de datos.';
COMMENT ON COLUMN stg_aulas_google.fecha_actualizacion IS 'Fecha en que el ETL cargó el registro.';

COMMENT ON TABLE cargas_acervo IS 'Control de los envíos ya procesados desde Acervo. Da el watermark de la carga incremental y evita reprocesar un envío cuyo archivo no cambió.';
COMMENT ON COLUMN cargas_acervo.id IS 'Identificador único del registro de carga.';
COMMENT ON COLUMN cargas_acervo.envio_id IS 'Identificador del envío en el formulario de datasets del SIEEJ.';
COMMENT ON COLUMN cargas_acervo.conjunto IS 'Nombre del conjunto de datos tal como lo capturó la dependencia.';
COMMENT ON COLUMN cargas_acervo.object_key IS 'Ruta del archivo dentro del bucket de Acervo.';
COMMENT ON COLUMN cargas_acervo.etag IS 'Hash MD5 del contenido. Si coincide con el de la carga anterior, el archivo no cambió. No es MD5 en subidas multiparte.';
COMMENT ON COLUMN cargas_acervo.fecha_corte IS 'Fecha a la que corresponden los datos del envío.';
COMMENT ON COLUMN cargas_acervo.fecha_actualizacion_fuente IS 'Fecha en que la dependencia actualizó el conjunto de datos.';
COMMENT ON COLUMN cargas_acervo.actualizado_en IS 'Última modificación del envío. Es el watermark de la carga incremental.';
COMMENT ON COLUMN cargas_acervo.procesado_en IS 'Momento en que el ETL procesó el envío.';

COMMENT ON VIEW vw_directorio_centros_trabajo IS 'Directorio de centros de trabajo con sus catálogos resueltos. Entidad y municipio provienen de cvegeo; localidad y colonia de los catálogos propios del pipeline.';
COMMENT ON COLUMN vw_directorio_centros_trabajo.clave_ct IS 'Clave del centro de trabajo (CCT).';
COMMENT ON COLUMN vw_directorio_centros_trabajo.nombre_ct IS 'Nombre del centro de trabajo.';
COMMENT ON COLUMN vw_directorio_centros_trabajo.turno IS 'Turno en que opera el centro de trabajo.';
COMMENT ON COLUMN vw_directorio_centros_trabajo.nivel IS 'Nivel educativo que imparte.';
COMMENT ON COLUMN vw_directorio_centros_trabajo.programa IS 'Modalidad educativa del centro de trabajo.';
COMMENT ON COLUMN vw_directorio_centros_trabajo.sostenimiento IS 'Origen del financiamiento.';
COMMENT ON COLUMN vw_directorio_centros_trabajo.medio IS 'Medio en que se ubica: rural o urbano.';
COMMENT ON COLUMN vw_directorio_centros_trabajo.region IS 'Región del estado a la que pertenece.';
COMMENT ON COLUMN vw_directorio_centros_trabajo.entidad IS 'Nombre de la entidad federativa, resuelto contra cvegeo.';
COMMENT ON COLUMN vw_directorio_centros_trabajo.municipio IS 'Nombre oficial del municipio, resuelto contra cvegeo.';
COMMENT ON COLUMN vw_directorio_centros_trabajo.localidad IS 'Nombre de la localidad.';
COMMENT ON COLUMN vw_directorio_centros_trabajo.colonia IS 'Nombre de la colonia. Nulo cuando el origen no la reporta.';
COMMENT ON COLUMN vw_directorio_centros_trabajo.domicilio IS 'Domicilio del centro de trabajo.';
COMMENT ON COLUMN vw_directorio_centros_trabajo.codigo_postal IS 'Código postal del domicilio.';
COMMENT ON COLUMN vw_directorio_centros_trabajo.telefono IS 'Teléfono de contacto.';
COMMENT ON COLUMN vw_directorio_centros_trabajo.director IS 'Nombre del director.';
COMMENT ON COLUMN vw_directorio_centros_trabajo.zona_escolar IS 'Zona escolar a la que pertenece. Nula cuando el origen la reporta en 0 o en 999.';
COMMENT ON COLUMN vw_directorio_centros_trabajo.sector IS 'Sector educativo al que pertenece. Nulo en los niveles donde el sector no aplica.';
COMMENT ON COLUMN vw_directorio_centros_trabajo.longitud IS 'Longitud geográfica en grados decimales.';
COMMENT ON COLUMN vw_directorio_centros_trabajo.latitud IS 'Latitud geográfica en grados decimales.';
COMMENT ON COLUMN vw_directorio_centros_trabajo.escuelas IS 'Indicador 0/1 que marca si la fila cuenta como escuela para el total oficial.';
COMMENT ON COLUMN vw_directorio_centros_trabajo.hombres_matriculados IS 'Matrícula de hombres inscritos.';
COMMENT ON COLUMN vw_directorio_centros_trabajo.mujeres_matriculadas IS 'Matrícula de mujeres inscritas.';
COMMENT ON COLUMN vw_directorio_centros_trabajo.total_matriculados IS 'Matrícula total inscrita.';
COMMENT ON COLUMN vw_directorio_centros_trabajo.total_docentes_directivo IS 'Total de docentes y directivos frente a grupo.';
COMMENT ON COLUMN vw_directorio_centros_trabajo.fecha_corte IS 'Fecha a la que corresponden los datos.';
COMMENT ON COLUMN vw_directorio_centros_trabajo.fecha_actualizacion_fuente IS 'Fecha en que la dependencia actualizó el conjunto de datos.';
COMMENT ON COLUMN vw_directorio_centros_trabajo.fecha_actualizacion IS 'Fecha en que el ETL cargó el registro.';

COMMENT ON VIEW vw_escuelas_programas_estrategicos IS 'Relación entre centros de trabajo y los programas estratégicos estatales, con el nombre del programa resuelto.';
COMMENT ON COLUMN vw_escuelas_programas_estrategicos.clave_ct IS 'Clave del centro de trabajo (CCT).';
COMMENT ON COLUMN vw_escuelas_programas_estrategicos.programa_estrategico IS 'Nombre del programa estratégico que beneficia al centro de trabajo.';
COMMENT ON COLUMN vw_escuelas_programas_estrategicos.fecha_corte IS 'Fecha a la que corresponden los datos.';
COMMENT ON COLUMN vw_escuelas_programas_estrategicos.fecha_actualizacion_fuente IS 'Fecha en que la dependencia actualizó el conjunto de datos.';
COMMENT ON COLUMN vw_escuelas_programas_estrategicos.fecha_actualizacion IS 'Fecha en que el ETL cargó el registro.';

COMMENT ON VIEW vw_aulas_google IS 'Equipamiento de aulas Google por centro de trabajo, con la región operativa y el municipio resueltos.';
COMMENT ON COLUMN vw_aulas_google.clave_ct IS 'Clave del centro de trabajo (CCT).';
COMMENT ON COLUMN vw_aulas_google.nombre_ct IS 'Nombre del centro de trabajo.';
COMMENT ON COLUMN vw_aulas_google.inmueble IS 'Clave del inmueble que ocupa el centro de trabajo.';
COMMENT ON COLUMN vw_aulas_google.region_operativa IS 'Región operativa de la dependencia.';
COMMENT ON COLUMN vw_aulas_google.entidad IS 'Nombre de la entidad federativa, resuelto contra cvegeo.';
COMMENT ON COLUMN vw_aulas_google.municipio IS 'Nombre oficial del municipio, resuelto contra cvegeo.';
COMMENT ON COLUMN vw_aulas_google.aulas_asignadas IS 'Número de aulas Google asignadas al centro de trabajo.';
COMMENT ON COLUMN vw_aulas_google.fecha_corte IS 'Fecha a la que corresponden los datos.';
COMMENT ON COLUMN vw_aulas_google.fecha_actualizacion_fuente IS 'Fecha en que la dependencia actualizó el conjunto de datos.';
COMMENT ON COLUMN vw_aulas_google.fecha_actualizacion IS 'Fecha en que el ETL cargó el registro.';
