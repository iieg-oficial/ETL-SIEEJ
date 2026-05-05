---
name: issue-template
description: Use when DEA needs to create the tracking issue for a new ETL pipeline from the local skill template.
---

# Skill: Issue Template

## Purpose
Use this skill during the DEA Git phase to draft the pipeline issue and create the branch seed.

## Steps

1. Read `template.md` in this folder first.
2. Fill every section only with confirmed planning data.
3. Keep the title format as `[PIPELINE] {Nombre del flujo}`.
4. Keep the labels `new-pipeline, feat` unless the user explicitly requests otherwise.
5. Create the issue and capture the assigned number.
6. Use the issue number to build the branch name: `{numero}-pipeline-{flujo}`.

## Template

See `template.md` in this folder.

## References

- Canonical issue template for sync reference: `.github/ISSUE_TEMPLATE/new-pipeline.md`
- Available labels: `.github/labels.yaml`
