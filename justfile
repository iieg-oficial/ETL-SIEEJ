default:
    just --list --unsorted


# Docker Compose: levantar servicios
[group('docker')]
up:
    docker compose up --build -d

# Docker Compose: detener servicios
[group('docker')]
down:
    docker compose down

# Docker Compose: detener servicios y eliminar volúmenes
[group('docker')]
down-volumes:
    docker compose down -v

# Docker Compose: rebuild de un servicio específico
[group('docker')]
rebuild service:
    docker compose up --build -d {{service}}

# Docker Compose: ver logs
[group('docker')]
logs service="":
    docker compose logs -f {{service}}

# Docker Compose: ver estado de los servicios
[group('docker')]
ps:
    docker compose ps

# Docker Compose: reiniciar un servicio
[group('docker')]
restart service:
    docker compose restart {{service}}

# Setup: instalar pre-commit hooks
[group('development')]
setup:
    pre-commit install
    pre-commit install --hook-type commit-msg

# Docker: contenedor PostGIS para desarrollo
[group('development')]
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

# Docker: detener y eliminar el contenedor de desarrollo
[group('development')]
stop-dev:
    docker stop postgres-dev && docker rm postgres-dev

# Crear base de datos cvegeo
[group('development')]
[arg("host", long)]
[arg("port", long)]
[arg("user", long)]
[arg("database", long)]
[arg("pass", long)]
create-cvegeo-db host="localhost" port="5432" user="test" database="test" pass="test":
    PGPASSWORD={{pass}} psql -h {{host}} -p {{port}} -U {{user}} -d {{database}} -c "CREATE DATABASE cvegeo;"

# Flyway: copiar flyway.conf.example a flyway.conf
[group('flyway')]
flyway-config pipeline:
    cp migrations/{{pipeline}}/flyway.conf.example migrations/{{pipeline}}/flyway.conf

# Flyway migrate
[group('flyway')]
flyway-migrate pipeline:
    flyway -configFiles=migrations/{{pipeline}}/flyway.conf migrate

# Flyway clean
[group('flyway')]
flyway-clean pipeline:
    flyway -configFiles=migrations/{{pipeline}}/flyway.conf clean

# Flyway clean + migrate
[group('flyway')]
flyway-reset pipeline:
    flyway -configFiles=migrations/{{pipeline}}/flyway.conf clean
    flyway -configFiles=migrations/{{pipeline}}/flyway.conf migrate

# Flyway info
[group('flyway')]
flyway-info pipeline:
    flyway -configFiles=migrations/{{pipeline}}/flyway.conf info

# Flyway validate
[group('flyway')]
flyway-validate pipeline:
    flyway -configFiles=migrations/{{pipeline}}/flyway.conf validate
