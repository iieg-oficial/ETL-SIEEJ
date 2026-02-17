default:
    just --list --unsorted

# Docker Compose: levantar servicios
up:
    docker compose up --build -d

# Docker Compose: detener servicios
down:
    docker compose down

# Docker Compose: detener servicios y eliminar volúmenes
down-volumes:
    docker compose down -v

# Docker Compose: rebuild de un servicio específico
rebuild service:
    docker compose up --build -d {{service}}

# Docker Compose: ver logs
logs service="":
    docker compose logs -f {{service}}

# Docker Compose: ver estado de los servicios
ps:
    docker compose ps

# Docker Compose: reiniciar un servicio
restart service:
    docker compose restart {{service}}

# Docker: contenedor PostGIS para desarrollo
build-dev user="test" pass="test" db="test" port="5432":
    docker run --name postgres-dev \
      -e POSTGRES_USER={{user}} \
      -e POSTGRES_PASSWORD={{pass}} \
      -e POSTGRES_DB={{db}} \
      -p {{port}}:5432 \
      -d postgis/postgis:17-3.5

# Crear base de datos cvegeo en el contenedor de desarrollo
create-cvegeo-db:
    docker exec postgres-dev psql -U test -c "CREATE DATABASE cvegeo;"

# Flyway migrate
flyway-migrate pipeline:
    flyway -configFiles=migrations/{{pipeline}}/flyway.conf migrate


# Flyway clean
flyway-clean pipeline:
    flyway -configFiles=migrations/{{pipeline}}/flyway.conf clean

# Flyway clean + migrate
flyway-reset pipeline:
    flyway -configFiles=migrations/{{pipeline}}/flyway.conf clean
    flyway -configFiles=migrations/{{pipeline}}/flyway.conf migrate

# Flyway info
flyway-info pipeline:
    flyway -configFiles=migrations/{{pipeline}}/flyway.conf info

# Flyway validate
flyway-validate pipeline:
    flyway -configFiles=migrations/{{pipeline}}/flyway.conf validate
