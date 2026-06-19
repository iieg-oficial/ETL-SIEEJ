-- =============================================================================
-- V8__comments.sql  |  Pipeline: delitos_fuero_comun
-- COMMENT ON TABLE / FOREIGN TABLE / VIEW / MATERIALIZED VIEW y columnas
-- para todos los objetos del esquema delitos_fuero_comun.
-- =============================================================================

-- =============================================================================
-- CATÁLOGOS
-- =============================================================================

COMMENT ON TABLE cat_bien_juridico_afectado IS
    'Catálogo de bienes jurídicos afectados según clasificación SSPC/RNID.';
COMMENT ON COLUMN cat_bien_juridico_afectado.id IS
    'Identificador único del bien jurídico afectado.';
COMMENT ON COLUMN cat_bien_juridico_afectado.bien_juridico_afectado IS
    'Descripción del bien jurídico afectado (ej. Vida e Integridad corporal).';

COMMENT ON TABLE cat_tipo_delito IS
    'Catálogo de tipos de delito según clasificación SSPC/RNID.';
COMMENT ON COLUMN cat_tipo_delito.id IS
    'Identificador único del tipo de delito.';
COMMENT ON COLUMN cat_tipo_delito.tipo_delito IS
    'Nombre del tipo de delito (ej. Feminicidio, Extorsión).';

COMMENT ON TABLE cat_subtipo_delito IS
    'Catálogo de subtipos de delito; cada subtipo pertenece a un tipo.';
COMMENT ON COLUMN cat_subtipo_delito.id IS
    'Identificador único del subtipo de delito.';
COMMENT ON COLUMN cat_subtipo_delito.subtipo_delito IS
    'Nombre del subtipo de delito (ej. Homicidio doloso, Lesiones dolosas).';
COMMENT ON COLUMN cat_subtipo_delito.tipo_delito_id IS
    'FK a cat_tipo_delito; tipo al que pertenece este subtipo.';

COMMENT ON TABLE cat_modalidad IS
    'Catálogo de modalidades de delito; cada modalidad pertenece a un subtipo.';
COMMENT ON COLUMN cat_modalidad.id IS
    'Identificador único de la modalidad.';
COMMENT ON COLUMN cat_modalidad.modalidad IS
    'Descripción de la modalidad (ej. Con arma de fuego, Con violencia).';
COMMENT ON COLUMN cat_modalidad.subtipo_delito_id IS
    'FK a cat_subtipo_delito; NULL cuando la modalidad no aplica a un subtipo específico.';

-- =============================================================================
-- TABLAS STAGING
-- =============================================================================

COMMENT ON TABLE stg_delitos_fuero_comun_2015_2025 IS
    'Staging histórico de delitos del fuero común 2015-2025. '
    'Carga bootstrap única. Fuente: SSPC/RNID (descarga anual). '
    'NK: (anio, cvegeo, bien_juridico_afectado_id, tipo_delito_id, subtipo_delito_id, modalidad_id).';
COMMENT ON COLUMN stg_delitos_fuero_comun_2015_2025.id IS
    'Identificador serial autogenerado.';
COMMENT ON COLUMN stg_delitos_fuero_comun_2015_2025.anio IS
    'Año del registro (YYYY).';
COMMENT ON COLUMN stg_delitos_fuero_comun_2015_2025.cvegeo IS
    'Clave geoestadística del municipio (entero sin padding). FK lógica a cvegeo_municipalities.cvegeo.';
COMMENT ON COLUMN stg_delitos_fuero_comun_2015_2025.bien_juridico_afectado_id IS
    'FK a cat_bien_juridico_afectado.';
COMMENT ON COLUMN stg_delitos_fuero_comun_2015_2025.tipo_delito_id IS
    'FK a cat_tipo_delito.';
COMMENT ON COLUMN stg_delitos_fuero_comun_2015_2025.subtipo_delito_id IS
    'FK a cat_subtipo_delito.';
COMMENT ON COLUMN stg_delitos_fuero_comun_2015_2025.modalidad_id IS
    'FK a cat_modalidad.';
COMMENT ON COLUMN stg_delitos_fuero_comun_2015_2025.enero IS
    'Carpetas de investigación iniciadas en enero; NULL si el mes no fue publicado.';
COMMENT ON COLUMN stg_delitos_fuero_comun_2015_2025.febrero IS
    'Carpetas de investigación iniciadas en febrero; NULL si el mes no fue publicado.';
COMMENT ON COLUMN stg_delitos_fuero_comun_2015_2025.marzo IS
    'Carpetas de investigación iniciadas en marzo; NULL si el mes no fue publicado.';
COMMENT ON COLUMN stg_delitos_fuero_comun_2015_2025.abril IS
    'Carpetas de investigación iniciadas en abril; NULL si el mes no fue publicado.';
COMMENT ON COLUMN stg_delitos_fuero_comun_2015_2025.mayo IS
    'Carpetas de investigación iniciadas en mayo; NULL si el mes no fue publicado.';
COMMENT ON COLUMN stg_delitos_fuero_comun_2015_2025.junio IS
    'Carpetas de investigación iniciadas en junio; NULL si el mes no fue publicado.';
COMMENT ON COLUMN stg_delitos_fuero_comun_2015_2025.julio IS
    'Carpetas de investigación iniciadas en julio; NULL si el mes no fue publicado.';
COMMENT ON COLUMN stg_delitos_fuero_comun_2015_2025.agosto IS
    'Carpetas de investigación iniciadas en agosto; NULL si el mes no fue publicado.';
COMMENT ON COLUMN stg_delitos_fuero_comun_2015_2025.septiembre IS
    'Carpetas de investigación iniciadas en septiembre; NULL si el mes no fue publicado.';
COMMENT ON COLUMN stg_delitos_fuero_comun_2015_2025.octubre IS
    'Carpetas de investigación iniciadas en octubre; NULL si el mes no fue publicado.';
COMMENT ON COLUMN stg_delitos_fuero_comun_2015_2025.noviembre IS
    'Carpetas de investigación iniciadas en noviembre; NULL si el mes no fue publicado.';
COMMENT ON COLUMN stg_delitos_fuero_comun_2015_2025.diciembre IS
    'Carpetas de investigación iniciadas en diciembre; NULL si el mes no fue publicado.';
COMMENT ON COLUMN stg_delitos_fuero_comun_2015_2025.created_at IS
    'Fecha y hora de inserción del registro.';

COMMENT ON TABLE stg_delitos_fuero_comun_2026 IS
    'Staging del año en curso de delitos del fuero común (2026+). '
    'Se actualiza mensualmente mediante upsert. Fuente: SSPC/RNID (descarga mensual). '
    'NK: (anio, cvegeo, bien_juridico_afectado_id, tipo_delito_id, subtipo_delito_id, modalidad_id).';
COMMENT ON COLUMN stg_delitos_fuero_comun_2026.id IS
    'Identificador serial autogenerado.';
COMMENT ON COLUMN stg_delitos_fuero_comun_2026.anio IS
    'Año del registro (YYYY).';
COMMENT ON COLUMN stg_delitos_fuero_comun_2026.cvegeo IS
    'Clave geoestadística del municipio (entero sin padding). FK lógica a cvegeo_municipalities.cvegeo.';
COMMENT ON COLUMN stg_delitos_fuero_comun_2026.bien_juridico_afectado_id IS
    'FK a cat_bien_juridico_afectado.';
COMMENT ON COLUMN stg_delitos_fuero_comun_2026.tipo_delito_id IS
    'FK a cat_tipo_delito.';
COMMENT ON COLUMN stg_delitos_fuero_comun_2026.subtipo_delito_id IS
    'FK a cat_subtipo_delito.';
COMMENT ON COLUMN stg_delitos_fuero_comun_2026.modalidad_id IS
    'FK a cat_modalidad.';
COMMENT ON COLUMN stg_delitos_fuero_comun_2026.enero IS
    'Carpetas de investigación iniciadas en enero; NULL si el mes no fue publicado.';
COMMENT ON COLUMN stg_delitos_fuero_comun_2026.febrero IS
    'Carpetas de investigación iniciadas en febrero; NULL si el mes no fue publicado.';
COMMENT ON COLUMN stg_delitos_fuero_comun_2026.marzo IS
    'Carpetas de investigación iniciadas en marzo; NULL si el mes no fue publicado.';
COMMENT ON COLUMN stg_delitos_fuero_comun_2026.abril IS
    'Carpetas de investigación iniciadas en abril; NULL si el mes no fue publicado.';
COMMENT ON COLUMN stg_delitos_fuero_comun_2026.mayo IS
    'Carpetas de investigación iniciadas en mayo; NULL si el mes no fue publicado.';
COMMENT ON COLUMN stg_delitos_fuero_comun_2026.junio IS
    'Carpetas de investigación iniciadas en junio; NULL si el mes no fue publicado.';
COMMENT ON COLUMN stg_delitos_fuero_comun_2026.julio IS
    'Carpetas de investigación iniciadas en julio; NULL si el mes no fue publicado.';
COMMENT ON COLUMN stg_delitos_fuero_comun_2026.agosto IS
    'Carpetas de investigación iniciadas en agosto; NULL si el mes no fue publicado.';
COMMENT ON COLUMN stg_delitos_fuero_comun_2026.septiembre IS
    'Carpetas de investigación iniciadas en septiembre; NULL si el mes no fue publicado.';
COMMENT ON COLUMN stg_delitos_fuero_comun_2026.octubre IS
    'Carpetas de investigación iniciadas en octubre; NULL si el mes no fue publicado.';
COMMENT ON COLUMN stg_delitos_fuero_comun_2026.noviembre IS
    'Carpetas de investigación iniciadas en noviembre; NULL si el mes no fue publicado.';
COMMENT ON COLUMN stg_delitos_fuero_comun_2026.diciembre IS
    'Carpetas de investigación iniciadas en diciembre; NULL si el mes no fue publicado.';
COMMENT ON COLUMN stg_delitos_fuero_comun_2026.created_at IS
    'Fecha y hora de inserción del registro.';
COMMENT ON COLUMN stg_delitos_fuero_comun_2026.updated_at IS
    'Fecha y hora de la última actualización (upsert).';

-- =============================================================================
-- TABLAS FORÁNEAS (FDW)
-- =============================================================================

COMMENT ON FOREIGN TABLE cvegeo_municipalities IS
    'Tabla foránea (FDW → BD cvegeo) con el catálogo de municipios de México. '
    'Incluye claves geoestadísticas, nombres y geometrías oficiales IIEG/INEGI.';
COMMENT ON COLUMN cvegeo_municipalities.id IS
    'Identificador primario del municipio en la BD cvegeo.';
COMMENT ON COLUMN cvegeo_municipalities.cvegeo IS
    'Clave geoestadística municipal (entero EEMMM, ej. 14001).';
COMMENT ON COLUMN cvegeo_municipalities.cve_ent IS
    'Clave de entidad federativa (entero, ej. 14 para Jalisco).';
COMMENT ON COLUMN cvegeo_municipalities.cve_mun IS
    'Clave de municipio dentro de la entidad (entero, 3 dígitos).';
COMMENT ON COLUMN cvegeo_municipalities.nomgeo IS
    'Nombre oficial del municipio.';
COMMENT ON COLUMN cvegeo_municipalities.nom_ent IS
    'Nombre de la entidad federativa a la que pertenece el municipio.';
COMMENT ON COLUMN cvegeo_municipalities.geom_iieg IS
    'Geometría MultiPolygon del municipio según delimitación IIEG (SRID 6368, LCC México).';
COMMENT ON COLUMN cvegeo_municipalities.geom_inegi IS
    'Geometría MultiPolygon del municipio según delimitación INEGI (SRID 6368, LCC México).';

COMMENT ON FOREIGN TABLE conapo_indicadores_demograficos IS
    'Tabla foránea (FDW → BD conapo) con proyecciones de población municipal a mitad de año. '
    'Se usa para calcular tasas por 100,000 habitantes en el gold layer.';
COMMENT ON COLUMN conapo_indicadores_demograficos.municipio_id IS
    'Clave geoestadística municipal (entero EEMMM). FK lógica a cvegeo_municipalities.cvegeo.';
COMMENT ON COLUMN conapo_indicadores_demograficos.entidad_id IS
    'Clave de entidad federativa (entero).';
COMMENT ON COLUMN conapo_indicadores_demograficos.anio IS
    'Año de la proyección.';
COMMENT ON COLUMN conapo_indicadores_demograficos.pob_mit_mun IS
    'Población municipal proyectada a mitad del año (personas).';

-- =============================================================================
-- VISTAS (V4)
-- =============================================================================

COMMENT ON VIEW vw_delitos_serie_historica IS
    'Serie histórica completa 2015-presente de delitos del fuero común a nivel municipal. '
    'Desanida columnas mensuales (enero..diciembre) en filas (mes, conteo). '
    'Excluye conteos NULL y cero. Abarca stg 2015-2025 y stg 2026 vía UNION ALL.';
COMMENT ON COLUMN vw_delitos_serie_historica.id IS
    'Identificador de fila generado por ROW_NUMBER().';
COMMENT ON COLUMN vw_delitos_serie_historica.anio IS
    'Año del registro.';
COMMENT ON COLUMN vw_delitos_serie_historica.cve_municipio IS
    'Clave geoestadística del municipio (VARCHAR 5 dígitos, EEMMM).';
COMMENT ON COLUMN vw_delitos_serie_historica.clave_ent IS
    'Clave de entidad federativa (VARCHAR 2 dígitos).';
COMMENT ON COLUMN vw_delitos_serie_historica.entidad IS
    'Nombre de la entidad federativa.';
COMMENT ON COLUMN vw_delitos_serie_historica.municipio IS
    'Nombre del municipio.';
COMMENT ON COLUMN vw_delitos_serie_historica.bien_juridico_afectado IS
    'Bien jurídico afectado según catálogo SSPC.';
COMMENT ON COLUMN vw_delitos_serie_historica.tipo_delito IS
    'Tipo de delito según catálogo SSPC.';
COMMENT ON COLUMN vw_delitos_serie_historica.subtipo_delito IS
    'Subtipo de delito según catálogo SSPC.';
COMMENT ON COLUMN vw_delitos_serie_historica.modalidad IS
    'Modalidad del delito según catálogo SSPC.';
COMMENT ON COLUMN vw_delitos_serie_historica.mes IS
    'Nombre del mes en español (Enero, Febrero, …, Diciembre).';
COMMENT ON COLUMN vw_delitos_serie_historica.conteo IS
    'Número de carpetas de investigación iniciadas en el mes.';

COMMENT ON VIEW vw_homicidio_doloso IS
    'Filtro de vw_delitos_serie_historica: subtipo_delito = ''Homicidio doloso''. Abarca 2015-presente.';
COMMENT ON COLUMN vw_homicidio_doloso.id IS 'Identificador de fila generado por ROW_NUMBER().';
COMMENT ON COLUMN vw_homicidio_doloso.anio IS 'Año del registro.';
COMMENT ON COLUMN vw_homicidio_doloso.cve_municipio IS 'Clave geoestadística del municipio (5 dígitos, EEMMM).';
COMMENT ON COLUMN vw_homicidio_doloso.clave_ent IS 'Clave de entidad federativa (2 dígitos).';
COMMENT ON COLUMN vw_homicidio_doloso.entidad IS 'Nombre de la entidad federativa.';
COMMENT ON COLUMN vw_homicidio_doloso.municipio IS 'Nombre del municipio.';
COMMENT ON COLUMN vw_homicidio_doloso.bien_juridico_afectado IS 'Bien jurídico afectado según catálogo SSPC.';
COMMENT ON COLUMN vw_homicidio_doloso.tipo_delito IS 'Tipo de delito según catálogo SSPC.';
COMMENT ON COLUMN vw_homicidio_doloso.subtipo_delito IS 'Subtipo de delito según catálogo SSPC.';
COMMENT ON COLUMN vw_homicidio_doloso.modalidad IS 'Modalidad del delito según catálogo SSPC.';
COMMENT ON COLUMN vw_homicidio_doloso.mes IS 'Nombre del mes en español.';
COMMENT ON COLUMN vw_homicidio_doloso.conteo IS 'Número de carpetas de investigación.';

COMMENT ON VIEW vw_tentativa_homicidio_doloso IS
    'Filtro de vw_delitos_serie_historica: subtipo = ''Tentativa de homicidio doloso''. Solo año 2026 (nueva categoría).';
COMMENT ON COLUMN vw_tentativa_homicidio_doloso.id IS 'Identificador de fila generado por ROW_NUMBER().';
COMMENT ON COLUMN vw_tentativa_homicidio_doloso.anio IS 'Año del registro.';
COMMENT ON COLUMN vw_tentativa_homicidio_doloso.cve_municipio IS 'Clave geoestadística del municipio (5 dígitos, EEMMM).';
COMMENT ON COLUMN vw_tentativa_homicidio_doloso.clave_ent IS 'Clave de entidad federativa (2 dígitos).';
COMMENT ON COLUMN vw_tentativa_homicidio_doloso.entidad IS 'Nombre de la entidad federativa.';
COMMENT ON COLUMN vw_tentativa_homicidio_doloso.municipio IS 'Nombre del municipio.';
COMMENT ON COLUMN vw_tentativa_homicidio_doloso.bien_juridico_afectado IS 'Bien jurídico afectado según catálogo SSPC.';
COMMENT ON COLUMN vw_tentativa_homicidio_doloso.tipo_delito IS 'Tipo de delito según catálogo SSPC.';
COMMENT ON COLUMN vw_tentativa_homicidio_doloso.subtipo_delito IS 'Subtipo de delito según catálogo SSPC.';
COMMENT ON COLUMN vw_tentativa_homicidio_doloso.modalidad IS 'Modalidad del delito según catálogo SSPC.';
COMMENT ON COLUMN vw_tentativa_homicidio_doloso.mes IS 'Nombre del mes en español.';
COMMENT ON COLUMN vw_tentativa_homicidio_doloso.conteo IS 'Número de carpetas de investigación.';

COMMENT ON VIEW vw_feminicidio IS
    'Filtro de vw_delitos_serie_historica: tipo = ''Feminicidio'', excluye tentativa. Abarca 2015-presente.';
COMMENT ON COLUMN vw_feminicidio.id IS 'Identificador de fila generado por ROW_NUMBER().';
COMMENT ON COLUMN vw_feminicidio.anio IS 'Año del registro.';
COMMENT ON COLUMN vw_feminicidio.cve_municipio IS 'Clave geoestadística del municipio (5 dígitos, EEMMM).';
COMMENT ON COLUMN vw_feminicidio.clave_ent IS 'Clave de entidad federativa (2 dígitos).';
COMMENT ON COLUMN vw_feminicidio.entidad IS 'Nombre de la entidad federativa.';
COMMENT ON COLUMN vw_feminicidio.municipio IS 'Nombre del municipio.';
COMMENT ON COLUMN vw_feminicidio.bien_juridico_afectado IS 'Bien jurídico afectado según catálogo SSPC.';
COMMENT ON COLUMN vw_feminicidio.tipo_delito IS 'Tipo de delito según catálogo SSPC.';
COMMENT ON COLUMN vw_feminicidio.subtipo_delito IS 'Subtipo de delito según catálogo SSPC.';
COMMENT ON COLUMN vw_feminicidio.modalidad IS 'Modalidad del delito según catálogo SSPC.';
COMMENT ON COLUMN vw_feminicidio.mes IS 'Nombre del mes en español.';
COMMENT ON COLUMN vw_feminicidio.conteo IS 'Número de carpetas de investigación.';

COMMENT ON VIEW vw_tentativa_feminicidio IS
    'Filtro de vw_delitos_serie_historica: subtipo = ''Tentativa de feminicidio''. Solo año 2026.';
COMMENT ON COLUMN vw_tentativa_feminicidio.id IS 'Identificador de fila generado por ROW_NUMBER().';
COMMENT ON COLUMN vw_tentativa_feminicidio.anio IS 'Año del registro.';
COMMENT ON COLUMN vw_tentativa_feminicidio.cve_municipio IS 'Clave geoestadística del municipio (5 dígitos, EEMMM).';
COMMENT ON COLUMN vw_tentativa_feminicidio.clave_ent IS 'Clave de entidad federativa (2 dígitos).';
COMMENT ON COLUMN vw_tentativa_feminicidio.entidad IS 'Nombre de la entidad federativa.';
COMMENT ON COLUMN vw_tentativa_feminicidio.municipio IS 'Nombre del municipio.';
COMMENT ON COLUMN vw_tentativa_feminicidio.bien_juridico_afectado IS 'Bien jurídico afectado según catálogo SSPC.';
COMMENT ON COLUMN vw_tentativa_feminicidio.tipo_delito IS 'Tipo de delito según catálogo SSPC.';
COMMENT ON COLUMN vw_tentativa_feminicidio.subtipo_delito IS 'Subtipo de delito según catálogo SSPC.';
COMMENT ON COLUMN vw_tentativa_feminicidio.modalidad IS 'Modalidad del delito según catálogo SSPC.';
COMMENT ON COLUMN vw_tentativa_feminicidio.mes IS 'Nombre del mes en español.';
COMMENT ON COLUMN vw_tentativa_feminicidio.conteo IS 'Número de carpetas de investigación.';

COMMENT ON VIEW vw_otros_vida_integridad IS
    'Filtro de vw_delitos_serie_historica: otros delitos contra la vida e integridad corporal. '
    'Incluye las tentativas de homicidio doloso y feminicidio de 2026 para comparabilidad histórica.';
COMMENT ON COLUMN vw_otros_vida_integridad.id IS 'Identificador de fila generado por ROW_NUMBER().';
COMMENT ON COLUMN vw_otros_vida_integridad.anio IS 'Año del registro.';
COMMENT ON COLUMN vw_otros_vida_integridad.cve_municipio IS 'Clave geoestadística del municipio (5 dígitos, EEMMM).';
COMMENT ON COLUMN vw_otros_vida_integridad.clave_ent IS 'Clave de entidad federativa (2 dígitos).';
COMMENT ON COLUMN vw_otros_vida_integridad.entidad IS 'Nombre de la entidad federativa.';
COMMENT ON COLUMN vw_otros_vida_integridad.municipio IS 'Nombre del municipio.';
COMMENT ON COLUMN vw_otros_vida_integridad.bien_juridico_afectado IS 'Bien jurídico afectado según catálogo SSPC.';
COMMENT ON COLUMN vw_otros_vida_integridad.tipo_delito IS 'Tipo de delito según catálogo SSPC.';
COMMENT ON COLUMN vw_otros_vida_integridad.subtipo_delito IS 'Subtipo de delito según catálogo SSPC.';
COMMENT ON COLUMN vw_otros_vida_integridad.modalidad IS 'Modalidad del delito según catálogo SSPC.';
COMMENT ON COLUMN vw_otros_vida_integridad.mes IS 'Nombre del mes en español.';
COMMENT ON COLUMN vw_otros_vida_integridad.conteo IS 'Número de carpetas de investigación.';

COMMENT ON VIEW vw_narcomenudeo IS
    'Filtro de vw_delitos_serie_historica: narcomenudeo (venta y posesión simple). Abarca 2015-presente.';
COMMENT ON COLUMN vw_narcomenudeo.id IS 'Identificador de fila generado por ROW_NUMBER().';
COMMENT ON COLUMN vw_narcomenudeo.anio IS 'Año del registro.';
COMMENT ON COLUMN vw_narcomenudeo.cve_municipio IS 'Clave geoestadística del municipio (5 dígitos, EEMMM).';
COMMENT ON COLUMN vw_narcomenudeo.clave_ent IS 'Clave de entidad federativa (2 dígitos).';
COMMENT ON COLUMN vw_narcomenudeo.entidad IS 'Nombre de la entidad federativa.';
COMMENT ON COLUMN vw_narcomenudeo.municipio IS 'Nombre del municipio.';
COMMENT ON COLUMN vw_narcomenudeo.bien_juridico_afectado IS 'Bien jurídico afectado según catálogo SSPC.';
COMMENT ON COLUMN vw_narcomenudeo.tipo_delito IS 'Tipo de delito según catálogo SSPC.';
COMMENT ON COLUMN vw_narcomenudeo.subtipo_delito IS 'Subtipo de delito según catálogo SSPC.';
COMMENT ON COLUMN vw_narcomenudeo.modalidad IS 'Modalidad del delito según catálogo SSPC.';
COMMENT ON COLUMN vw_narcomenudeo.mes IS 'Nombre del mes en español.';
COMMENT ON COLUMN vw_narcomenudeo.conteo IS 'Número de carpetas de investigación.';

COMMENT ON VIEW vw_extorsion IS
    'Filtro de vw_delitos_serie_historica: extorsión, excluyendo tentativas de 2026.';
COMMENT ON COLUMN vw_extorsion.id IS 'Identificador de fila generado por ROW_NUMBER().';
COMMENT ON COLUMN vw_extorsion.anio IS 'Año del registro.';
COMMENT ON COLUMN vw_extorsion.cve_municipio IS 'Clave geoestadística del municipio (5 dígitos, EEMMM).';
COMMENT ON COLUMN vw_extorsion.clave_ent IS 'Clave de entidad federativa (2 dígitos).';
COMMENT ON COLUMN vw_extorsion.entidad IS 'Nombre de la entidad federativa.';
COMMENT ON COLUMN vw_extorsion.municipio IS 'Nombre del municipio.';
COMMENT ON COLUMN vw_extorsion.bien_juridico_afectado IS 'Bien jurídico afectado según catálogo SSPC.';
COMMENT ON COLUMN vw_extorsion.tipo_delito IS 'Tipo de delito según catálogo SSPC.';
COMMENT ON COLUMN vw_extorsion.subtipo_delito IS 'Subtipo de delito según catálogo SSPC.';
COMMENT ON COLUMN vw_extorsion.modalidad IS 'Modalidad del delito según catálogo SSPC.';
COMMENT ON COLUMN vw_extorsion.mes IS 'Nombre del mes en español.';
COMMENT ON COLUMN vw_extorsion.conteo IS 'Número de carpetas de investigación.';

COMMENT ON VIEW vw_tentativa_extorsion IS
    'Filtro de vw_delitos_serie_historica: tentativa de extorsión (presencial y por otros medios). Solo año 2026.';
COMMENT ON COLUMN vw_tentativa_extorsion.id IS 'Identificador de fila generado por ROW_NUMBER().';
COMMENT ON COLUMN vw_tentativa_extorsion.anio IS 'Año del registro.';
COMMENT ON COLUMN vw_tentativa_extorsion.cve_municipio IS 'Clave geoestadística del municipio (5 dígitos, EEMMM).';
COMMENT ON COLUMN vw_tentativa_extorsion.clave_ent IS 'Clave de entidad federativa (2 dígitos).';
COMMENT ON COLUMN vw_tentativa_extorsion.entidad IS 'Nombre de la entidad federativa.';
COMMENT ON COLUMN vw_tentativa_extorsion.municipio IS 'Nombre del municipio.';
COMMENT ON COLUMN vw_tentativa_extorsion.bien_juridico_afectado IS 'Bien jurídico afectado según catálogo SSPC.';
COMMENT ON COLUMN vw_tentativa_extorsion.tipo_delito IS 'Tipo de delito según catálogo SSPC.';
COMMENT ON COLUMN vw_tentativa_extorsion.subtipo_delito IS 'Subtipo de delito según catálogo SSPC.';
COMMENT ON COLUMN vw_tentativa_extorsion.modalidad IS 'Modalidad del delito según catálogo SSPC.';
COMMENT ON COLUMN vw_tentativa_extorsion.mes IS 'Nombre del mes en español.';
COMMENT ON COLUMN vw_tentativa_extorsion.conteo IS 'Número de carpetas de investigación.';

COMMENT ON VIEW vw_otros_patrimonio IS
    'Filtro de vw_delitos_serie_historica: otros delitos contra el patrimonio. '
    'Incluye tentativas de extorsión de 2026 para comparabilidad histórica.';
COMMENT ON COLUMN vw_otros_patrimonio.id IS 'Identificador de fila generado por ROW_NUMBER().';
COMMENT ON COLUMN vw_otros_patrimonio.anio IS 'Año del registro.';
COMMENT ON COLUMN vw_otros_patrimonio.cve_municipio IS 'Clave geoestadística del municipio (5 dígitos, EEMMM).';
COMMENT ON COLUMN vw_otros_patrimonio.clave_ent IS 'Clave de entidad federativa (2 dígitos).';
COMMENT ON COLUMN vw_otros_patrimonio.entidad IS 'Nombre de la entidad federativa.';
COMMENT ON COLUMN vw_otros_patrimonio.municipio IS 'Nombre del municipio.';
COMMENT ON COLUMN vw_otros_patrimonio.bien_juridico_afectado IS 'Bien jurídico afectado según catálogo SSPC.';
COMMENT ON COLUMN vw_otros_patrimonio.tipo_delito IS 'Tipo de delito según catálogo SSPC.';
COMMENT ON COLUMN vw_otros_patrimonio.subtipo_delito IS 'Subtipo de delito según catálogo SSPC.';
COMMENT ON COLUMN vw_otros_patrimonio.modalidad IS 'Modalidad del delito según catálogo SSPC.';
COMMENT ON COLUMN vw_otros_patrimonio.mes IS 'Nombre del mes en español.';
COMMENT ON COLUMN vw_otros_patrimonio.conteo IS 'Número de carpetas de investigación.';

COMMENT ON VIEW vw_trata_personas IS
    'Filtro de vw_delitos_serie_historica: trata de personas y pornografía infantil. Abarca 2015-presente.';
COMMENT ON COLUMN vw_trata_personas.id IS 'Identificador de fila generado por ROW_NUMBER().';
COMMENT ON COLUMN vw_trata_personas.anio IS 'Año del registro.';
COMMENT ON COLUMN vw_trata_personas.cve_municipio IS 'Clave geoestadística del municipio (5 dígitos, EEMMM).';
COMMENT ON COLUMN vw_trata_personas.clave_ent IS 'Clave de entidad federativa (2 dígitos).';
COMMENT ON COLUMN vw_trata_personas.entidad IS 'Nombre de la entidad federativa.';
COMMENT ON COLUMN vw_trata_personas.municipio IS 'Nombre del municipio.';
COMMENT ON COLUMN vw_trata_personas.bien_juridico_afectado IS 'Bien jurídico afectado según catálogo SSPC.';
COMMENT ON COLUMN vw_trata_personas.tipo_delito IS 'Tipo de delito según catálogo SSPC.';
COMMENT ON COLUMN vw_trata_personas.subtipo_delito IS 'Subtipo de delito según catálogo SSPC.';
COMMENT ON COLUMN vw_trata_personas.modalidad IS 'Modalidad del delito según catálogo SSPC.';
COMMENT ON COLUMN vw_trata_personas.mes IS 'Nombre del mes en español.';
COMMENT ON COLUMN vw_trata_personas.conteo IS 'Número de carpetas de investigación.';

COMMENT ON VIEW vw_otros_libertad_personal IS
    'Filtro de vw_delitos_serie_historica: otros delitos contra la libertad personal. Abarca 2015-presente.';
COMMENT ON COLUMN vw_otros_libertad_personal.id IS 'Identificador de fila generado por ROW_NUMBER().';
COMMENT ON COLUMN vw_otros_libertad_personal.anio IS 'Año del registro.';
COMMENT ON COLUMN vw_otros_libertad_personal.cve_municipio IS 'Clave geoestadística del municipio (5 dígitos, EEMMM).';
COMMENT ON COLUMN vw_otros_libertad_personal.clave_ent IS 'Clave de entidad federativa (2 dígitos).';
COMMENT ON COLUMN vw_otros_libertad_personal.entidad IS 'Nombre de la entidad federativa.';
COMMENT ON COLUMN vw_otros_libertad_personal.municipio IS 'Nombre del municipio.';
COMMENT ON COLUMN vw_otros_libertad_personal.bien_juridico_afectado IS 'Bien jurídico afectado según catálogo SSPC.';
COMMENT ON COLUMN vw_otros_libertad_personal.tipo_delito IS 'Tipo de delito según catálogo SSPC.';
COMMENT ON COLUMN vw_otros_libertad_personal.subtipo_delito IS 'Subtipo de delito según catálogo SSPC.';
COMMENT ON COLUMN vw_otros_libertad_personal.modalidad IS 'Modalidad del delito según catálogo SSPC.';
COMMENT ON COLUMN vw_otros_libertad_personal.mes IS 'Nombre del mes en español.';
COMMENT ON COLUMN vw_otros_libertad_personal.conteo IS 'Número de carpetas de investigación.';

COMMENT ON VIEW vw_otros_libertad_sexual IS
    'Filtro de vw_delitos_serie_historica: otros delitos contra la libertad y seguridad sexual. Abarca 2015-presente.';
COMMENT ON COLUMN vw_otros_libertad_sexual.id IS 'Identificador de fila generado por ROW_NUMBER().';
COMMENT ON COLUMN vw_otros_libertad_sexual.anio IS 'Año del registro.';
COMMENT ON COLUMN vw_otros_libertad_sexual.cve_municipio IS 'Clave geoestadística del municipio (5 dígitos, EEMMM).';
COMMENT ON COLUMN vw_otros_libertad_sexual.clave_ent IS 'Clave de entidad federativa (2 dígitos).';
COMMENT ON COLUMN vw_otros_libertad_sexual.entidad IS 'Nombre de la entidad federativa.';
COMMENT ON COLUMN vw_otros_libertad_sexual.municipio IS 'Nombre del municipio.';
COMMENT ON COLUMN vw_otros_libertad_sexual.bien_juridico_afectado IS 'Bien jurídico afectado según catálogo SSPC.';
COMMENT ON COLUMN vw_otros_libertad_sexual.tipo_delito IS 'Tipo de delito según catálogo SSPC.';
COMMENT ON COLUMN vw_otros_libertad_sexual.subtipo_delito IS 'Subtipo de delito según catálogo SSPC.';
COMMENT ON COLUMN vw_otros_libertad_sexual.modalidad IS 'Modalidad del delito según catálogo SSPC.';
COMMENT ON COLUMN vw_otros_libertad_sexual.mes IS 'Nombre del mes en español.';
COMMENT ON COLUMN vw_otros_libertad_sexual.conteo IS 'Número de carpetas de investigación.';

COMMENT ON VIEW vw_otros_sociedad IS
    'Filtro de vw_delitos_serie_historica: otros delitos contra la sociedad y discriminación. Abarca 2015-presente.';
COMMENT ON COLUMN vw_otros_sociedad.id IS 'Identificador de fila generado por ROW_NUMBER().';
COMMENT ON COLUMN vw_otros_sociedad.anio IS 'Año del registro.';
COMMENT ON COLUMN vw_otros_sociedad.cve_municipio IS 'Clave geoestadística del municipio (5 dígitos, EEMMM).';
COMMENT ON COLUMN vw_otros_sociedad.clave_ent IS 'Clave de entidad federativa (2 dígitos).';
COMMENT ON COLUMN vw_otros_sociedad.entidad IS 'Nombre de la entidad federativa.';
COMMENT ON COLUMN vw_otros_sociedad.municipio IS 'Nombre del municipio.';
COMMENT ON COLUMN vw_otros_sociedad.bien_juridico_afectado IS 'Bien jurídico afectado según catálogo SSPC.';
COMMENT ON COLUMN vw_otros_sociedad.tipo_delito IS 'Tipo de delito según catálogo SSPC.';
COMMENT ON COLUMN vw_otros_sociedad.subtipo_delito IS 'Subtipo de delito según catálogo SSPC.';
COMMENT ON COLUMN vw_otros_sociedad.modalidad IS 'Modalidad del delito según catálogo SSPC.';
COMMENT ON COLUMN vw_otros_sociedad.mes IS 'Nombre del mes en español.';
COMMENT ON COLUMN vw_otros_sociedad.conteo IS 'Número de carpetas de investigación.';

COMMENT ON VIEW vw_otros_fuero_comun IS
    'Filtro de vw_delitos_serie_historica: otros delitos del fuero común y suplantación de identidad. Abarca 2015-presente.';
COMMENT ON COLUMN vw_otros_fuero_comun.id IS 'Identificador de fila generado por ROW_NUMBER().';
COMMENT ON COLUMN vw_otros_fuero_comun.anio IS 'Año del registro.';
COMMENT ON COLUMN vw_otros_fuero_comun.cve_municipio IS 'Clave geoestadística del municipio (5 dígitos, EEMMM).';
COMMENT ON COLUMN vw_otros_fuero_comun.clave_ent IS 'Clave de entidad federativa (2 dígitos).';
COMMENT ON COLUMN vw_otros_fuero_comun.entidad IS 'Nombre de la entidad federativa.';
COMMENT ON COLUMN vw_otros_fuero_comun.municipio IS 'Nombre del municipio.';
COMMENT ON COLUMN vw_otros_fuero_comun.bien_juridico_afectado IS 'Bien jurídico afectado según catálogo SSPC.';
COMMENT ON COLUMN vw_otros_fuero_comun.tipo_delito IS 'Tipo de delito según catálogo SSPC.';
COMMENT ON COLUMN vw_otros_fuero_comun.subtipo_delito IS 'Subtipo de delito según catálogo SSPC.';
COMMENT ON COLUMN vw_otros_fuero_comun.modalidad IS 'Modalidad del delito según catálogo SSPC.';
COMMENT ON COLUMN vw_otros_fuero_comun.mes IS 'Nombre del mes en español.';
COMMENT ON COLUMN vw_otros_fuero_comun.conteo IS 'Número de carpetas de investigación.';

COMMENT ON VIEW vw_servidores_publicos IS
    'Filtro de vw_delitos_serie_historica: delitos cometidos por servidores públicos (tortura, delitos contra la administración de justicia). Abarca 2015-presente.';
COMMENT ON COLUMN vw_servidores_publicos.id IS 'Identificador de fila generado por ROW_NUMBER().';
COMMENT ON COLUMN vw_servidores_publicos.anio IS 'Año del registro.';
COMMENT ON COLUMN vw_servidores_publicos.cve_municipio IS 'Clave geoestadística del municipio (5 dígitos, EEMMM).';
COMMENT ON COLUMN vw_servidores_publicos.clave_ent IS 'Clave de entidad federativa (2 dígitos).';
COMMENT ON COLUMN vw_servidores_publicos.entidad IS 'Nombre de la entidad federativa.';
COMMENT ON COLUMN vw_servidores_publicos.municipio IS 'Nombre del municipio.';
COMMENT ON COLUMN vw_servidores_publicos.bien_juridico_afectado IS 'Bien jurídico afectado según catálogo SSPC.';
COMMENT ON COLUMN vw_servidores_publicos.tipo_delito IS 'Tipo de delito según catálogo SSPC.';
COMMENT ON COLUMN vw_servidores_publicos.subtipo_delito IS 'Subtipo de delito según catálogo SSPC.';
COMMENT ON COLUMN vw_servidores_publicos.modalidad IS 'Modalidad del delito según catálogo SSPC.';
COMMENT ON COLUMN vw_servidores_publicos.mes IS 'Nombre del mes en español.';
COMMENT ON COLUMN vw_servidores_publicos.conteo IS 'Número de carpetas de investigación.';

COMMENT ON VIEW vw_delitos_comparables_general IS
    'Serie unificada 2015-2026 con re-etiquetado de tipo_delito para subtipos exclusivos de 2026 '
    'que corresponden a categorías históricas. Permite comparabilidad longitudinal. '
    'Branch 1 (2015-2025): pass-through. Branch 2 (2026): 10 reglas de re-etiquetado.';
COMMENT ON COLUMN vw_delitos_comparables_general.id IS 'Identificador de fila generado por ROW_NUMBER().';
COMMENT ON COLUMN vw_delitos_comparables_general.anio IS 'Año del registro.';
COMMENT ON COLUMN vw_delitos_comparables_general.cve_municipio IS 'Clave geoestadística del municipio (5 dígitos, EEMMM).';
COMMENT ON COLUMN vw_delitos_comparables_general.clave_ent IS 'Clave de entidad federativa (2 dígitos).';
COMMENT ON COLUMN vw_delitos_comparables_general.entidad IS 'Nombre de la entidad federativa.';
COMMENT ON COLUMN vw_delitos_comparables_general.municipio IS 'Nombre del municipio.';
COMMENT ON COLUMN vw_delitos_comparables_general.bien_juridico_afectado IS 'Bien jurídico afectado según catálogo SSPC.';
COMMENT ON COLUMN vw_delitos_comparables_general.tipo_delito IS
    'Tipo de delito normalizado para comparabilidad: los subtipos de 2026 sin equivalente histórico '
    'se re-etiquetan a su categoría histórica correspondiente.';
COMMENT ON COLUMN vw_delitos_comparables_general.subtipo_delito IS 'Subtipo de delito original del catálogo SSPC (sin modificar).';
COMMENT ON COLUMN vw_delitos_comparables_general.modalidad IS 'Modalidad del delito según catálogo SSPC.';
COMMENT ON COLUMN vw_delitos_comparables_general.mes IS 'Nombre del mes en español.';
COMMENT ON COLUMN vw_delitos_comparables_general.conteo IS 'Número de carpetas de investigación.';

-- =============================================================================
-- VISTA MATERIALIZADA GOLD (V6)
-- =============================================================================

COMMENT ON MATERIALIZED VIEW vw_gold_delitos_fuero_comun IS
    'Gold layer de delitos del fuero común para Jalisco (cve_ent = 14). '
    'Consolida 13 delitos seleccionados con total mensual (nivel_jerarquico = delito) '
    'y 5 con desagregación por modalidad (nivel_jerarquico = modalidad). '
    'Tasa por 100,000 habitantes con población CONAPO (pob_mit_mun). '
    'Fuente: SSPC/RNID 2015-2025 (stg_delitos_fuero_comun_2015_2025) y '
    '2026+ (stg_delitos_fuero_comun_2026).';
COMMENT ON COLUMN vw_gold_delitos_fuero_comun.fecha_anio IS
    'Año del registro (YYYY).';
COMMENT ON COLUMN vw_gold_delitos_fuero_comun.fecha_mes IS
    'Mes del registro en formato YYYY-MM.';
COMMENT ON COLUMN vw_gold_delitos_fuero_comun.clave_ent IS
    'Clave de entidad federativa; siempre 14 (Jalisco).';
COMMENT ON COLUMN vw_gold_delitos_fuero_comun.cve_municipio IS
    'Clave geoestadística del municipio (VARCHAR 5 dígitos, EEMMM).';
COMMENT ON COLUMN vw_gold_delitos_fuero_comun.nivel_jerarquico IS
    'Nivel de agregación: delito (total mensual) | modalidad (desglose por modalidad).';
COMMENT ON COLUMN vw_gold_delitos_fuero_comun.bien_juridico IS
    'Bien jurídico afectado según catálogo SSPC.';
COMMENT ON COLUMN vw_gold_delitos_fuero_comun.delito IS
    'Nombre normalizado del delito en el gold layer.';
COMMENT ON COLUMN vw_gold_delitos_fuero_comun.modalidad IS
    'Modalidad del delito; NULL cuando nivel_jerarquico = delito.';
COMMENT ON COLUMN vw_gold_delitos_fuero_comun.carpetas_investigacion IS
    'Número de carpetas de investigación iniciadas en el mes.';
COMMENT ON COLUMN vw_gold_delitos_fuero_comun.tasa_carpetas_investigacion IS
    'Tasa por 100,000 habitantes (CONAPO pob_mit_mun). NULL si sin dato poblacional.';

-- =============================================================================
-- VISTAS MATERIALIZADAS SECRETARIADO (V7)  — columnas comunes
-- =============================================================================

COMMENT ON MATERIALIZED VIEW vwm_datos_delitos_homicidio_doloso_secretariado IS
    'Vista materializada de homicidio doloso a nivel municipal mensual para Jalisco. '
    'Fuente: vw_gold_delitos_fuero_comun, delito = ''Homicidio doloso''. '
    'Incluye geometría municipal y pivot de armas por modalidad.';
COMMENT ON COLUMN vwm_datos_delitos_homicidio_doloso_secretariado.fid IS 'Identificador de fila incremental.';
COMMENT ON COLUMN vwm_datos_delitos_homicidio_doloso_secretariado.geom_iieg IS 'Geometría MultiPolygon del municipio según delimitación IIEG (SRID 6368).';
COMMENT ON COLUMN vwm_datos_delitos_homicidio_doloso_secretariado.geom_inegi IS 'Geometría MultiPolygon del municipio según delimitación INEGI (SRID 6368).';
COMMENT ON COLUMN vwm_datos_delitos_homicidio_doloso_secretariado.nombre IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN vwm_datos_delitos_homicidio_doloso_secretariado.fecha IS 'Primer día del mes al que corresponde el registro (YYYY-MM-DD).';
COMMENT ON COLUMN vwm_datos_delitos_homicidio_doloso_secretariado.clave_entidad IS 'Clave de entidad federativa; siempre 14 (Jalisco).';
COMMENT ON COLUMN vwm_datos_delitos_homicidio_doloso_secretariado.clave_municipio IS 'Clave geoestadística del municipio (5 dígitos, EEMMM).';
COMMENT ON COLUMN vwm_datos_delitos_homicidio_doloso_secretariado.bien_juridico IS 'Bien jurídico afectado según catálogo SSPC.';
COMMENT ON COLUMN vwm_datos_delitos_homicidio_doloso_secretariado.delito IS 'Nombre del delito.';
COMMENT ON COLUMN vwm_datos_delitos_homicidio_doloso_secretariado.con_arma_de_fuego IS 'Carpetas de investigación donde la modalidad incluye arma de fuego.';
COMMENT ON COLUMN vwm_datos_delitos_homicidio_doloso_secretariado.con_arma_blanca IS 'Carpetas de investigación donde la modalidad incluye arma blanca.';
COMMENT ON COLUMN vwm_datos_delitos_homicidio_doloso_secretariado.con_otro_elemento IS 'Carpetas de investigación donde la modalidad incluye otro elemento.';
COMMENT ON COLUMN vwm_datos_delitos_homicidio_doloso_secretariado.no_especificado IS 'Carpetas de investigación sin especificar el elemento utilizado.';
COMMENT ON COLUMN vwm_datos_delitos_homicidio_doloso_secretariado.carpetas_investigacion IS 'Total de carpetas de investigación iniciadas en el mes.';
COMMENT ON COLUMN vwm_datos_delitos_homicidio_doloso_secretariado.tasa_carpetas_investigacion IS 'Tasa por 100,000 habitantes (CONAPO pob_mit_mun). NULL si sin dato poblacional.';

COMMENT ON MATERIALIZED VIEW vwm_datos_delitos_feminicidio_secretariado IS
    'Vista materializada de feminicidio a nivel municipal mensual para Jalisco. '
    'Fuente: vw_gold_delitos_fuero_comun, delito = ''Feminicidio''. '
    'Incluye geometría municipal y pivot de armas por modalidad.';
COMMENT ON COLUMN vwm_datos_delitos_feminicidio_secretariado.fid IS 'Identificador de fila incremental.';
COMMENT ON COLUMN vwm_datos_delitos_feminicidio_secretariado.geom_iieg IS 'Geometría MultiPolygon del municipio según delimitación IIEG (SRID 6368).';
COMMENT ON COLUMN vwm_datos_delitos_feminicidio_secretariado.geom_inegi IS 'Geometría MultiPolygon del municipio según delimitación INEGI (SRID 6368).';
COMMENT ON COLUMN vwm_datos_delitos_feminicidio_secretariado.nombre IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN vwm_datos_delitos_feminicidio_secretariado.fecha IS 'Primer día del mes al que corresponde el registro (YYYY-MM-DD).';
COMMENT ON COLUMN vwm_datos_delitos_feminicidio_secretariado.clave_entidad IS 'Clave de entidad federativa; siempre 14 (Jalisco).';
COMMENT ON COLUMN vwm_datos_delitos_feminicidio_secretariado.clave_municipio IS 'Clave geoestadística del municipio (5 dígitos, EEMMM).';
COMMENT ON COLUMN vwm_datos_delitos_feminicidio_secretariado.bien_juridico IS 'Bien jurídico afectado según catálogo SSPC.';
COMMENT ON COLUMN vwm_datos_delitos_feminicidio_secretariado.delito IS 'Nombre del delito.';
COMMENT ON COLUMN vwm_datos_delitos_feminicidio_secretariado.con_arma_de_fuego IS 'Carpetas de investigación donde la modalidad incluye arma de fuego.';
COMMENT ON COLUMN vwm_datos_delitos_feminicidio_secretariado.con_arma_blanca IS 'Carpetas de investigación donde la modalidad incluye arma blanca.';
COMMENT ON COLUMN vwm_datos_delitos_feminicidio_secretariado.con_otro_elemento IS 'Carpetas de investigación donde la modalidad incluye otro elemento.';
COMMENT ON COLUMN vwm_datos_delitos_feminicidio_secretariado.no_especificado IS 'Carpetas de investigación sin especificar el elemento utilizado.';
COMMENT ON COLUMN vwm_datos_delitos_feminicidio_secretariado.carpetas_investigacion IS 'Total de carpetas de investigación iniciadas en el mes.';
COMMENT ON COLUMN vwm_datos_delitos_feminicidio_secretariado.tasa_carpetas_investigacion IS 'Tasa por 100,000 habitantes (CONAPO pob_mit_mun). NULL si sin dato poblacional.';

COMMENT ON MATERIALIZED VIEW vwm_datos_delitos_lesiones_dolosas_secretariado IS
    'Vista materializada de lesiones dolosas a nivel municipal mensual para Jalisco. '
    'Fuente: vw_gold_delitos_fuero_comun, delito = ''Lesiones dolosas''. '
    'Incluye geometría municipal y pivot de armas por modalidad.';
COMMENT ON COLUMN vwm_datos_delitos_lesiones_dolosas_secretariado.fid IS 'Identificador de fila incremental.';
COMMENT ON COLUMN vwm_datos_delitos_lesiones_dolosas_secretariado.geom_iieg IS 'Geometría MultiPolygon del municipio según delimitación IIEG (SRID 6368).';
COMMENT ON COLUMN vwm_datos_delitos_lesiones_dolosas_secretariado.geom_inegi IS 'Geometría MultiPolygon del municipio según delimitación INEGI (SRID 6368).';
COMMENT ON COLUMN vwm_datos_delitos_lesiones_dolosas_secretariado.nombre IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN vwm_datos_delitos_lesiones_dolosas_secretariado.fecha IS 'Primer día del mes al que corresponde el registro (YYYY-MM-DD).';
COMMENT ON COLUMN vwm_datos_delitos_lesiones_dolosas_secretariado.clave_entidad IS 'Clave de entidad federativa; siempre 14 (Jalisco).';
COMMENT ON COLUMN vwm_datos_delitos_lesiones_dolosas_secretariado.clave_municipio IS 'Clave geoestadística del municipio (5 dígitos, EEMMM).';
COMMENT ON COLUMN vwm_datos_delitos_lesiones_dolosas_secretariado.bien_juridico IS 'Bien jurídico afectado según catálogo SSPC.';
COMMENT ON COLUMN vwm_datos_delitos_lesiones_dolosas_secretariado.delito IS 'Nombre del delito.';
COMMENT ON COLUMN vwm_datos_delitos_lesiones_dolosas_secretariado.con_arma_de_fuego IS 'Carpetas de investigación donde la modalidad incluye arma de fuego.';
COMMENT ON COLUMN vwm_datos_delitos_lesiones_dolosas_secretariado.con_arma_blanca IS 'Carpetas de investigación donde la modalidad incluye arma blanca.';
COMMENT ON COLUMN vwm_datos_delitos_lesiones_dolosas_secretariado.con_otro_elemento IS 'Carpetas de investigación donde la modalidad incluye otro elemento.';
COMMENT ON COLUMN vwm_datos_delitos_lesiones_dolosas_secretariado.no_especificado IS 'Carpetas de investigación sin especificar el elemento utilizado.';
COMMENT ON COLUMN vwm_datos_delitos_lesiones_dolosas_secretariado.carpetas_investigacion IS 'Total de carpetas de investigación iniciadas en el mes.';
COMMENT ON COLUMN vwm_datos_delitos_lesiones_dolosas_secretariado.tasa_carpetas_investigacion IS 'Tasa por 100,000 habitantes (CONAPO pob_mit_mun). NULL si sin dato poblacional.';

COMMENT ON MATERIALIZED VIEW vwm_datos_delitos_violacion_secretariado IS
    'Vista materializada de violación a nivel municipal mensual para Jalisco. '
    'Fuente: vw_gold_delitos_fuero_comun, delito = ''Violación'' '
    '(fusiona Violación simple + Violación equiparada). '
    'Incluye geometría municipal y pivot de armas por modalidad.';
COMMENT ON COLUMN vwm_datos_delitos_violacion_secretariado.fid IS 'Identificador de fila incremental.';
COMMENT ON COLUMN vwm_datos_delitos_violacion_secretariado.geom_iieg IS 'Geometría MultiPolygon del municipio según delimitación IIEG (SRID 6368).';
COMMENT ON COLUMN vwm_datos_delitos_violacion_secretariado.geom_inegi IS 'Geometría MultiPolygon del municipio según delimitación INEGI (SRID 6368).';
COMMENT ON COLUMN vwm_datos_delitos_violacion_secretariado.nombre IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN vwm_datos_delitos_violacion_secretariado.fecha IS 'Primer día del mes al que corresponde el registro (YYYY-MM-DD).';
COMMENT ON COLUMN vwm_datos_delitos_violacion_secretariado.clave_entidad IS 'Clave de entidad federativa; siempre 14 (Jalisco).';
COMMENT ON COLUMN vwm_datos_delitos_violacion_secretariado.clave_municipio IS 'Clave geoestadística del municipio (5 dígitos, EEMMM).';
COMMENT ON COLUMN vwm_datos_delitos_violacion_secretariado.bien_juridico IS 'Bien jurídico afectado según catálogo SSPC.';
COMMENT ON COLUMN vwm_datos_delitos_violacion_secretariado.delito IS 'Nombre del delito.';
COMMENT ON COLUMN vwm_datos_delitos_violacion_secretariado.con_arma_de_fuego IS 'Carpetas de investigación donde la modalidad incluye arma de fuego.';
COMMENT ON COLUMN vwm_datos_delitos_violacion_secretariado.con_arma_blanca IS 'Carpetas de investigación donde la modalidad incluye arma blanca.';
COMMENT ON COLUMN vwm_datos_delitos_violacion_secretariado.con_otro_elemento IS 'Carpetas de investigación donde la modalidad incluye otro elemento.';
COMMENT ON COLUMN vwm_datos_delitos_violacion_secretariado.no_especificado IS 'Carpetas de investigación sin especificar el elemento utilizado.';
COMMENT ON COLUMN vwm_datos_delitos_violacion_secretariado.carpetas_investigacion IS 'Total de carpetas de investigación iniciadas en el mes.';
COMMENT ON COLUMN vwm_datos_delitos_violacion_secretariado.tasa_carpetas_investigacion IS 'Tasa por 100,000 habitantes (CONAPO pob_mit_mun). NULL si sin dato poblacional.';

COMMENT ON MATERIALIZED VIEW vwm_datos_delitos_abuso_sexual_secretariado IS
    'Vista materializada de abuso sexual a nivel municipal mensual para Jalisco. '
    'Fuente: vw_gold_delitos_fuero_comun, delito = ''Abuso sexual''.';
COMMENT ON COLUMN vwm_datos_delitos_abuso_sexual_secretariado.fid IS 'Identificador de fila incremental.';
COMMENT ON COLUMN vwm_datos_delitos_abuso_sexual_secretariado.geom_iieg IS 'Geometría MultiPolygon del municipio según delimitación IIEG (SRID 6368).';
COMMENT ON COLUMN vwm_datos_delitos_abuso_sexual_secretariado.geom_inegi IS 'Geometría MultiPolygon del municipio según delimitación INEGI (SRID 6368).';
COMMENT ON COLUMN vwm_datos_delitos_abuso_sexual_secretariado.nombre IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN vwm_datos_delitos_abuso_sexual_secretariado.fecha IS 'Primer día del mes al que corresponde el registro (YYYY-MM-DD).';
COMMENT ON COLUMN vwm_datos_delitos_abuso_sexual_secretariado.clave_entidad IS 'Clave de entidad federativa; siempre 14 (Jalisco).';
COMMENT ON COLUMN vwm_datos_delitos_abuso_sexual_secretariado.clave_municipio IS 'Clave geoestadística del municipio (5 dígitos, EEMMM).';
COMMENT ON COLUMN vwm_datos_delitos_abuso_sexual_secretariado.bien_juridico IS 'Bien jurídico afectado según catálogo SSPC.';
COMMENT ON COLUMN vwm_datos_delitos_abuso_sexual_secretariado.delito IS 'Nombre del delito.';
COMMENT ON COLUMN vwm_datos_delitos_abuso_sexual_secretariado.con_arma_de_fuego IS 'Carpetas de investigación donde la modalidad incluye arma de fuego.';
COMMENT ON COLUMN vwm_datos_delitos_abuso_sexual_secretariado.con_arma_blanca IS 'Carpetas de investigación donde la modalidad incluye arma blanca.';
COMMENT ON COLUMN vwm_datos_delitos_abuso_sexual_secretariado.con_otro_elemento IS 'Carpetas de investigación donde la modalidad incluye otro elemento.';
COMMENT ON COLUMN vwm_datos_delitos_abuso_sexual_secretariado.no_especificado IS 'Carpetas de investigación sin especificar el elemento utilizado.';
COMMENT ON COLUMN vwm_datos_delitos_abuso_sexual_secretariado.carpetas_investigacion IS 'Total de carpetas de investigación iniciadas en el mes.';
COMMENT ON COLUMN vwm_datos_delitos_abuso_sexual_secretariado.tasa_carpetas_investigacion IS 'Tasa por 100,000 habitantes (CONAPO pob_mit_mun). NULL si sin dato poblacional.';

COMMENT ON MATERIALIZED VIEW vwm_datos_delitos_violencia_familiar_secretariado IS
    'Vista materializada de violencia familiar a nivel municipal mensual para Jalisco. '
    'Fuente: vw_gold_delitos_fuero_comun, delito = ''Violencia familiar''.';
COMMENT ON COLUMN vwm_datos_delitos_violencia_familiar_secretariado.fid IS 'Identificador de fila incremental.';
COMMENT ON COLUMN vwm_datos_delitos_violencia_familiar_secretariado.geom_iieg IS 'Geometría MultiPolygon del municipio según delimitación IIEG (SRID 6368).';
COMMENT ON COLUMN vwm_datos_delitos_violencia_familiar_secretariado.geom_inegi IS 'Geometría MultiPolygon del municipio según delimitación INEGI (SRID 6368).';
COMMENT ON COLUMN vwm_datos_delitos_violencia_familiar_secretariado.nombre IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN vwm_datos_delitos_violencia_familiar_secretariado.fecha IS 'Primer día del mes al que corresponde el registro (YYYY-MM-DD).';
COMMENT ON COLUMN vwm_datos_delitos_violencia_familiar_secretariado.clave_entidad IS 'Clave de entidad federativa; siempre 14 (Jalisco).';
COMMENT ON COLUMN vwm_datos_delitos_violencia_familiar_secretariado.clave_municipio IS 'Clave geoestadística del municipio (5 dígitos, EEMMM).';
COMMENT ON COLUMN vwm_datos_delitos_violencia_familiar_secretariado.bien_juridico IS 'Bien jurídico afectado según catálogo SSPC.';
COMMENT ON COLUMN vwm_datos_delitos_violencia_familiar_secretariado.delito IS 'Nombre del delito.';
COMMENT ON COLUMN vwm_datos_delitos_violencia_familiar_secretariado.con_arma_de_fuego IS 'Carpetas de investigación donde la modalidad incluye arma de fuego.';
COMMENT ON COLUMN vwm_datos_delitos_violencia_familiar_secretariado.con_arma_blanca IS 'Carpetas de investigación donde la modalidad incluye arma blanca.';
COMMENT ON COLUMN vwm_datos_delitos_violencia_familiar_secretariado.con_otro_elemento IS 'Carpetas de investigación donde la modalidad incluye otro elemento.';
COMMENT ON COLUMN vwm_datos_delitos_violencia_familiar_secretariado.no_especificado IS 'Carpetas de investigación sin especificar el elemento utilizado.';
COMMENT ON COLUMN vwm_datos_delitos_violencia_familiar_secretariado.carpetas_investigacion IS 'Total de carpetas de investigación iniciadas en el mes.';
COMMENT ON COLUMN vwm_datos_delitos_violencia_familiar_secretariado.tasa_carpetas_investigacion IS 'Tasa por 100,000 habitantes (CONAPO pob_mit_mun). NULL si sin dato poblacional.';

COMMENT ON MATERIALIZED VIEW vwm_datos_delitos_violencia_genero_no_familiar_secretariado IS
    'Vista materializada de violencia de género en el ámbito no familiar a nivel municipal mensual para Jalisco. '
    'Fuente: vw_gold_delitos_fuero_comun, delito = ''Violencia de género en todas sus modalidades distinta a la violencia familiar''.';
COMMENT ON COLUMN vwm_datos_delitos_violencia_genero_no_familiar_secretariado.fid IS 'Identificador de fila incremental.';
COMMENT ON COLUMN vwm_datos_delitos_violencia_genero_no_familiar_secretariado.geom_iieg IS 'Geometría MultiPolygon del municipio según delimitación IIEG (SRID 6368).';
COMMENT ON COLUMN vwm_datos_delitos_violencia_genero_no_familiar_secretariado.geom_inegi IS 'Geometría MultiPolygon del municipio según delimitación INEGI (SRID 6368).';
COMMENT ON COLUMN vwm_datos_delitos_violencia_genero_no_familiar_secretariado.nombre IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN vwm_datos_delitos_violencia_genero_no_familiar_secretariado.fecha IS 'Primer día del mes al que corresponde el registro (YYYY-MM-DD).';
COMMENT ON COLUMN vwm_datos_delitos_violencia_genero_no_familiar_secretariado.clave_entidad IS 'Clave de entidad federativa; siempre 14 (Jalisco).';
COMMENT ON COLUMN vwm_datos_delitos_violencia_genero_no_familiar_secretariado.clave_municipio IS 'Clave geoestadística del municipio (5 dígitos, EEMMM).';
COMMENT ON COLUMN vwm_datos_delitos_violencia_genero_no_familiar_secretariado.bien_juridico IS 'Bien jurídico afectado según catálogo SSPC.';
COMMENT ON COLUMN vwm_datos_delitos_violencia_genero_no_familiar_secretariado.delito IS 'Nombre del delito.';
COMMENT ON COLUMN vwm_datos_delitos_violencia_genero_no_familiar_secretariado.con_arma_de_fuego IS 'Carpetas de investigación donde la modalidad incluye arma de fuego.';
COMMENT ON COLUMN vwm_datos_delitos_violencia_genero_no_familiar_secretariado.con_arma_blanca IS 'Carpetas de investigación donde la modalidad incluye arma blanca.';
COMMENT ON COLUMN vwm_datos_delitos_violencia_genero_no_familiar_secretariado.con_otro_elemento IS 'Carpetas de investigación donde la modalidad incluye otro elemento.';
COMMENT ON COLUMN vwm_datos_delitos_violencia_genero_no_familiar_secretariado.no_especificado IS 'Carpetas de investigación sin especificar el elemento utilizado.';
COMMENT ON COLUMN vwm_datos_delitos_violencia_genero_no_familiar_secretariado.carpetas_investigacion IS 'Total de carpetas de investigación iniciadas en el mes.';
COMMENT ON COLUMN vwm_datos_delitos_violencia_genero_no_familiar_secretariado.tasa_carpetas_investigacion IS 'Tasa por 100,000 habitantes (CONAPO pob_mit_mun). NULL si sin dato poblacional.';

COMMENT ON MATERIALIZED VIEW vwm_datos_delitos_robo_coche_cuatro_ruedas_secretariado IS
    'Vista materializada de robo de coche de cuatro ruedas a nivel municipal mensual para Jalisco. '
    'Fuente: vw_gold_delitos_fuero_comun, delito = ''Robo de coche de cuatro ruedas''. '
    'Las columnas con_arma_* reflejan modalidad vehicular (Con/Sin violencia), no armas de fuego.';
COMMENT ON COLUMN vwm_datos_delitos_robo_coche_cuatro_ruedas_secretariado.fid IS 'Identificador de fila incremental.';
COMMENT ON COLUMN vwm_datos_delitos_robo_coche_cuatro_ruedas_secretariado.geom_iieg IS 'Geometría MultiPolygon del municipio según delimitación IIEG (SRID 6368).';
COMMENT ON COLUMN vwm_datos_delitos_robo_coche_cuatro_ruedas_secretariado.geom_inegi IS 'Geometría MultiPolygon del municipio según delimitación INEGI (SRID 6368).';
COMMENT ON COLUMN vwm_datos_delitos_robo_coche_cuatro_ruedas_secretariado.nombre IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN vwm_datos_delitos_robo_coche_cuatro_ruedas_secretariado.fecha IS 'Primer día del mes al que corresponde el registro (YYYY-MM-DD).';
COMMENT ON COLUMN vwm_datos_delitos_robo_coche_cuatro_ruedas_secretariado.clave_entidad IS 'Clave de entidad federativa; siempre 14 (Jalisco).';
COMMENT ON COLUMN vwm_datos_delitos_robo_coche_cuatro_ruedas_secretariado.clave_municipio IS 'Clave geoestadística del municipio (5 dígitos, EEMMM).';
COMMENT ON COLUMN vwm_datos_delitos_robo_coche_cuatro_ruedas_secretariado.bien_juridico IS 'Bien jurídico afectado según catálogo SSPC.';
COMMENT ON COLUMN vwm_datos_delitos_robo_coche_cuatro_ruedas_secretariado.delito IS 'Nombre del delito.';
COMMENT ON COLUMN vwm_datos_delitos_robo_coche_cuatro_ruedas_secretariado.con_arma_de_fuego IS 'NULL para este delito (las modalidades son Con/Sin violencia, no por tipo de arma).';
COMMENT ON COLUMN vwm_datos_delitos_robo_coche_cuatro_ruedas_secretariado.con_arma_blanca IS 'NULL para este delito.';
COMMENT ON COLUMN vwm_datos_delitos_robo_coche_cuatro_ruedas_secretariado.con_otro_elemento IS 'NULL para este delito.';
COMMENT ON COLUMN vwm_datos_delitos_robo_coche_cuatro_ruedas_secretariado.no_especificado IS 'NULL para este delito.';
COMMENT ON COLUMN vwm_datos_delitos_robo_coche_cuatro_ruedas_secretariado.carpetas_investigacion IS 'Total de carpetas de investigación iniciadas en el mes.';
COMMENT ON COLUMN vwm_datos_delitos_robo_coche_cuatro_ruedas_secretariado.tasa_carpetas_investigacion IS 'Tasa por 100,000 habitantes (CONAPO pob_mit_mun). NULL si sin dato poblacional.';

COMMENT ON MATERIALIZED VIEW vwm_datos_delitos_robo_motocicleta_secretariado IS
    'Vista materializada de robo de motocicleta a nivel municipal mensual para Jalisco. '
    'Fuente: vw_gold_delitos_fuero_comun, delito = ''Robo de motocicleta''.';
COMMENT ON COLUMN vwm_datos_delitos_robo_motocicleta_secretariado.fid IS 'Identificador de fila incremental.';
COMMENT ON COLUMN vwm_datos_delitos_robo_motocicleta_secretariado.geom_iieg IS 'Geometría MultiPolygon del municipio según delimitación IIEG (SRID 6368).';
COMMENT ON COLUMN vwm_datos_delitos_robo_motocicleta_secretariado.geom_inegi IS 'Geometría MultiPolygon del municipio según delimitación INEGI (SRID 6368).';
COMMENT ON COLUMN vwm_datos_delitos_robo_motocicleta_secretariado.nombre IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN vwm_datos_delitos_robo_motocicleta_secretariado.fecha IS 'Primer día del mes al que corresponde el registro (YYYY-MM-DD).';
COMMENT ON COLUMN vwm_datos_delitos_robo_motocicleta_secretariado.clave_entidad IS 'Clave de entidad federativa; siempre 14 (Jalisco).';
COMMENT ON COLUMN vwm_datos_delitos_robo_motocicleta_secretariado.clave_municipio IS 'Clave geoestadística del municipio (5 dígitos, EEMMM).';
COMMENT ON COLUMN vwm_datos_delitos_robo_motocicleta_secretariado.bien_juridico IS 'Bien jurídico afectado según catálogo SSPC.';
COMMENT ON COLUMN vwm_datos_delitos_robo_motocicleta_secretariado.delito IS 'Nombre del delito.';
COMMENT ON COLUMN vwm_datos_delitos_robo_motocicleta_secretariado.con_arma_de_fuego IS 'NULL para este delito (las modalidades son Con/Sin violencia).';
COMMENT ON COLUMN vwm_datos_delitos_robo_motocicleta_secretariado.con_arma_blanca IS 'NULL para este delito.';
COMMENT ON COLUMN vwm_datos_delitos_robo_motocicleta_secretariado.con_otro_elemento IS 'NULL para este delito.';
COMMENT ON COLUMN vwm_datos_delitos_robo_motocicleta_secretariado.no_especificado IS 'NULL para este delito.';
COMMENT ON COLUMN vwm_datos_delitos_robo_motocicleta_secretariado.carpetas_investigacion IS 'Total de carpetas de investigación iniciadas en el mes.';
COMMENT ON COLUMN vwm_datos_delitos_robo_motocicleta_secretariado.tasa_carpetas_investigacion IS 'Tasa por 100,000 habitantes (CONAPO pob_mit_mun). NULL si sin dato poblacional.';

COMMENT ON MATERIALIZED VIEW vwm_datos_delitos_robo_autopartes_secretariado IS
    'Vista materializada de robo de autopartes a nivel municipal mensual para Jalisco. '
    'Fuente: vw_gold_delitos_fuero_comun, delito = ''Robo de autopartes''.';
COMMENT ON COLUMN vwm_datos_delitos_robo_autopartes_secretariado.fid IS 'Identificador de fila incremental.';
COMMENT ON COLUMN vwm_datos_delitos_robo_autopartes_secretariado.geom_iieg IS 'Geometría MultiPolygon del municipio según delimitación IIEG (SRID 6368).';
COMMENT ON COLUMN vwm_datos_delitos_robo_autopartes_secretariado.geom_inegi IS 'Geometría MultiPolygon del municipio según delimitación INEGI (SRID 6368).';
COMMENT ON COLUMN vwm_datos_delitos_robo_autopartes_secretariado.nombre IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN vwm_datos_delitos_robo_autopartes_secretariado.fecha IS 'Primer día del mes al que corresponde el registro (YYYY-MM-DD).';
COMMENT ON COLUMN vwm_datos_delitos_robo_autopartes_secretariado.clave_entidad IS 'Clave de entidad federativa; siempre 14 (Jalisco).';
COMMENT ON COLUMN vwm_datos_delitos_robo_autopartes_secretariado.clave_municipio IS 'Clave geoestadística del municipio (5 dígitos, EEMMM).';
COMMENT ON COLUMN vwm_datos_delitos_robo_autopartes_secretariado.bien_juridico IS 'Bien jurídico afectado según catálogo SSPC.';
COMMENT ON COLUMN vwm_datos_delitos_robo_autopartes_secretariado.delito IS 'Nombre del delito.';
COMMENT ON COLUMN vwm_datos_delitos_robo_autopartes_secretariado.con_arma_de_fuego IS 'Carpetas de investigación donde la modalidad incluye arma de fuego.';
COMMENT ON COLUMN vwm_datos_delitos_robo_autopartes_secretariado.con_arma_blanca IS 'Carpetas de investigación donde la modalidad incluye arma blanca.';
COMMENT ON COLUMN vwm_datos_delitos_robo_autopartes_secretariado.con_otro_elemento IS 'Carpetas de investigación donde la modalidad incluye otro elemento.';
COMMENT ON COLUMN vwm_datos_delitos_robo_autopartes_secretariado.no_especificado IS 'Carpetas de investigación sin especificar el elemento utilizado.';
COMMENT ON COLUMN vwm_datos_delitos_robo_autopartes_secretariado.carpetas_investigacion IS 'Total de carpetas de investigación iniciadas en el mes.';
COMMENT ON COLUMN vwm_datos_delitos_robo_autopartes_secretariado.tasa_carpetas_investigacion IS 'Tasa por 100,000 habitantes (CONAPO pob_mit_mun). NULL si sin dato poblacional.';

COMMENT ON MATERIALIZED VIEW vwm_datos_delitos_robo_casa_habitacion_secretariado IS
    'Vista materializada de robo a casa habitación a nivel municipal mensual para Jalisco. '
    'Fuente: vw_gold_delitos_fuero_comun, delito = ''Robo a casa habitación''.';
COMMENT ON COLUMN vwm_datos_delitos_robo_casa_habitacion_secretariado.fid IS 'Identificador de fila incremental.';
COMMENT ON COLUMN vwm_datos_delitos_robo_casa_habitacion_secretariado.geom_iieg IS 'Geometría MultiPolygon del municipio según delimitación IIEG (SRID 6368).';
COMMENT ON COLUMN vwm_datos_delitos_robo_casa_habitacion_secretariado.geom_inegi IS 'Geometría MultiPolygon del municipio según delimitación INEGI (SRID 6368).';
COMMENT ON COLUMN vwm_datos_delitos_robo_casa_habitacion_secretariado.nombre IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN vwm_datos_delitos_robo_casa_habitacion_secretariado.fecha IS 'Primer día del mes al que corresponde el registro (YYYY-MM-DD).';
COMMENT ON COLUMN vwm_datos_delitos_robo_casa_habitacion_secretariado.clave_entidad IS 'Clave de entidad federativa; siempre 14 (Jalisco).';
COMMENT ON COLUMN vwm_datos_delitos_robo_casa_habitacion_secretariado.clave_municipio IS 'Clave geoestadística del municipio (5 dígitos, EEMMM).';
COMMENT ON COLUMN vwm_datos_delitos_robo_casa_habitacion_secretariado.bien_juridico IS 'Bien jurídico afectado según catálogo SSPC.';
COMMENT ON COLUMN vwm_datos_delitos_robo_casa_habitacion_secretariado.delito IS 'Nombre del delito.';
COMMENT ON COLUMN vwm_datos_delitos_robo_casa_habitacion_secretariado.con_arma_de_fuego IS 'Carpetas de investigación donde la modalidad incluye arma de fuego.';
COMMENT ON COLUMN vwm_datos_delitos_robo_casa_habitacion_secretariado.con_arma_blanca IS 'Carpetas de investigación donde la modalidad incluye arma blanca.';
COMMENT ON COLUMN vwm_datos_delitos_robo_casa_habitacion_secretariado.con_otro_elemento IS 'Carpetas de investigación donde la modalidad incluye otro elemento.';
COMMENT ON COLUMN vwm_datos_delitos_robo_casa_habitacion_secretariado.no_especificado IS 'Carpetas de investigación sin especificar el elemento utilizado.';
COMMENT ON COLUMN vwm_datos_delitos_robo_casa_habitacion_secretariado.carpetas_investigacion IS 'Total de carpetas de investigación iniciadas en el mes.';
COMMENT ON COLUMN vwm_datos_delitos_robo_casa_habitacion_secretariado.tasa_carpetas_investigacion IS 'Tasa por 100,000 habitantes (CONAPO pob_mit_mun). NULL si sin dato poblacional.';

COMMENT ON MATERIALIZED VIEW vwm_datos_delitos_robo_negocio_secretariado IS
    'Vista materializada de robo a negocio a nivel municipal mensual para Jalisco. '
    'Fuente: vw_gold_delitos_fuero_comun, delito = ''Robo a negocio''.';
COMMENT ON COLUMN vwm_datos_delitos_robo_negocio_secretariado.fid IS 'Identificador de fila incremental.';
COMMENT ON COLUMN vwm_datos_delitos_robo_negocio_secretariado.geom_iieg IS 'Geometría MultiPolygon del municipio según delimitación IIEG (SRID 6368).';
COMMENT ON COLUMN vwm_datos_delitos_robo_negocio_secretariado.geom_inegi IS 'Geometría MultiPolygon del municipio según delimitación INEGI (SRID 6368).';
COMMENT ON COLUMN vwm_datos_delitos_robo_negocio_secretariado.nombre IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN vwm_datos_delitos_robo_negocio_secretariado.fecha IS 'Primer día del mes al que corresponde el registro (YYYY-MM-DD).';
COMMENT ON COLUMN vwm_datos_delitos_robo_negocio_secretariado.clave_entidad IS 'Clave de entidad federativa; siempre 14 (Jalisco).';
COMMENT ON COLUMN vwm_datos_delitos_robo_negocio_secretariado.clave_municipio IS 'Clave geoestadística del municipio (5 dígitos, EEMMM).';
COMMENT ON COLUMN vwm_datos_delitos_robo_negocio_secretariado.bien_juridico IS 'Bien jurídico afectado según catálogo SSPC.';
COMMENT ON COLUMN vwm_datos_delitos_robo_negocio_secretariado.delito IS 'Nombre del delito.';
COMMENT ON COLUMN vwm_datos_delitos_robo_negocio_secretariado.con_arma_de_fuego IS 'Carpetas de investigación donde la modalidad incluye arma de fuego.';
COMMENT ON COLUMN vwm_datos_delitos_robo_negocio_secretariado.con_arma_blanca IS 'Carpetas de investigación donde la modalidad incluye arma blanca.';
COMMENT ON COLUMN vwm_datos_delitos_robo_negocio_secretariado.con_otro_elemento IS 'Carpetas de investigación donde la modalidad incluye otro elemento.';
COMMENT ON COLUMN vwm_datos_delitos_robo_negocio_secretariado.no_especificado IS 'Carpetas de investigación sin especificar el elemento utilizado.';
COMMENT ON COLUMN vwm_datos_delitos_robo_negocio_secretariado.carpetas_investigacion IS 'Total de carpetas de investigación iniciadas en el mes.';
COMMENT ON COLUMN vwm_datos_delitos_robo_negocio_secretariado.tasa_carpetas_investigacion IS 'Tasa por 100,000 habitantes (CONAPO pob_mit_mun). NULL si sin dato poblacional.';

COMMENT ON MATERIALIZED VIEW vwm_datos_delitos_robo_transeunte_via_publica_secretariado IS
    'Vista materializada de robo a transeúnte en vía pública a nivel municipal mensual para Jalisco. '
    'Fuente: vw_gold_delitos_fuero_comun, delito = ''Robo a transeúnte en vía pública''.';
COMMENT ON COLUMN vwm_datos_delitos_robo_transeunte_via_publica_secretariado.fid IS 'Identificador de fila incremental.';
COMMENT ON COLUMN vwm_datos_delitos_robo_transeunte_via_publica_secretariado.geom_iieg IS 'Geometría MultiPolygon del municipio según delimitación IIEG (SRID 6368).';
COMMENT ON COLUMN vwm_datos_delitos_robo_transeunte_via_publica_secretariado.geom_inegi IS 'Geometría MultiPolygon del municipio según delimitación INEGI (SRID 6368).';
COMMENT ON COLUMN vwm_datos_delitos_robo_transeunte_via_publica_secretariado.nombre IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN vwm_datos_delitos_robo_transeunte_via_publica_secretariado.fecha IS 'Primer día del mes al que corresponde el registro (YYYY-MM-DD).';
COMMENT ON COLUMN vwm_datos_delitos_robo_transeunte_via_publica_secretariado.clave_entidad IS 'Clave de entidad federativa; siempre 14 (Jalisco).';
COMMENT ON COLUMN vwm_datos_delitos_robo_transeunte_via_publica_secretariado.clave_municipio IS 'Clave geoestadística del municipio (5 dígitos, EEMMM).';
COMMENT ON COLUMN vwm_datos_delitos_robo_transeunte_via_publica_secretariado.bien_juridico IS 'Bien jurídico afectado según catálogo SSPC.';
COMMENT ON COLUMN vwm_datos_delitos_robo_transeunte_via_publica_secretariado.delito IS 'Nombre del delito.';
COMMENT ON COLUMN vwm_datos_delitos_robo_transeunte_via_publica_secretariado.con_arma_de_fuego IS 'Carpetas de investigación donde la modalidad incluye arma de fuego.';
COMMENT ON COLUMN vwm_datos_delitos_robo_transeunte_via_publica_secretariado.con_arma_blanca IS 'Carpetas de investigación donde la modalidad incluye arma blanca.';
COMMENT ON COLUMN vwm_datos_delitos_robo_transeunte_via_publica_secretariado.con_otro_elemento IS 'Carpetas de investigación donde la modalidad incluye otro elemento.';
COMMENT ON COLUMN vwm_datos_delitos_robo_transeunte_via_publica_secretariado.no_especificado IS 'Carpetas de investigación sin especificar el elemento utilizado.';
COMMENT ON COLUMN vwm_datos_delitos_robo_transeunte_via_publica_secretariado.carpetas_investigacion IS 'Total de carpetas de investigación iniciadas en el mes.';
COMMENT ON COLUMN vwm_datos_delitos_robo_transeunte_via_publica_secretariado.tasa_carpetas_investigacion IS 'Tasa por 100,000 habitantes (CONAPO pob_mit_mun). NULL si sin dato poblacional.';

COMMENT ON MATERIALIZED VIEW vwm_datos_delitos_robo_transportista_secretariado IS
    'Vista materializada de robo a transportista a nivel municipal mensual para Jalisco. '
    'Fuente: vw_gold_delitos_fuero_comun, delito = ''Robo a transportista''.';
COMMENT ON COLUMN vwm_datos_delitos_robo_transportista_secretariado.fid IS 'Identificador de fila incremental.';
COMMENT ON COLUMN vwm_datos_delitos_robo_transportista_secretariado.geom_iieg IS 'Geometría MultiPolygon del municipio según delimitación IIEG (SRID 6368).';
COMMENT ON COLUMN vwm_datos_delitos_robo_transportista_secretariado.geom_inegi IS 'Geometría MultiPolygon del municipio según delimitación INEGI (SRID 6368).';
COMMENT ON COLUMN vwm_datos_delitos_robo_transportista_secretariado.nombre IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN vwm_datos_delitos_robo_transportista_secretariado.fecha IS 'Primer día del mes al que corresponde el registro (YYYY-MM-DD).';
COMMENT ON COLUMN vwm_datos_delitos_robo_transportista_secretariado.clave_entidad IS 'Clave de entidad federativa; siempre 14 (Jalisco).';
COMMENT ON COLUMN vwm_datos_delitos_robo_transportista_secretariado.clave_municipio IS 'Clave geoestadística del municipio (5 dígitos, EEMMM).';
COMMENT ON COLUMN vwm_datos_delitos_robo_transportista_secretariado.bien_juridico IS 'Bien jurídico afectado según catálogo SSPC.';
COMMENT ON COLUMN vwm_datos_delitos_robo_transportista_secretariado.delito IS 'Nombre del delito.';
COMMENT ON COLUMN vwm_datos_delitos_robo_transportista_secretariado.con_arma_de_fuego IS 'Carpetas de investigación donde la modalidad incluye arma de fuego.';
COMMENT ON COLUMN vwm_datos_delitos_robo_transportista_secretariado.con_arma_blanca IS 'Carpetas de investigación donde la modalidad incluye arma blanca.';
COMMENT ON COLUMN vwm_datos_delitos_robo_transportista_secretariado.con_otro_elemento IS 'Carpetas de investigación donde la modalidad incluye otro elemento.';
COMMENT ON COLUMN vwm_datos_delitos_robo_transportista_secretariado.no_especificado IS 'Carpetas de investigación sin especificar el elemento utilizado.';
COMMENT ON COLUMN vwm_datos_delitos_robo_transportista_secretariado.carpetas_investigacion IS 'Total de carpetas de investigación iniciadas en el mes.';
COMMENT ON COLUMN vwm_datos_delitos_robo_transportista_secretariado.tasa_carpetas_investigacion IS 'Tasa por 100,000 habitantes (CONAPO pob_mit_mun). NULL si sin dato poblacional.';

COMMENT ON MATERIALIZED VIEW vwm_datos_delitos_robo_institucion_bancaria_secretariado IS
    'Vista materializada de robo a institución bancaria a nivel municipal mensual para Jalisco. '
    'Fuente: vw_gold_delitos_fuero_comun, delito = ''Robo a institución bancaria''.';
COMMENT ON COLUMN vwm_datos_delitos_robo_institucion_bancaria_secretariado.fid IS 'Identificador de fila incremental.';
COMMENT ON COLUMN vwm_datos_delitos_robo_institucion_bancaria_secretariado.geom_iieg IS 'Geometría MultiPolygon del municipio según delimitación IIEG (SRID 6368).';
COMMENT ON COLUMN vwm_datos_delitos_robo_institucion_bancaria_secretariado.geom_inegi IS 'Geometría MultiPolygon del municipio según delimitación INEGI (SRID 6368).';
COMMENT ON COLUMN vwm_datos_delitos_robo_institucion_bancaria_secretariado.nombre IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN vwm_datos_delitos_robo_institucion_bancaria_secretariado.fecha IS 'Primer día del mes al que corresponde el registro (YYYY-MM-DD).';
COMMENT ON COLUMN vwm_datos_delitos_robo_institucion_bancaria_secretariado.clave_entidad IS 'Clave de entidad federativa; siempre 14 (Jalisco).';
COMMENT ON COLUMN vwm_datos_delitos_robo_institucion_bancaria_secretariado.clave_municipio IS 'Clave geoestadística del municipio (5 dígitos, EEMMM).';
COMMENT ON COLUMN vwm_datos_delitos_robo_institucion_bancaria_secretariado.bien_juridico IS 'Bien jurídico afectado según catálogo SSPC.';
COMMENT ON COLUMN vwm_datos_delitos_robo_institucion_bancaria_secretariado.delito IS 'Nombre del delito.';
COMMENT ON COLUMN vwm_datos_delitos_robo_institucion_bancaria_secretariado.con_arma_de_fuego IS 'Carpetas de investigación donde la modalidad incluye arma de fuego.';
COMMENT ON COLUMN vwm_datos_delitos_robo_institucion_bancaria_secretariado.con_arma_blanca IS 'Carpetas de investigación donde la modalidad incluye arma blanca.';
COMMENT ON COLUMN vwm_datos_delitos_robo_institucion_bancaria_secretariado.con_otro_elemento IS 'Carpetas de investigación donde la modalidad incluye otro elemento.';
COMMENT ON COLUMN vwm_datos_delitos_robo_institucion_bancaria_secretariado.no_especificado IS 'Carpetas de investigación sin especificar el elemento utilizado.';
COMMENT ON COLUMN vwm_datos_delitos_robo_institucion_bancaria_secretariado.carpetas_investigacion IS 'Total de carpetas de investigación iniciadas en el mes.';
COMMENT ON COLUMN vwm_datos_delitos_robo_institucion_bancaria_secretariado.tasa_carpetas_investigacion IS 'Tasa por 100,000 habitantes (CONAPO pob_mit_mun). NULL si sin dato poblacional.';

-- =============================================================================
-- vwm_feminicidios  (V7 — especial desarrollo social)
-- =============================================================================

COMMENT ON MATERIALIZED VIEW vwm_feminicidios IS
    'Feminicidios del Secretariado reubicados en desarrollo social por su uso como '
    'indicador de igualdad de género. Conserva nivel_jerarquico y modalidad para '
    'permitir desagregación completa (total + modalidad por arma). '
    'Fuente: vw_gold_delitos_fuero_comun, delito = ''Feminicidio'', Jalisco.';
COMMENT ON COLUMN vwm_feminicidios.fid IS 'Identificador de fila incremental.';
COMMENT ON COLUMN vwm_feminicidios.geom_iieg IS 'Geometría MultiPolygon del municipio según delimitación IIEG (SRID 6368).';
COMMENT ON COLUMN vwm_feminicidios.geom_inegi IS 'Geometría MultiPolygon del municipio según delimitación INEGI (SRID 6368).';
COMMENT ON COLUMN vwm_feminicidios.nombre IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN vwm_feminicidios.fecha IS 'Primer día del mes al que corresponde el registro (YYYY-MM-DD).';
COMMENT ON COLUMN vwm_feminicidios.clave_entidad IS 'Clave de entidad federativa; siempre 14 (Jalisco).';
COMMENT ON COLUMN vwm_feminicidios.clave_municipio IS 'Clave geoestadística del municipio (5 dígitos, EEMMM).';
COMMENT ON COLUMN vwm_feminicidios.nivel_jerarquico IS 'Nivel de agregación: delito (total mensual) | modalidad (por tipo de arma).';
COMMENT ON COLUMN vwm_feminicidios.modalidad IS 'Modalidad del feminicidio (tipo de arma); NULL cuando nivel_jerarquico = delito.';
COMMENT ON COLUMN vwm_feminicidios.carpetas_investigacion IS 'Número de carpetas de investigación iniciadas en el mes.';
COMMENT ON COLUMN vwm_feminicidios.tasa_carpetas_investigacion IS 'Tasa por 100,000 habitantes (CONAPO pob_mit_mun). NULL si sin dato poblacional.';
