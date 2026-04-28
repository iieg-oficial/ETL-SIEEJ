---
name: bootstrap-update-rules
description: Reglas para distinguir y manejar bootstrap, update incremental y SCD en pipelines ETL.
applyTo: "core/pipelines/**/stages/**/*.py,dags/**/*.py"
---

## Definiciones

- **Bootstrap**: primera ejecución. Procesa todo el histórico disponible.
- **Update**: ejecuciones subsecuentes. Procesa solo lo nuevo o lo cambiado desde la última corrida.

## Variantes de update

### Variante A — Append puro

La fuente solo agrega registros nuevos sin modificar los existentes.

- Estrategia de carga: `bulk_insert` con `conflict_keys` para evitar duplicados.
- No se requiere historial.

### Variante B — Mezcla (SCD Tipo 2)

La fuente publica nuevos registros **y** actualiza registros previos.

- Generar `hash_id` con las columnas a monitorear para cambios.
- Comparar `hash_id` contra el almacenado para detectar cambios.
- Versionar registros con:
  - `valid_from: Date NOT NULL`
  - `valid_to: Date NULL`
  - `is_current: Bool NOT NULL`
- Inserción de nueva versión: `is_current=True`, marca la versión anterior con `valid_to` y `is_current=False`.
- **Vistas de integración**: filtrar `WHERE is_current = TRUE`.

## DAG

- `bootstrap`: `schedule=None`, ejecutar manualmente o vía param `bootstrap=True`.
- `update`: schedule cron / preset (`@yearly`, `@monthly`, etc.) según periodicidad real de la fuente.
- Catchup desactivado salvo justificación explícita.

## Iterables vs no-iterables

| Aspecto | Iterable | No-iterable |
|---|---|---|
| URL | Fija, parametrizada por año/entidad | Cambia con cada release |
| `Stage.__init__` | `__init__(self, year)` | `__init__(self)` |
| Archivos | `extract_{year}.pkl` | nombre estático |
| Carga | `upsert_records` con `conflict_keys` | `bulk_insert` (bootstrap) |
| Update | Automático por DAG | Manual con nueva URL en `.env` |

## Checklist al cerrar el pipeline

- [ ] Variante de update declarada en README interno.
- [ ] Modo bootstrap probado.
- [ ] Modo update probado y sin duplicados.
- [ ] Si SCD: vista filtra `is_current=True`.
