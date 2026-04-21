Mapea qué pipelines comparten catálogos por nombre de tabla.

## Pasos

1. Para cada pipeline en `core/pipelines/`, lee `schemas.py` y extrae todos los `__tablename__`.

2. Agrupa las tablas que aparecen en más de un pipeline (mismo nombre exacto).

3. Escribe el reporte en este formato:

```
CATÁLOGOS COMPARTIDOS

localidades
  → establecimientos_de_salud
  → fiscalia
  → centros_educativos

municipios
  → marginacion
  → intensidad_migratoria

entidades
  → censo_poblacion
  → marginacion
```

4. Al final, lista los pipelines que no comparten ningún catálogo con otros:

```
PIPELINES INDEPENDIENTES (sin catálogos compartidos)
  - {pipeline}
```

Solo reporta, no modifica nada.
