# {Nombre del Pipeline}

> {Descripción breve en una oración: qué datos contiene, de qué fuente y para qué sirve.}

---

## Fuente

| Campo        | Valor                              |
|--------------|------------------------------------|
| Proveedor    | {nombre del organismo o sistema}   |
| URL          | {URL de descarga o N/A}            |
| Formato      | {CSV / XLSX / JSON / API / Otro}   |
| Frecuencia   | {mensual / anual / on-demand / …}  |
| Último dato  | {periodo o fecha del último dato}  |

---

## Esquema de Base de Datos

![Diagrama ER](assets/er_{flujo}.png)

### Tablas catálogo

| Tabla                  | Descripción                          |
|------------------------|--------------------------------------|
| `cat_{nombre}`         | {qué representa cada catálogo}       |

### Tabla principal

| Tabla          | Descripción                                          |
|----------------|------------------------------------------------------|
| `stg_{flujo}`  | Registro principal con claves foráneas a catálogos.  |

### Vista de integración

| Vista         | Descripción                                                  |
|---------------|--------------------------------------------------------------|
| `v_{flujo}`   | Desnormalización de `stg_{flujo}` con todos los catálogos.   |

---

## Implementación ETL

| Modo        | Implementado | Tipo              |
|-------------|:------------:|-------------------|
| Bootstrap   | ✅ / ❌       | Carga histórica completa |
| Update      | ✅ / ❌       | {solo-inserciones / SCD} |

---

## Diagrama de archivos

```
core/pipelines/{flujo}/
├── config.py
├── constants.py
├── schemas.py
├── .env.example
├── README.md  ← este archivo
├── eda/
│   ├── eda_{flujo}.py
│   └── reporte_eda.json
├── stages/
│   ├── extract.py
│   ├── transform.py
│   └── load.py
├── helpers/
└── assets/
    └── er_{flujo}.png

dags/
└── etl_{flujo}.py

migrations/{flujo}/sql/
├── V1__{flujo}__catalogos.sql
├── V2__{flujo}__geo.sql      (si aplica)
├── V3__{flujo}__tabla_principal.sql
└── V4__{flujo}__vista.sql
```

---

## Metodología ETL

### Extract
{Describir cómo se obtienen los datos: descarga directa, API, SFTP, archivo manual, etc. Indicar si requiere credenciales.}

### Transform
{Describir las transformaciones principales: limpieza de nulos, normalización de texto, homologación de catálogos, cálculo de hashes para SCD, etc.}

### Load
{Describir cómo se insertan los datos: insert_records, bulk_insert, upsert. Indicar si se usa SCD y cómo se gestiona la vigencia.}

---

## Variables de entorno

Definidas en `.env.example`. Crear `.env` local con los valores reales (no commitear).

| Variable              | Descripción                              |
|-----------------------|------------------------------------------|
| `{VARIABLE_1}`        | {descripción}                            |
| `{VARIABLE_2}`        | {descripción}                            |

---

## Pasos manuales requeridos

> Acciones que el usuario debe realizar antes de ejecutar el pipeline por primera vez.

1. {Paso 1: p.ej. solicitar acceso a la fuente de datos}
2. {Paso 2: p.ej. colocar el archivo descargado en `data/extract/{flujo}/`}
3. {Paso 3: p.ej. ejecutar las migraciones con `just migrate {flujo}`}
