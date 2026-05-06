Crea el Pull Request en GitHub para el pipeline actual.

## Pasos

1. Detecta el nombre del pipeline del contexto actual (rama, archivos recientes, conversación).

2. Busca el issue abierto relacionado:
   ```bash
   gh issue list --state open --search "{pipeline}" --json number,title,url
   ```
   Usa el número encontrado para `Closes #N`. Si hay más de uno, pregunta al usuario cuál es el correcto.

3. Obtén el resumen de commits de esta rama:
   ```bash
   git log main..HEAD --oneline
   ```

4. Crea el PR:
   ```bash
   gh pr create \
     --title "feat(pipeline): {pipeline}" \
     --body "$(cat <<'EOF'
   ## Issue

   Closes #{numero_issue}

   ---

   ## Qué se hizo

   {descripcion_breve_basada_en_commits}

   ---

   ## Tipo

   - [x] `feat` - Nueva funcionalidad

   ---

   ## Tareas completadas

   - [x] Schemas (constants, attributes, schemas)
   - [x] Extract
   - [x] Transform
   - [x] Load
   - [x] DAG
   - [x] Migraciones
   - [x] README

   ---

   ## Notas

   <!-- Información adicional para el reviewer -->
   EOF
   )"
   ```

5. Muestra la URL del PR creado.
