---
name: Nuevo Pipeline
about: Solicitar implementación de un nuevo pipeline ETL
title: '[PIPELINE] {Nombre del flujo}'
labels: 'new-pipeline, feat'
assignees: ''
---

<!-- Keep this local skill template synchronized with .github/ISSUE_TEMPLATE/new-pipeline.md. -->

## 📊 Información del Pipeline

<!-- Write the confirmed internal pipeline name in snake_case. -->

**Nombre del pipeline:**

<!-- Mark only the real source type. Add acquisition details in notes when needed. -->

**Fuente de datos:**
- [ ] API
- [ ] Base de datos
- [ ] Web Scraping
- [ ] Archivo (CSV/Excel)
- [ ] Otro: ___

<!-- Select the actual operating frequency or state that it is still pending approval. -->

**Frecuencia de ejecución:**
- [ ] Mensual
- [ ] Quincenal
- [ ] Semanal
- [ ] Diaria
- [ ] On-demand
- [ ] Otra: ___

---

## 🗃️ Tablas destino

<!-- Include the expected staging table and only the catalog tables that are actually known. -->

**Staging:**
- [ ] `stg_`

**Catálogos:**
- [ ] `cat_`
- [ ] `cat_`
- [ ] `cat_`

---

## 📝 Información adicional

<!-- Check only the credentials that are truly required for extraction. -->

**Credenciales necesarias:**
- [ ] API Key
- [ ] Usuario/Contraseña BD
- [ ] Token
- [ ] Otro: ___

**Notas:**
<!-- Add concrete restrictions, dependencies, geography filters, business rules, or unresolved decisions. -->

{Breve descripción del pipeline: qué datos contiene, de dónde provienen y por qué se necesitan.}

---

## Fuente de datos

- **Proveedor:** {nombre del organismo / sistema}
- **Tipo de fuente:**
  - [ ] API
  - [ ] Archivo descargable (CSV / XLSX)
  - [ ] Base de datos externa
  - [ ] Web Scraping
  - [ ] Otro: ___
- **URL o ruta:** {URL de acceso o instrucción para obtener el archivo}

---

## Frecuencia de actualización

- [ ] Mensual
- [ ] Trimestral
- [ ] Anual
- [ ] On-demand
- [ ] Otra: ___

---

## Tipo de update

- [ ] Solo-inserciones (la fuente solo agrega registros nuevos)
- [ ] SCD — Slowly Changing Dimension (la fuente puede modificar registros existentes)

---

## Esquema propuesto

**Tabla principal:**
- `stg_{flujo}`

**Tablas catálogo:**
- `cat_{nombre1}`
- `cat_{nombre2}`

**¿Requiere conexión con `cve_geo`?**
- [ ] Sí — nivel: [ ] municipal [ ] estatal
- [ ] No

---

## Credenciales necesarias

- [ ] API Key / Token
- [ ] Usuario y contraseña
- [ ] Acceso a carpeta compartida
- [ ] Ninguna (datos abiertos)

---

## Checklist de fases

- [ ] Fase 0 — Revisión de contexto (DEA)
- [ ] Fase 1 — EDA y reporte JSON (EDA)
- [ ] Fase 2 — Esquema de BD y migraciones (DB)
- [ ] Fase 3 — Plan ETL aprobado (DEA)
- [ ] Fase 4 — Issue y rama creados (GIT) ← este issue
- [ ] Fase 5 — Implementación ETL (ETL)
- [ ] Fase 6 — Pruebas end-to-end (TEST)
- [ ] Fase 7 — Documentación del pipeline (DOCS)
- [ ] Fase 8 — Commits y Pull Request (GIT)

---

## Notas adicionales

{Cualquier contexto adicional: acuerdos, restricciones, dependencias con otros pipelines.}
