
# Base de datos de comercio exterior de Mexico (DataMexico)

**URL/API:** Los datos se obtienen a partir de la [api del vizbuilder](https://www.economia.gob.mx/datamexico/es/vizbuilder).

**Datos de interés:** Los datos de interés obtenidos corresponden a los **valor comercial** (en dolares) de los productos desagregados por **subpartida HS6**. Los datos están desagregados tanto por país, entidad federativa y tipo flujo (compra internacional o venta interncional).

**Frecuencia:** La actualización de los datos de DataMexico es **Trimestral**.

> **Nota** 🔎: No parece tener fechas especfícas de actualización.



## Esquema de base de datos

### Catálogos estáticos (IDs provenientes de la API)

```
┌──────────────────────────┐  ┌──────────────────────────┐  ┌──────────────────────────┐
│         periodos         │  │ tipos_flujos_comerciales  │  │         productos        │
│──────────────────────────│  │──────────────────────────│  │──────────────────────────│
│  id INTEGER PK           │  │  id INTEGER PK           │  │  id INTEGER PK           │
│  anio INTEGER            │  │  flujo TEXT              │  │  descripcion TEXT        │
│  trimestre INTEGER       │  └──────────────────────────┘  └──────────────────────────┘
│  etiqueta_trimestre      │
│    VARCHAR(7)            │
└──────────────────────────┘
```

### Catálogo dinámico (auto-incremental)

```
┌──────────────────────────┐
│          paises          │
│──────────────────────────│
│  id SERIAL PK            │
│  codigo_pais VARCHAR(3)  │
│    UNIQUE NOT NULL       │
│  nombre_pais TEXT        │
└──────────────────────────┘
```

### Tabla principal

```
┌─────────────────────────────────────────────────────────────────────┐
│                          flujo_comercio                             │
│─────────────────────────────────────────────────────────────────────│
│  id SERIAL PK                                                       │
│  pais_id → paises(id)                                               │
│  entidad_id INTEGER (ref. cvegeo_states.cve_ent)                    │
│  periodo_id → periodos(id)                                          │
│  tipo_flujo_id → tipos_flujos_comerciales(id)                       │
│  producto_id → productos(id)                                        │
│  valor_comercio FLOAT NOT NULL                                      │
└─────────────────────────────────────────────────────────────────────┘
```
