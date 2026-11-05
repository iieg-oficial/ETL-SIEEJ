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
3. [Generar la estructura](#2-generar-la-estructura)
4. [Implementar los Stages](#3-implementar-los-stages)
5. [Crear las Migraciones](#4-crear-las-migraciones)
6. [Completar el DAG de Airflow](#5-completar-el-dag-de-airflow)
7. [Probar localmente](#6-probar-localmente)
8. [Probar en Airflow](#7-probar-en-airflow)
9. [Comandos `just`](#comandos-just)

---

## Visión General

Un pipeline vive en tres lugares:

| Componente | Ubicación | Qué contiene |
|:----------:|:----------|:-------------|
| Lógica ETL | `core/pipelines/<nombre>/` | `config.py`, `schemas.py`, `constants/`, `attributes/`, `mappings/`, `queries/`, `assets/`, `stages/` (extract, transform, load), `README.md` |
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

## 2. Generar la estructura

Para crear la estructura general del pipeline es necesario ejecutar lo siguiente con el entorno virtual activo:

```bash
just new-pipeline mi_pipeline
just new-pipeline mi_pipeline "Nombre del responsable"   # opcional: owner del DAG, por defecto IIEG
```

El comando muestra lo que creó y falla sin modificar nada si el nombre es inválido o si el pipeline ya existe. El detalle está en [`templates/pipeline/README.md`](../templates/pipeline/README.md).

---

## 3. Implementar los Stages

```
core/pipelines/mi_pipeline/
├── config.py          ← hereda BaseConfig, apunta al .env del pipeline
├── schemas.py         ← modelos SQLAlchemy (tablas)
├── constants/         ← PIPELINE_NAME, URLs y columnas, por submódulo
├── attributes/        ← enums con los nombres de las tablas
├── mappings/          ← catálogos estáticos, por submódulo
├── queries/           ← consultas y vistas SQL
├── assets/            ← ERD y archivos estáticos
├── README.md          ← parte de docs/readme-pipeline.md
├── .env.example
├── .env               ← no se versiona
└── stages/
    ├── __init__.py
    ├── extract.py     ← descarga, descomprime, genera inventario
    ├── transform.py   ← lee inventario, limpia con utils/, escribe parquet
    └── load.py        ← lee parquet, bulk insert en BD, cierra conexión
```

- **`extract.py`**:  descarga los datos de la fuente y guarda en `data/extract/<pipeline>/` en caso de ser necesario.
- **`transform.py`**:  lee el inventario de extract, aplica `core/utils/` (`lowercase_headers`, `list_values_to_null`, etc.).
- **`load.py`**:  abre sesión con `Database` e  inserta los datos con las operaciones que se encuentranm en [bulk_ops]("core/utils/bulk_ops.py")  y cierra la conexión.

> 💡 Toma los pipelines existentes como referencia antes de empezar.
> 📐 Para nomenclatura de tablas/vistas, tipos de campos comunes y el uso estándar de `core/utils/`, consulta [`docs/estandares_datos.md`](estandares_datos.md).

---

## 4. Crear las Migraciones

`just new-pipeline` ya generó `migrations/mi_pipeline/` con `flyway.conf.example`, `flyway.conf` y `sql/`. Agrega ahí tus migraciones:

```bash
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

## 5. Completar el DAG de Airflow

`just new-pipeline` ya generó `dags/etl_mi_pipeline.py` con el DAG de bootstrap (`schedule=None`) y `if __name__ == "__main__"` para ejecutarlo como script.

Si el pipeline tiene update, agrega su DAG y registra el calendario en `core/schedules/registry.py`. Toma como referencia los DAGs existentes en `dags/`.

---

## 6. Probar localmente

```bash

# 1. Levantar base de datos de desarrollo
just build-dev user=sieej_user pass=mi_pass db=mi_pipeline

# 2. Crear migración de la base de datos de cvegeo y hacer la migración:
just create-cvegeo-db user=sieej_user && just flyway-migrate cvegeo

# 3. Configurar variables de entorno del pipeline
# → Editar core/pipelines/mi_pipeline/.env con las credenciales

# 4. Configurar Flyway
just flyway-config mi_pipeline

# 5. Aplicar migraciones
just flyway-migrate mi_pipeline

# 6. Ejecutar
python dags/etl_mi_pipeline.py
```

---

## 7. Probar en Airflow

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

### Pipelines

| Comando | Descripción |
|:--------|:------------|
| `just new-pipeline <pipeline> [owner]` | Genera la estructura inicial del pipeline, sus migraciones y su DAG |

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
| `just stop-dev` | Detiene y elimina el contenedor `postgres-dev` (conserva los datos) |
| `just reset-dev` | Elimina el contenedor y el volumen `postgres-dev-data` ⚠️ |
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
