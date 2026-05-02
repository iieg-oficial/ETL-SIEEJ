Detecta elementos huérfanos o incompletos en el proyecto.

## Pasos

1. Lista todos los pipelines:
   ```bash
   ls core/pipelines/
   ```

2. Para cada pipeline verifica:

   **Pipelines sin DAG:**
   ```bash
   ls core/dags/
   ```
   Reporta pipelines que existen en `core/pipelines/` pero no tienen carpeta en `core/dags/`.

   **Pipelines sin migraciones:**
   ```bash
   ls migrations/
   ```
   Reporta pipelines sin carpeta en `migrations/`.

   **Tablas definidas en schemas.py sin vista en migraciones:**
   Lee cada `schemas.py` para obtener `__tablename__` y busca si aparece en `V4__views_*.sql`.

   **Archivos pickle huérfanos:**
   ```bash
   ls data/extract/ data/transform/ 2>/dev/null
   ```
   Reporta carpetas en `data/` que no correspondan a ningún pipeline activo.

   **Pipelines sin README:**
   Verifica `core/pipelines/{pipeline}/README.md`.

## Reporte

```
ELEMENTOS HUÉRFANOS / INCOMPLETOS

Pipelines sin DAG:
  - {pipeline}

Pipelines sin migraciones:
  - {pipeline}

Tablas sin vista:
  - {pipeline}: {tabla}

Pickles huérfanos en data/:
  - data/extract/{nombre}

Pipelines sin README:
  - {pipeline}
```

Solo reporta, no modifica nada.
