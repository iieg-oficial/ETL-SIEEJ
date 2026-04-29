---
name: pull-request-template
description: Abre el Pull Request del pipeline usando el template estandarizado del proyecto.
---

# Skill: Pull Request Template

## Purpose
Invocar en la Fase 8, después de hacer todos los commits, para abrir el PR que cierra el ciclo de desarrollo del pipeline.

## Steps

1. Leer el template en `.github/pull_request_template.md` para conocer las secciones requeridas.
2. Completar el título del PR con el formato: `feat({flujo}): pipeline {nombre del flujo}`.
3. Llenar la descripción con los cambios realizados por fase (qué se generó en cada fase).
4. Referenciar el issue correspondiente con `Closes #{numero}` en la sección de issue.
5. Completar el checklist de tipo de cambio (`feat`) y el de tareas completadas.
6. Agregar notas relevantes para el reviewer (pasos manuales pendientes, credenciales, migraciones a aplicar).
7. Asignar reviewers si aplica y abrir el PR desde la rama del pipeline hacia `develop`.

## Template

→ Ver `template.md` en esta carpeta.

## References

- Template de PR: `.github/pull_request_template.md`
