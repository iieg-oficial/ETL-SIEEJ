Genera un reporte de estado de todos los pipelines en `core/pipelines/`.

## Pasos

1. Lista todos los pipelines:
   ```bash
   ls core/pipelines/
   ```

2. Para cada pipeline, verifica la existencia de:
   - `schemas.py`
   - `constants.py`
   - `stages/extract.py`, `stages/transform.py`, `stages/load.py`
   - `mappings.py`
   - `README.md`
   - `migrations/{pipeline}/sql/` — cuenta los archivos `.sql`
   - `core/dags/{pipeline}/` — existe el DAG

3. Escribe `docs/pipeline-status.md` con esta tabla:

```markdown
# Pipeline Status

_Actualizado: {fecha}_

| Pipeline | Schemas | Stages | Mappings | Migrations | DAG | README |
|---|---|---|---|---|---|---|
| establecimien... | ✓ | ✓ | ✓ | 4 | ✓ | ✓ |
| fiscalia | ✓ | ✓ | — | 3 | ✓ | ✗ |
```

- `✓` si existe, `✗` si falta, `—` si es opcional y no aplica
- Para Migrations muestra el número de archivos SQL
- Ordena alfabéticamente por nombre de pipeline

4. Imprime la ruta del archivo generado.
