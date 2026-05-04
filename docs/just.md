<div align="center">

# Guía de just - ETL SIEEJ
<img src="https://img.shields.io/badge/IIEG-Jalisco-5C2D91?style=for-the-badge" alt="IIEG"/>
<img src="https://img.shields.io/badge/just-1D1D1D?style=for-the-badge&logoColor=white" alt="just"/>

</div>

### Automatización de tareas del proyecto


---

## Índice

- [¿Qué es just?](#qué-es-just)
- [Instalación](#instalación)
- [Ver comandos disponibles](#ver-comandos-disponibles)
- [Comandos Docker](#comandos-docker)
- [Comandos de desarrollo](#comandos-de-desarrollo)
- [Comandos de configuración](#comandos-de-configuración)
- [Comandos de base de datos](#comandos-de-base-de-datos)
- [Comandos Flyway](#comandos-flyway)
- [Comandos de deploy](#comandos-de-deploy)

---

## ¿Qué es just?

**just** es un ejecutor de comandos (similar a `make`) que permite definir recetas reutilizables en un archivo `justfile`. En este proyecto se usa para simplificar operaciones frecuentes de Docker, Flyway y deploy sin tener que recordar flags largos.

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
  [docker]
    up                    # Levantar servicios
    down                  # Detener servicios
    down-volumes          # Detener servicios y eliminar volúmenes
    rebuild service       # Rebuild de un servicio específico
    logs service=""       # Ver logs de un servicio
    ps                    # Ver estado de los servicios
    restart service       # Reiniciar un servicio

  [development]
    setup                 # Instalar pre-commit hooks y dependencias
    build-dev ...         # Levantar contenedor PostGIS para desarrollo
    stop-dev              # Detener y eliminar el contenedor de desarrollo
    data-clean pipeline   # Eliminar archivos temporales de extract y transform de un pipeline

  [setup]
    env-init pipeline     # Inicializar .env de un pipeline desde su .env.example
    env-init-all          # Inicializar .env de todos los pipelines desde sus .env.example
    env-diff              # Verificar que todos los .env están completos

  [database]
    create-db pipeline    # Crear base de datos de un pipeline leyendo credenciales de su .env

  [flyway]
    flyway-config pipeline       # Generar flyway.conf desde flyway.conf.example
    flyway-config-all            # Generar flyway.conf para todos los pipelines
    flyway-migrate pipeline      # Aplicar migraciones pendientes de un pipeline
    flyway-migrate-all           # Aplicar migraciones pendientes de todos los pipelines
    flyway-clean pipeline        # Limpiar el schema de un pipeline (destructivo)
    flyway-reset pipeline        # Limpiar y re-aplicar migraciones (destructivo)
    flyway-info pipeline         # Ver estado de las migraciones de un pipeline
    flyway-validate pipeline     # Validar las migraciones de un pipeline
    flyway-repair pipeline       # Reparar checksums en el historial de migraciones

  [deploy]
    pipeline-deploy pipeline     # Deploy completo: env-init → flyway-config → create-db → flyway-migrate
```

---

## Comandos Docker

| Comando | Descripción |
| :--- | :--- |
| `just up` | Levanta todos los servicios (`docker compose up --build -d`) |
| `just down` | Detiene todos los servicios |
| `just down-volumes` | Detiene servicios y elimina volúmenes |
| `just ps` | Muestra el estado de los servicios |
| `just logs [servicio]` | Muestra los logs (sin argumento muestra todos) |
| `just restart <servicio>` | Reinicia un servicio específico |
| `just rebuild <servicio>` | Reconstruye y levanta un servicio específico |

> ⚠️ `down`, `down-volumes` y `restart` piden confirmación antes de ejecutarse.

```bash
just up
just logs airflow-webserver
just restart airflow-scheduler
just down
```

---

## Comandos de desarrollo

### setup

Instala dependencias y configura los pre-commit hooks.

```bash
just setup
```

### build-dev

Levanta un contenedor PostgreSQL/PostGIS standalone para desarrollo local, sin depender del stack de producción.

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

### stop-dev

Detiene y elimina el contenedor `postgres-dev`.

```bash
just stop-dev
```

### data-clean

Elimina los archivos temporales de `data/extract/<pipeline>` y `data/transform/<pipeline>`. Pide confirmación antes de ejecutarse.

```bash
just data-clean censos_economicos
```

---

## Comandos de configuración

### env-init

Copia el `.env.example` de un pipeline a `.env`. Si ya existe, lo omite.

```bash
just env-init censos_economicos
```

### env-init-all

Inicializa el `.env` de todos los pipelines de una sola vez.

```bash
just env-init-all
```

### env-diff

Verifica que todos los `.env` estén completos: detecta variables faltantes y placeholders sin llenar (`<valor>`).

```bash
just env-diff
```

```
censos_economicos:
  unfilled: DB_PASSWORD=<DB_PASSWORD>
fiscalia:
  missing: API_KEY
All passed   ← si no hay problemas
```

---

## Comandos de base de datos

### create-db

Crea la base de datos del pipeline leyendo las credenciales de su `.env`. Es idempotente: si la base de datos ya existe, lo indica y continúa sin error.

```bash
just create-db censos_economicos
```

---

## Comandos Flyway

Todos los comandos reciben el nombre del pipeline como argumento. Para más detalle sobre migraciones consulta la [Guía de Flyway](flyway.md).

#### flyway-config. Configurar Flyway para un pipeline

```bash
just flyway-config censos_economicos
```

Genera `flyway.conf` en la carpeta del pipeline a partir de `flyway.conf.example`, sustituyendo las variables del `.env`. Ejecutar una vez antes de correr migraciones por primera vez.

#### flyway-config-all. Configurar Flyway para todos los pipelines

```bash
just flyway-config-all
```

Ejecuta `flyway-config` para cada pipeline que tenga un `.env` disponible.

#### flyway-migrate. Aplicar migraciones pendientes

```bash
just flyway-migrate censos_economicos
```

Aplica todos los scripts `V*.sql` que aún no se hayan ejecutado, en orden numérico. Es el comando principal del flujo de trabajo.

#### flyway-migrate-all. Migrar todos los pipelines

```bash
just flyway-migrate-all
```

Ejecuta `flyway-migrate` para cada pipeline que tenga un `flyway.conf` generado.

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

#### flyway-repair. Reparar checksums

```bash
just flyway-repair censos_economicos
```

Sincroniza los checksums del historial de Flyway con el estado actual de los scripts SQL. Usar cuando `flyway-validate` reporta un mismatch tras modificar un script ya aplicado.

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

## Comandos de deploy

### pipeline-deploy

Deploy completo de un pipeline en un solo comando: inicializa el `.env`, genera el `flyway.conf`, crea la base de datos y aplica las migraciones.

```bash
just pipeline-deploy censos_economicos
```

Equivale a ejecutar en secuencia:

```bash
just env-init censos_economicos
just flyway-config censos_economicos
just create-db censos_economicos
just flyway-migrate censos_economicos
```

---

<div align="center">

<sub>Guía de just - ETL SIEEJ - IIEG Jalisco</sub>

</div>
