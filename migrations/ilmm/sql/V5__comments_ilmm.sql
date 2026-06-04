-- ---------------------------------------------------------------------------
-- Comentarios para cat_ilmm_estimador
-- Catálogo de tipos de estimador utilizados en la ENOE/ILMM.
-- id = 1: estimador puntual (valor de la proporción).
-- id = 2: error estándar (para calcular intervalos de confianza).
-- ---------------------------------------------------------------------------
COMMENT ON TABLE cat_ilmm_estimador IS 'Catálogo de tipos de estimador estadístico de la ILMM. El id 1 representa el estimador puntual (proporción) y el id 2 representa el error estándar asociado, utilizado para construir intervalos de confianza.';
COMMENT ON COLUMN cat_ilmm_estimador.id IS 'Identificador del tipo de estimador. Valores válidos: 1 (estimador puntual) y 2 (error estándar).';
COMMENT ON COLUMN cat_ilmm_estimador.descripcion IS 'Nombre descriptivo del estimador (ej: Estimador puntual, Error estándar).';

-- ---------------------------------------------------------------------------
-- Comentarios para stg_ilmm
-- Tabla de staging con indicadores de mercado laboral municipal (ILMM).
-- Fuente: Encuesta Nacional de Ocupación y Empleo (ENOE), INEGI.
-- Una fila = municipio × fecha × estimador.
-- ---------------------------------------------------------------------------
COMMENT ON TABLE stg_ilmm IS 'Tabla de staging que contiene indicadores del mercado laboral municipal (ILMM). Cada registro representa un estimador puntual o error estándar para un municipio, fecha y tipo de indicador. Fuente: Encuesta Nacional de Ocupación y Empleo (ENOE), INEGI. Periodicidad: trimestral. Historico: 2017-2024.';
COMMENT ON COLUMN stg_ilmm.id IS 'Identificador único autogenerado para cada registro.';
COMMENT ON COLUMN stg_ilmm.clave_municipio IS 'Clave INEGI de 5 dígitos que identifica al municipio (cve_ent + cve_mun). Ejemplo: ''01001'' para Acapulco, Gro. Referencia implícita a cvegeo_municipalities.cvegeo.';
COMMENT ON COLUMN stg_ilmm.fecha IS 'Fecha de referencia del trimestre (formato YYYY-MM-DD, primer día del trimestre). Ejemplo: 2024-01-01 para el primer trimestre de 2024.';
COMMENT ON COLUMN stg_ilmm.estimador_id IS 'Tipo de estimador (FK a cat_ilmm_estimador). 1 = estimador puntual, 2 = error estándar.';
COMMENT ON COLUMN stg_ilmm.pob_econo_activa IS 'Población económicamente activa (PEA). Número de personas de 15 años o más que trabajaron o buscaron trabajo durante la semana de referencia.';
COMMENT ON COLUMN stg_ilmm.ocupados IS 'Número de personas ocupadas (empleo formal o informal). Utilizar estimador_id=1 para el valor y estimador_id=2 para el error estándar.';
COMMENT ON COLUMN stg_ilmm.informales IS 'Número de personas en el sector informal (empleo informal no agrícola). Utilizar estimador_id=1 para el valor y estimador_id=2 para el error estándar.';

-- ---------------------------------------------------------------------------
-- Comentarios para vw_ocupacion_informal
-- Vista materializada: porcentaje de ocupación en el sector informal.
-- indicador = 'porcentaje_ocupacion_informal'
-- valor = informales (estimador_id=1)
-- error_estandar = informales (estimador_id=2)
-- ---------------------------------------------------------------------------
COMMENT ON MATERIALIZED VIEW vw_ocupacion_informal IS 'Vista materializada que presenta el porcentaje de ocupación en el sector informal por municipio y fecha. El indicador ''porcentaje_ocupacion_informal'' se calcula como (informales / pob_econo_activa * 100) cuando se combina con la vista vw_ilmm.';

COMMENT ON COLUMN vw_ocupacion_informal.id IS 'Identificador único que corresponde al registro en stg_ilmm.';
COMMENT ON COLUMN vw_ocupacion_informal.fecha IS 'Fecha de referencia del trimestre (primer día del trimestre).';
COMMENT ON COLUMN vw_ocupacion_informal.clave_municipio IS 'Clave INEGI de 5 dígitos del municipio.';
COMMENT ON COLUMN vw_ocupacion_informal.cvegeo IS 'Código geográfico de 5 dígitos con ceros izquierdo (cve_ent + cve_mun).';
COMMENT ON COLUMN vw_ocupacion_informal.nom_municipio IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN vw_ocupacion_informal.nom_ent IS 'Nombre de la entidad federativa.';
COMMENT ON COLUMN vw_ocupacion_informal.indicador IS 'Nombre del indicador: ''porcentaje_ocupacion_informal''.';
COMMENT ON COLUMN vw_ocupacion_informal.valor IS 'Porcentaje de ocupación en el sector informal (dato puntual, estimador_id=1).';
COMMENT ON COLUMN vw_ocupacion_informal.error_estandar IS 'Error estándar del porcentaje de ocupación informal (estimador_id=2). Usar para construir intervalos de confianza.';

-- ---------------------------------------------------------------------------
-- Comentarios para vw_tasa_desocupacion
-- Vista materializada: tasa de desocupación.
-- indicador = 'tasa_desocupacion'
-- valor = 100 - ocupados (estimador_id=1)
-- error_estandar = ocupados (estimador_id=2)
-- ---------------------------------------------------------------------------
COMMENT ON MATERIALIZED VIEW vw_tasa_desocupacion IS 'Vista materializada que presenta la tasa de desocupación por municipio y fecha. El indicador ''tasa_desocupacion'' se calcula como (desocupados / pob_econo_activa * 100).';

COMMENT ON COLUMN vw_tasa_desocupacion.id IS 'Identificador único que corresponde al registro en stg_ilmm.';
COMMENT ON COLUMN vw_tasa_desocupacion.fecha IS 'Fecha de referencia del trimestre (primer día del trimestre).';
COMMENT ON COLUMN vw_tasa_desocupacion.clave_municipio IS 'Clave INEGI de 5 dígitos del municipio.';
COMMENT ON COLUMN vw_tasa_desocupacion.cvegeo IS 'Código geográfico de 5 dígitos con ceros izquierdo.';
COMMENT ON COLUMN vw_tasa_desocupacion.nom_municipio IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN vw_tasa_desocupacion.nom_ent IS 'Nombre de la entidad federativa.';
COMMENT ON COLUMN vw_tasa_desocupacion.indicador IS 'Nombre del indicador: ''tasa_desocupacion''.';
COMMENT ON COLUMN vw_tasa_desocupacion.valor IS 'Tasa de desocupación en porcentaje (dato puntual, estimador_id=1).';
COMMENT ON COLUMN vw_tasa_desocupacion.error_estandar IS 'Error estándar de la tasa de desocupación (estimador_id=2). Usar para construir intervalos de confianza.';

-- ---------------------------------------------------------------------------
-- Comentarios para vw_ilmm
-- Vista regular: todos los registros de stg_ilmm con descripción de estimador
-- y nombre de municipio.
-- ---------------------------------------------------------------------------
COMMENT ON VIEW vw_ilmm IS 'Vista de integración que desnormaliza stg_ilmm con descripción del estimador y nombre del municipio. Une stg_ilmm con cat_ilmm_estimador y cvegeo_municipalities para agregar nombres descriptivos.';

COMMENT ON COLUMN vw_ilmm.id IS 'Identificador único que corresponde al registro en stg_ilmm.';
COMMENT ON COLUMN vw_ilmm.fecha IS 'Fecha de referencia del trimestre (primer día del trimestre).';
COMMENT ON COLUMN vw_ilmm.clave_municipio IS 'Clave INEGI de 5 dígitos del municipio.';
COMMENT ON COLUMN vw_ilmm.municipio IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN vw_ilmm.nom_ent IS 'Nombre de la entidad federativa.';
COMMENT ON COLUMN vw_ilmm.estimador_id IS 'Tipo de estimador (1 = puntual, 2 = error estándar).';
COMMENT ON COLUMN vw_ilmm.estimador IS 'Descripción textual del tipo de estimador.';
COMMENT ON COLUMN vw_ilmm.pob_econo_activa IS 'Población económicamente activa (PEA).';
COMMENT ON COLUMN vw_ilmm.ocupados IS 'Número de personas ocupadas.';
COMMENT ON COLUMN vw_ilmm.informales IS 'Número de personas en el sector informal.';