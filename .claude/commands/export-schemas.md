Genera `context_schemas/schemas.md` ejecutando el siguiente script bash:

```bash
mkdir -p context_schemas
output="context_schemas/schemas.md"
> "$output"

for env_file in core/pipelines/*/.env; do
  pipeline=$(basename $(dirname "$env_file"))
  sql_dir="migrations/$pipeline/sql"

  [ ! -d "$sql_dir" ] && continue

  db_name=$(grep '^DB_NAME=' "$env_file" | cut -d'=' -f2)

  echo "# $db_name" >> "$output"
  echo "" >> "$output"
  echo "## Variables de entorno" >> "$output"
  echo "" >> "$output"
  cat "$env_file" >> "$output"
  echo "" >> "$output"

  schemas="core/pipelines/$pipeline/schemas.py"
  if [ -f "$schemas" ]; then
    echo "## Schemas" >> "$output"
    echo "" >> "$output"
    echo '```python' >> "$output"
    cat "$schemas" >> "$output"
    echo '```' >> "$output"
    echo "" >> "$output"
  fi

  echo "## Migraciones" >> "$output"
  echo "" >> "$output"
  for sql_file in $(ls "$sql_dir"/V*.sql 2>/dev/null | sort -V); do
    fname=$(basename "$sql_file")
    echo "### $fname" >> "$output"
    echo "" >> "$output"
    echo '```sql' >> "$output"
    cat "$sql_file" >> "$output"
    echo '```' >> "$output"
    echo "" >> "$output"
  done

  echo "---" >> "$output"
  echo "" >> "$output"
done
```

Corre el script con Bash y confirma cuántos pipelines se exportaron.
