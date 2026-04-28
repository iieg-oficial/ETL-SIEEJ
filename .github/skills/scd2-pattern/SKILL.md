---
name: scd2-pattern
description: Patrón SCD Type 2 (Slowly Changing Dimensions) usado en pipelines SIEEJ para versionar registros que cambian (ej. `repd`). Incluye el esquema `_current` + `_history`, el cálculo de `record_hash`, y la lógica de load para bootstrap y update. Úsalo solo cuando el EDA indique `update_strategy: scd2`.
argument-hint: <pipeline>
---

# Skill: Patrón SCD2

Implementación canónica de Slowly Changing Dimensions Type 2 en pipelines SIEEJ. Fuente única de este patrón — los agentes `db` y `etl` lo invocan cuando aplica.

## Cuándo usar SCD2

Aplica cuando la fuente entrega **archivos acumulativos mixtos**: cada nueva descarga trae registros viejos sin cambios + registros nuevos + registros existentes con campos modificados. El patrón permite dos cosas clave gracias al `record_hash`:

1. **Filtrado rápido** — descartar en O(1) las filas cuyo hash ya existe vigente (no hay que comparar campo por campo).
2. **Versionado** — detectar las filas cuya llave natural ya existe pero con hash distinto → cerrar la versión anterior y abrir una nueva.

Condiciones necesarias:

- La fuente tiene **llave natural estable** (folio, UUID, nº de expediente).
- Los campos de negocio **pueden cambiar** entre cargas sucesivas.
- Se necesita **trazabilidad histórica** de los cambios.

**No** usar:

- Fuente que solo agrega registros nuevos (sin modificar los viejos) → upsert simple.
- Fuente que se sobreescribe completa cada periodo → `bootstrap_only`.
- Fuente sin llave natural confiable → no hay cómo versionar.

Ejemplo canónico: `core/pipelines/repd/` — cada corte trae el padrón completo de personas desaparecidas; algunas filas cambian (se localizan, se actualizan datos) y otras son nuevas.

## Arquitectura

```
+---------------------------+     +--------------------------------+
| stg_{p}_{entity}_current  |     | stg_{p}_{entity}_history       |
| (una fila vigente por LK) |     | (snapshot por versión)         |
|---------------------------|     |--------------------------------|
| id SERIAL PK              |<----| current_id FK                  |
| llave_natural UNIQUE      |     | llave_natural                  |
| campos_de_negocio...      |     | version_num                    |
| record_hash VARCHAR(64)   |     | is_current BOOLEAN             |
| current_version INTEGER   |     | valid_from TIMESTAMP           |
+---------------------------+     | valid_to TIMESTAMP             |
                                  | campos_de_negocio... (snapshot)|
                                  | record_hash                    |
                                  | UNIQUE (llave_natural, version)|
                                  +--------------------------------+
```

**Invariantes**:

1. `_current` tiene exactamente una fila por `llave_natural`.
2. `_history` tiene todas las versiones; una de ellas tiene `is_current=TRUE`.
3. `current_version` en `_current` == `version_num` de la fila `is_current=TRUE` en `_history`.
4. `record_hash` en `_current` == `record_hash` de la versión vigente.

## Migración SQL

Ver skill `generate-migration` → "Variante SCD2". Resumen:

- Tabla `stg_{pipeline}_{entity}_current` con `record_hash`, `current_version`.
- Tabla `stg_{pipeline}_{entity}_history` con `version_num`, `is_current`, `valid_from`, `valid_to`.
- Constraint `UNIQUE (llave_natural, version_num)` en `_history`.
- FK `_history.current_id → _current.id`.

## Schemas SQLAlchemy

Dos modelos con los mismos campos de negocio. Ver `core/pipelines/repd/schemas.py` como referencia canónica (`CaseCurrent` + `CaseHistory`).

## Configuración en `consts.py`

```python
# Campos determinísticos para calcular record_hash (orden estable)
HASH_FIELDS = [
    "feb",
    "sex_id",
    "nationality_id",
    "report_date",
    # ... todos los campos de negocio resueltos (IDs de catálogo ya mapeados)
]
```

**Reglas para `HASH_FIELDS`**:

- Incluir los **IDs de catálogo ya resueltos** (ej. `sex_id`), no los nombres.
- Incluir `municipio_id` si aplica cvegeo.
- **No** incluir `id`, `created_at`, `updated_at`, `record_hash`, `current_version`.
- El orden **importa** — cambiarlo invalida todos los hashes previos.

## Cálculo de `record_hash`

```python
from core.utils.records import compute_record_hash

df["record_hash"] = df.apply(
    lambda row: compute_record_hash(row.to_dict(), HASH_FIELDS),
    axis=1,
)
```

`compute_record_hash` produce un SHA-256 hex determinista normalizando `None`, fechas y valores numéricos.

## Lógica de load

### Bootstrap

Inserción inicial. Todos los registros van a `_current` con `current_version=1` y una versión correspondiente en `_history` con `is_current=TRUE`, `valid_from=now()`, `valid_to=NULL`.

```python
def _load_bootstrap(self, df: pd.DataFrame) -> dict:
    now = datetime.now()
    with self.db.get_session() as session:
        # 1) Insertar _current
        current_records = df.to_dict("records")
        bulk_insert(session, {Entity}Current, current_records, batch_size=5000)

        # 2) Construir mapa llave_natural → current_id
        current_map = get_mapping(session, {Entity}Current, "llave_natural", "id")

        # 3) Insertar _history (version_num=1)
        history_records = [
            {**rec, "current_id": current_map[rec["llave_natural"]],
             "version_num": 1, "is_current": True, "valid_from": now}
            for rec in current_records
        ]
        bulk_insert(session, {Entity}History, history_records, batch_size=5000)

        sync_id_sequence(session, {Entity}Current)
        sync_id_sequence(session, {Entity}History)

    return {"inserted": len(df)}
```

### Update

Comparar `record_hash` por llave natural:

1. **Nuevos** (llave no existe en `_current`) → insertar como bootstrap (version=1).
2. **Sin cambios** (hash idéntico) → no hacer nada.
3. **Con cambios** (hash distinto) → nueva versión:
   - `_history`: marcar la versión actual `is_current=FALSE, valid_to=now`.
   - `_history`: insertar nueva versión con `version_num = previous + 1`.
   - `_current`: `UPDATE` con los nuevos valores y `current_version += 1`.

```python
def _load_update(self, df: pd.DataFrame) -> dict:
    now = datetime.now()
    stats = {"new": 0, "changed": 0, "unchanged": 0}

    with self.db.get_session() as session:
        existing = get_mapping(session, {Entity}Current, "llave_natural", "record_hash")
        existing_ids = get_mapping(session, {Entity}Current, "llave_natural", "id")
        existing_vers = get_mapping(session, {Entity}Current, "llave_natural", "current_version")

        new_rows, changed_rows = [], []
        for rec in df.to_dict("records"):
            lk = rec["llave_natural"]
            if lk not in existing:
                new_rows.append(rec)
            elif existing[lk] != rec["record_hash"]:
                changed_rows.append(rec)
            else:
                stats["unchanged"] += 1

        # Nuevos (igual que bootstrap)
        if new_rows:
            bulk_insert(session, {Entity}Current, new_rows)
            # ... mismo flujo que bootstrap para _history
            stats["new"] = len(new_rows)

        # Cambios: versionar
        for rec in changed_rows:
            lk = rec["llave_natural"]
            current_id = existing_ids[lk]
            new_version = existing_vers[lk] + 1

            # Cerrar versión anterior en _history
            session.execute(
                update({Entity}History)
                .where(({Entity}History.llave_natural == lk) &
                       ({Entity}History.is_current.is_(True)))
                .values(is_current=False, valid_to=now)
            )

            # Insertar nueva versión en _history
            session.add({Entity}History(
                **rec, current_id=current_id, version_num=new_version,
                is_current=True, valid_from=now,
            ))

            # Actualizar _current
            session.execute(
                update({Entity}Current)
                .where({Entity}Current.id == current_id)
                .values(**rec, current_version=new_version)
            )
        stats["changed"] = len(changed_rows)

    return stats
```

## Vista con histórico

Para consultas analíticas sobre versiones vigentes, usar `_current`. Para auditoría histórica, consultar `_history` filtrando por fecha:

```sql
-- Estado de un registro en una fecha X
SELECT * FROM stg_{pipeline}_{entity}_history
WHERE llave_natural = 'ABC123'
  AND valid_from <= '2024-06-01'
  AND (valid_to IS NULL OR valid_to > '2024-06-01');
```

## Checklist de implementación SCD2

- [ ] `V3__tabla_principal.sql` con tablas `_current` + `_history` (variante SCD2 de `generate-migration`).
- [ ] `schemas.py` con ambos modelos y constraint `UNIQUE(llave_natural, version_num)`.
- [ ] `HASH_FIELDS` en `consts.py` con IDs resueltos y orden estable.
- [ ] `transform.py` no calcula `record_hash` (se hace en `load.py` con IDs resueltos).
- [ ] `load.py` implementa `_load_bootstrap` y `_load_update`.
- [ ] Vista analítica apunta a `_current`, no a `_history`.

## Referencia canónica

- `core/pipelines/repd/` — implementación completa de SCD2 con cvegeo y catálogos.
- `migrations/repd/sql/V2__tabla_stg_repd.sql` — migración con `_current` + `_history`.
- `core/utils/records.py` — `compute_record_hash`.
