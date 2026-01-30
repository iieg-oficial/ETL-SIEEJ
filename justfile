default:
    just --list --unsorted

# Docker test-container
build-test user="test" pass="test" db="test" port="5432" version="17":
    docker run --name postgres-test \
      -e POSTGRES_USER={{user}} \
      -e POSTGRES_PASSWORD={{pass}} \
      -e POSTGRES_DB={{db}} \
      -p {{port}}:5432 \
      -d postgres:{{version}}
