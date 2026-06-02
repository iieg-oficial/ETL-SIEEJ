# Escuelas

> Pipeline ETL para cargar el directorio de escuelas y la estadística agregada de escuelas de Jalisco desde archivos CSV almacenados en Google Drive.

---

## Fuente

| Campo | Valor |
|-------|-------|
| Proveedor | Carpeta compartida de Google Drive |
| URL | Configurada por `GDRIVE_FOLDER_ID` |
| Formato | CSV |
| Frecuencia | On-demand |
| Último dato | `SOURCE_YEAR=2026` |

---

## Esquema de Base de Datos

El diagrama ER no está versionado todavía para este pipeline.

### Tablas catálogo

| Tabla | Descripción |
|-------|-------------|
| `cat_turnos` | Turnos escolares del directorio. |
| `cat_sostenimientos` | Sostenimientos normalizados del directorio y estadística. |
| `cat_codigos_sostenimiento` | Códigos de sostenimiento del directorio vinculados al catálogo de sostenimientos. |
| `cat_niveles` | Niveles educativos del directorio. |
| `cat_programas` | Programas o servicios educativos del directorio. |
| `cat_regiones` | Regiones educativas del directorio. |
| `cat_medios` | Clasificación urbana/rural del centro educativo. |
| `cat_niveles_programa` | Nivel/programa usado en la estadística agregada. |

### Tablas principales

| Tabla | Descripción |
|-------|-------------|
| `stg_directorio_escuelas` | Directorio por centro de trabajo, turno, nivel y programa, con ubicación, contacto y métricas de matrícula/docentes. |
| `stg_estadistica_escuelas` | Estadística agregada por año, nivel/programa y sostenimiento. |

### Vistas de integración

| Vista | Descripción |
|-------|-------------|
| `v_directorio_escuelas` | Desnormalización de `stg_directorio_escuelas` con catálogos y referencias a `cve_geo`. |
| `v_estadistica_escuelas` | Desnormalización de `stg_estadistica_escuelas` con catálogos de nivel/programa y sostenimiento. |

---

## Implementación ETL

| Modo | Implementado | Tipo |
|------|:------------:|------|
| Bootstrap | ✅ | Carga completa on-demand |
| Update | ❌ | No implementado en v1 |

---

## Diagrama de archivos

```
core/pipelines/escuelas/
├── config.py
├── constants.py
├── schemas.py
├── .env.example
├── README.md
├── eda/
│   ├── eda_escuelas.py
│   └── reporte_eda.json
├── stages/
│   ├── extract.py
│   ├── transform.py
│   └── load.py
├── helpers/
│   └── values.py
└── assets/

dags/
└── etl_escuelas.py

migrations/escuelas/sql/
├── V1__foreign_tables.sql
├── V2__catalogs_escuelas.sql
├── V3__tables_escuelas.sql
└── V4__views_escuelas.sql
```

---

## Metodología ETL

### Extract

Descarga los archivos `directorio_escuelas.csv` y `estadistica_escuelas.csv` desde una carpeta de Google Drive usando cuenta de servicio. La carpeta se configura con `GDRIVE_FOLDER_ID`; las credenciales se configuran con `GDRIVE_CLIENT_EMAIL` y `GDRIVE_PRIVATE_KEY`.

### Transform

Normaliza encabezados a `snake_case`, limpia valores nulos textuales, convierte tipos numéricos, conserva los datos de contacto del directorio y transforma ceros de campos opcionales de contacto/ubicación a `NULL`. También construye los catálogos dinámicos de turnos, sostenimientos, niveles, programas, regiones, medios y nivel/programa estadístico.

### Load

Inserta catálogos con `insert_records`, resuelve claves foráneas en memoria y recarga las tablas staging para el `SOURCE_YEAR` configurado. La carga usa `bulk_insert` para `stg_directorio_escuelas` y `stg_estadistica_escuelas`; no implementa SCD en v1.

---

## Variables de entorno

Definidas en `.env.example`. Crear `.env` local con los valores reales y no commitearlo.

| Variable | Descripción |
|----------|-------------|
| `LOG_LEVEL` | Nivel de logging del pipeline. |
| `DB_USER` | Usuario de PostgreSQL. |
| `DB_PASSWORD` | Password de PostgreSQL. |
| `DB_HOST` | Host de PostgreSQL. |
| `DB_PORT` | Puerto de PostgreSQL. |
| `DB_NAME` | Base de datos destino. |
| `SOURCE_YEAR` | Año asignado a la carga. |
| `DIRECTORIO_FILENAME` | Nombre esperado del CSV de directorio. |
| `ESTADISTICA_FILENAME` | Nombre esperado del CSV de estadística agregada. |
| `GDRIVE_FOLDER_ID` | ID de la carpeta de Google Drive. |
| `GDRIVE_CLIENT_EMAIL` | Email de la cuenta de servicio. |
| `GDRIVE_PRIVATE_KEY` | Llave privada de la cuenta de servicio. |

---

## Pasos manuales requeridos

1. Compartir la carpeta de Google Drive con la cuenta de servicio configurada.
2. Crear `core/pipelines/escuelas/.env` desde `.env.example` y completar las variables de base de datos y Google Drive.
3. Ejecutar `just flyway-config escuelas`.
4. Ejecutar `just create-db escuelas` si la base aún no existe.
5. Ejecutar `just flyway-migrate escuelas`.
6. Ejecutar `conda run -n etl python dags/etl_escuelas.py` para correr el bootstrap local.
