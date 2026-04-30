---
name: git-pipeline-commits
description: Define la convención de commits para la implementación de pipelines ETL en este proyecto.
---

# Skill: Git Pipeline Commits

## Purpose
Invocar en la Fase 8 para generar commits atómicos y con mensajes consistentes antes de abrir el Pull Request.

## Steps

1. Verificar que los archivos a commitear no incluyan `.env`, datos crudos (`.csv`, `.xlsx`), `.pyc` ni archivos generados no deseados. Revisar con `git status` y comparar con `.gitignore`.
2. Ejecutar `ruff check` sobre los archivos Python del commit: `ruff check <archivos>`.
3. Hacer `git add` de los archivos específicos del cambio. Nunca `git add .`.
4. Escribir el mensaje de commit siguiendo la convención de la tabla de abajo.
5. Ejecutar el commit y revisar el output del pre-commit. Si Ruff falla, corregir los errores y repetir desde el paso 2.
6. Repetir por cada funcionalidad hasta tener todos los cambios commiteados.

## Template

Tipos de commit válidos y ejemplos aplicados al contexto ETL:

| Tipo       | Cuándo usar                                           | Ejemplo de mensaje                                          |
|------------|-------------------------------------------------------|------------------------------------------------------------|
| `feat`     | Nuevo archivo de pipeline o funcionalidad             | `feat({flujo}): add extract stage`                         |
| `feat`     | Nuevo DAG de Airflow                                  | `feat({flujo}): add airflow dag bootstrap and update`      |
| `feat`     | Nueva migración Flyway                                | `feat({flujo}): add V1 catalogs migration`                  |
| `feat`     | Nuevo schemas.py                                      | `feat({flujo}): add sqlalchemy models`                      |
| `fix`      | Corrección de bug en un stage                         | `fix({flujo}): handle null values in transform stage`      |
| `fix`      | Corrección de migración                               | `fix({flujo}): correct column type in V3 migration`         |
| `chore`    | Actualización de dependencias, .env.example, config   | `chore({flujo}): update requirements and env example`      |
| `docs`     | README del pipeline                                   | `docs({flujo}): add pipeline readme and er diagram`         |
| `test`     | Script de prueba o reporte de testing                 | `test({flujo}): add eda script and report`                  |
| `refactor` | Reestructuración sin cambio de comportamiento         | `refactor({flujo}): split load stage into helpers`          |

**Reglas del mensaje:**
- Formato: `{tipo}({scope}): {descripcion imperativa en ingles}`
- El scope es el nombre del flujo, no el componente.
- Descripción en minúsculas, sin punto final, máximo 72 caracteres.
- El proyecto usa commitlint; un mensaje fuera del formato bloqueará el push.
