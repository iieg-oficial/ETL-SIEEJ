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
- [Calendario de actualización](#calendario-de-actualización)
- [Operación con Docker](#operación-con-docker)
- [Operación con la API REST](#operación-con-la-api-rest)
- [flowrs: la TUI de Airflow](#flowrs-la-tui-de-airflow)
- [Flujo completo: REPD](#flujo-completo-repd)
- [Sincronización de GeoServer](#sincronización-de-geoserver)
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

### Pipelines pesados

Los límites globales no bastan por sí solos: dos pipelines "pesados" (alto fan-out de tareas, mucha memoria pico, payloads grandes o corridas largas) pueden coincidir en los dos slots de `PARALLELISM` y saturar la memoria del `airflow-scheduler`. Un pipeline se clasifica como pesado si cumple **cualquiera** de estas señales:

| Señal | Umbral |
|:------|:------:|
| Fan-out (task instances por corrida) | > ~20 |
| Memoria pico del scheduler | > ~25% de `mem_limit` |
| Payload de un solo extract | > ~500 MB |
| Duración de la corrida completa | > ~30 min |

Clasificación actual:

| Pipeline | Señal que dispara |
|:---------|:-------------------|
| `denue` | Fan-out: 97 task instances por corrida (32 entidades × 3 stages + `cleanup`) |
| `nacimientos_dgis` | Payload: extract anual > 500 MB |

**Topología de pools.** Un único pool, `heavy_pipeline`, con 1 slot, asignado a **todas** las tareas de cada DAG pesado (extract, transform, load y `cleanup` — no solo extract/load). Un pool con más slots, o pools separados por stage, no evita que dos DAGs pesados corran tareas simultáneas: solo un pool único con 1 slot para todas las tareas garantiza que como máximo una tarea pesada se ejecute a la vez en todo el clúster.

Esa serialización deja al menos un slot de `PARALLELISM` libre para pipelines livianos: cada tarea pesada declara `priority_weight` negativo (`weight_rule="absolute"`), así que cuando se libera un slot compartido, el trabajo liviano en cola gana sobre el pesado en cola.

**Provisión.** El pool se define en `core/constants/concurrency.py` (única fuente) y se provisiona con:

```bash
just airflow-pools   # también se ejecuta automáticamente con `just up`
```

Es idempotente: correrlo de nuevo no duplica ni falla si el pool ya existe.

**Envolvente de concurrencia resultante.** Como máximo una tarea pesada y una tarea liviana corriendo a la vez, en todo el clúster.

---

## Calendario de actualización

Los pools evitan que dos pipelines pesados se pisen mientras corren. El calendario es el frente anterior: evitar que arranquen todos en el mismo instante.

Cada DAG tenía su `schedule` como literal en su propio archivo, y los alias de cron ocultaban las colisiones: `@monthly`, `@yearly` y `@quarterly` expanden todos a `0 0 1 * *`, así que el 1 de enero a las 00:00 disparaban siete DAGs a la vez con `PARALLELISM=2`. Nadie podía verlo sin abrir los 27 archivos.

### El registro

`core/schedules/` es la única fuente del calendario:

| Módulo | Contiene |
|:-------|:---------|
| `registry.py` | El mapeo `dag_id → Schedule(pipeline, cron, frecuencia)`. **Esto es lo que se edita.** |
| `policy.py` | El modelo `Schedule` y las reglas: `MIN_SEPARATION_MINUTES`, `SIMULATED_YEARS` |
| `firings.py` | Expande los crons a instantes de disparo con el parser de Airflow |

Los DAGs no llevan literal: piden su horario al registro.

```python
from core.schedules import schedule_for

schedule=schedule_for("etl_rastros_update"),
```

`schedule_for` levanta `KeyError` si el DAG no está registrado: no se puede programar un pipeline sin entrar a la reja.

`pool` y `priority` no se declaran en el registro, se **derivan** de `HEAVY_PIPELINES` en `core/constants/concurrency.py`. Un pipeline no puede ser pesado en un archivo y liviano en otro.

Reglas del registro:

- **Solo crons explícitos.** Nada de alias ni de `timedelta`: si el horario no se lee, la colisión no se ve.

```python
# No: el alias esconde que dispara a la misma hora que otros seis DAGs
Schedule("rastros", "@monthly", "cada mes, el día 1")

# No: un timedelta deriva a instantes que no se pueden leer en un calendario
Schedule("denue", timedelta(days=10), "cada 10 días")

# Sí
Schedule("rastros", "0 9 1 * *", "cada mes, el día 1")
Schedule("denue", "0 11 11 * *", "cada mes, el día 11")
```

- **Solo DAGs programados.** Los `bootstrap` corren bajo demanda con `schedule=None` y no están en el registro.

### Política: separación mínima, no solo colisión

Dos DAGs no pueden disparar a menos de **60 minutos** (`MIN_SEPARATION_MINUTES`). Es una ventana, no una igualdad: con `PARALLELISM=2` un vecino se tolera, pero un amontonamiento deja al resto en cola detrás de la corrida más lenta.

La reja actual asigna **una hora por DAG en el día 1**, de modo que un mensual, un trimestral y un anual que caen en la misma fecha nunca comparten instante. Los pipelines que publican otro día (el 10) conservan su fecha.

### Ver el calendario

```bash
just schedules        # próximos 90 días
just schedules 365    # ventana explícita en días
```

Ordena todas las ejecuciones por fecha y muestra la frecuencia y si el DAG es pesado. Si dos quedan a menos de la ventana mínima, lo marca en la fila y termina con código de salida 1.

Airflow dispara al **cierre** del intervalo de datos: un DAG mensual con `0 0 1 * *` corre el 1 de octubre procesando septiembre. La columna `SE EJECUTA` es el momento real de ejecución, no el inicio del período.

### Elegir horario para un pipeline nuevo

1. Correr `just schedules 365` y buscar una hora libre en la fecha de publicación de la fuente.
2. Agregar la entrada en `core/schedules/registry.py` con el cron explícito.
3. En el DAG, `schedule=schedule_for("<dag_id>")`.
4. Correr `pytest tests/dags tests/schedules` — `test_no_two_dags_fire_within_the_separation_window` simula 5 años de ejecuciones y falla si la nueva entrada queda a menos de 60 minutos de otra.

El paso 4 lo dispara solo el hook de `pre-commit` cuando el commit toca `dags/`, `core/schedules/` o `core/constants/concurrency.py`, siempre que hayas corrido `pre-commit install` en la máquina. Ver CONTRIBUTING.md.

---

## Configuración del host

`AIRFLOW_BASE_URL` define la URL pública de Airflow. Se usa para los enlaces de la UI y, sobre todo, **como issuer del JWT**. En el servidor va en el `.env` de la raíz:

```bash
# .env
AIRFLOW_UID=1000
AIRFLOW_BASE_URL=http://<ip-del-servidor>:8080
```

Debe ser la URL por la que **se accede realmente** a Airflow. Si se entra por IP pero aquí queda `localhost`, el token se emite para un host y se consume desde otro, y la UI responde `Invalid issuer` con 403.

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

Los ejemplos de esta sección usan `$AIRFLOW_URL`. Definirla primero, según dónde corra Airflow:

```bash
AIRFLOW_URL=http://localhost:8080          # local, con just up
# AIRFLOW_URL=http://<ip-del-servidor>:8080  # servidor
```

### 1. Obtener token

```bash
TOKEN=$(curl -s -X POST "$AIRFLOW_URL/auth/token" \
  -H "Content-Type: application/json" \
  -d '{"username":"airflow","password":"airflow"}' \
  | python3 -c 'import sys,json;print(json.load(sys.stdin)["access_token"])')
```

> Escribir el comando en **una sola línea** o cuidar que no quede un espacio después de las barras de continuación: `\ ` seguido de espacio deja de ser continuación y el shell corta ahí, con un `-H: command not found` que despista.

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
  "$AIRFLOW_URL/api/v2/dags/etl_repd_bootstrap?update_mask=is_paused" \
  -d '{"is_paused": false}'

curl -s -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  "$AIRFLOW_URL/api/v2/dags/etl_repd_bootstrap/dagRuns" \
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
  "$AIRFLOW_URL/api/v2/dags/etl_repd_bootstrap/dagRuns/$RUN_ENC"
```

Estados de una corrida: `queued` → `running` → `success` o `failed`.

### 4. Logs

```bash
curl -s -H "Authorization: Bearer $TOKEN" -H "Accept: application/json" \
  ".../taskInstances/run_bootstrap/logs/1?full_content=true"
```

Devuelve JSON con una lista `content`, cada elemento un objeto con el campo `event` (la línea del log) y su timestamp. No es texto plano.

---

## flowrs: la TUI de Airflow

[flowrs](https://github.com/jvanbuel/flowrs) es una interfaz de terminal para Airflow. Sirve para ver DAGs, corridas y logs sin abrir el navegador. Habla la misma API REST v2 de la sección anterior, así que hereda sus mismos requisitos de autenticación.

### Instalación

```bash
curl -sSL https://github.com/jvanbuel/flowrs/releases/download/flowrs-tui-v0.13.2/flowrs-tui-x86_64-unknown-linux-gnu.tar.xz | tar -xJ
install -m 755 flowrs-tui-x86_64-unknown-linux-gnu/flowrs ~/.local/bin/flowrs
```

También hay `brew install flowrs` y `cargo install flowrs-tui --locked`.

### Configuración

El archivo va en `~/.config/flowrs/config.toml` y **se escribe a mano**.

En la plantilla, `<AIRFLOW_HOST>` es la URL de la instancia, con esquema y puerto. Aparece **dos veces** y ambas deben coincidir: en `endpoint` y dentro de `cmd`.

```toml
managed_services = []
poll_interval_ms = 2000
theme = "auto"

[[servers]]
name = "<NOMBRE>"
endpoint = "<AIRFLOW_HOST>"
version = "V3"
timeout_secs = 30
insecure = false

[servers.auth.Token]
cmd = """curl -sS -X POST <AIRFLOW_HOST>/auth/token -H "Content-Type: application/json" -d '{"username":"airflow","password":"airflow"}' | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])""""
```

Valores según dónde corra Airflow:

| Entorno | `<AIRFLOW_HOST>` |
|:--------|:-----------------|
| Local, con `just up` | `http://localhost:8080` |
| Servidor | `http://<ip-del-servidor>:8080` |

> **`endpoint` no admite variables de entorno.** TOML no interpola, así que la URL va literal. El `cmd` sí se ejecuta con `sh -c`, por lo que ahí sí funcionarían `$VAR` o `$(...)`, pero solo si la variable existe en el entorno desde el que se lanza `flowrs` — conviene no depender de eso y escribir la URL completa.

Se pueden declarar varias instancias repitiendo el bloque `[[servers]]` con distinto `name` y `<AIRFLOW_HOST>`; flowrs permite cambiar entre ellas.

Luego:

```bash
just up          # solo si Airflow corre en local
flowrs run
```

### Por qué la config es así

Tres decisiones que no son obvias y que cuestan tiempo si se descubren a golpes:

**`version = "V3"` significa Airflow 3.** flowrs traduce `V2` a la ruta `/api/v1/` y `V3` a `/api/v2/`. Como este despliegue corre Airflow 3, un `V2` produce **404** en todas las llamadas.

**La autenticación debe ser `Token`, nunca `Basic`.** Airflow 3 eliminó Basic Auth de la API: responde **401**. flowrs con `auth.Basic` manda las credenciales directo a `/api/v2/dags` y no hace el intercambio a JWT por su cuenta.

**Se usa la variante `Token` con `cmd`, no con `token`.** flowrs admite un token fijo (`token = "..."`) o un comando que lo imprima (`cmd = "..."`). El JWT de Airflow caduca a las **24 horas**, así que un token fijo obliga a reeditar el archivo a diario. Con `cmd`, flowrs ejecuta el comando mediante `sh -c` y cachea el resultado 60 segundos.

### No usar `flowrs config add`

El asistente interactivo solo ofrece usuario y contraseña, así que escribe `auth.Basic` — que no funciona contra Airflow 3. Peor aún: **reescribe el archivo completo**, de modo que puede pisar la configuración `Token` de instancias que ya funcionaban.

Si aparece un 401 después de tocar la configuración, lo primero es verificar que no se haya revertido a `Basic`:

```bash
python3 -c "
import tomllib
d=tomllib.load(open('$HOME/.config/flowrs/config.toml','rb'))
for s in d['servers']: print(s['name'],'->',list(s['auth'].keys()))"
```

La salida debe decir `Token` en cada instancia.

### Errores frecuentes

| Síntoma | Causa |
|:--------|:------|
| 404 en `/api/v1/dags` | `version = "V2"` en un Airflow 3 |
| 401 en `/api/v2/dags` | La instancia quedó con `auth.Basic` |
| `Token helper command failed` | El `cmd` falló; su stderr aparece en el propio error |
| 500 al pedir el token | Ver la tabla de la sección [Diagnóstico](#diagnóstico) |

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
TOKEN=$(curl -s -X POST "$AIRFLOW_URL/auth/token" \
  -H "Content-Type: application/json" \
  -d '{"username":"airflow","password":"airflow"}' \
  | python3 -c 'import sys,json;print(json.load(sys.stdin)["access_token"])')

curl -s -X PATCH -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  "$AIRFLOW_URL/api/v2/dags/etl_repd_bootstrap?update_mask=is_paused" \
  -d '{"is_paused": false}'

curl -s -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  "$AIRFLOW_URL/api/v2/dags/etl_repd_bootstrap/dagRuns" \
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

## Sincronización de GeoServer

`etl_geoserver_sync` publica/actualiza en GeoServer (workspace + datastore PostGIS + un featuretype por vista) las vistas materializadas con geometría de cada pipeline, y borra las que ya no correspondan (huérfanas — renombradas, eliminadas, o que perdieron su columna de geometría). Es idempotente: seguro correrlo las veces que haga falta.

No tiene `schedule` propio (`schedule=None`) ni entra al registro de `core/schedules/` — es como los `bootstrap`, pero disparado por otro DAG en vez de por una persona. Normalmente lo dispara un `TriggerDagRunOperator` al final del bootstrap/update de cada pipeline geo (`produccion_ganadera`, `agropecuario_siap`, `marginacion`, `intensidad_migratoria`, `efipem`, `conapo`, `asg_imss`, `repd`, `fiscalia`, `participacion_ciudadana`, `ilmm`, `pobreza_multidimensional`, `delitos_fuero_comun`), pasándole `conf={"pipeline": "<nombre>"}`. Ese trigger tiene `wait_for_completion=False`: si GeoServer está caído, el pipeline de datos igual queda en `success`.

Los pipelines que se sincronizan no están en una lista fija: `scripts/create_geoserver_layers.py` los descubre solos (`discover_pipelines()`), iterando `core/pipelines/*` y quedándose con los que declaran `MATERIALIZED_VIEWS`. Un pipeline nuevo con geometría entra automáticamente, sin tocar este DAG ni el script.

Además de disparado automáticamente, hay tres formas de correrlo por separado, sin pasar por el bootstrap/update completo de un pipeline:

### Vía Airflow (UI)

"Trigger DAG w/ config" en `etl_geoserver_sync`, con:

```json
{"pipeline": "conapo"}
```

### Vía Airflow (CLI o API REST)

Mismo patrón que el resto de esta guía, agregando `conf`:

```bash
docker compose exec airflow-scheduler airflow dags trigger etl_geoserver_sync --conf '{"pipeline": "conapo"}'
```

```bash
curl -s -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  "$AIRFLOW_URL/api/v2/dags/etl_geoserver_sync/dagRuns" \
  -d '{"logical_date": null, "conf": {"pipeline": "conapo"}}'
```

### Saltándose Airflow — el script directo

`etl_geoserver_sync` es un wrapper delgado sobre `scripts/create_geoserver_layers.py` (necesita `scripts/` montado al contenedor, ya declarado en `compose.yaml`):

```bash
docker compose exec airflow-scheduler bash -c \
  "PYTHONPATH=. python3 scripts/create_geoserver_layers.py --pipeline conapo"
```

Sin `--pipeline` corre contra **todos** los pipelines detectados automáticamente. `--dry-run` solo loggea qué haría, sin llamar al REST API de GeoServer.

### Variables de entorno

```bash
# .env (raíz)
GEOSERVER_URL=https://10.25.7.4/sextante/rest
GEOSERVER_USER=iieg
GEOSERVER_PASSWORD=<real>
GEOSERVER_VERIFY_SSL=false
```

GeoServer vive en un host distinto (`10.25.7.4`) al de la base de datos de cada pipeline — no es un error de tipeo, son máquinas separadas.

### Advertencia: el host que se escribe en GeoServer

En cada corrida, por cada pipeline, el script **sobrescribe** los parámetros de conexión del datastore `proxmox_<pipeline>` en GeoServer (`host`, `port`, `database`, `schema`, `user`, `passwd`) con los del `.env` de ese pipeline (`DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`). Si el datastore ya existía, lo actualiza; no pregunta.

GeoServer está en otro servidor (`10.25.7.4`), así que **`DB_HOST` debe ser una dirección que GeoServer pueda alcanzar**. `localhost` no sirve (para GeoServer es su propia máquina), y `host.docker.internal` normalmente tampoco (solo se resuelve dentro de Docker en el host que corre Airflow).

> **No correr el script desde una máquina de desarrollo contra el GeoServer de producción.** Con el `.env` local (`DB_HOST=localhost`), el datastore de producción queda apuntando a un host inalcanzable y sus capas dejan de poder leer datos. Síntoma: `HTTP 500` al actualizar el featuretype (GeoServer intenta reconectarse para recalcular el bounding box) y, después, errores en WMS/WFS. Pasó con `repd`.

Antes de correrlo contra un GeoServer real, usar `--dry-run`, y confirmar que el `DB_HOST` del `.env` del pipeline es el que GeoServer debe usar.

**Reparación:** volver a correr el script (o `etl_geoserver_sync`) desde un entorno cuyo `.env` tenga el host correcto. Como siempre sobrescribe esos campos, el datastore se corrige solo.

### Prerrequisito: datos ya cargados

El script solo *lee* Postgres (`pg_matviews`, `geometry_columns`, `pg_attribute`) — nunca crea ni llena datos. Si se corre antes de que el pipeline haya hecho bootstrap, `resolve_matviews` devuelve una lista vacía y no publica nada (sin error, 0 layers). Si la vista existe pero sigue vacía (`CREATE MATERIALIZED VIEW ... WITH NO DATA`, o antes del primer `refresh_materialized_views`), la layer se crea igual pero con bounding box vacío hasta la siguiente corrida después de un refresh con datos reales.

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
| `POST /auth/token` → 500, `Flask app is not initialized` | `apache-airflow-providers-fab` 3.6.1; se requiere 3.7.2 o superior |
| UI con `Invalid issuer` y 403 al entrar por IP | `AIRFLOW_BASE_URL` sin definir: el token se emite para `localhost` y se consume desde otro host |
| Tareas fallan con `Token is missing the "iss" claim` | Servicios recreados a medias, con entornos distintos |
| Corrida atorada en `queued` | DAG pausado, o `parallelism` saturado |
| Tarea con `deferrable=True` colgada | No hay triggerer |
| Pipeline no conecta a la base | `DB_HOST=localhost` en vez de `host.docker.internal` |
| 404 al consultar una corrida | `run_id` sin codificar en URL |
| Tarea atorada indefinidamente en `scheduled`, sin fallar nunca | Referencia a un pool no provisionado (`NONEXISTENT_POOL`); confirmar con `docker compose exec -T airflow-scheduler airflow pools list` — si el pool no aparece, correr `just airflow-pools` |

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
