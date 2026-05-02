Crea o encuentra el issue de GitHub para el pipeline actual.

## Pasos

1. Detecta el nombre del pipeline del contexto actual (rama, archivos recientes, conversación).

2. Busca issues abiertos relacionados:
   ```bash
   gh issue list --state open --search "{pipeline}" --json number,title,url
   ```

3. Si ya existe un issue claro para este pipeline, muéstralo y pregunta:
   "¿Es este el issue correcto? (#N — título)"
   - Si sí: termina, devuelve el número para uso en `/fill-pr`.
   - Si no: continúa a crear uno nuevo.

4. Si no existe, crea el issue con la información del pipeline:

```bash
gh issue create \
  --title "feat(pipeline): {pipeline}" \
  --body "$(cat <<'EOF'
**Nombre del pipeline:** {pipeline}

**Fuente de datos:**
- [ ] API
- [ ] Base de datos
- [ ] Web Scraping
- [x] Archivo (CSV/Excel)

**Frecuencia de ejecución:**
- [ ] Mensual
- [ ] Quincenal
- [ ] Semanal
- [ ] Diaria
- [ ] On-demand

---

## Tablas destino

**Principal:**
- `{tabla_principal}`

**Catálogos:**
- (listar)

---

## Notas

<!-- Cualquier detalle adicional -->
EOF
)"
```

5. Muestra la URL del issue creado.
