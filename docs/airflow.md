<div align="center">

# Guía de Airflow - ETL SIEEJ
<img src="https://img.shields.io/badge/IIEG-Jalisco-5C2D91?style=for-the-badge" alt="IIEG"/>
<img src="https://img.shields.io/badge/Apache_Airflow-017CEE?style=for-the-badge&logo=apacheairflow&logoColor=white" alt="Airflow"/>

</div>

### Operación de Airflow 3 con LocalExecutor: Docker y API REST

---

## Índice

- [Arquitectura](#arquitectura)
- [Límites de recursos](#límites-de-recursos)
- [Operación con Docker](#operación-con-docker)
- [Operación con la API REST](#operación-con-la-api-rest)
- [Flujo completo: REPD](#flujo-completo-repd)
- [Diagnóstico](#diagnóstico)
- [Notas para clientes automatizados](#notas-para-clientes-automatizados)

---

## Arquitectura

El despliegue corre en una sola máquina con `LocalExecutor`. No hay Celery, ni Redis, ni workers separados.

```text
┌──────────────────────────────────────────┐
│ airflow-apiserver   :8080  UI + API v2   │
├──────────────────────────────────────────┤
│ airflow-scheduler          aquí corren   │
│                            las tareas    │
├──────────────────────────────────────────┤
│ airflow-dag-processor      parsea DAGs   │
├──────────────────────────────────────────┤
│ postgres                   metadatos     │
└──────────────────────────────────────────┘
```

Cuatro servicios. Se eliminaron `redis`, `airflow-worker`, `flower` y `airflow-triggerer`.

> **El triggerer no está.** Ningún DAG usa `deferrable=True`. Si algún operador lo usa, la tarea se queda colgada indefinidamente sin ningún error visible. Hay que volver a levantar el servicio.

**Con `LocalExecutor` las tareas son procesos hijos del scheduler.** Esto tiene dos consecuencias que dominan todo lo demás:

1. El `mem_limit` del scheduler es también el techo de memoria de los pipelines. Un pipeline que lo exceda se lleva al scheduler por delante.
2. Dentro de una tarea, `localhost` es el contenedor del scheduler, no el servidor. Un pipeline cuyo `.env` diga `DB_HOST=localhost` no encuentra la base.

Para el punto 2 el compose define `host.docker.internal`:

```bash
# core/pipelines/<pipeline>/.env
DB_HOST=host.docker.internal   # base en el host, fuera de compose
DB_PORT=5434
```

---

## Límites de recursos

Dimensionados para un servidor de 16 GB, dejando ~3 GB al host (kernel, SSH, Docker, caché de disco).

| Servicio | CPU | Memoria |
|:---------|:---:|:-------:|
| `airflow-scheduler` | 2.5 | 8 GB |
| `postgres` | 1.0 | 2 GB |
| `airflow-apiserver` | 0.5 | 1.5 GB |
| `airflow-dag-processor` | 0.5 | 1.5 GB |

Concurrencia: `PARALLELISM=2`, `MAX_ACTIVE_TASKS_PER_DAG=1`, `MAX_ACTIVE_RUNS_PER_DAG=1`. Dos pipelines distintos a la vez como máximo, y nunca dos corridas del mismo DAG.

---

## Configuración del host

`AIRFLOW_BASE_URL` define la URL pública de Airflow. Se usa para los enlaces de la UI y, sobre todo, **como issuer del JWT**. En el servidor va en el `.env` de la raíz:

```bash
# .env
AIRFLOW_UID=1000
AIRFLOW_BASE_URL=http://10.0.0.5:8080
```

Si queda vacío, `POST /auth/token` responde **500 Internal Server Error** con `TypeError: Issuer (iss) must be a string` en los logs del apiserver.

---

## Operación con Docker

Las recetas de `just` envuelven los comandos de compose:

```bash
just up                      # levantar todo
just down                    # bajar
just ps                      # estado de los servicios
just logs airflow-scheduler  # seguir logs de un servicio
just restart airflow-scheduler
just rebuild airflow-scheduler
```

Equivalentes directos:

```bash
docker compose up -d
docker compose ps
docker compose logs -f airflow-scheduler
```

> **Al cambiar variables de entorno hay que recrear todos los servicios**, no solo uno. `docker compose up -d <servicio>` deja a los demás con el entorno viejo. Si el scheduler y el apiserver no comparten el mismo `AIRFLOW__API_AUTH__JWT_ISSUER`, el scheduler genera tokens sin `iss` y **todas las tareas fallan** con `Invalid auth token: Token is missing the "iss" claim`.

### CLI dentro del contenedor

```bash
docker compose exec airflow-scheduler airflow dags list
docker compose exec airflow-scheduler airflow config get-value api base_url
docker compose exec airflow-scheduler airflow dags trigger etl_repd_bootstrap
```

---

## Operación con la API REST

Airflow 3 expone **API v2** bajo `/api/v2` y usa **JWT**, no Basic Auth.

### 1. Obtener token

```bash
TOKEN=$(curl -s -X POST http://localhost:8080/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username":"airflow","password":"airflow"}' \
  | python3 -c 'import sys,json;print(json.load(sys.stdin)["access_token"])')
```

El token dura **24 horas**. Sus claims incluyen `iss` (el `base_url`), `exp` e `iat`.

### 2. Endpoints

Todos requieren `Authorization: Bearer $TOKEN`, salvo `/api/v2/version`.

| Acción | Método y ruta |
|:-------|:--------------|
| Versión (sin auth) | `GET /api/v2/version` |
| Salud de componentes | `GET /api/v2/monitor/health` |
| Listar DAGs | `GET /api/v2/dags?dag_id_pattern=repd` |
| Pausar / reanudar | `PATCH /api/v2/dags/{dag_id}?update_mask=is_paused` |
| Disparar corrida | `POST /api/v2/dags/{dag_id}/dagRuns` |
| Estado de la corrida | `GET /api/v2/dags/{dag_id}/dagRuns/{run_id}` |
| Tareas de la corrida | `GET /api/v2/dags/{dag_id}/dagRuns/{run_id}/taskInstances` |
| Logs de una tarea | `GET /api/v2/dags/{dag_id}/dagRuns/{run_id}/taskInstances/{task_id}/logs/{try_number}` |

Sin token, la respuesta es `401`.

### 3. Reanudar y disparar

Un DAG pausado acepta el `POST` pero la corrida se queda en `queued` para siempre. Hay que reanudarlo primero:

```bash
curl -s -X PATCH -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  "http://localhost:8080/api/v2/dags/etl_repd_bootstrap?update_mask=is_paused" \
  -d '{"is_paused": false}'

curl -s -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  "http://localhost:8080/api/v2/dags/etl_repd_bootstrap/dagRuns" \
  -d '{"logical_date": null, "conf": {}}'
```

La respuesta trae el `dag_run_id`, con este formato:

```text
manual__2026-07-21T18:08:20.621631+00:00
```

> **El `run_id` lleva `:` y `+`, hay que codificarlo en URL** antes de meterlo en una ruta. Sin codificar, los endpoints de estado y de logs responden 404.

```bash
RUN_ENC=$(python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1],safe=''))" "$RUN_ID")
curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8080/api/v2/dags/etl_repd_bootstrap/dagRuns/$RUN_ENC"
```

Estados de una corrida: `queued` → `running` → `success` o `failed`.

### 4. Logs

```bash
curl -s -H "Authorization: Bearer $TOKEN" -H "Accept: application/json" \
  ".../taskInstances/run_bootstrap/logs/1?full_content=true"
```

Devuelve JSON con una lista `content`, cada elemento un objeto con el campo `event` (la línea del log) y su timestamp. No es texto plano.

---

## Flujo completo: REPD

Probado de extremo a extremo el 2026-07-21.

### Preparar la base

```bash
just build-dev --port 5434       # postgres de desarrollo
just pipeline-deploy repd        # env-init + flyway-config + create-db + flyway-migrate
```

`pipeline-deploy` aplica las 6 migraciones de REPD: catálogos, tabla staging, vista, FDW a conapo, vistas materializadas y comments.

### Ejecutar

```bash
TOKEN=$(curl -s -X POST http://localhost:8080/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username":"airflow","password":"airflow"}' \
  | python3 -c 'import sys,json;print(json.load(sys.stdin)["access_token"])')

curl -s -X PATCH -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  "http://localhost:8080/api/v2/dags/etl_repd_bootstrap?update_mask=is_paused" \
  -d '{"is_paused": false}'

curl -s -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  "http://localhost:8080/api/v2/dags/etl_repd_bootstrap/dagRuns" \
  -d '{"logical_date": null, "conf": {}}'
```

### Resultado

| Métrica | Valor |
|:--------|:------|
| Duración | ~2 minutos |
| Estado final | `success` |
| Registros | 38,435 en `stg_repd_casos` y `stg_repd_casos_historial` |
| Vistas materializadas | 6, todas pobladas |
| Memoria pico del scheduler | ~483 MiB de 8 GiB |

El load inserta en chunks de 5,000 (`REPD_LOAD_BATCH_SIZE`), así que el consumo se mantiene plano. El límite de 8 GB del scheduler quedó holgado.

---

## Diagnóstico

### Consumo por contenedor

```bash
docker stats --no-stream --format '{{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}'
```

`MemUsage` muestra `usado / límite`, así que sirve para confirmar que los límites se aplicaron.

### ¿Lo mató el OOM killer?

```bash
docker inspect etl_sieej-airflow-scheduler-1 --format='{{.State.OOMKilled}}'
sudo dmesg -T | grep -Ei 'out of memory|oom|killed process'
```

### Errores frecuentes

| Síntoma | Causa |
|:--------|:------|
| `POST /auth/token` → 500, `Issuer (iss) must be a string` | `AIRFLOW_BASE_URL` vacío |
| Tareas fallan con `Token is missing the "iss" claim` | Servicios recreados a medias, con entornos distintos |
| Corrida atorada en `queued` | DAG pausado, o `parallelism` saturado |
| Tarea con `deferrable=True` colgada | No hay triggerer |
| Pipeline no conecta a la base | `DB_HOST=localhost` en vez de `host.docker.internal` |
| 404 al consultar una corrida | `run_id` sin codificar en URL |

---

## Notas para clientes automatizados

Puntos a considerar al construir un cliente o MCP sobre esta API:

1. **JWT, no Basic Auth.** El flujo es `POST /auth/token` y luego `Bearer`. El token dura 24 h; conviene cachearlo y renovarlo ante un `401`.
2. **El issuer debe coincidir.** El token que emite el apiserver y el que valida tienen que compartir `base_url`. Un despliegue mal configurado da 500 en el login, no un error de credenciales.
3. **Codificar el `run_id`.** Es el error más fácil de cometer: contiene `:` y `+`.
4. **Reanudar antes de disparar.** Un `POST` a un DAG pausado devuelve 200 y la corrida nunca arranca. Conviene verificar `is_paused` y avisar, en lugar de dejar al usuario esperando.
5. **Los logs son JSON estructurado**, con una lista `content` de objetos, no texto plano.
6. **`GET /api/v2/version` no pide auth**, sirve como sonda de disponibilidad antes de intentar el login.
7. **`GET /api/v2/monitor/health`** reporta metadatabase, scheduler, triggerer y dag_processor por separado. Con el triggerer eliminado su `status` es `null`, que es lo esperado y no debe tratarse como falla.
8. **Hacer polling con paciencia.** Los pipelines tardan minutos. Intervalos de 15-30 s son razonables; los estados terminales son `success` y `failed`.

---
