levanta la base de datos del pipeline actual que se está trabajando.

## pasos

### 1. Verificar si la base de datos  postgres-dev está activa.

Si está activa, pasar directamente al paso 2.

1.1  Si no está activa usar `just build-dev` para levantar la base de datos.

1.2  Crear la base de datos de cvegeo: `just create-cvegeo-db`.

### 2. Hacer la migración de la base de datos

Ejecutar `flyway-migrate {pipeline}` donde pipeline es el nombre del pipeline

### 3. Ingesta de datos

Ejectutar `python dags/etl_{pipeline}.py` para ingestar los datos en la base de datos.
