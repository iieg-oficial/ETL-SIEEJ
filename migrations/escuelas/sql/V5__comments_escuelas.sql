COMMENT ON TABLE cat_turnos IS 'Catálogo de turnos escolares del sistema educativo mexicano. Define los horarios de funcionamiento de los centros de trabajo (ej: Matutino, Vespertino, Nocturno, discontinuous, etc.). Utilizado para clasificar las escuelas por su horario de operación.';
COMMENT ON COLUMN cat_turnos.id IS 'Identificador único del turno escolar. Valor numérico que corresponde al código oficial del turno.';
COMMENT ON COLUMN cat_turnos.nombre_turno IS 'Nombre descriptivo del turno escolar (ej: Matutino, Vespertino, Nocturno).';

COMMENT ON TABLE cat_sostenimientos IS 'Catálogo de tipos de sostenimiento educativo. Clasifica las escuelas según la fuente de financiamiento público o privado. Es la dimensión principal para analizar la cobertura educativa por tipo de servicio.';
COMMENT ON COLUMN cat_sostenimientos.id IS 'Identificador único del tipo de sostenimiento.';
COMMENT ON COLUMN cat_sostenimientos.sostenimiento IS 'Nombre del sostenimiento (ej: Público, Privado).';

COMMENT ON TABLE cat_codigos_sostenimiento IS 'Catálogo de códigos que vinculan sostenimiento con nivel educativo. Cada código representa una combinación única de sostenimiento y nivel, utilizada en el DIRECTORIO de escuelas para clasificar el tipo de servicio.';
COMMENT ON COLUMN cat_codigos_sostenimiento.id IS 'Código numérico que identifica la combinación sostenimiento-nivel.';
COMMENT ON COLUMN cat_codigos_sostenimiento.sostenimiento_id IS 'Referencia al tipo de sostenimiento (FK a cat_sostenimientos).';

COMMENT ON TABLE cat_niveles IS 'Catálogo de niveles educativos del sistema mexicano (Preescolar, Primaria, Secundaria, Bachillerato, Profesional Técnico). Es la dimensión principal para analizar la estructura educativa por nivel.';
COMMENT ON COLUMN cat_niveles.id IS 'Identificador único del nivel educativo.';
COMMENT ON COLUMN cat_niveles.nivel IS 'Nombre del nivel educativo (ej: Preescolar, Primaria, Secundaria).';

COMMENT ON TABLE cat_programas IS 'Catálogo de programas educativos especiales o diferenciados. Incluye programas como CONAFE, Educación Indígena, Educación Militar, etc. Permite clasificar escuelas por su programa especial.';
COMMENT ON COLUMN cat_programas.id IS 'Identificador único del programa educativo.';
COMMENT ON COLUMN cat_programas.programa IS 'Nombre del programa educativo especial.';

COMMENT ON TABLE cat_regiones IS 'Catálogo de regiones educativas del estado de Jalisco. El estado se divide en regiones para administración educativa. Cada región agrupa varios municipios y tiene un número de región asignado por la autoridad educativa.';
COMMENT ON COLUMN cat_regiones.id IS 'Número de región educativa asignado por la SEP Jalisco.';
COMMENT ON COLUMN cat_regiones.nombre_region IS 'Nombre de la región educativa (ej: Región 02 Altos Norte).';

COMMENT ON TABLE cat_medios IS 'Catálogo de medios de difusión o comunicación educativa. Clasifica las escuelas por el medio través del cual se imparte la educación (ej: Presencial, a distancia, radio, televisión).';
COMMENT ON COLUMN cat_medios.id IS 'Identificador único del medio de difusión.';
COMMENT ON COLUMN cat_medios.medio IS 'Nombre del medio de difusión educativa.';

COMMENT ON TABLE cat_niveles_programa IS 'Catálogo combinado de nivel y programa educativo. Se usa en las estadísticas de la SECRETARÍA DE EDUCACIÓN para agregar datos por la combinación única de nivel y programa, creando categorías como "Primaria CONAFE" o "Secundaria General".';
COMMENT ON COLUMN cat_niveles_programa.id IS 'Identificador único de la combinación nivel-programa.';
COMMENT ON COLUMN cat_niveles_programa.nivel_programa IS 'Nombre combinado de nivel y programa (ej: Primaria General, Secundaria Técnica).';

COMMENT ON TABLE stg_directorio_escuelas IS 'Tabla de staging que contiene el DIRECTORIO de Centros de Trabajo (CT) del estado de Jalisco. Cada registro representa una escuela única identificada por su clave CT, con información de ubicación geográfica, datos del director, contacto y estadísticas de matrícula. Es la tabla principal del pipeline de escuelas. Fuente: Directorio de la Secretaría de Educación Jalisco.';
COMMENT ON COLUMN stg_directorio_escuelas.id IS 'Identificador único autogenerado para cada registro en la tabla de staging.';
COMMENT ON COLUMN stg_directorio_escuelas.anio IS 'Año escolar al que pertenecen los datos del directorio (ej: 2026). El directorio se actualiza anualmente.';
COMMENT ON COLUMN stg_directorio_escuelas.entidad_id IS 'Clave numérica de la entidad federativa (cve_ent). Jalisco tiene el código 14. Todos los registros en esta tabla pertenecen a Jalisco.';
COMMENT ON COLUMN stg_directorio_escuelas.clave_ct IS 'Clave del Centro de Trabajo (CT). Código de 10 caracteres que identifica de forma única a cada escuela en el sistema educativo nacional. Formato: estado(2) + municipio(3) + núcleo(3) + tipo(2).';
COMMENT ON COLUMN stg_directorio_escuelas.turno_id IS 'Referencia al turno escolar (FK a cat_turnos). Indica si la escuela es matutina, vespertina, nocturna, etc.';
COMMENT ON COLUMN stg_directorio_escuelas.nombre_ct IS 'Nombre oficial del Centro de Trabajo asignado por la autoridad educativa.';
COMMENT ON COLUMN stg_directorio_escuelas.domicilio IS 'Dirección completa de la ubicación de la escuela (calle, número, área).';
COMMENT ON COLUMN stg_directorio_escuelas.localidad_id IS 'Clave INEGI de la localidad donde se ubica la escuela.';
COMMENT ON COLUMN stg_directorio_escuelas.nombre_localidad IS 'Nombre de la localidad (ciudad, pueblo o comunidad) donde está la escuela.';
COMMENT ON COLUMN stg_directorio_escuelas.colonia_id IS 'Clave INEGI de la colonia o asentamiento urbano.';
COMMENT ON COLUMN stg_directorio_escuelas.nombre_colonia IS 'Nombre de la colonia o asentamiento urbano.';
COMMENT ON COLUMN stg_directorio_escuelas.municipio_id IS 'Clave numérica del municipio (cve_mun) según INEGI.';
COMMENT ON COLUMN stg_directorio_escuelas.nombre_municipio IS 'Nombre oficial del municipio.';
COMMENT ON COLUMN stg_directorio_escuelas.medio_id IS 'Referencia al medio de difusión educativa (FK a cat_medios).';
COMMENT ON COLUMN stg_directorio_escuelas.director IS 'Nombre completo del director o responsable de la escuela.';
COMMENT ON COLUMN stg_directorio_escuelas.codigo_postal IS 'Código postal de la dirección de la escuela.';
COMMENT ON COLUMN stg_directorio_escuelas.telefono IS 'Número de teléfono de contacto de la escuela.';
COMMENT ON COLUMN stg_directorio_escuelas.zona_escolar IS 'Número de zona escolar a la que pertenece la escuela. Las zonas agrupan escuelas para administración.';
COMMENT ON COLUMN stg_directorio_escuelas.sector IS 'Número de sector educativo. Los sectores agrupan varias zonas escolares.';
COMMENT ON COLUMN stg_directorio_escuelas.codigo_sostenimiento_id IS 'Referencia al código de sostenimiento-nivel (FK a cat_codigos_sostenimiento).';
COMMENT ON COLUMN stg_directorio_escuelas.nivel_id IS 'Referencia al nivel educativo (FK a cat_niveles).';
COMMENT ON COLUMN stg_directorio_escuelas.programa_id IS 'Referencia al programa educativo especial (FK a cat_programas).';
COMMENT ON COLUMN stg_directorio_escuelas.region_id IS 'Referencia a la región educativa de Jalisco (FK a cat_regiones).';
COMMENT ON COLUMN stg_directorio_escuelas.longitud IS 'Coordenada de longitud geográfica (longitud) de la ubicación de la escuela en grados decimales.';
COMMENT ON COLUMN stg_directorio_escuelas.latitud IS 'Coordenada de latitud geográfica (latitud) de la ubicación de la escuela en grados decimales.';
COMMENT ON COLUMN stg_directorio_escuelas.escuelas IS 'Número de planteles que comparten esta Clave CT. Generalmente es 1, pero puede ser más si hay varios turnos o niveles en el mismo edificio.';
COMMENT ON COLUMN stg_directorio_escuelas.hombres_matriculados IS 'Cantidad de alumnos hombres actualmente matriculados en la escuela.';
COMMENT ON COLUMN stg_directorio_escuelas.mujeres_matriculadas IS 'Cantidad de alumnas mujeres actualmente matriculadas en la escuela.';
COMMENT ON COLUMN stg_directorio_escuelas.total_matriculados IS 'Total de alumnos matriculados (hombres + mujeres).';
COMMENT ON COLUMN stg_directorio_escuelas.total_docentes_directivo IS 'Total de docentes y personal directivo (directores, subdirectores) en la escuela.';
COMMENT ON COLUMN stg_directorio_escuelas.fecha_actualizacion IS 'Fecha en que la fuente de datos actualizó este registro por última vez.';

COMMENT ON TABLE stg_estadistica_escuelas IS 'Tabla de staging que contiene ESTADÍSTICAS educativas agregadas por año, nivel-programa y sostenimiento. Cada registro representa el total de escuelas, matrícula y docentes para una combinación única. Fuente: Estadísticas de la Secretaría de Educación Jalisco.';
COMMENT ON COLUMN stg_estadistica_escuelas.id IS 'Identificador único autogenerado para cada registro en la tabla de staging.';
COMMENT ON COLUMN stg_estadistica_escuelas.anio IS 'Año escolar de las estadísticas (ej: 2026).';
COMMENT ON COLUMN stg_estadistica_escuelas.nivel_programa_id IS 'Referencia a la combinación nivel-programa (FK a cat_niveles_programa).';
COMMENT ON COLUMN stg_estadistica_escuelas.sostenimiento_id IS 'Referencia al tipo de sostenimiento (FK a cat_sostenimientos).';
COMMENT ON COLUMN stg_estadistica_escuelas.escuelas IS 'Número total de escuelas que corresponden a esa combinación de nivel-programa y sostenimiento en el año.';
COMMENT ON COLUMN stg_estadistica_escuelas.matricula IS 'Total de alumnos matriculados en todas las escuelas de esa categoría.';
COMMENT ON COLUMN stg_estadistica_escuelas.docentes IS 'Número total de docentes en todas las escuelas de esa categoría.';
COMMENT ON COLUMN stg_estadistica_escuelas.fecha_actualizacion IS 'Fecha en que la fuente de datos actualizó este registro por última vez.';
