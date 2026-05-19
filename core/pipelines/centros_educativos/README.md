# Pipeline: Centros Educativos

Pipeline ETL para el padrón de centros educativos (escuelas) publicado por la Secretaría de Educación Pública (SEP) a través del sistema SIGED.

## Fuentes de datos

El pipeline consume la API REST del SIGED, consultada por entidad federativa:

- **URL**: `CENTROS_EDUCATIVOS_URL` configurada en `.env`, con parámetro `{entidad}` (clave numérica 1–32)
- **Cobertura histórica**: Instantánea — representa el estado actual del padrón al momento de la descarga
- **Frecuencia de publicación**: Continua. La API refleja el estado vigente del padrón en cada consulta

## ERD

![ERD](assets/erd.svg)

### Catálogos estáticos (IDs predefinidos)

```
┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐
│        turnos        │  │   tipos_educativos   │  │  niveles_educativos  │
│──────────────────────│  │──────────────────────│  │──────────────────────│
│  id INTEGER PK       │  │  id INTEGER PK       │  │  id INTEGER PK       │
│  turno               │  │  tipo_educativo      │  │  nivel_educativo     │
└──────────────────────┘  └──────────────────────┘  └──────────────────────┘

┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐
│ servicios_educativos │  │   tipos_controles    │  │ tipos_sostenimiento  │
│──────────────────────│  │──────────────────────│  │──────────────────────│
│  id INTEGER PK       │  │  id INTEGER PK       │  │  id INTEGER PK       │
│  servicio_educativo  │  │  tipo_control        │  │  tipo_sostenimiento  │
└──────────────────────┘  └──────────────────────┘  └──────────────────────┘
```

### Catálogos dinámicos (auto-incrementales)

```
┌──────────────────────────┐
│        localidades       │
│──────────────────────────│
│  id SERIAL PK            │
│  cve_geo_id UNIQUE       │
│  clave_localidad         │
│  municipio_id            │
│  entidad_id              │
│  localidad               │
└──────────────┬───────────┘
               │
┌──────────────┴───────────┐     ┌──────────────────────┐
│         colonias         │     │       domicilios      │
│──────────────────────────│     │──────────────────────│
│  id SERIAL PK            │     │  id SERIAL PK        │
│  colonia                 │     │  domicilio           │
│  localidad_id FK         │     │  numero_exterior     │
│  UNIQUE(colonia,         │     │  codigo_postal       │
│    localidad_id)         │     │  entre_calle         │
└──────────────────────────┘     │  y_calle             │
                                 │  calle_posterior     │
                                 └──────────────────────┘
```

### Tabla principal

```
┌─────────────────────────────────────────────────────────────────────┐
│                              centros                                │
│─────────────────────────────────────────────────────────────────────│
│  clave_centro_trabajo VARCHAR(20) PK                                │
│  nombre_centro_trabajo TEXT                                         │
│  turno_id → turnos(id)                                              │
│  tipos_educativos_id → tipos_educativos(id)                         │
│  nivel_educativo_id → niveles_educativos(id)                        │
│  servicio_educativo_id → servicios_educativos(id)                   │
│  tipo_control_id → tipos_controles(id)                              │
│  tipo_sostenimiento_id → tipos_sostenimiento(id)                    │
│  entidad_id (ref. cvegeo_states)                                    │
│  municipio_id (ref. cvegeo_municipalities)                          │
│  localidades_id → localidades(id)                                   │
│  domicilios_id → domicilios(id)                                     │
│  colonias_id → colonias(id)                                         │
│  total_alumnos_hombres INTEGER                                      │
│  total_alumnas_mujeres INTEGER                                      │
│  total_docentes_hombres INTEGER                                     │
│  total_docentes_mujeres INTEGER                                     │
│  aulas_en_uso INTEGER                                               │
│  aulas_existentes INTEGER                                           │
│  latitud FLOAT                                                      │
│  longitud FLOAT                                                     │
│  fecha_actualizacion DATE NOT NULL                                  │
└─────────────────────────────────────────────────────────────────────┘
```

**Catálogos estáticos**: `turnos`, `tipos_educativos`, `niveles_educativos`, `servicios_educativos`, `tipos_controles`, `tipos_sostenimiento` tienen IDs predefinidos en `mappings/secondary_tables.py`.

**Catálogos dinámicos**: `localidades`, `domicilios` y `colonias` se extraen de los propios datos y se insertan con `ON CONFLICT DO NOTHING`.

**Llave geográfica**: `cve_geo_id` se computa como `int(f"{entidad_id:02}{municipio_id:03}{localidad_id:04}")` y actúa como clave única en `localidades`.

**Llave primaria**: `clave_centro_trabajo` — identifica unívocamente cada escuela en el padrón SEP.

## Flujo del pipeline

### Extract

1. Itera sobre las 32 entidades federativas de México (`ENTIDADES_MEXICO`)
2. Consulta la API del SIGED por entidad con hasta 6 reintentos ante fallas de conexión
3. Renombra columnas crudas de la API a nombres de base de datos usando `RENAME_HEADER`
4. Agrega `fecha_actualizacion` con la fecha de ejecución
5. Persiste el resultado por entidad en `.pkl` (`data/extract/centros_educativos/centros_educativos_{entidad}.pkl`)

### Transform

1. Carga los pickles generados en la etapa de extracción
2. Parsea `fecha_actualizacion` al tipo `date`
3. Aplica mayúsculas a columnas de catálogo (`tipo_educativo`, `nivel_educativo`, `servicio_educativo`, `tipo_control`, `tipo_sostenimiento`)
4. Aplica title case y acentos a columnas de nombre propio (`nombre_centro_trabajo`, `localidad`, `municipio`, `domicilio`, `colonia`, etc.)
5. Reemplaza abreviaturas conocidas (`U.S.A.E.R.`, `CAM`) por su nombre completo
6. Limpia valores nulos conocidos (`NULL_VALUES`)
7. Construye catálogos dinámicos:
   - `localidades`: registros únicos por `cve_geo_id`, calculado desde `entidad_id`, `municipio_id`, `localidad_id`
   - `domicilios`: registros únicos por combinación de campos de dirección
   - `colonias`: registros únicos por `(colonia, localidad)`
8. Persiste el DataFrame y los catálogos en `.pkl` (`data/transform/centros_educativos/`)

### Load

1. Sincroniza secuencias de IDs para `localidades`, `domicilios` y `colonias`
2. Inserta catálogos estáticos con IDs predefinidos (`ON CONFLICT DO NOTHING`)
3. Inserta `localidades` y `domicilios` como catálogos dinámicos (`ON CONFLICT DO NOTHING`)
4. Mapea `colonias_id` vía `cve_geo_id` para obtener el `localidad_id` correcto, luego inserta con conflicto en `(colonia, localidad_id)`
5. Construye mapeos de FKs:
   - Catálogos estáticos: normaliza con `normalize_col()` y mapea por valor
   - `localidades`: computa `cve_geo_id` desde el DataFrame y mapea a `localidades_id`
   - `domicilios` y `colonias`: mapa directo por ID
6. Inserta registros en `centros` con conflicto en `clave_centro_trabajo`

## Periodicidad

- **Bootstrap**: Bajo demanda. Procesa las 32 entidades federativas en una sola ejecución del DAG `etl_centros_educativos_bootstrap`
- **Update**: Sin programación definida — el padrón SEP no expone un histórico; cada bootstrap reemplaza el estado anterior vía `ON CONFLICT`
