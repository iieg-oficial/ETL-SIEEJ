<div align="center">

# 🆕 Iniciar un Nuevo Flujo ETL — ETL SIEEJ

<img src="https://img.shields.io/badge/Python_3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
<img src="https://img.shields.io/badge/Apache_Airflow-017CEE?style=for-the-badge&logo=Apache%20Airflow&logoColor=white" alt="Airflow"/>
<img src="https://img.shields.io/badge/just-1D1D1D?style=for-the-badge&logoColor=white" alt="just"/>

---

### De fuente de datos a pipeline productivo, paso a paso

</div>

---

## Índice

1. [Visión General](#visión-general)
2. [Crear el Issue](#1-crear-el-issue)
3. [Implementar los Stages](#2-implementar-los-stages)
4. [Crear las Migraciones](#3-crear-las-migraciones)
5. [Crear el DAG de Airflow](#4-crear-el-dag-de-airflow)
6. [Probar localmente](#5-probar-localmente)
7. [Probar en Airflow](#6-probar-en-airflow)
8. [Comandos `just`](#comandos-just)

---

## Visión General

Un pipeline vive en tres lugares:

| Componente | Ubicación | Qué contiene |
|:----------:|:----------|:-------------|
| Lógica ETL | `core/pipelines/<nombre>/` | `config.py`, `consts.py`, `schemas.py`, `stages/` (extract, transform, load) |
| Migraciones | `migrations/<nombre>/` | `flyway.conf.example`, `sql/V*.sql` |
| DAG | `dags/etl_<nombre>.py` | DAGs de bootstrap y update para Airflow |

### El patrón Stage

Cada etapa hereda de `Stage` e implementa tres métodos:

| Método | Qué hace |
|:------:|:---------|
| `source()` | Define las entradas / abre conexiones |
| `action()` | Lógica principal (descarga, transforma o carga) |
| `finalization()` | Cierre de recursos, inventario de salida |

El `Pipeline` los encadena en orden y pasa el contexto entre etapas:

```python
Pipeline(
    name="mi_pipeline",
    stages=[MiExtractor(mode="bootstrap"), MiTransformer(mode="bootstrap"), MiLoader(mode="bootstrap")],
).run(mode="bootstrap")
```

---

## 1. Crear el Issue

Antes de escribir código, crea un issue con label `new-pipeline` que incluya:

- Fuente de datos (URL)
- Descripción de los datos
- Tablas que se crearán
- Criterios de aceptación (bootstrap ✓, update ✓, migraciones reproducibles ✓)

---

## 2. Implementar los Stages

```
core/pipelines/mi_pipeline/
├── __init__.py
├── config.py          ← hereda BaseConfig, apunta al .env del pipeline
├── consts.py          ← PIPELINE_NAME, SOURCE_URL, EXPECTED_COLUMNS
├── schemas.py         ← modelos SQLAlchemy (tablas)
└── stages/
    ├── __init__.py
    ├── extract.py     ← descarga, descomprime, genera inventario
    ├── transform.py   ← lee inventario, limpia con utils/, escribe parquet
    └── load.py        ← lee parquet, bulk insert en BD, cierra conexión
```

- **`extract.py`**:  descarga los datos de la fuente y guarda en `data/extract/<pipeline>/` en caso de ser necesario.
- **`transform.py`**:  lee el inventario de extract, aplica `core/utils/` (`normalize_headers`, `list_values_to_null`, etc.).
- **`load.py`**:  abre sesión con `Database` e  inserta los datos con las operaciones que se encuentranm en [bulk_ops]("core/utils/bulk_ops.py")  y cierra la conexión.

> 💡 Toma los pipelines existentes como referencia antes de empezar.

---

## 3. Crear las Migraciones

```bash
mkdir -p migrations/mi_pipeline/sql
cp migrations/censos_economicos/flyway.conf.example migrations/mi_pipeline/flyway.conf.example
touch migrations/mi_pipeline/sql/V1__tablas_iniciales.sql
```

Escribe el SQL idempotente (`IF NOT EXISTS`) para que `flyway-reset` sea seguro:

```sql
CREATE TABLE IF NOT EXISTS public.mi_pipeline_datos (
    id         SERIAL PRIMARY KEY,
    anio       INTEGER NOT NULL,
    municipio  VARCHAR(100),
    valor      NUMERIC
);

CREATE INDEX IF NOT EXISTS idx_mi_pipeline_anio ON public.mi_pipeline_datos (anio);
```

Consulta la [Guía de Flyway](flyway.md) para convenciones de nombres y comandos.

---

## 4. Crear el DAG de Airflow

Crea `dags/etl_mi_pipeline.py` con dos DAGs: uno con `schedule=None` para bootstrap y otro con el cron de update. Incluye `if __name__ == "__main__"` para poder ejecutarlo directamente como script.

Toma como referencia los DAGs existentes en `dags/`.

---

## 5. Probar localmente

```bash

# 1. Levantar base de datos de desarrollo
just build-dev user=sieej_user pass=mi_pass db=mi_pipeline

# 2. Crear migración de la base de datos de cvegeo y hacer la migración:
just create-cvegeo-db user=sieej_user && just flyway-migrate cvegeo

# 3. Configurar Flyway
just flyway-config mi_pipeline
#4. aplicar migraciones
just flyway-migrate mi_pipeline

# 5. Configurar variables de entorno del pipeline
cp core/pipelines/mi_pipeline/.env.example core/pipelines/mi_pipeline/.env
# → Editar .env con las credenciales
# 6. Ejecutar
python dags/etl_mi_pipeline.py
```

---

## 6. Probar en Airflow

```bash
just up
```

Abre `http://localhost:8080` y busca `etl_mi_pipeline_bootstrap`. Si no aparece:

```bash
just logs airflow-dag-processor   # errores de importación
```

> ⚠️ En Docker, cambia `DB_HOST=localhost` por `DB_HOST=host.docker.internal` en el `.env` del pipeline.

### Checklist antes del PR

```
- [ ] Pipeline corre en modo bootstrap localmente
- [ ] Pipeline corre en modo update localmente
- [ ] just flyway-reset mi_pipeline pasa sin errores
- [ ] DAG aparece en Airflow sin errores de importación
- [ ] DAG corre exitosamente en Airflow
- [ ] No hay .env ni flyway.conf en el PR
- [ ] .env.example y flyway.conf.example están commiteados
```

---

## Comandos `just`

Ejecuta `just` sin argumentos para ver todos los comandos disponibles.

### Docker

| Comando | Descripción |
|:--------|:------------|
| `just up` | Construye la imagen y levanta todos los servicios |
| `just down` | Detiene los servicios |
| `just down-volumes` | Detiene y elimina volúmenes ⚠️ |
| `just rebuild <servicio>` | Reconstruye un servicio específico |
| `just logs [servicio]` | Logs en tiempo real (todos o uno específico) |
| `just ps` | Estado de los contenedores |
| `just restart <servicio>` | Reinicia un servicio |

### Airflow

| Comando | Descripción |
|:--------|:------------|
| `just airflow-init` | Inicializa Airflow (solo la primera vez) |

### Desarrollo local

| Comando | Descripción |
|:--------|:------------|
| `just build-dev [user] [pass] [db] [port]` | Levanta un contenedor PostGIS para desarrollo |
| `just stop-dev` | Detiene y elimina el contenedor `postgres-dev` |
| `just create-cvegeo-db` | Crea la base de datos `cvegeo` en el contenedor de dev |

### Flyway

| Comando | Descripción |
|:--------|:------------|
| `just flyway-config <pipeline>` | Copia `flyway.conf.example` → `flyway.conf` |
| `just flyway-migrate <pipeline>` | Aplica las migraciones pendientes |
| `just flyway-info <pipeline>` | Estado de las migraciones |
| `just flyway-validate <pipeline>` | Valida integridad de los scripts |
| `just flyway-clean <pipeline>` | Elimina todos los objetos del schema ⚠️ |
| `just flyway-reset <pipeline>` | `clean` + `migrate` (reset completo) ⚠️ |

---

<div align="center">

<sub>Guía de nuevo flujo — ETL SIEEJ · IIEG Jalisco</sub>

</div>
