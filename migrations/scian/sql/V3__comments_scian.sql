-- =============================================================================
-- V3__comments_scian.sql  |  Pipeline: scian
-- COMMENT ON TABLE / VIEW y columnas para todos los objetos del pipeline.
-- =============================================================================

-- =============================================================================
-- TABLAS DE LA JERARQUÍA
-- =============================================================================

COMMENT ON TABLE sectores IS
    'Sectores del SCIAN México 2023: primer nivel del clasificador de actividades económicas del INEGI. '
    '20 categorías.';
COMMENT ON COLUMN sectores.id IS 'Identificador único de la fila (clave primaria).';
COMMENT ON COLUMN sectores.codigo IS
    'Clave del sector, de dos dígitos. Dos sectores agrupan un rango de claves: 31-33 (industrias '
    'manufactureras) y 48-49 (transportes, correos y almacenamiento), por lo que la clave no siempre '
    'es prefijo de la de sus subsectores.';
COMMENT ON COLUMN sectores.descripcion IS 'Nombre del sector.';
COMMENT ON COLUMN sectores.comparable_trinacional IS
    'La categoría es comparable con el NAICS de Estados Unidos y Canadá. En el archivo del INEGI se '
    'marca con una T como exponente al final de la descripción.';

COMMENT ON TABLE subsectores IS
    'Subsectores del SCIAN México 2023: segundo nivel del clasificador. 94 categorías.';
COMMENT ON COLUMN subsectores.id IS 'Identificador único de la fila (clave primaria).';
COMMENT ON COLUMN subsectores.codigo IS 'Clave del subsector, de tres dígitos.';
COMMENT ON COLUMN subsectores.descripcion IS 'Nombre del subsector.';
COMMENT ON COLUMN subsectores.comparable_trinacional IS
    'La categoría es comparable con el NAICS de Estados Unidos y Canadá.';
COMMENT ON COLUMN subsectores.sector_id IS 'Referencia al sector al que pertenece el subsector.';

COMMENT ON TABLE ramas IS
    'Ramas del SCIAN México 2023: tercer nivel del clasificador. 305 categorías.';
COMMENT ON COLUMN ramas.id IS 'Identificador único de la fila (clave primaria).';
COMMENT ON COLUMN ramas.codigo IS 'Clave de la rama, de cuatro dígitos.';
COMMENT ON COLUMN ramas.descripcion IS 'Nombre de la rama.';
COMMENT ON COLUMN ramas.comparable_trinacional IS
    'La categoría es comparable con el NAICS de Estados Unidos y Canadá.';
COMMENT ON COLUMN ramas.subsector_id IS 'Referencia al subsector al que pertenece la rama.';

COMMENT ON TABLE subramas IS
    'Subramas del SCIAN México 2023: cuarto nivel del clasificador. 610 categorías.';
COMMENT ON COLUMN subramas.id IS 'Identificador único de la fila (clave primaria).';
COMMENT ON COLUMN subramas.codigo IS 'Clave de la subrama, de cinco dígitos.';
COMMENT ON COLUMN subramas.descripcion IS 'Nombre de la subrama.';
COMMENT ON COLUMN subramas.comparable_trinacional IS
    'La categoría es comparable con el NAICS de Estados Unidos y Canadá.';
COMMENT ON COLUMN subramas.rama_id IS 'Referencia a la rama a la que pertenece la subrama.';

COMMENT ON TABLE clases IS
    'Clases de actividad del SCIAN México 2023: quinto y último nivel del clasificador, el más '
    'desagregado. 1,086 categorías. Es el nivel con el que se codifican las unidades económicas en '
    'fuentes como el DENUE y los Censos Económicos.';
COMMENT ON COLUMN clases.id IS 'Identificador único de la fila (clave primaria).';
COMMENT ON COLUMN clases.codigo IS 'Clave de la clase de actividad, de seis dígitos.';
COMMENT ON COLUMN clases.descripcion IS 'Nombre de la clase de actividad.';
COMMENT ON COLUMN clases.subrama_id IS 'Referencia a la subrama a la que pertenece la clase.';

-- =============================================================================
-- VISTAS
-- =============================================================================

COMMENT ON VIEW view_scian_estructura IS
    'Jerarquía completa del SCIAN México 2023 aplanada: un renglón por clase de actividad con la '
    'clave y el nombre de sus cinco niveles. 1,086 renglones.';
COMMENT ON COLUMN view_scian_estructura.codigo_sector IS 'Clave del sector (puede ser un rango: 31-33, 48-49).';
COMMENT ON COLUMN view_scian_estructura.sector IS 'Nombre del sector.';
COMMENT ON COLUMN view_scian_estructura.codigo_subsector IS 'Clave del subsector, de tres dígitos.';
COMMENT ON COLUMN view_scian_estructura.subsector IS 'Nombre del subsector.';
COMMENT ON COLUMN view_scian_estructura.codigo_rama IS 'Clave de la rama, de cuatro dígitos.';
COMMENT ON COLUMN view_scian_estructura.rama IS 'Nombre de la rama.';
COMMENT ON COLUMN view_scian_estructura.codigo_subrama IS 'Clave de la subrama, de cinco dígitos.';
COMMENT ON COLUMN view_scian_estructura.subrama IS 'Nombre de la subrama.';
COMMENT ON COLUMN view_scian_estructura.codigo_clase IS 'Clave de la clase de actividad, de seis dígitos.';
COMMENT ON COLUMN view_scian_estructura.clase IS 'Nombre de la clase de actividad.';
