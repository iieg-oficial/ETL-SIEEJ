# CONAPO - Proyecciones de Población

> Pipeline ETL para cargar proyecciones de población de CONAPO a nivel municipal en Jalisco, incluyendo datos por grupos de edad quinquenales, grandes grupos de edad e indicadores demográficos diversos (1990-2040).

---

## Fuente

| Campo        | Valor                                                                 |
|--------------|-----------------------------------------------------------------------|
| Proveedor    | CONAPO (Consejo Nacional de Población)                                |
| URL          | https://conapo.segob.gob.mx/work/models/CONAPO/pry23/DBMun/14_Jalisco.zip |
| Formato      | XLSX (dentro de ZIP)                                                  |
| Frecuencia   | On-demand (actualización manual cuando CONAPO publica nuevos datos)   |
| Último dato  | 1990-2040 (proyecciones)                                              |

---

## Esquema de Base de Datos

![Diagrama ER](assets/erd.svg)

### Tablas catálogo

| Tabla        | Descripción                                          |
|--------------|------------------------------------------------------|
| `cat_sexo`   | Catálogo de sexo (HOMBRES, MUJERES)                  |

### Tablas principales

| Tabla                          | Descripción                                                                 |
|--------------------------------|-----------------------------------------------------------------------------|
| `stg_poblacion_mitad_anio`     | Población a mitad de año por grupo quinquenal de edad, sexo, municipio y año |
| `stg_grandes_grupos_edad`      | Población por grandes grupos de edad, sexo, municipio y año                 |
| `stg_indicadores_demograficos` | Indicadores demográficos diversos por municipio y año                       |

### Vistas de integración

| Vista                            | Descripción                                                                 |
|----------------------------------|-----------------------------------------------------------------------------|
| `view_poblacion_mitad_anio`      | Desnormalización de `stg_poblacion_mitad_anio` con nombres de municipio, entidad y sexo |
| `view_grandes_grupos_edad`       | Desnormalización de `stg_grandes_grupos_edad` con nombres de municipio, entidad y sexo |
| `view_indicadores_demograficos`  | Desnormalización de `stg_indicadores_demograficos` con nombres de municipio y entidad |

Todas las vistas filtran datos de Jalisco (`cve_ent = 14`) y hacen JOIN con las tablas foráneas `cvegeo_municipalities` y `cvegeo_states`.

---

## Implementación ETL

| Modo        | Implementado | Tipo                        |
|-------------|:------------:|-----------------------------|
| Bootstrap   | ✅           | Carga histórica completa    |
| Update      | ❌           | No implementado             |

---

## Diagrama de archivos

```
core/pipelines/conapo/
├── __init__.py
├── attributes.py
├── config.py
├── constants.py
├── schemas.py
├── .env.example
├── README.md  ← este archivo
├── eda/
│   └── __init__.py
├── stages/
│   ├── __init__.py
│   ├── extract.py
│   ├── transform.py
│   └── load.py
├── helpers/
│   └── __init__.py
└── assets/
    └── er_conapo.png

dags/
└── etl_conapo.py

migrations/conapo/sql/
├── V1__foreign_tables.sql
├── V2__catalogs_conapo.sql
├── V3__tables_conapo.sql
└── V4__views_conapo.sql
```

---

## Metodología ETL

### Extract
Descarga directa del archivo ZIP desde el sitio de CONAPO. El ZIP contiene archivos XLSX con tres hojas de datos:
- `1_Grupo_Quinq_14_JL.xlsx`: Población por grupos quinquenales de edad
- `2_Gran_Gedad_14_JL.xlsx`: Población por grandes grupos de edad
- `3_Indicadores_Dem_14_JL.xlsx`: Indicadores demográficos diversos

No requiere credenciales. Se descarga en memoria y se extrae usando `zipfile`.

### Transform
- Renombrado de columnas a `snake_case` en español
- Conversión de tipos de datos (enteros y flotantes)
- Mapeo de sexo a foreign key (`cat_sexo.id`)
- Renombrado de `cve_mun` a `municipio_id` y `cve_ent` a `entidad_id`
- Limpieza de valores nulos usando `NULL_VALUES`
- Conversión de `fecha_actualizacion` a tipo `DATE`

### Load
- Inserción del catálogo `cat_sexo` usando `insert_records` con `ON CONFLICT DO NOTHING`
- Inserción masiva de las tres tablas principales usando `bulk_insert`
- Sincronización de secuencias para IDs autoincrementales
- Limpieza automática de archivos temporales al finalizar

---

## Variables de entorno

Definidas en `.env.example`. Crear `.env` local con los valores reales (no commitear).

| Variable              | Descripción                              |
|-----------------------|------------------------------------------|
| `LOG_LEVEL`           | Nivel de logging (INFO, DEBUG, etc.)     |
| `DB_USER`             | Usuario de base de datos                 |
| `DB_PASSWORD`         | Contraseña de base de datos              |
| `DB_HOST`             | Host de base de datos                    |
| `DB_PORT`             | Puerto de base de datos                  |
| `DB_NAME`             | Nombre de la base de datos (conapo)      |
| `FDW_DB_NAME`         | Nombre de la BD de cvegeo (FDW)          |
| `FDW_DB_HOST`         | Host de la BD de cvegeo (FDW)            |
| `FDW_DB_PORT`         | Puerto de la BD de cvegeo (FDW)          |
| `FDW_DB_USER`         | Usuario de la BD de cvegeo (FDW)         |
| `FDW_DB_PASSWORD`     | Contraseña de la BD de cvegeo (FDW)      |
| `CONAPO_URL`          | URL de descarga del ZIP de CONAPO        |

---

## Pasos manuales requeridos

> Acciones que el usuario debe realizar antes de ejecutar el pipeline por primera vez.

1. Clonar el repositorio y navegar al directorio del proyecto
2. Crear el archivo `.env` a partir de `.env.example` con las credenciales reales
3. Iniciar el contenedor de PostgreSQL: `just build-dev`
4. Desplegar el pipeline: `just pipeline-deploy conapo`
5. Ejecutar el bootstrap: `conda run -n etl python dags/etl_conapo.py`
