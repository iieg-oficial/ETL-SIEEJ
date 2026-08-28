-- Comments for Edafologia schema documentation.

COMMENT ON TABLE grupos_edafologicos IS 'Catalogo versionado de grupos edafologicos principales observados en Grupo1 para Edafologia historica INEGI Serie III. Los codigos y descripciones estan transcritos y auditados en mappings.py; no se generan automaticamente desde el PDF durante la ejecucion.';
COMMENT ON COLUMN grupos_edafologicos.id IS 'Identificador autogenerado del grupo edafologico.';
COMMENT ON COLUMN grupos_edafologicos.clave IS 'Clave controlada del grupo edafologico segun Grupo1 en la fuente INEGI.';
COMMENT ON COLUMN grupos_edafologicos.descripcion IS 'Descripcion controlada del grupo edafologico versionada en mappings.py.';

COMMENT ON TABLE calificadores_edafologicos IS 'Catalogo unificado de calificadores edafologicos usado por los roles calificador primario y calificador secundario. Incluye codigos documentales auditados contra el Diccionario de Datos Edafologicos de INEGI y valores operativos controlados N y N/A.';
COMMENT ON COLUMN calificadores_edafologicos.id IS 'Identificador autogenerado del calificador edafologico.';
COMMENT ON COLUMN calificadores_edafologicos.clave IS 'Clave controlada del calificador edafologico. El mismo catalogo atiende los roles primario y secundario.';
COMMENT ON COLUMN calificadores_edafologicos.descripcion IS 'Descripcion controlada del calificador. N y N/A son valores operativos controlados, no codigos documentales oficiales de INEGI.';

COMMENT ON TABLE fuentes_limites_municipales IS 'Catalogo local de fuentes de limites municipales usadas para productos derivados. Diferencia los limites IIEG e INEGI sin declarar que una fuente sea la correcta.';
COMMENT ON COLUMN fuentes_limites_municipales.id IS 'Identificador local de la fuente de limite municipal; no corresponde a un id remoto de cvegeo.';
COMMENT ON COLUMN fuentes_limites_municipales.clave IS 'Clave local de la fuente territorial: iieg o inegi.';
COMMENT ON COLUMN fuentes_limites_municipales.nombre_fuente IS 'Nombre legible de la fuente de limite municipal.';
COMMENT ON COLUMN fuentes_limites_municipales.descripcion IS 'Descripcion metodologica de la fuente territorial usada en overlay.';
COMMENT ON COLUMN fuentes_limites_municipales.version IS 'Version del artefacto institucional cvegeo que suministra la geometria territorial.';
COMMENT ON COLUMN fuentes_limites_municipales.procedencia IS 'Detalle de procedencia de la fuente territorial, sin combinar ni sustituir las geometrias IIEG e INEGI.';

COMMENT ON TABLE edafologias IS 'Tabla canonica persistente de poligonos edafologicos INEGI Serie III recortados a la cobertura territorial canonica, normalizados a EPSG:6368 y almacenados como MultiPolygon. Conserva atributos originales y trazabilidad de fuente.';
COMMENT ON COLUMN edafologias.id IS 'Identificador autogenerado del poligono edafologico canonico en esta base.';
COMMENT ON COLUMN edafologias.version_fuente IS 'Version del conjunto fuente INEGI. Para esta implementacion corresponde a Serie III; una publicacion futura debe registrarse como nueva version.';
COMMENT ON COLUMN edafologias.identificador_objeto_fuente IS 'OBJECTID original de la capa fuente. Es clave logica junto con version_fuente para Serie III, pero no se asume estable entre publicaciones futuras.';
COMMENT ON COLUMN edafologias.clave_wrb IS 'Clave WRB original conservada desde la fuente INEGI.';
COMMENT ON COLUMN edafologias.grupo_edafologico_id IS 'FK al grupo edafologico principal normalizado desde Grupo1.';
COMMENT ON COLUMN edafologias.calificador_primario_id IS 'FK al catalogo unificado de calificadores en rol primario, normalizado desde Califp_g1.';
COMMENT ON COLUMN edafologias.calificador_secundario_id IS 'FK al catalogo unificado de calificadores en rol secundario, normalizado desde Califs_g1.';
COMMENT ON COLUMN edafologias.grupo1_origen IS 'Valor literal original Grupo1 conservado para auditoria.';
COMMENT ON COLUMN edafologias.califp_g1_origen IS 'Valor literal original Califp_g1 conservado para auditoria del calificador primario.';
COMMENT ON COLUMN edafologias.califs_g1_origen IS 'Valor literal original Califs_g1 conservado para auditoria del calificador secundario.';
COMMENT ON COLUMN edafologias.grupo2_origen IS 'Valor literal original Grupo2 conservado sin normalizacion en esta fase.';
COMMENT ON COLUMN edafologias.califp_g2_origen IS 'Valor literal original Califp_g2 conservado sin normalizacion en esta fase.';
COMMENT ON COLUMN edafologias.califs_g2_origen IS 'Valor literal original Califs_g2 conservado sin normalizacion en esta fase.';
COMMENT ON COLUMN edafologias.grupo3_origen IS 'Valor literal original Grupo3 conservado sin normalizacion en esta fase.';
COMMENT ON COLUMN edafologias.califp_g3_origen IS 'Valor literal original Califp_g3 conservado sin normalizacion en esta fase.';
COMMENT ON COLUMN edafologias.clase_textural_origen IS 'Valor original Clase_tex conservado como atributo de fuente.';
COMMENT ON COLUMN edafologias.limite_superior_origen IS 'Valor original Lmte_sup conservado como atributo de fuente.';
COMMENT ON COLUMN edafologias.fase_fisica_origen IS 'Valor original Fase_fis_u conservado como atributo de fuente.';
COMMENT ON COLUMN edafologias.fase_quimica_origen IS 'Valor original Fase_qui_u conservado como atributo de fuente.';
COMMENT ON COLUMN edafologias.longitud_origen IS 'Shape_Leng original reportado por la fuente antes de normalizacion espacial.';
COMMENT ON COLUMN edafologias.superficie_origen IS 'Shape_Area original reportado por la fuente antes de recorte y reproyeccion.';
COMMENT ON COLUMN edafologias.nombre_fuente IS 'Nombre institucional de la fuente: INEGI Edafologia historica 1:250 000 Serie III.';
COMMENT ON COLUMN edafologias.url_fuente IS 'URL oficial configurada para la descarga de la fuente; no contiene credenciales.';
COMMENT ON COLUMN edafologias.nombre_archivo_fuente IS 'Nombre del archivo ZIP fuente conservado para trazabilidad.';
COMMENT ON COLUMN edafologias.sha256_archivo_fuente IS 'SHA-256 del ZIP fuente validado antes de transformar y cargar.';
COMMENT ON COLUMN edafologias.fecha_descarga_fuente IS 'Fecha/hora de descarga o reutilizacion verificable del archivo fuente.';
COMMENT ON COLUMN edafologias.fecha_procesamiento IS 'Fecha/hora de procesamiento que produjo la geometria canonica cargada.';
COMMENT ON COLUMN edafologias.fecha_actualizacion IS 'Fecha operativa de actualizacion del registro en el pipeline.';
COMMENT ON COLUMN edafologias.geometria IS 'Geometria canonica MultiPolygon en EPSG:6368. Se reparan geometrias fuente cuando es tecnicamente procedente antes del recorte.';

COMMENT ON TABLE edafologia_fragmentos_municipales IS 'Tabla persistente de fragmentos municipales producidos por la interseccion real entre edafologias y cada fuente de limite municipal. Conserva todos los fragmentos poligonales con area positiva.';
COMMENT ON COLUMN edafologia_fragmentos_municipales.id IS 'Identificador autogenerado del fragmento municipal persistente.';
COMMENT ON COLUMN edafologia_fragmentos_municipales.edafologia_id IS 'FK al poligono canonico edafologico que origina el fragmento.';
COMMENT ON COLUMN edafologia_fragmentos_municipales.municipio_id IS 'Clave cve_mun de Jalisco usada como referencia logica a cvegeo_municipalities; no existe FK fisica porque cvegeo vive en otra base.';
COMMENT ON COLUMN edafologia_fragmentos_municipales.version_fuente IS 'Version de la fuente edafologica usada para reconstruir idempotentemente el overlay.';
COMMENT ON COLUMN edafologia_fragmentos_municipales.fuente_limite_municipal_id IS 'FK local a la fuente de limite municipal usada para el overlay: IIEG o INEGI.';
COMMENT ON COLUMN edafologia_fragmentos_municipales.superficie_m2 IS 'Superficie del fragmento de interseccion en metros cuadrados, calculada en EPSG:6368 con DOUBLE PRECISION.';
COMMENT ON COLUMN edafologia_fragmentos_municipales.superficie_ha IS 'Superficie del fragmento en hectareas, derivada de superficie_m2.';
COMMENT ON COLUMN edafologia_fragmentos_municipales.porcentaje_poligono_fuente IS 'Porcentaje del area del poligono edafologico canonico representada por este fragmento. Denominador: area total del poligono fuente canonico.';
COMMENT ON COLUMN edafologia_fragmentos_municipales.porcentaje_municipio_total IS 'Porcentaje del territorio municipal cubierto por este fragmento. Denominador: area total del municipio de la fuente de limite correspondiente.';
COMMENT ON COLUMN edafologia_fragmentos_municipales.porcentaje_cobertura_edafologica IS 'Porcentaje de la cobertura edafologica municipal representada por este fragmento. Denominador: suma de fragmentos edafologicos positivos del municipio para la misma fuente territorial.';
COMMENT ON COLUMN edafologia_fragmentos_municipales.es_fragmento_pequenio IS 'Indicador de control para fragmentos pequenos; no implica eliminacion. Se conservan todos los componentes poligonales con area positiva.';
COMMENT ON COLUMN edafologia_fragmentos_municipales.geometria IS 'Geometria MultiPolygon de la interseccion real entre poligono edafologico y municipio, en EPSG:6368.';

COMMENT ON VIEW vw_edafologia_resumenes_municipales IS 'Vista SQL normal no materializada que agrega fragmentos municipales por municipio, version, categoria edafologica y fuente de limite. No tiene PK fisica, no almacena geometria y no recibe cargas directas.';
COMMENT ON COLUMN vw_edafologia_resumenes_municipales.fuente_limite_municipal_id IS 'Fuente territorial del resumen, heredada de los fragmentos municipales.';
COMMENT ON COLUMN vw_edafologia_resumenes_municipales.municipio_id IS 'Clave cve_mun del municipio dentro de Jalisco.';
COMMENT ON COLUMN vw_edafologia_resumenes_municipales.version_fuente IS 'Version de la fuente edafologica resumida.';
COMMENT ON COLUMN vw_edafologia_resumenes_municipales.grupo_edafologico_id IS 'Grupo edafologico principal de la categoria resumida.';
COMMENT ON COLUMN vw_edafologia_resumenes_municipales.calificador_primario_id IS 'Calificador en rol primario de la categoria resumida.';
COMMENT ON COLUMN vw_edafologia_resumenes_municipales.calificador_secundario_id IS 'Calificador en rol secundario de la categoria resumida.';
COMMENT ON COLUMN vw_edafologia_resumenes_municipales.superficie_m2 IS 'Suma de superficie_m2 de los fragmentos del grupo de agregacion.';
COMMENT ON COLUMN vw_edafologia_resumenes_municipales.superficie_ha IS 'Suma de superficie_ha de los fragmentos del grupo de agregacion.';
COMMENT ON COLUMN vw_edafologia_resumenes_municipales.porcentaje_municipio IS 'Suma de porcentaje_municipio_total de los fragmentos del grupo de agregacion.';
COMMENT ON COLUMN vw_edafologia_resumenes_municipales.cantidad_fragmentos IS 'Numero de fragmentos persistentes incluidos en el agregado.';
