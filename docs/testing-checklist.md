# Testing Checklist. ETL-SIEEJ Production Pipelines

> **Fecha de generación**: 2026-05-21
> **Versión del sistema**: v1.1.0
> **Pipelines en producción**: 18

---

## Instrucciones de uso

1. Antes de cada despliegue o revisión, ejecuta los checks de las secciones en orden.

---

## Sección A. Checks comunes a todos los pipelines

### A1. Migraciones (Flyway)

- [ ] `just flyway-info {pipeline}` muestra todos los scripts como `Success`
- [ ] `V2__catalogs.sql` existe y crea tablas con prefijo `cat_`
- [ ] `V3__tables_{pipeline}.sql` crea tablas principales con prefijo `stg_`
- [ ] Columna `id SERIAL PRIMARY KEY` en todas las tablas

### A2. DAG (Airflow)

- [ ] El DAG bootstrap tiene `schedule=None` (disparo manual)
- [ ] El DAG update tiene el cron correcto (ver tabla por pipeline)
- [ ] `catchup=False` configurado en el DAG update
- [ ] Nombre del dag sigue el patrón `etl_{pipeline}_bootstrap` / `etl_{pipeline}_update`

### A3. Estructura de archivos

- [ ] `core/pipelines/{pipeline}/constants.py` existe (solo MAYÚSCULAS)
- [ ] `core/pipelines/{pipeline}/schemas.py` existe con modelos SQLAlchemy 2.x

### A4. Calidad de código

- [ ] Imports ordenados: stdlib → third-party → `core.*` (línea en blanco entre los grupos 1 y 2 con el 3)
- [ ] Sin URLs hardcodeadas en stages (deben estar en `constants.py` o `config.py`)
- [ ] Sin lógica duplicada de `core/utils/` (usar `normalize_col`, `list_values_to_null`, etc.)
- [ ] Schemas SQLAlchemy 2.0 (`Mapped`, `mapped_column`) — sin sintaxis 1.x

### A5. Extract stage

- [ ] Modo bootstrap descarga el dataset completo
- [ ] Modo update descarga solo datos incrementales/recientes
- [ ] Registros extraídos > 0 (o log explícito si la fuente está vacía)

### A6. Transform stage

- [ ] `NULL_VALUES` convertidos a `None` (incluyendo `"N/A"`, `"n/a"`, `"NA"`, `"-"`, `""`)
- [ ] Renombrado de columnas completo y correcto
- [ ] Columnas numéricas casteadas a `int`/`float` (sin dtype `object`)
- [ ] Duplicados removidos donde aplique
- [ ] Output guardado en `data/transform/{pipeline}/` como parquet o pickle
- [ ] Shape del DataFrame razonable (columnas y filas en rango esperado)

### A7. Load stage

- [ ] `sync_id_sequence()` llamado tras cargar catálogos con IDs fijos
- [ ] `insert_records()` o `upsert_records()` de `core.utils.bulk_ops` (sin `session.add()`)
- [ ] FK constraints satisfechos (sin IDs huérfanos)
- [ ] `cleanup_pipeline_data()` llamado al finalizar
- [ ] Sesión de base de datos cerrada correctamente
- [ ] Logs muestran conteo de registros por tabla

### A8. Calidad de datos (post-load)

- [ ] Conteos de registros razonables (se puede usar just summary)
- [ ] Fechas en rango plausible (sin fechas futuras inesperadas)
- [ ] Métricas numéricas no negativas (salvo que el dominio lo permita)
- [ ] Códigos geográficos (`municipio_id`, `estado_id`) resueltos a valores conocidos de `cvegeo`
- [ ] Encoding correcto: acentos y ñ preservados en campos de texto
- [ ] Columnas de timestamp (`fecha_actualizacion`, `updated_at`) tienen valores recientes

---


## Sección B. Checks de infraestructura compartida

- [ ] `pyproject.toml` y `requirements.txt` sincronizados

---

## Apéndice. Comandos de referencia rápida

```bash
# Levantar entorno
just up

# Migrar un pipeline
just flyway-migrate {pipeline}

# Resetear migraciones de un pipeline (destructivo, solo dev)
just flyway-reset {pipeline}

# Validar DAG sin errores de importación
python dags/etl_{pipeline}.py

# Verificar estado de migraciones
just flyway-info {pipeline}

```
