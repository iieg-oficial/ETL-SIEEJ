---
name: git-pipeline-commits
description: Use when preparing atomic commits for a pipeline implementation with the repository commit convention.
---

# Skill: Git Pipeline Commits

## Purpose
Use this skill in the DEA Git phase to create atomic commits with consistent conventional messages.

## Steps

1. Verify that the files to commit do not include `.env`, raw data (`.csv`, `.xlsx`), `.pyc`, or unwanted generated files. Review `git status` and compare against `.gitignore`.
2. Run `ruff check` on the Python files included in the commit.
3. Stage only the files that belong to the current change set. Never use `git add .`.
4. Write the commit message using the convention from the table below.
5. Run the commit and review the pre-commit output. If Ruff fails, fix the errors and repeat from step 2.
6. Repeat per feature until the branch is fully committed.

## Commit types

| Type       | When to use it                                        | Example message                                            |
|------------|-------------------------------------------------------|------------------------------------------------------------|
| `feat`     | New pipeline file or feature                          | `feat({flujo}): add extract stage`                         |
| `feat`     | New Airflow DAG                                       | `feat({flujo}): add airflow dag bootstrap and update`      |
| `feat`     | New Flyway migration                                  | `feat({flujo}): add V1 catalogs migration`                |
| `feat`     | New `schemas.py`                                      | `feat({flujo}): add sqlalchemy models`                     |
| `fix`      | Stage bug fix                                         | `fix({flujo}): handle null values in transform stage`     |
| `fix`      | Migration fix                                         | `fix({flujo}): correct column type in V3 migration`        |
| `chore`    | Dependencies, `.env.example`, or config updates       | `chore({flujo}): update requirements and env example`       |
| `docs`     | Pipeline README                                       | `docs({flujo}): add pipeline readme and er diagram`        |
| `test`     | Validation script or testing report                   | `test({flujo}): add eda script and report`                  |
| `refactor` | Behavior-preserving restructuring                     | `refactor({flujo}): split load stage into helpers`         |

**Message rules:**
- Format: `{tipo}({scope}): {imperative description in English}`.
- The scope is the pipeline name, not the component.
- Keep the description lowercase, with no trailing period, and at most 72 characters.
- The project uses commitlint, so an invalid message format will block the push.
