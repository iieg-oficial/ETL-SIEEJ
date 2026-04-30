---
name: issue-template
description: Crea el GitHub Issue estandarizado para un nuevo pipeline ETL usando el template del proyecto.
---

# Skill: Issue Template

## Purpose
Invocar en la Fase 4 para registrar el pipeline en el tracker del proyecto antes de comenzar el desarrollo.

## Steps

1. Leer el template en `.github/ISSUE_TEMPLATE/new-pipeline.md` para conocer las secciones requeridas.
2. Completar el título con el formato: `[PIPELINE] {Nombre del flujo en mayúsculas}`.
3. Llenar cada sección del template con la información del contexto (fuente, frecuencia, tablas destino, credenciales necesarias).
4. Asignar las etiquetas `new-pipeline` y `feat` (definidas en `.github/labels.yaml`).
5. Crear el issue vía `gh issue create` y capturar el número asignado.
6. Usar el número de issue para construir el nombre de la rama: `{numero}-pipeline-{flujo}`.

## References

- Template de issue: `.github/ISSUE_TEMPLATE/new-pipeline.md`
- Labels disponibles: `.github/labels.yaml`
