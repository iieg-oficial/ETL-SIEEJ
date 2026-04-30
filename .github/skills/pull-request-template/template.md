## Issue

Closes #{numero_issue}

---

## Qué se hizo

Implementación del pipeline ETL `{flujo}` con las siguientes fases:

- **Fase 1 (EDA):** Script `eda_{flujo}.py` y `reporte_eda.json` generados.
- **Fase 2 (DB):** Migraciones V1–V4 aplicadas. Modelos SQLAlchemy en `schemas.py`. Diagrama ER en `assets/`.
- **Fase 5 (ETL):** Stages `extract`, `transform`, `load` implementados. DAG `etl_{flujo}.py` creado.
- **Fase 6 (Test):** Pipeline probado en modo bootstrap. {N} registros insertados en `stg_{flujo}`.
- **Fase 7 (Docs):** `README.md` del pipeline generado.

---

## Tipo

- [x] `feat` - Nueva funcionalidad
- [ ] `bug` - Corrección
- [ ] `refactor` - Refactorización
- [ ] `docs` - Documentación

---

## Tareas completadas

- [x] EDA ejecutado y `reporte_eda.json` generado
- [x] Migraciones Flyway aplicadas sin errores
- [x] `schemas.py` en sincronía con las migraciones
- [x] Stages ETL implementados (extract / transform / load)
- [x] DAG de Airflow creado (bootstrap + update)
- [x] Pipeline ejecutado en modo bootstrap sin errores
- [x] BD validada con `just psql` — tablas pobladas correctamente
- [x] `README.md` del pipeline completado
- [x] `.env.example` actualizado
- [x] Commits atómicos con mensajes convencionales
- [x] `ruff check` pasado en todos los archivos Python

---

## Checklist de revisión de código

- [ ] No hay credenciales ni archivos `.env` commiteados
- [ ] No hay datos crudos (`.csv`, `.xlsx`) commiteados
- [ ] Los imports siguen el orden: stdlib → third-party → local
- [ ] No hay `print()` en el código de producción (solo `logging`)
- [ ] Los tipos de dato SQL coinciden con los modelos SQLAlchemy
- [ ] La vista `v_{flujo}` es consultable sin errores

---

## Notas para el reviewer

{Indicar si hay pasos manuales pendientes antes de hacer merge: credenciales necesarias, migraciones a aplicar en staging/producción, configuración del FDW, etc.}
