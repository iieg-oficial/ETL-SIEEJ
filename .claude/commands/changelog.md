Genera un changelog para el release actual.

## Pasos

1. Obtén el último tag:
   ```bash
   git describe --tags --abbrev=0
   ```

2. Obtén los commits desde ese tag:
   ```bash
   git log {ultimo_tag}..HEAD --oneline --no-merges
   ```

3. Agrupa los commits por pipeline (detectado del scope en el mensaje, e.g. `feat(marginacion): ...`):
   - Commits sin scope van a una sección **General**

4. Escribe el changelog en este formato:

```markdown
## [Unreleased] — {fecha_hoy}

### {pipeline_1}
- {descripcion legible del cambio}

### {pipeline_2}
- ...

### General
- ...
```

- Usa lenguaje legible en español, no copies el mensaje de commit literal si es críptico
- Omite commits de tipo `chore` o `style` a menos que sean relevantes
- Si no hay commits desde el último tag, indícalo
