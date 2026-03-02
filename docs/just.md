<div align="center">

# Guía de just - ETL SIEEJ
<img src="https://img.shields.io/badge/just-1D1D1D?style=for-the-badge&logoColor=white" alt="just"/>
</div>

### Automatización de tareas del proyecto


---

## Índice

- [¿Qué es just?](#qué-es-just)
- [Instalación](#instalación)
- [Ver comandos disponibles](#ver-comandos-disponibles)
- [Comandos Docker](#comandos-docker)
- [Comandos Flyway](#comandos-flyway)

---

## ¿Qué es just?

**just** es un ejecutor de comandos (similar a `make`) que permite definir recetas reutilizables en un archivo `justfile`. En este proyecto se usa para simplificar operaciones frecuentes de Docker y Flyway sin tener que recordar flags largos.

```bash
# En lugar de escribir esto:
flyway -configFiles=migrations/censos_economicos/flyway.conf migrate

# Solo escribes:
just flyway-migrate censos_economicos
```

---

## Instalación

### Linux

```bash
curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to ~/.local/bin
```

Asegúrate de que `~/.local/bin` esté en tu `PATH`:

```bash
echo 'export PATH=$PATH:$HOME/.local/bin' >> ~/.bashrc
source ~/.bashrc
```

### macOS

```bash
brew install just
```

### Windows

**Opción 1.  Scoop (recomendado):**

Si tienes Scoop instalado:

```powershell
scoop install just
```

**Opción 2.  Manual Installation:**

Si prefieres no usar un gestor de paquetes, puedes instalar manualmente el ejecutable prediseñado:

1. **Descargar:** Descargue el último ejecutable de Windows (just.exe) desde la página oficial de versiones de [GitHub](https://github.com/casey/just/releases).
2. **Extraer:** Descomprime el archivo descargado en una ubicación permanente en tu ordenador.
3. **Añadir a PATH:** Añade el directorio que contiene el archivo just.exe a la variable de entorno PATH de tu sistema. Esto le permite ejecutar just desde cualquier símbolo del sistema o ventana de PowerShell.

### Verificar instalación

```bash
just --version
```

---

## Ver comandos disponibles

Ejecuta `just` sin argumentos desde la raíz del proyecto para listar todos los comandos disponibles:

```bash
just
```

```
Available recipes:
    build-dev user="test" pass="test" db="test" port="5432"
    create-cvegeo-db host="localhost" port="5432" user="test"
    down
    down-volumes
    flyway-clean pipeline
    flyway-info pipeline
    flyway-migrate pipeline
    flyway-reset pipeline
    flyway-validate pipeline
    logs service=""
    ps
    rebuild service
    restart service
    up
```

---

## Comandos Docker

### Servicios principales

| Comando | Descripción |
| :--- | :--- |
| `just up` | Levanta todos los servicios (`docker compose up --build -d`) |
| `just down` | Detiene todos los servicios |
| `just down-volumes` | Detiene servicios y elimina volúmenes |
| `just ps` | Muestra el estado de los servicios |
| `just logs [servicio]` | Muestra los logs (sin argumento muestra todos) |
| `just restart <servicio>` | Reinicia un servicio específico |
| `just rebuild <servicio>` | Reconstruye y levanta un servicio específico |

```bash
just up
just logs airflow-webserver
just restart airflow-scheduler
just down
```

### Base de datos de desarrollo

`build-dev` levanta un contenedor PostgreSQL/PostGIS standalone para desarrollo local, sin depender del stack de producción.

```bash
# Valores por defecto: user=test, pass=test, db=test, port=5432
just build-dev

# Con valores personalizados
just build-dev user=sieej_user pass=mi_pass db=sieej
```

| Parámetro | Default | Descripción |
| :--- | :--- | :--- |
| `user` | `test` | Usuario de PostgreSQL |
| `pass` | `test` | Contraseña |
| `db` | `test` | Nombre de la base de datos |
| `port` | `5432` | Puerto expuesto en el host |

### create-cvegeo-db

Crea la base de datos `cvegeo` ejecutando `psql` contra el servidor indicado.

```bash
# Con valores por defecto (localhost:5432, user=test)
just create-cvegeo-db

# Apuntando a otro servidor
just create-cvegeo-db host=192.168.1.10 port=5433 user=sieej_user
```

| Parámetro | Default | Descripción |
| :--- | :--- | :--- |
| `host` | `localhost` | Host del servidor PostgreSQL |
| `port` | `5432` | Puerto del servidor |
| `user` | `test` | Usuario con permisos para crear bases de datos |

---

## Comandos Flyway

Todos los comandos reciben el nombre del pipeline como argumento. Los pipelines disponibles son: `censos_economicos`, `repd`, `fiscalia`, `cvegeo`. Para más detalle sobre migraciones consulta la [Guía de Flyway](flyway.md).

#### flyway-migrate. Aplicar migraciones pendientes

```bash
just flyway-migrate censos_economicos
```

Aplica todos los scripts `V*.sql` que aún no se hayan ejecutado, en orden numérico. Es el comando principal del flujo de trabajo.

#### flyway-info. Ver estado de migraciones

```bash
just flyway-info censos_economicos
```

Muestra una tabla con el estado de cada script: `Success`, `Pending` o `Failed`. Útil para saber en qué punto está el schema antes de migrar.

#### flyway-validate. Validar integridad de scripts

```bash
just flyway-validate censos_economicos
```

Verifica que los scripts ya aplicados no hayan sido modificados desde que se ejecutaron. Ejecutar antes de abrir un PR para garantizar consistencia.

#### flyway-clean. Eliminar todos los objetos

```bash
just flyway-clean censos_economicos
```

Elimina **todas** las tablas, vistas, funciones e índices del schema. Requiere `flyway.cleanDisabled=false` en `flyway.conf`.

> ⚠️ **Destructivo.** Solo usar en desarrollo local. Nunca en producción.

#### flyway-reset. Clean + Migrate

```bash
just flyway-reset censos_economicos
```

Ejecuta `clean` seguido de `migrate`: borra todo y reconstruye el schema desde cero. Útil para verificar que las migraciones son reproducibles.

> ⚠️ **Destructivo.** Solo usar en desarrollo local. Nunca en producción.

---

<div align="center">

<sub>Guía de just — ETL SIEEJ · IIEG Jalisco</sub>

</div>
