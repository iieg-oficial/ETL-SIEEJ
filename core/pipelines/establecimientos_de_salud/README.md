# Pipeline: Establecimientos de Salud

Pipeline ETL para el catálogo nacional de establecimientos de salud (CLUES) publicado por la Secretaría de Salud del Gobierno de México.

## Fuentes de datos

El pipeline consume archivos Excel publicados mensualmente en el portal de la Secretaría de Salud:

- **URL**: `ESTABLECIMIENTOS_URL` configurada en `.env`, con parámetros `{year}` y `{month}` (ej. `ESTABLECIMIENTO_SALUD_202501.xlsx`)
- **Cobertura histórica**: A partir de mayo de 2017
- **Frecuencia de publicación**: Mensual. Cada archivo representa el estado del padrón en ese período

## ERD

![ERD](assets/erd.svg)

### Catálogos estáticos (IDs predefinidos)

```
┌──────────────────────────┐  ┌──────────────────────────┐
│   tipos_establecimiento  │  │  estatus_establecimiento  │
│──────────────────────────│  │──────────────────────────│
│  id INTEGER PK           │  │  id INTEGER PK           │
│  tipo_establecimiento    │  │  estatus_establecimiento  │
└──────────────────────────┘  └──────────────────────────┘

┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  nivel_atencion  │  │  estrato_unidad  │  │    movimientos   │
│──────────────────│  │──────────────────│  │──────────────────│
│  id INTEGER PK   │  │  id INTEGER PK   │  │  id INTEGER PK   │
│  nivel_atencion  │  │  estrato_unidad  │  │  movimiento      │
└──────────────────┘  └──────────────────┘  └──────────────────┘
```

### Catálogos dinámicos (auto-incrementales)

```
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   instituciones  │  │    tipologias    │  │  subtipologias   │
│──────────────────│  │──────────────────│  │──────────────────│
│  id SERIAL PK    │  │  id SERIAL PK    │  │  id SERIAL PK    │
│  institucion     │  │  tipologia       │  │  subtipologia    │
└──────────────────┘  └──────────────────┘  └──────────────────┘

┌──────────────────┐  ┌───────────────────────────┐
│   localidades    │  │       jurisdicciones       │
│──────────────────│  │───────────────────────────│
│  id SERIAL PK    │  │  id SERIAL PK             │
│  clave_localidad │  │  jurisdiccion UNIQUE       │
│  municipio_id    │  │  municipio_id              │
│  entidad_id      │  │  entidad_id               │
│  localidad       │  └───────────────────────────┘
└──────────────────┘

┌──────────────────────┐     ┌──────────────────────┐
│    tipos_vialidad    │     │  tipos_asentamiento  │
│──────────────────────│     │──────────────────────│
│  id SERIAL PK        │     │  id SERIAL PK        │
│  tipo_vialidad UNIQUE│     │  tipo_asentamiento   │
└──────────┬───────────┘     └──────────────────────┘
           │
┌──────────┴───────────┐
│      vialidades      │
│──────────────────────│
│  id SERIAL PK        │
│  vialidad            │
│  tipo_vialidad_id FK │
│  UNIQUE(vialidad,    │
│    tipo_vialidad_id) │
└──────────────────────┘

┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐
│   marcas_moviles     │  │  programas_moviles   │  │   unidades_moviles   │
│──────────────────────│  │──────────────────────│  │──────────────────────│
│  id SERIAL PK        │  │  id SERIAL PK        │  │  id SERIAL PK        │
│  marca               │  │  programa_movil      │  │  nombre_unidad_movil │
│  marca_especifica    │  │  UNIQUE              │  │  nombre_comercial    │
│  modelo              │  └──────────────────────┘  │  UNIQUE              │
│  UNIQUE(marca,       │                             └──────────────────────┘
│    marca_especifica, │
│    modelo)           │
└──────────────────────┘

┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐
│  tipos_unidad_movil  │  │  tipologias_moviles  │  │       tipos_obra     │
│──────────────────────│  │──────────────────────│  │──────────────────────│
│  id SERIAL PK        │  │  id SERIAL PK        │  │  id SERIAL PK        │
│  tipo_unidad_movil   │  │  tipologia_movil     │  │  tipo_obra UNIQUE    │
│  UNIQUE              │  │  UNIQUE              │  └──────────────────────┘
└──────────────────────┘  └──────────────────────┘

┌──────────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐
│  institutos_administracion│  │  rfc_establecimientos│  │    motivos_baja      │
│──────────────────────────│  │──────────────────────│  │──────────────────────│
│  id SERIAL PK            │  │  id SERIAL PK        │  │  id SERIAL PK        │
│  instituto_administracion│  │  rfc UNIQUE          │  │  motivo_baja UNIQUE  │
│  UNIQUE                  │  └──────────────────────┘  └──────────────────────┘
└──────────────────────────┘
```

### Tabla principal

```
┌─────────────────────────────────────────────────────────────────────┐
│                          establecimientos                           │
│─────────────────────────────────────────────────────────────────────│
│  clues VARCHAR(11) PK                                               │
│  fecha_actualizacion DATE PK                                        │
│  institucion_id → instituciones(id)                                 │
│  entidad_id (ref. cvegeo_states)                                    │
│  municipio_id (ref. cvegeo_municipalities)                          │
│  localidad_id → localidades(id)                                     │
│  jurisdiccion_id → jurisdicciones(id)                               │
│  tipo_establecimiento_id → tipos_establecimiento(id)                │
│  tipologia_id → tipologias(id)                                      │
│  subtipologia_id → subtipologias(id)                                │
│  unidad_movil_id → unidades_moviles(id)                             │
│  vialidad_id → vialidades(id)                                       │
│  numero_exterior TEXT                                               │
│  numero_interior TEXT                                               │
│  tipo_asentamiento_id → tipos_asentamiento(id)                      │
│  estatus_id → estatus_establecimiento(id)                           │
│  nivel_atencion_id → nivel_atencion(id)                             │
│  estrato_unidad_id → estrato_unidad(id)                             │
│  tipo_obra_id → tipos_obra(id)                                      │
│  instituto_adm_id → institutos_administracion(id)                   │
│  rfc_id → rfc_establecimientos(id)                                  │
│  marca_movil_id → marcas_moviles(id)                                │
│  programa_movil_id → programas_moviles(id)                          │
│  tipo_unidad_movil_id → tipos_unidad_movil(id)                      │
│  tipologia_movil_id → tipologias_moviles(id)                        │
│  movimiento_id → movimientos(id)                                    │
│  motivo_baja_id → motivos_baja(id)                                  │
│  fecha_ultimo_movimiento DATE                                       │
│  fecha_efectiva_baja DATE                                           │
│  fecha_construccion DATE                                            │
│  fecha_inicio_operacion DATE                                        │
│  telefono_1 TEXT                                                    │
│  extension_1 TEXT                                                   │
│  telefono_2 TEXT                                                    │
│  extension_2 TEXT                                                   │
│  latitud FLOAT                                                      │
│  longitud FLOAT                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Catálogos estáticos**: `tipos_establecimiento`, `estatus_establecimiento`, `nivel_atencion`, `estrato_unidad`, `movimientos` tienen IDs predefinidos definidos en `mappings.py`.

**Catálogos dinámicos**: El resto de catálogos se extraen de los propios datos y se insertan con `ON CONFLICT DO NOTHING`.

**Llave primaria**: `(clues, fecha_actualizacion)` — cada registro representa el estado de un establecimiento en un mes dado.

## Flujo del pipeline

### Extract

1. Calcula los períodos a descargar según el modo:
   - **Bootstrap**: año por año desde `BOOTSTRAP_START_YEAR/MONTH` (configurado en `.env`) hasta hoy
   - **Update**: desde el mes siguiente al último `fecha_actualizacion` en la base de datos hasta hoy
2. Descarga cada archivo `.xlsx` desde la URL pública; omite períodos no disponibles
3. Normaliza nombres de columnas (renombres de encabezados del xlsx)
4. Concatena todos los períodos en un único DataFrame y lo persiste en `.pkl`

### Transform

1. Renombra columnas del xlsx a nombres de base de datos usando `EstablecimientosColMap`
2. Normaliza texto: capitalize para catálogos generales, title case para topónimos (localidad, jurisdicción)
3. Sanitiza números exteriores/interiores (elimina valores vacíos, ceros, variantes de "sin número")
4. Limpia claves geográficas como strings con ceros a la izquierda
5. Parsea fechas y convierte `modelo` a string entero
6. Reemplaza valores nulos conocidos
7. Extrae catálogos únicos para cada tabla de referencia

### Load

1. Inserta catálogos estáticos con IDs predefinidos (`ON CONFLICT DO NOTHING`)
2. Inserta catálogos dinámicos (`ON CONFLICT DO NOTHING`)
3. Construye mapeos de FKs y asigna IDs al DataFrame; los lookups compuestos (localidad, vialidad, marca) usan `pd.MultiIndex` en lugar de `apply(lambda)`
4. Inserta registros en `establecimientos` vía `bulk_insert` en chunks de 50,000 (bootstrap) o 10,000 (update)

## Periodicidad

- **Bootstrap**: Bajo demanda. Corre año por año desde 2017 para acotar el uso de RAM
- **Update**: Mensual, el día 15 de cada mes a las 8:00 (`0 8 15 * *`). Procesa todos los meses pendientes desde el último registro en base de datos
