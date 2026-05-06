---
name: flyway
description: Comandos `just` para gestionar Flyway y la base de datos local de desarrollo en el proyecto SIEEJ. Aplica a operaciones de setup, migración, validación y reset.
applyTo: "justfile,migrations/**,compose.yaml"
---

# Flyway & BD Local — Reglas operativas

> Convenciones de escritura de SQL y schemas → `db.instructions.md`. Integración cvegeo → skill `cvegeo-integration`. Este archivo cubre **qué comandos ejecutar y en qué orden**.

## Comandos disponibles

### Docker (stack completo)

```bash
just up              # Construye imagen y levanta todos los servicios
just down            # Detiene servicios
just down-volumes    # Detiene y elimina volúmenes  ⚠️ destructivo
just rebuild <svc>   # Reconstruye un servicio
just logs [svc]      # Logs en tiempo real
just ps              # Estado de los contenedores
just restart <svc>   # Reinicia un servicio
just airflow-init    # Inicializa Airflow (solo primera vez, antes de just up)
```

### BD local de desarrollo (standalone)

```bash
just build-dev [user=test] [pass=test] [db=test] [port=5432]
just stop-dev
just create-cvegeo-db [host=localhost] [port=5432] [user=test] [database=test] [pass=test]
```

### Flyway (por pipeline)

```bash
just flyway-config   <pipeline>   # Copia flyway.conf.example → flyway.conf
just flyway-migrate  <pipeline>   # Aplica migraciones pendientes
just flyway-info     <pipeline>   # Estado de las migraciones
just flyway-validate <pipeline>   # Valida integridad de los scripts
just flyway-clean    <pipeline>   # ⚠️ DESTRUCTIVO — elimina todos los objetos
just flyway-reset    <pipeline>   # ⚠️ DESTRUCTIVO — clean + migrate
```

## Flujo de setup de un pipeline nuevo

Orden **exacto**. No saltarse pasos.

```bash
# 1. Levantar BD de desarrollo (si no está)
just build-dev user=sieej_user pass=mi_pass db={pipeline}

# 2. (Solo si requiere cvegeo) — crear y migrar la BD cvegeo
just create-cvegeo-db user=sieej_user
just flyway-migrate cvegeo

# 3. Configurar Flyway para el pipeline
just flyway-config {pipeline}
# Editar manualmente migrations/{pipeline}/flyway.conf con las credenciales reales

# 4. Aplicar migraciones
just flyway-migrate {pipeline}

# 5. Verificar estado
just flyway-info {pipeline}

# 6. Probar reproducibilidad (solo dev)
just flyway-reset {pipeline}

# 7. Validar integridad antes del PR
just flyway-validate {pipeline}
```

## Prueba local de un pipeline

```bash
conda activate etl
python dags/etl_{pipeline}.py   # Ejecuta el DAG bootstrap como script
```

Si falla:

- `ImportError` → revisar `sys.path.append(...)` al inicio del DAG.
- Error de BD → verificar `core/pipelines/{pipeline}/.env`, revisar que `postgres-dev` está corriendo.
- Error de migración → revisar SQL en `migrations/{pipeline}/sql/` y `just flyway-reset`.

## Prueba en Airflow (Docker)

```bash
just up
just logs airflow-dag-processor    # Verificar que el DAG se registra sin errores
```

En Docker, las variables del `.env` del pipeline deben usar `DB_HOST=host.docker.internal` (no `localhost`).

## Reglas de seguridad

- `just flyway-clean` y `just flyway-reset` son **destructivos** — solo en desarrollo local, nunca en producción ni entornos compartidos.
- Siempre `just flyway-info` antes de `just flyway-migrate` en entornos no-locales para ver qué se va a aplicar.
- `migrations/{pipeline}/flyway.conf` **nunca** se commitea (solo `.conf.example`).
- `core/pipelines/{pipeline}/.env` **nunca** se commitea (solo `.env.example`).
- `just down-volumes` borra todos los datos de Docker — confirmar con el usuario antes de ejecutarlo.

## Diagnóstico rápido

| Error | Causa | Solución |
|---|---|---|
| `Connection refused` en Flyway | `postgres-dev` no corriendo | `just build-dev` |
| `flyway.conf not found` | No se ejecutó `flyway-config` | `just flyway-config {pipeline}` |
| `relation "cvegeo_municipalities" does not exist` | FDW sin setup | Aplicar skill `cvegeo-integration` |
| `password authentication failed` en FDW | `USER MAPPING` con credenciales vacías | Editar el USER MAPPING tras correr V2__cvegeo.sql |
| `Import error` en `dag-processor` | `sys.path` mal configurado | Revisar el DAG |
| `DB_HOST localhost` no resuelve en Docker | Falta `host.docker.internal` | Editar `.env` del pipeline |
| `Migration V{n} failed` | SQL no idempotente o error de sintaxis | Corregir y `just flyway-reset {pipeline}` |
