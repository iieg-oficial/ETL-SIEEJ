# Pipeline: Fiscalia

Pipeline ETL para datos de incidencia delictiva de la Fiscalia del Estado de Jalisco.

## Fuentes de datos

El pipeline consume archivos Excel almacenados en una carpeta compartida de Google Drive:

- **Archivo histórico**: Un único `.xlsx` (~50,000 registros) con incidentes de años anteriores. Usa coordenadas WGS84 y carece de algunas columnas presentes en las actualizaciones (violencia, calle, cruce).
- **Archivos de actualización**: Archivos `.xlsx` mensuales enviados por la Fiscalía vía correo electrónico. Deben subirse a la carpeta de Drive con el formato de nombre `dd-mm-yyyy.xlsx` (ej. `01-12-2025.xlsx`). Estos archivos usan coordenadas UTM Zona 13N que se convierten durante la transformación.

## Esquema de base de datos

```
┌──────────────────┐     ┌───────────────────┐
│  bien_afectado   │     │ zonas_geograficas │
│──────────────────│     │───────────────────│
│  id INTEGER PK   │     │  id INTEGER PK    │
│  bien_afectado   │     │  zona_geografica  │
└───────┬──────────┘     └───────────────────┘
        │
┌───────┴──────────┐     ┌──────────────────┐
│     delitos      │     │    violencia     │
│──────────────────│     │──────────────────│
│  id INTEGER PK   │     │  id INTEGER PK   │
│  delito          │     │  violencia       │
│  bien_afectado_id│     └──────────────────┘
└──────────────────┘

┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│    colonias      │  │     calles       │  │     cruces       │
│──────────────────│  │──────────────────│  │──────────────────│
│  id SERIAL PK    │  │  id SERIAL PK    │  │  id SERIAL PK    │
│  colonia UNIQUE  │  │  calle UNIQUE    │  │  cruce UNIQUE    │
└──────────────────┘  └──────────────────┘  └──────────────────┘

┌─────────────────────────────────────────────────────────┐
│                        casos                            │
│─────────────────────────────────────────────────────────│
│  id SERIAL PK                                           │
│  delitos_id INTEGER NOT NULL → delitos(id)              │
│  violencia_id INTEGER → violencia(id)                   │
│  zonas_geograficas_id INTEGER → zonas_geograficas(id)   │
│  municipios_id INTEGER                                  │
│  colonias_id INTEGER → colonias(id)                     │
│  calles_id INTEGER → calles(id)                         │
│  cruces_id INTEGER → cruces(id)                         │
│  hora VARCHAR(5) NOT NULL                               │
│  longitud FLOAT NOT NULL                                │
│  latitud FLOAT NOT NULL                                 │
│  fecha_denuncia DATE NOT NULL                           │
│  fecha_actualizacion DATE NOT NULL                      │
│─────────────────────────────────────────────────────────│
│  UNIQUE (delitos_id, fecha_denuncia, hora,              │
│          longitud, latitud)                             │
└─────────────────────────────────────────────────────────┘
```

**Catálogos**: `zonas_geograficas`, `bien_afectado`, `delitos`, `violencia` son estáticos (IDs predefinidos). `colonias`, `calles`, `cruces` son dinámicos (auto-incrementales, extraídos de los datos).

**Constraints**: `casos` tiene una llave natural única en `(delitos_id, fecha_denuncia, hora, longitud, latitud)`. Las filas con coordenadas nulas o en cero se descartan antes de la inserción.

## Flujo del pipeline


### Extract

1. Descarga los archivos desde Google Drive
2. Lee cada `.xlsx`
3. Distingue archivos históricos de actualizaciones por el formato del nombre (fechas parseables como `dd-mm-yyyy` son actualizaciones)
4. A los datos históricos se les agregan las columnas faltantes como `NULL` (`violencia`, `calle`, `cruce`)

### Transform

1. Aplica titlecase y reemplaza valores nulos conocidos
2. Convierte coordenadas UTM 13N a WGS84 (solo filas de actualización)
3. Parsea `hora` (HH:MM) y `fecha_denuncia` (date)
4. Descarta filas con `longitud`, `latitud`, `fecha_denuncia` u `hora` nulos o en cero
5. Deduplica sobre la llave natural
6. Extrae `colonias`, `calles` y `cruces` únicos para inserción en catálogos

### Load

1. Inserta catálogos estáticos (idempotente vía `ON CONFLICT DO NOTHING`)
2. Inserta catálogos dinámicos (colonias, calles, cruces)
3. Construye mapeos de FKs y asigna los IDs al DataFrame
4. Upsert de registros en `casos` (`ON CONFLICT DO UPDATE`)

## Periodicidad

Mensual (`@monthly`). Se espera que los archivos de actualización se suban a la carpeta de Drive antes de la ejecución programada.
