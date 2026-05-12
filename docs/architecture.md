# Arquitectura - Qué significa "hacer un buen trabajo"

## Principios Fundamentales

### 1. Separación estricta de capas ETL
Cada pipeline tiene tres módulos con responsabilidades exclusivas y no intercambiables:

- **Extract** — Solo descarga o lee datos de la fuente externa. No transforma nada.
- **Transform** — Solo limpia, normaliza y construye catálogos en memoria o en `data/transform/`. No hace I/O de red ni escribe a la base de datos.
- **Load** — Solo inserta o hace upsert a PostgreSQL usando `core.utils.bulk_ops`. No transforma datos.

Si una función de `load.py` está limpiando strings, o una de `extract.py` está construyendo un catálogo, el código está mal ubicado.

### 2. Cada pipeline es autónomo
Un pipeline no debe depender de la ejecución o el estado de otro pipeline. Las referencias cruzadas a tablas de otros pipelines se declaran como foreign tables en `V1__foreign_tables.sql`, no como dependencias de código Python.

### 3. Las operaciones de escritura siempre pasan por `bulk_ops`
Ningún código de pipeline inserta filas directamente con `session.add()` o `conn.execute(INSERT ...)`. Toda escritura usa `insert_records` o `upsert_records` de `core.utils.bulk_ops`. Esto garantiza consistencia en el manejo de errores, secuencias y rendimiento.

### 4. La normalización es centralizada
Toda limpieza de texto, fechas y valores nulos usa las utilidades de `core/utils/`. No se reimplementan estas funciones en los pipelines. Si una transformación recurrente no existe en `core/utils/`, se añade ahí y no se duplica en cada pipeline.

### 5. Las migraciones son la fuente de verdad del esquema
El esquema de la base de datos se define en `migrations/{pipeline}/sql/`. Los modelos SQLAlchemy en `schemas.py` deben reflejar exactamente ese esquema. Si hay discrepancia, las migraciones tienen precedencia.

### 6. Las constantes definen el contrato del dataset
`constants.py` de cada pipeline declara explícitamente qué columnas se renombran, qué valores son nulos, qué columnas se capitalizan y cómo se parsean fechas. Cambiar el comportamiento de una transformación significa cambiar `constants.py`, no hardcodear lógica condicional en `transform.py`.

## Flujo de Datos

```
Fuente externa (API / archivo / Google Drive)
        ↓
   extract.py  ──→  data/extract/{pipeline}/   (pkl / csv)
        ↓
  transform.py ──→  data/transform/{pipeline}/ (pkl / csv)
        ↓
    load.py    ──→  PostgreSQL / PostGIS
        ↓
cleanup_pipeline_data()  (borra data/extract/ y data/transform/)
```

El flujo es unidireccional. Los archivos en `data/` son temporales: existen solo entre stages y se eliminan al terminar el load. Si un pipeline no necesita persistir entre stages, puede operar completamente en memoria.

## Prácticas Prohibidas

### Prohibido ✗
- Usar `os.path.join` — siempre usar `pathlib.Path`
- Escribir comentarios en el código que expliquen *qué* hace el código
- Agregar emojis en logs o mensajes de error
- Usar el estilo SQLAlchemy 1.x (`Column`, `relationship` sin `Mapped`)
- Insertar filas directamente con `session.add()` o SQL crudo en los stages
- Mezclar responsabilidades entre `extract`, `transform` y `load`
- Reimplementar en un pipeline lógica que ya existe en `core/utils/`
- Leer o escribir archivos dentro de bucles de transformación
- Hardcodear strings de conexión o credenciales fuera de variables de entorno
- crear funciones helper dentro del flujo de ETL (Extract, transform, load).


### Permitido ✓
- Type hints completos en funciones públicas
- `Path` para todas las rutas de archivos
- Logging con mensajes cortos en inglés usando `core.utils.logger`
- Catálogos estáticos en `mappings.py` y dinámicos construidos en `transform._build_catalogs()`
- Uso de `data/` solo cuando la persistencia entre stages sea necesaria
- Pipelines con variantes `bootstrap` e `incremental` cuando la fuente lo requiera
- Atributos de tabla en forma plana (`attributes.py`) o carpeta (`attributes/`) según la cantidad de enums necesarios
- crear funciones helper dentro de helpers/.
