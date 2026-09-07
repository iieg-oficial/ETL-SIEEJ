set shell := ["bash", "-cu"]

default:
    just --list --unsorted


[group('docker')]
[doc("Levantar servicios")]
up:
    docker compose up --build -d
    just airflow-pools

[group('docker')]
[doc("Detener servicios")]
[confirm("¿Detener todos los servicios? [Y/N]:")]
down:
    docker compose down

[group('docker')]
[doc("Detener servicios y eliminar volúmenes")]
[confirm("¿Detener los servicios y eliminar los volúmenes? Los datos se perderán. [Y/N]:")]
down-volumes:
    docker compose down -v

[group('docker')]
[doc("Rebuild de un servicio específico")]
rebuild service:
    docker compose up --build -d {{service}}

[group('docker')]
[doc("Ver logs de un servicio")]
logs service="":
    docker compose logs -f {{service}}

[group('docker')]
[doc("Ver estado de los servicios")]
ps:
    docker compose ps

[group('docker')]
[doc("Reiniciar un servicio")]
[confirm("¿Reiniciar el servicio? [Y/N]:")]
restart service:
    docker compose restart {{service}}

[group('development')]
[doc("Instalar pre-commit hooks y dependencias")]
setup:
    pip install -r requirements.txt
    chmod +x .githooks/commit-msg
    pre-commit install
    pre-commit install --hook-type commit-msg

[group('development')]
[doc("Levantar contenedor PostGIS para desarrollo")]
[arg("user", long)]
[arg("pass", long)]
[arg("db", long)]
[arg("port", long)]
build-dev user="test" pass="test" db="test" port="5432":
    docker run --name postgres-dev \
      -e POSTGRES_USER={{user}} \
      -e POSTGRES_PASSWORD={{pass}} \
      -e POSTGRES_DB={{db}} \
      -p {{port}}:5432 \
      -d postgis/postgis:17-3.5

[group('development')]
[doc("Detener y eliminar el contenedor de desarrollo")]
stop-dev:
    docker stop postgres-dev && docker rm postgres-dev

[group('development')]
[doc("Eliminar archivos temporales de extract y transform de un pipeline")]
[confirm("¿Eliminar los archivos temporales del pipeline? [Y/N]:")]
data-clean pipeline:
    #!/usr/bin/env bash
    set -euo pipefail
    for dir in data/extract/{{pipeline}} data/transform/{{pipeline}}; do
        if [ -d "$dir" ]; then
            rm -rf "$dir"
            echo "Cleaned: $dir"
        fi
    done

[group('database')]
[doc("Crear base de datos de un pipeline leyendo credenciales de su .env")]
create-db pipeline: (_load-env pipeline)
    #!/usr/bin/env bash
    set -euo pipefail
    env_file="core/pipelines/{{pipeline}}/.env"
    [ -f "$env_file" ] || env_file="migrations/{{pipeline}}/.env"
    DB_HOST=$(grep '^DB_HOST=' "$env_file" | cut -d= -f2-)
    DB_PORT=$(grep '^DB_PORT=' "$env_file" | cut -d= -f2-)
    DB_NAME=$(grep '^DB_NAME=' "$env_file" | cut -d= -f2-)
    DB_USER=$(grep '^DB_USER=' "$env_file" | cut -d= -f2-)
    DB_PASSWORD=$(grep '^DB_PASSWORD=' "$env_file" | cut -d= -f2-)
    run_psql() {
      if command -v psql >/dev/null 2>&1; then
        PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$@"
      elif docker ps --filter name='^/postgres-dev$' --quiet | grep -q .; then
        docker exec -e PGPASSWORD="$DB_PASSWORD" postgres-dev psql -h 127.0.0.1 -p 5432 -U "$DB_USER" "$@"
      elif docker compose ps postgres --status running --quiet | grep -q .; then
        docker compose exec -T -e PGPASSWORD="$DB_PASSWORD" postgres psql -h 127.0.0.1 -p 5432 -U "$DB_USER" "$@"
      else
        echo "No PostgreSQL client available. Install psql or start postgres-dev with: just build-dev"
        exit 127
      fi
    }
    exists=$(run_psql -d postgres -tc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" | tr -d '[:space:]')
    if [ "$exists" = "1" ]; then
        echo "Already exists: $DB_NAME"
    else
        run_psql -d postgres -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
        echo "Created: $DB_NAME"
    fi

[group('setup')]
[doc("Inicializar .env de un pipeline desde su .env.example")]
env-init pipeline:
    #!/usr/bin/env bash
    set -euo pipefail
    if [ -f core/pipelines/{{pipeline}}/.env.example ]; then
        dir="core/pipelines/{{pipeline}}"
    elif [ -f migrations/{{pipeline}}/.env.example ]; then
        dir="migrations/{{pipeline}}"
    else
        echo "No .env.example found for '{{pipeline}}'"
        exit 1
    fi
    if [ -f "$dir/.env" ]; then
        echo "Already exists: $dir/.env"
    else
        cp "$dir/.env.example" "$dir/.env"
        echo "Created: $dir/.env"
    fi

[group('setup')]
[doc("Inicializar .env de todos los pipelines desde sus .env.example")]
env-init-all:
    #!/usr/bin/env bash
    set -euo pipefail
    for example in core/pipelines/*/.env.example migrations/*/.env.example; do
        dir=$(dirname "$example")
        if [ -f "$dir/.env" ]; then
            echo "Skipped (exists): $dir/.env"
        else
            cp "$example" "$dir/.env"
            echo "Created: $dir/.env"
        fi
    done

[group('setup')]
[doc("Verificar que todos los .env están completos (sin placeholders ni variables faltantes)")]
env-diff:
    #!/usr/bin/env bash
    set -euo pipefail
    issues=0
    for example in core/pipelines/*/.env.example migrations/*/.env.example; do
        dir=$(dirname "$example")
        pipeline=$(basename "$dir")
        env_file="$dir/.env"
        if [ ! -f "$env_file" ]; then
            echo "$pipeline: .env missing"
            issues=$((issues + 1))
            continue
        fi
        missing=() unfilled=()
        while IFS= read -r line; do
            [[ "$line" =~ ^#.*$ || -z "$line" ]] && continue
            var=$(echo "$line" | cut -d= -f1)
            val=$(echo "$line" | cut -d= -f2-)
            if ! grep -q "^${var}=" "$env_file"; then
                missing+=("$var")
            else
                actual=$(grep "^${var}=" "$env_file" | cut -d= -f2-)
                [[ "$actual" =~ ^\<.*\>$ ]] && unfilled+=("${var}=${actual}")
            fi
        done < "$example"
        if [ ${#missing[@]} -gt 0 ] || [ ${#unfilled[@]} -gt 0 ]; then
            echo "$pipeline:"
            for m in "${missing[@]+"${missing[@]}"}"; do echo "  missing: $m"; done
            for u in "${unfilled[@]+"${unfilled[@]}"}"; do echo "  unfilled: $u"; done
            issues=$((issues + 1))
        fi
    done
    if [ "$issues" -eq 0 ]; then echo "All passed"; fi

[group('airflow')]
[doc("Mostrar el calendario de DAGs ordenado por instante de disparo")]
schedules days="90":
    #!/usr/bin/env bash
    set -euo pipefail
    PYTHONPATH=. AIRFLOW_HOME=$(pwd) python3 scripts/schedules.py {{days}}

[group('airflow')]
[doc("Provisionar los pools de Airflow desde core/constants/concurrency.py (idempotente)")]
airflow-pools:
    #!/usr/bin/env bash
    set -euo pipefail
    PYTHONPATH=. python3 -c 'import json; from core.constants.concurrency import POOLS; json.dump(POOLS, open("config/airflow_pools.json", "w"), indent=2)'
    echo "Generated: config/airflow_pools.json"
    for _ in $(seq 1 30); do
        if docker compose exec -T airflow-scheduler airflow version >/dev/null 2>&1; then
            docker compose exec -T airflow-scheduler airflow pools import /opt/airflow/config/airflow_pools.json
            docker compose exec -T airflow-scheduler airflow pools list
            exit 0
        fi
        sleep 5
    done
    echo "airflow-scheduler no respondió en 150s. Ejecutar 'just airflow-pools' cuando esté arriba."
    exit 1

[group('flyway')]
[doc("Generar flyway.conf desde flyway.conf.example usando variables del .env")]
flyway-config pipeline: (_load-env pipeline)
    #!/usr/bin/env bash
    set -euo pipefail
    env_file="core/pipelines/{{pipeline}}/.env"
    [ -f "$env_file" ] || env_file="migrations/{{pipeline}}/.env"
    DEFAULT_FDW_PORT=5432
    read_env_var() {
        grep "^$2=" "$1" 2>/dev/null | head -1 | cut -d= -f2- || true
    }
    DB_HOST=$(grep '^DB_HOST=' "$env_file" | cut -d= -f2-)
    DB_PORT=$(grep '^DB_PORT=' "$env_file" | cut -d= -f2-)
    DB_NAME=$(grep '^DB_NAME=' "$env_file" | cut -d= -f2-)
    DB_USER=$(grep '^DB_USER=' "$env_file" | cut -d= -f2-)
    DB_PASSWORD=$(grep '^DB_PASSWORD=' "$env_file" | cut -d= -f2-)
    sed_args=(
      -e "s|<DB_HOST>|$DB_HOST|g"
      -e "s|<DB_PORT>|$DB_PORT|g"
      -e "s|<DB_NAME>|$DB_NAME|g"
      -e "s|<DB_USER>|$DB_USER|g"
      -e "s|<DB_PASSWORD>|$DB_PASSWORD|g"
    )
    # La conexion FDW primaria (cvegeo) usa placeholders genericos <FDW_DB_*>
    # y se resuelve desde migrations/cvegeo/.env, igual que el host.
    if [ -f migrations/cvegeo/.env ]; then
        FDW_DB_NAME=$(grep '^DB_NAME=' migrations/cvegeo/.env | cut -d= -f2-)
        FDW_DB_HOST=$(grep '^DB_HOST=' migrations/cvegeo/.env | cut -d= -f2-)
        FDW_DB_PORT=$(read_env_var migrations/cvegeo/.env DB_PORT)
        FDW_DB_USER=$(grep '^DB_USER=' migrations/cvegeo/.env | cut -d= -f2-)
        FDW_DB_PASSWORD=$(grep '^DB_PASSWORD=' migrations/cvegeo/.env | cut -d= -f2-)
        sed_args+=(
          -e "s|<FDW_DB_NAME>|$FDW_DB_NAME|g"
          -e "s|<FDW_DB_HOST>|$FDW_DB_HOST|g"
          -e "s|<FDW_DB_PORT>|${FDW_DB_PORT:-$DEFAULT_FDW_PORT}|g"
          -e "s|<FDW_DB_USER>|$FDW_DB_USER|g"
          -e "s|<FDW_DB_PASSWORD>|$FDW_DB_PASSWORD|g"
        )
    fi
    # Cada conexion FDW extra referencia <FDW_<DB>_DBNAME> etc. en el .example,
    # con <DB> el nombre de la base real (CVEGEO, CONAPO, INPC...). Se resuelve
    # cada una leyendo el .env del pipeline homonimo, igual que el pipeline actual.
    fdw_dbs=$(grep -oE '<FDW_[A-Z0-9_]+_DBNAME>' migrations/{{pipeline}}/flyway.conf.example | sed -E 's/<FDW_(.*)_DBNAME>/\1/' | sort -u || true)
    for db in $fdw_dbs; do
        db_lower=$(echo "$db" | tr '[:upper:]' '[:lower:]')
        fdw_env="core/pipelines/$db_lower/.env"
        [ -f "$fdw_env" ] || fdw_env="migrations/$db_lower/.env"
        FDW_NAME="" FDW_HOST="" FDW_PORT="" FDW_USER="" FDW_PASSWORD=""
        if [ -f "$fdw_env" ]; then
            FDW_NAME=$(grep '^DB_NAME=' "$fdw_env" | cut -d= -f2-)
            FDW_HOST=$(grep '^DB_HOST=' "$fdw_env" | cut -d= -f2-)
            FDW_PORT=$(read_env_var "$fdw_env" DB_PORT)
            FDW_USER=$(grep '^DB_USER=' "$fdw_env" | cut -d= -f2-)
            FDW_PASSWORD=$(grep '^DB_PASSWORD=' "$fdw_env" | cut -d= -f2-)
        else
            echo "Aviso: no se encontro .env para la DB FDW '$db_lower' (pipeline {{pipeline}}); <FDW_${db}_*> quedara vacio"
        fi
        sed_args+=(
          -e "s|<FDW_${db}_DBNAME>|$FDW_NAME|g"
          -e "s|<FDW_${db}_HOST>|$FDW_HOST|g"
          -e "s|<FDW_${db}_PORT>|${FDW_PORT:-$DEFAULT_FDW_PORT}|g"
          -e "s|<FDW_${db}_USER>|$FDW_USER|g"
          -e "s|<FDW_${db}_PASSWORD>|$FDW_PASSWORD|g"
        )
    done
    sed "${sed_args[@]}" migrations/{{pipeline}}/flyway.conf.example > migrations/{{pipeline}}/flyway.conf
    echo "Generated: migrations/{{pipeline}}/flyway.conf"

[group('flyway')]
[doc("Generar flyway.conf para todos los pipelines")]
flyway-config-all:
    #!/usr/bin/env bash
    set -euo pipefail
    for conf in migrations/*/flyway.conf.example; do
        pipeline=$(basename "$(dirname "$conf")")
        if [ -f "migrations/$pipeline/.env" ] || [ -f "core/pipelines/$pipeline/.env" ]; then
            just flyway-config "$pipeline"
        else
            echo "Skipped (no .env): $pipeline"
        fi
    done

[group('flyway')]
[doc("Aplicar migraciones pendientes de un pipeline")]
flyway-migrate pipeline:
    flyway -configFiles=migrations/{{pipeline}}/flyway.conf migrate

[group('flyway')]
[doc("Aplicar migraciones pendientes de todos los pipelines")]
flyway-migrate-all:
    #!/usr/bin/env bash
    set -euo pipefail
    for conf in migrations/*/flyway.conf; do
        pipeline=$(basename "$(dirname "$conf")")
        just flyway-migrate "$pipeline"
    done

[group('flyway')]
[doc("Limpiar el schema de un pipeline (destructivo)")]
[confirm("¿Eliminar todas las tablas del schema? [Y/N]:")]
flyway-clean pipeline:
    flyway -configFiles=migrations/{{pipeline}}/flyway.conf clean

[group('flyway')]
[doc("Limpiar y re-aplicar migraciones de un pipeline (destructivo)")]
[confirm("¿Eliminar todas las tablas y re-aplicar las migraciones? [Y/N]:")]
flyway-reset pipeline:
    flyway -configFiles=migrations/{{pipeline}}/flyway.conf clean
    flyway -configFiles=migrations/{{pipeline}}/flyway.conf migrate

[group('flyway')]
[doc("Ver estado de las migraciones de un pipeline")]
flyway-info pipeline:
    flyway -configFiles=migrations/{{pipeline}}/flyway.conf info

[group('flyway')]
[doc("Validar las migraciones de un pipeline")]
flyway-validate pipeline:
    flyway -configFiles=migrations/{{pipeline}}/flyway.conf validate

[group('flyway')]
[doc("Reparar checksums en el historial de migraciones")]
flyway-repair pipeline:
    flyway -configFiles=migrations/{{pipeline}}/flyway.conf repair

[group('deploy')]
[doc("Deploy completo: env-init → flyway-config → create-db → flyway-migrate")]
pipeline-deploy pipeline:
    just env-init {{pipeline}}
    just flyway-config {{pipeline}}
    just create-db {{pipeline}}
    just flyway-migrate {{pipeline}}

[group('database')]
[doc("Dump comprimido de la base de datos de un pipeline")]
db-dump pipeline: (_load-env pipeline)
    #!/usr/bin/env bash
    set -euo pipefail
    env_file="core/pipelines/{{pipeline}}/.env"
    [ -f "$env_file" ] || env_file="migrations/{{pipeline}}/.env"
    DB_HOST=$(grep '^DB_HOST=' "$env_file" | cut -d= -f2-)
    DB_PORT=$(grep '^DB_PORT=' "$env_file" | cut -d= -f2-)
    DB_NAME=$(grep '^DB_NAME=' "$env_file" | cut -d= -f2-)
    DB_USER=$(grep '^DB_USER=' "$env_file" | cut -d= -f2-)
    DB_PASSWORD=$(grep '^DB_PASSWORD=' "$env_file" | cut -d= -f2-)
    mkdir -p dumps/{{pipeline}}
    ts=$(date +%Y%m%d_%H%M%S)
    filename="${DB_NAME}_${ts}.dump"
    echo "Dumping ${DB_NAME} (${DB_HOST}:${DB_PORT}) ..."
    docker run --rm --network host \
      -e PGPASSWORD="$DB_PASSWORD" \
      -v "$(pwd)/dumps/{{pipeline}}:/dumps" \
      postgis/postgis:17-3.5 \
      pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" \
      -Fc --no-owner --no-acl --verbose \
      -f "/dumps/${filename}" "$DB_NAME"
    size=$(du -sh "dumps/{{pipeline}}/${filename}" | cut -f1)
    echo "Saved: dumps/{{pipeline}}/${filename} (${size})"

[group('database')]
[doc("Dump comprimido de todos los pipelines con DB activa")]
db-dump-all:
    #!/usr/bin/env bash
    set -euo pipefail
    for pipeline_dir in core/pipelines/*/; do
        pipeline=$(basename "$pipeline_dir")
        [[ "$pipeline" == __* ]] && continue
        env_file=""
        [ -f "core/pipelines/$pipeline/.env" ] && env_file="core/pipelines/$pipeline/.env"
        [ -z "$env_file" ] && [ -f "migrations/$pipeline/.env" ] && env_file="migrations/$pipeline/.env"
        if [ -z "$env_file" ]; then
            echo "Skipped (no .env): $pipeline"
            continue
        fi
        if grep -q '<' "$env_file"; then
            echo "Skipped (unset): $pipeline"
            continue
        fi
        just db-dump "$pipeline"
    done

[group('database')]
[doc("Listar contenido de un dump (sin restaurar)")]
db-list dump:
    docker run --rm \
      -v "$(pwd):/project" \
      postgis/postgis:17-3.5 \
      pg_restore --list /project/{{dump}}

[group('database')]
[doc("Restaurar un dump comprimido en la base de datos de un pipeline")]
[confirm("Esto ejecuta pg_restore con --clean --if-exists y SOBRESCRIBE los objetos existentes en la base destino. ¿Continuar? (y/N)")]
db-restore pipeline dump: (_load-env pipeline) (create-db pipeline)
    #!/usr/bin/env bash
    set -euo pipefail
    env_file="core/pipelines/{{pipeline}}/.env"
    [ -f "$env_file" ] || env_file="migrations/{{pipeline}}/.env"
    DB_HOST=$(grep '^DB_HOST=' "$env_file" | cut -d= -f2-)
    DB_PORT=$(grep '^DB_PORT=' "$env_file" | cut -d= -f2-)
    DB_NAME=$(grep '^DB_NAME=' "$env_file" | cut -d= -f2-)
    DB_USER=$(grep '^DB_USER=' "$env_file" | cut -d= -f2-)
    DB_PASSWORD=$(grep '^DB_PASSWORD=' "$env_file" | cut -d= -f2-)
    [ -f "{{dump}}" ] || { echo "Dump not found: {{dump}}"; exit 1; }
    echo "Restoring {{dump}} into ${DB_NAME} (${DB_HOST}:${DB_PORT}) ..."
    docker run --rm --network host \
      -e PGPASSWORD="$DB_PASSWORD" \
      -v "$(pwd)/{{dump}}:/restore.dump:ro" \
      postgis/postgis:17-3.5 \
      pg_restore -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" \
      -d "$DB_NAME" --no-owner --no-acl --clean --if-exists --verbose \
      /restore.dump
    echo "Restored: ${DB_NAME}"

[group('database')]
[doc("Resumen de estado de todos los pipelines (env, db, datos)")]
summary:
    #!/usr/bin/env bash
    set -euo pipefail
    printf "%-28s  %-4s  %-4s  %s\n" "pipeline" "env" "db" "size"
    printf '%0.s─' {1..52}; echo
    total=0 with_env=0 with_db=0
    for pipeline_dir in core/pipelines/*/; do
        pipeline=$(basename "$pipeline_dir")
        [[ "$pipeline" == __* ]] && continue
        total=$((total + 1))
        env_file=""
        [ -f "core/pipelines/$pipeline/.env" ] && env_file="core/pipelines/$pipeline/.env"
        [ -z "$env_file" ] && [ -f "migrations/$pipeline/.env" ] && env_file="migrations/$pipeline/.env"
        if [ -z "$env_file" ]; then
            printf "%-28s  %-4s  %-4s  %s\n" "$pipeline" "no" "-" "-"
            continue
        fi
        DB_HOST=$(grep '^DB_HOST=' "$env_file" | cut -d= -f2-)
        DB_PORT=$(grep '^DB_PORT=' "$env_file" | cut -d= -f2-)
        DB_NAME=$(grep '^DB_NAME=' "$env_file" | cut -d= -f2-)
        DB_USER=$(grep '^DB_USER=' "$env_file" | cut -d= -f2-)
        DB_PASSWORD=$(grep '^DB_PASSWORD=' "$env_file" | cut -d= -f2-)
        if echo "$DB_HOST$DB_PORT$DB_NAME$DB_USER$DB_PASSWORD" | grep -q '<'; then
            printf "%-28s  %-4s  %-4s  %s\n" "$pipeline" "unset" "-" "-"
            continue
        fi
        with_env=$((with_env + 1))
        db_exists=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres \
          -tc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" 2>/dev/null | tr -d '[:space:]') || true
        if [ "$db_exists" != "1" ]; then
            printf "%-28s  %-4s  %-4s  %s\n" "$pipeline" "yes" "no" "-"
            continue
        fi
        with_db=$((with_db + 1))
        size=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
          -tc "SELECT COALESCE(pg_size_pretty(SUM(pg_total_relation_size(schemaname||'.'||tablename))), '0 bytes') \
               FROM pg_tables WHERE schemaname = 'public';" 2>/dev/null | xargs) || true
        printf "%-28s  %-4s  %-4s  %s\n" "$pipeline" "yes" "yes" "$size"
    done
    printf '%0.s─' {1..52}; echo
    printf "total: %s  |  env: %s  |  db: %s\n" "$total" "$with_env" "$with_db"

[private]
_load-env pipeline:
    @test -f core/pipelines/{{pipeline}}/.env \
      || test -f migrations/{{pipeline}}/.env \
      || (echo "Missing .env for '{{pipeline}}' — copy from .env.example" && exit 1)
